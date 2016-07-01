define(function(require, module, exports) {
    main.consumes = ["Dialog", "utils"];
    main.provides = ["dialog.patchinfo"];
    return main;
    
    function main(options, imports, register) {
        var Dialog = imports.Dialog;
        var utils = imports.utils;

        var plugin = new Dialog("Ajax.org", main.consumes, {
            name: "dialog.patchinfo",
            allowClose: true,
            modal: true,
            elements: [
                { type: "button", id: "ok", caption: "OK", visible: true, hotkey: "ESC" }
            ]
        });

        function escapeHTML(str) {                                       
        	return str.replace(/&/g,'&amp;').replace(/>/g,'&gt;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
        };

        function show(title, msg, html, width) {
        	html = html || 0;
        	plugin.width = width || 800;

            return plugin.queue(function(){
            	plugin.title = title;
            	plugin.heading = "";
            	if (html)
            	    plugin.body = msg;
            	else
            	    plugin.body = "<pre>" + escapeHTML(msg) + "</pre>";

            	plugin.update([
                     { id: "ok", onclick: function(){ plugin.hide(); } },
                ]);
            });
        }

        plugin.freezePublicAPI({
            show: show
        })
        
        register(null, {
            "dialog.patchinfo": plugin
        });
    }
});