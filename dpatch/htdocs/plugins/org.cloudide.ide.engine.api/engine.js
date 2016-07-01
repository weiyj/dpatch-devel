define(function(require, exports, module) {
    main.consumes = ["Plugin", "api"];
    main.provides = ["engine"];
    return main;

    function main(options, imports, register) {
        var Plugin = imports.Plugin;
        var api = imports.api;

        var plugin = new Plugin("Ajax.org", main.consumes);

        var engines = api.apiWrapper('/engine/');

        plugin.freezePublicAPI({
        	engines: engines
        });

        register(null, {
        	engine: plugin
        });
    }
});