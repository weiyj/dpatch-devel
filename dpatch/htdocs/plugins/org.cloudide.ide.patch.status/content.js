define(function(require, exports, module) {
    main.consumes = ["Panel", "ui", "patch", "patch.editor", "engine.editor", "utils"];
    main.provides = ["patch.content"];
    return main;

    function main(options, imports, register) {
        var Panel = imports.Panel;
        var ui = imports.ui;
        var editor = imports["patch.editor"];
        var eeditor = imports["engine.editor"];
        var patch = imports.patch;
        var utils = imports.utils;

        var plugin = new Panel("Wei Yongjun", main.consumes, {
            index: 100,
            height: 250,
            caption: "Content",
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
            ui.insertHtml(e.html, require("text!./content.html"), plugin);

            ui.insertCss(require("text!./style.css"), plugin);

            contentNode = e.html.querySelector("pre");

            editor.on("changeSelection", function (e) {
                var node = e.node;
                
                if (node && node.content) {
                    if (node.content.length != 0)
                        contentNode.innerHTML = utils.escapeXml(node.content);
                    else
                        contentNode.innerHTML = utils.escapeXml(node.report);
                } else {
                    contentNode.innerHTML = "";
                }
            });

            eeditor.on("changeSelection", function (e) {
                var node = e.node;
                
                if (node && node.content) {
                    if (node.content.length != 0)
                        contentNode.innerHTML = utils.escapeXml(node.content);
                    else
                        contentNode.innerHTML = utils.escapeXml(node.report);
                } else {
                    contentNode.innerHTML = "";
                }
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
            "patch.content": plugin
        });
    }
});