define(function(require, exports, module) {
    main.consumes = ["Panel", "ui", "layout", "engine", "app", "dialog.error",
                     "tabManager"];
    main.provides = ["engine.navigate"];
    return main;

    function main(options, imports, register) {
        var Panel = imports.Panel;
        var layout = imports.layout;
        var ui = imports.ui;
        var engine = imports.engine;
        var app = imports.app;
        var showError = imports["dialog.error"].show;
        var tabs = imports.tabManager;

        var markup = require("text!./navigate.xml");
        var Tree = require("ace_tree/tree");
        var ListData = require("./dataprovider");
        var search = require('../org.cloudide.core.ui.widgets/search');

        var plugin = new Panel("Ajax.org", main.consumes, {
            index: options.index || 200,
            width: 300,
            caption: "PatchEngine",
            buttonCSSClass: "navigate",
            minWidth: 150,
            where: options.where || "left"
        });
        var emit = plugin.getEmitter();

        var winEngineFilter, txtEngineFilter, tree, ldSearch;
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
            
            var treeParent = plugin.getElement("engineList");
            txtEngineFilter = plugin.getElement("txtEngineFilter");
            winEngineFilter = options.aml;

            tree = new Tree(treeParent.$int);
            ldSearch = new ListData(arrayCache);
            ldSearch.search = search;

            tree.setDataProvider(ldSearch);

            tree.renderer.setScrollMargin(0, 10);

            layout.on("resize", function(){ tree.resize() }, plugin);

            tree.textInput = txtEngineFilter.ace.textInput;

            txtEngineFilter.ace.commands.addCommands([
                {
                    bindKey: "Enter",
                    exec: function(){ openEngineList(true); }
                }
            ]);
            
            setTimeout(function(){
            	txtEngineFilter.focus();
            	tree.resize();
            }, 10);

            tree.on("click", function(ev) {
                var e = ev.domEvent;
                if (!e.shiftKey && !e.metaKey  && !e.ctrlKey  && !e.altKey)
                if (tree.selection.getSelectedNodes().length === 1)
                	openEngineList(true);
            });

        }

        function formatEngine(engine) {
        	nengine = {
        		"id": engine.id,
        		"name": engine.name,
        		"total": engine.total,
        		"status": engine.status
        	}

        	return JSON.stringify(nengine);
        }

        function updateEngineList() {
        	engine.engines.get('engines/', {}, function (err, data, res) {
        		if (err) {
        			showError("Failed to get engines list");
        		} else {
                	arrayCache = [];
                	for (var idx in data) {
                		arrayCache.push(formatEngine(data[idx]));
                	}

        			if (ldSearch)
        			    ldSearch.updateData(arrayCache);
        		}
        	});
        }

        function focusOpenEngineEditor(name){
            var pages = tabs.getTabs();
            for (var i = 0, tab = pages[i]; tab; tab = pages[i++]) {
                if (tab.editorType == "engineeditor" && tab.name == name) {
                    tabs.focusTab(tab);
                    return true;
                }
            }
        }

        function openEngineList(noanim, nohide) {
            var nodes = tree.selection.getSelectedNodes();
            var cursor = tree.selection.getCursor();

            for (var i = 0, l = nodes.length; i < l; i++) {
                var id = nodes[i].id;
                if (!id) continue;
                
                var node = JSON.parse(id);
                var path = node.name;
                var eid = node.id;
                var focus = id === cursor.id;

                if (!focusOpenEngineEditor(path)) {
                    var fn = function(){};
                    tab = tabs.open({
                        name: path,
                        eid: eid,
                        editorType: 'engineeditor',
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
        	updateEngineList();
        else
            app.once("connect", updateEngineList);

        register(null, {
        	"engine.navigate": plugin
        });
    }
});