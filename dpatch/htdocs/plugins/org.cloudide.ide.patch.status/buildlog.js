define(function(require, exports, module) {
    main.consumes = ["Panel", "ui", "patch", "patch.editor", "utils"];
    main.provides = ["patch.buildlog"];
    return main;

    function main(options, imports, register) {
        var Panel = imports.Panel;
        var ui = imports.ui;
        var editor = imports["patch.editor"];
        var patch = imports.patch;
        var utils = imports.utils;

        var plugin = new Panel("(Company) Name", main.consumes, {
        	index: 100,
        	height: 250,
        	caption: "Build Log",
        	minHeight: 130,
        	where: "bottom"
        });

        var contentNode;

        var loaded = false;
        function load(){
            if (loaded) return false;
            loaded = true;

        }

        var drawn = false;
        function draw(e) {
            if (drawn) return;
            drawn = true;
            
            // Create UI elements
            ui.insertHtml(e.html, require("text!./buildlog.html"), plugin);

            contentNode = e.html.querySelector("pre");

            editor.on("changeSelection", function (e) {
            	var node = e.node;
            	
          	    contentNode.innerHTML = utils.escapeXml(node.buildlog);
            });
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

        register(null, {
        	"patch.buildlog": plugin
        });
    }
});