define(["require", "exports", "module"], function(require, exports, module) {
    main.consumes = ["Plugin"];
    main.provides = ["utils"];
    return main;

    function main(options, imports, register) {
        var Plugin = imports.Plugin;

        var plugin = new Plugin("Ajax.org", main.consumes);
        var emit = plugin.getEmitter();

        plugin.escapeXpathString = function(name) {
            if (!name)
                return "";
        
            if (name.indexOf('"') > -1) {
                var out = [];
                var parts = name.split('"');
                parts.each(function(part) {
                    out.push(part === "" ? "'\"'" : '"' + part + '"');
                });
                return "concat(" + out.join(", ") + ")";
            }
            return '"' + name + '"';
        };

        var SupportedIcons = {
            "c9search": "page_white_magnify",
            "js": "page_white_code",
            "jsx": "page_white_code_red",
            "ts": "page_white_code",
            "tsx": "page_white_code_red",
            "json": "page_white_code",
            "css": "css",
            "scss": "css",
            "sass": "css",
            "less": "css",
            "xml": "page_white_code_red",
            "svg": "page_white_picture",
            "php": "page_white_php",
            "phtml": "page_white_php",
            "html": "html",
            "xhtml": "html",
            "coffee": "page_white_cup",
            "py": "page_white_code",
            "go": "page_white_code",
            "java": "page_white_cup",
            "logic": "logiql",
            "ru": "page_white_ruby",
            "gemspec": "page_white_ruby",
            "rake": "page_white_ruby",
            "rb": "page_white_ruby",
            "c": "page_white_c",
            "cc": "page_white_c",
            "cpp": "page_white_cplusplus",
            "cxx": "page_white_c",
            "h": "page_white_h",
            "hh": "page_white_h",
            "hpp": "page_white_h",
            "bmp": "image",
            "djv": "image",
            "djvu": "image",
            "gif": "image",
            "ico": "image",
            "jpeg": "image",
            "jpg": "image",
            "pbm": "image",
            "pgm": "image",
            "png": "image",
            "pnm": "image",
            "ppm": "image",
            "psd": "image",
            "svgz": "image",
            "tif": "image",
            "tiff": "image",
            "xbm": "image",
            "xpm": "image",
            "pdf": "page_white_acrobat",
            "clj": "page_white_code",
            "ml": "page_white_code",
            "mli": "page_white_code",
            "cfm": "page_white_coldfusion",
            "sql": "page_white_database",
            "db": "page_white_database",
            "sh": "page_white_wrench",
            "bash": "page_white_wrench",
            "xq": "page_white_code",
            "xz": "page_white_zip",
            "gz": "page_white_zip",
            "bz": "page_white_zip",
            "zip": "page_white_zip",
            "tar": "page_white_zip",
            "rar": "page_white_compressed",
            "exe": "page_white_swoosh",
            "o": "page_white_swoosh",
            "lnk": "page_white_swoosh",
            "txt": "page_white_text",
            "settings": "page_white_gear",
            "run": "page_white_gear",
            "build": "page_white_gear",
            "gitignore": "page_white_gear",
            "profile": "page_white_gear",
            "bashrc": "page_white_gear",
        };

        plugin.getFileIcon = function(name) {
            var icon = "page_white_text";
            var ext;
        
            if (name) {
                ext = name.split(".").pop().toLowerCase();
                icon = SupportedIcons[ext] || "page_white_text";
            }
            return icon;
        };
        
        plugin.getFileIconCss = function(staticPrefix) {
            function iconCss(name, icon) {
                return ".filetree-icon." + name + "{background-image:"
                    +"url(\"" + staticPrefix + "/icons/" + (icon || name) + ".png\")}";
            }
            var css = "";
            var added = {};
            for (var i in SupportedIcons) {
                var icon = SupportedIcons[i];
                if (!added[icon]) {
                    css += iconCss(icon) + "\n";
                    added[icon] = true;
                }
            }
            return css;
        };

        plugin.stableStringify = function(obj, replacer, spaces) {
            var sortByKeys = function(obj) {
                if (!obj || typeof obj != "object" || Array.isArray(obj)) {
                    return obj;
                }
                var sorted = {};
                Object.keys(obj).sort().forEach(function(key) {
                    sorted[key] = sortByKeys(obj[key]);
                });
                // assert(_.isEqual(obj, sorted));
                return sorted;
            };
            return JSON.stringify(sortByKeys(obj), replacer, spaces);
        };
        
        plugin.escapeRegExp = function(str) {
            return str.replace(/[-[\]{}()*+?.,\\^$|#\s"']/g, "\\$&");
        };

        plugin.escapeHTML = function(str) {                                       
        	return str.replace(/&/g,'&amp;').replace(/>/g,'&gt;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
        };

        plugin.escapeXml = window.apf ? apf.escapeXML : plugin.escapeHTML;

        plugin.nextFrame = window.requestAnimationFrame ||
            window.mozRequestAnimationFrame || window.webkitRequestAnimationFrame ||
            window.msRequestAnimationFrame || window.oRequestAnimationFrame;
    
        if (plugin.nextFrame) {
            plugin.nextFrame = plugin.nextFrame.bind(window);
        } else {
            plugin.nextFrame = function(callback) {
                setTimeout(callback, 17);
            };
        }

        plugin.shadeColor = function(base, factor) {
            var m = base.match(/(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);
            if (!m) {
                m = base.match(/(\w\w)(\w\w)(\w\w)/);
                if (!m) {
                    m = base.match(/(\w)(\w)(\w)/);
                    if (!m)
                        return base; // not a color
                    m = [0, m[1] + m[1], m[2] + m[2], m[3] + m[3]];
                }
                m = [0, parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
            }
            
            var R = m[1], G = m[2], B = m[3];
            
            return {
                isLight: (0.2126 * R + 0.7152 * G + 0.0722 * B) > 150,
                color: "rgb(" + parseInt(R * factor, 10) + ", " 
                    + parseInt(G * factor, 10) + ", " 
                    + parseInt(B * factor, 10) + ")"
            };
        };

        var reHome = new RegExp("^" + plugin.escapeRegExp("/home/ubuntu"));
        plugin.normalizePath = function(path){
            if (!path || path.charAt(0) == "~") return path;
            return ("/" + path.replace(/^[\/]+/, "")).replace(reHome, "~");
        };

        plugin.extend = function(dest, src) {
            var prop, i, x = !dest.notNull;
            if (arguments.length == 2) {
                for (prop in src) {
                    if (x || src[prop])
                        dest[prop] = src[prop];
                }
                return dest;
            }
    
            for (i = 1; i < arguments.length; i++) {
                src = arguments[i];
                for (prop in src) {
                    if (x || src[prop])
                        dest[prop] = src[prop];
                }
            }
            return dest;
        };

        plugin.getcookie = function(objname) {
        	var arrstr = document.cookie.split("; ");
        	for(var i = 0;i < arrstr.length;i ++){
        	var temp = arrstr[i].split("=");
        	if(temp[0] == objname) return unescape(temp[1]);
        	}
        }

        register(null, {
        	utils: plugin
        });
    }
});