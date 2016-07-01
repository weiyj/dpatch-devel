define(function(require, exports, module) {
    main.consumes = [
        "Plugin", "layout", "commands", "menus", "settings", "ui", 
        "tabManager", "dialog.error", "utils", "patch", "engine"
    ];
    main.provides = ["filesave"];
    return main;

    function main(options, imports, register) {
        var Plugin = imports.Plugin;
        var commands = imports.commands;
        var tabManager = imports.tabManager;
        var menus = imports.menus;
        var ui = imports.ui;
        var patch = imports.patch;
        var engine = imports.engine;
        var showError = imports["dialog.error"].show;
        var utils = imports.utils;

        var plugin = new Plugin("Ajax.org", main.consumes);
        var emit = plugin.getEmitter();

        var loaded = false;
        function load(){
            if (loaded) return false;
            loaded = true;

            function available(editor) {
                return !!editor && (!tabManager.focussedTab
                    || typeof tabManager.focussedTab.path == "string");
            }

            commands.addCommand({
                name: "save",
                hint: "save the currently active file to disk",
                bindKey: {mac: "Command-S", win: "Ctrl-S"},
                isAvailable: available,
                exec: function () {
                    save(null, null, function(){});
                }
            }, plugin);

            menus.addItemByPath("File/~", new ui.divider(), 600, plugin);
            
            menus.addItemByPath("File/Save", new ui.item({
                command: "save"
            }), 700, plugin);

        }
        
        function savePatch(tab, id, value) {
        	console.log("savePatch id: " + id + ' value: ' + value.substring(0, 10));
        	patch.patchs.put('content/' + id + '/', {
		    	"body": JSON.stringify({'content': value})
        	}, function (err, data, res) {
        		if (err) {
                  	showError("Failed to save patch");
        		} else {
                  	showError("Success to save patch");
                  	tab.close();
        		}
        	});
        }
        
        function saveFile(tab, id, value) {
        	console.log("saveFile id: " + id + ' value: ' + value.substring(0, 10));
        	patch.patchs.put('file/' + id + '/', {
		    	"body": JSON.stringify({'content': value})
        	}, function (err, data, res) {
        		if (err) {
                  	showError("Failed to save patch file");
        		} else {
                  	showError("Success to save patch file");
                  	tab.close();
        		}
        	});
        }

        function saveCocciScript(tab, id, value) {
        	engine.engines.put('coccinelle/file/' + id + '/', {
		    	"body": JSON.stringify({'content': value})
        	}, function (err, data, res) {
        		if (err) {
                  	showError("Failed to save coccinelle script");
        		} else {
                  	showError("Success to save coccinelle script");
                  	tab.close();
        		}
        	});
        }

        function save(tab, options, callback) {
            if (!tab && !(tab = tabManager.focussedTab)) {
                return;
            }

            var doc = tab.document;
            if (!doc.changed) {
            	tab.close();
            	return;
            }

            if (tab.options.tabtype == 'patch')
            	savePatch(tab, tab.options.patchid, doc.value)
            else if (tab.options.tabtype == 'file')
            	saveFile(tab, tab.options.patchid, doc.value)
            else if (tab.options.tabtype == 'checkcoccinelle')
            	saveCocciScript(tab, tab.options.patchid, doc.value)
            else
            	console.log('unknow type' + tab.options.tabtype);
        }
        /***** Lifecycle *****/
        
        plugin.on("load", function(){
            load();
        });
        plugin.on("enable", function(){
            btnSave && btnSave.enable();
        });
        plugin.on("disable", function(){
        });
        plugin.on("unload", function(){
            loaded = false;
        });

        register(null, {
        	filesave: plugin
        });
    }
});