define("string",["require", "exports", "module"], function(require, exports, module) {
    "use strict";
exports.uCaseFirst = function(str) {
    return str.substr(0, 1).toUpperCase() + str.substr(1);
};
exports.trim = function(str) {
    return str.replace(/[\s\n\r]*$/, "").replace(/^[\s\n\r]*/, "");
};
exports.repeat = function(str, times) {
    return new Array(times + 1).join(str);
};
exports.count = function(str, substr){
    return str.split(substr).length - 1;
};
 
});

