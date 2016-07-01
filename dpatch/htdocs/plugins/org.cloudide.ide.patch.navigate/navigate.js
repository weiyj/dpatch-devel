define(function(require, exports, module) {
    main.consumes = ["Panel", "ui", "layout", "patch", "app", "dialog.error",
                     "tabManager"];
    main.provides = ["patch.navigate"];
    return main;

    function main(options, imports, register) {
        var Panel = imports.Panel;
        var layout = imports.layout;
        var ui = imports.ui;
        var patch = imports.patch;
        var app = imports.app;
        var showError = imports["dialog.error"].show;
        var tabs = imports.tabManager;

        var markup = require("text!./navigate.xml");
        var Tree = require("ace_tree/tree");
        var ListData = require("./dataprovider");
        var search = require('../org.cloudide.core.ui.widgets/search');

        var plugin = new Panel("Ajax.org", main.consumes, {
            index: options.index || 100,
            width: 300,
            caption: "Navigate",
            buttonCSSClass: "navigate",
            minWidth: 150,
            where: options.where || "left"
        });
        var emit = plugin.getEmitter();

        var winPatchFilter, txtPatchFilter, tree, ldSearch;
        var lastSearch;

        var arrayCache = [];

        var loaded = false;
        function load(){
            if (loaded) return false;
            loaded = true;

            app.once("ready", function(){ tree && tree.resize(); });
        }

        var drawn = false;
        function draw(options) {
            if (drawn) return;
            drawn = true;
            
            // Create UI elements
            ui.insertMarkup(options.aml, markup, plugin);
            
            // Import CSS
            ui.insertCss(require("text!./style.css"), plugin);
            
            var treeParent = plugin.getElement("navigateList");
            txtPatchFilter = plugin.getElement("txtPatchFilter");
            winPatchFilter = options.aml;

            tree = new Tree(treeParent.$int);
            ldSearch = new ListData(arrayCache);
            ldSearch.search = search;

            tree.setDataProvider(ldSearch);

            tree.renderer.setScrollMargin(0, 10);

            layout.on("resize", function(){ tree.resize() }, plugin);

            tree.textInput = txtPatchFilter.ace.textInput;

            txtPatchFilter.ace.commands.addCommands([
                {
                    bindKey: "Enter",
                    exec: function(){ openPatchList(true); }
                }
            ]);
            
            setTimeout(function(){
            	txtPatchFilter.focus();
            	tree.resize();
            }, 10);

            tree.on("click", function(ev) {
                var e = ev.domEvent;
                if (!e.shiftKey && !e.metaKey  && !e.ctrlKey  && !e.altKey)
                if (tree.selection.getSelectedNodes().length === 1)
                	openPatchList(true);
            });

        }

        function formatTag(tag) {
        	return JSON.stringify(tag);
        	//return tag.id + "||" + tag.reponame + "||" + tag.name + "||" + tag.total + "||" + tag.repoid;
        }

        function updateTagsList() {
        	patch.tags.get('', {}, function (err, data, res) {
        		if (err) {
        			showError("Failed to get tags list");
        		} else {
                	arrayCache = [];
                	for (var idx in data) {
                		arrayCache.push(formatTag(data[idx]));
                	}

        			if (ldSearch)
        			    ldSearch.updateData(arrayCache);
        		}
        	});
        }

        function focusOpenPatchEditor(name){
            var pages = tabs.getTabs();
            for (var i = 0, tab = pages[i]; tab; tab = pages[i++]) {
                if (tab.editorType == "patcheditor" && tab.name == name) {
                    tabs.focusTab(tab);
                    return true;
                }
            }
        }

        function openPatchList(noanim, nohide) {
            var nodes = tree.selection.getSelectedNodes();
            var cursor = tree.selection.getCursor();

            for (var i = 0, l = nodes.length; i < l; i++) {
                var id = nodes[i].id;
                if (!id) continue;
                
                var node = JSON.parse(id);
                var path = node.name + " " + node.reponame;
                var tagid = node.id;
                var repoid = node.reponame;
                var focus = id === cursor.id;
                
                if (!focusOpenPatchEditor(path)) {
                    var fn = function(){};
                    tab = tabs.open({
                        name: path,
                        tagid: tagid,
                        repoid: repoid,
                        editorType: 'patcheditor',
                        noanim: l > 1,
                        active: true,
                        focus: focus && (nohide ? "soft" : true)
                    }, fn);
                }
            }
        }

        /***** Lifecycle *****/
        
        plugin.on("load", function(){
            load();
        });
        plugin.on("draw", function(e) {
            draw(e);
        });
        plugin.on("enable", function(){
            
        });
        plugin.on("disable", function(){
            
        });

        if (app.connected) 
            updateTagsList();
        else
            app.once("connect", updateTagsList);

        register(null, {
        	"patch.navigate": plugin
        });
    }
});