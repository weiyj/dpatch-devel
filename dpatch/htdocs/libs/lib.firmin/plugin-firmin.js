module.exports = function setup(options, imports, register) {
    var base = __dirname + "/www";
    var statics = imports["httpd.static"];

    statics.addStatics([{
        path: base,
        mount: "/lib",
        rjs: {
            "firmin": "/lib/firmin-1.0.0-min"
        }
    }]);

    register(null, {
        "lib.firmin": {}
    });
};