define(function(require, exports, module) {
    main.consumes = ["Plugin", "api"];
    main.provides = ["patch"];
    return main;

    function main(options, imports, register) {
        var Plugin = imports.Plugin;
        var api = imports.api;

        var plugin = new Plugin("Ajax.org", main.consumes);

        var tags = api.apiWrapper('/repository/tags', ["get"]);
        var patchs = api.apiWrapper('/patch/');

        plugin.freezePublicAPI({
        	tags: tags,
        	patchs: patchs
        });

        register(null, {
            patch: plugin
        });
    }
});