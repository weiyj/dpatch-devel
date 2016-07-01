var start = Date.now();

require(["architect"], function (Architect) {
	Architect.resolveConfig(plugins, function (err, config) {
        if (err)
            throw err;

        var app = Architect.createApp(config, function(err) {
            if (err) throw err;
            console.log("Application started");
        });

        app.on("error", function(err){
            throw err;
        });

        app.on("service", function(name, plugin) {
            if (!plugin.name) {
                plugin.name = name;
            }

            console.log("Service loaded " + name);
        });

        app.once("ready", function() {
            if (app.services.configure)
                app.services.configure.services = app.services;

            //app.services.main.ready();
            console.warn("Total Load Time: ", Date.now() - start);
        });
        
    });
});
