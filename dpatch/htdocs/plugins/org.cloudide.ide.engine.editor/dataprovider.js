define(function(require, exports, module) {
    var oop = require("ace/lib/oop");
    var TreeData = require("ace_tree/data_provider");
    
    var DataProvider = function(root) {
        TreeData.call(this, root);
        this.rowHeight = 24;
    };
    oop.inherits(DataProvider, TreeData);
    
    (function() {
            
        this.getChildren = function(node) {
            return node.children;
        };
        
        this.hasChildren = function(node) {
            return false;
        };
        
        // this.getCaptionHTML = function(node) {
        //     if (node.tagName == "scope")
        //         return node.name || "Scope";
        //     return node.name + "";
        // };
        
        // this.updateNode = function(node) {
        //     var isOpen = node.isOpen;
        //     this.close(node, null, true);
        //     if (isOpen)
        //         this.open(node, null, true);
        // };
        
        // this.getIconHTML = function(node) {
        //     return node.className == "newwatch" ? "" : "<span class='dbgVarIcon'></span>";
        // };
        this.formatRowData = function(node) {
        	if (!node.hasOwnProperty('bugfix') || node.bugfix == false)
        		node.bugfix_txt = "FALSE";
        	else
        		node.bugfix_txt = "TRUE";
        	if (!node.hasOwnProperty('reportonly') || node.reportonly == true)
        		node.reportonly_txt = "TRUE";
        	else
        		node.reportonly_txt = "FALSE";

        	if (node.totalfile == 0) {
        		node.perfmance = "0";
        	} else {
        		node.perfmance = "" + (node.totaltime / node.totalfile);
        	}

        	if (node.status) {
        		node.status_txt = "ENABLED";
        	} else {
        		node.status_txt = "DISABLED";
        	}
        }

        this.getClassName = function(node) {
            return (node.className || "")
                + (node.status == "loading" ? " loading" : "")
                + (node.error ? " watcherror" : "");
        };

    }).call(DataProvider.prototype);
 
    return DataProvider;
});
