define(function(require, exports, module) {
    main.consumes = ["Plugin", "http"];
    main.provides = ["vfs"];
    return main;

    function main(options, imports, register) {
        var Plugin = imports.Plugin;
        var http = imports.http;

        var plugin = new Plugin("Ajax.org", main.consumes);
        var emit = plugin.getEmitter();
        //var Socket = require("socket.io");

        var buffer = [];
        var eioOptions, connection, consumer, vfs;

        var region, vfsBaseUrl, homeUrl, projectUrl, pingUrl, serviceUrl;

        var loaded = false;
        function load(){
            if (loaded) return false;
            loaded = true;
            
            emit("connect");
            /*
            connection = Socket(options.server || location.host);
            
            connection.on("connect", onConnect);
            connection.on("disconnect", onDisconnect);

            connection.on('error', function () {
        		emit("error");
        	});

            connection.on('reconnect', function () {
        		emit("reconnect");
        	});

            connection.on('reconnecting', function () {
        		emit("reconnecting");
        	});

            connection.on('disconnect', function () {
        		emit("disconnect");
        	});*/

        }

        function emptyBuffer(){
            var b = buffer;
            buffer = [];
            b.forEach(function(item) {
                if (!item) return;
                
                var xhr = rest.apply(null, item);
                if (item.length > 3)
                    item[3].abort = xhr.abort.bind(xhr);
            });
        }

        function join(a, b) {
            return (a || "").replace(/\/?$/, "/") + (b || "").replace(/^\//, "");
        }
        
        function vfsUrl(path) {
            // resolve home and project url
            return path.charAt(0) == "~"
                ? join(homeUrl, escape(path.slice(1)))
                : join(projectUrl, escape(path));
        }

        function rest(path, options, callback) {
            /*if (!vfs || !connection || connection.readyState != "open") {
                // console.error("[vfs-client] Cannot perform rest action for ", path, " vfs is disconnected");
                var stub = { abort: function(){ buffer[this.id]= null; } };
                stub.id = buffer.push([path, options, callback, stub]) - 1;
                return stub;
            }*/
            
            // resolve home and project url
            var url = vfsUrl(path);

            options.overrideMimeType = options.contentType || "application/json";
            options.contentType = options.contentType || "application/json";

            return http.request(url, options, function(err, data, res) {
                var reErrorCode = /(ENOENT|EISDIR|ENOTDIR|EEXIST|EACCES|ENOTCONNECTED)/;
                
                if (err) {
                    var isConnected = !connection || connection.readyState == "open";
                    if (err.code === 499 || (err.code === 0) && !isConnected) {
                        if (isConnected)
                            buffer.push([path, options, callback]);
                        else
                            rest(path, options, callback);
                        return;
                    }
                    
                    if (!res) return callback(err);
                    
                    var message = (res.body || "").replace(/^Error:\s+/, "");
                    var code = res.status === 0
                        ? "ENOTCONNECTED"
                        : message.match(reErrorCode) && RegExp.$1;
                    
                    err = new Error(res.body);
                    err.code = code || undefined;
                    err.status = res.status;
                    return callback(err);
                }
                callback(null, data, res);
            });
        }

        function onConnect() {
        	emit("connect");
        }

        function onDisconnect() {
            emit("disconnect");
        }

        plugin.on("load", function(){
            load();
        });

        plugin.freezePublicAPI({
            get connection(){ return true;/*connection; */},
            get connected(){ return true; },
            rest: rest
        });

        register(null, {
            vfs: plugin
        });
    }
});