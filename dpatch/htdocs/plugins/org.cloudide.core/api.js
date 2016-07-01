define(["require", "exports", "module"], function(require, exports, module) {
    main.consumes = ["Plugin", "http", "utils"];
    main.provides = ["api"];
    return main;

    function main(options, imports, register) {
        var Plugin = imports.Plugin;
        var http = imports.http;
        var utils = imports.utils;

        var plugin = new Plugin("Ajax.org", main.consumes);
        var apiUrl = options.apiUrl || "";
        var pid = options.projectId || 0;

        Plugin.instance.api = plugin;

        var REST_METHODS = ["get", "post", "put", "delete", "patch"];

        function wrapMethod(urlPrefix, method) {
            return function(url, options, callback) {
                url = apiUrl + urlPrefix + url;
                if (!callback) {
                    callback = options;
                    options = {};
                }
                var headers = options.headers = options.headers || {};
                headers.Accept = headers.Accept || "application/json";
                if (method != "get")
                    headers["X-CSRFToken"] = headers["X-CSRFToken"] || utils.getcookie('csrftoken');
                options.method = method.toUpperCase();
                if (!options.timeout)
                    options.timeout = 60000;
                    
                http.request(url, options, function(err, data, res) {
                    if (err) {
                        err = (data && data.error) || err;
                        err.message = err.message || String(err);
                        return callback(err, data, res);
                    }
                    callback(err, data, res);
                });
            };
        }

        function apiWrapper(urlPrefix, methods) {
            var wrappers = (methods || REST_METHODS).map(wrapMethod.bind(null, urlPrefix));
            var wrappedApi = {};
            for (var i = 0; i < wrappers.length; i++)
                wrappedApi[REST_METHODS[i]] = wrappers[i];
            return wrappedApi;
        }

        var settings = apiWrapper("/settings/");
        var vfs = apiWrapper("/vfs/");

        plugin.freezePublicAPI({
            get apiUrl() { return apiUrl; },
            
            apiWrapper: apiWrapper,

            settings: settings,
            vfs: vfs
        });

        register(null, {
        	api: plugin
        });
    }
});