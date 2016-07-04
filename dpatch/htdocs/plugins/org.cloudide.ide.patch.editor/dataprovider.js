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
        	var className = "";
    		switch (node.build) {
    		case 0:
    			node.build_txt = 'TBD';
    			className = 'build_tbd';
    			break;
    		case 1:
    			node.build_txt = 'PASS';
    			className = 'build_pass';
    			break;
    		case 2:
    			node.build_txt = 'FAIL';
    			className = 'build_fail';
    			break;
    		case 3:
    			node.build_txt = 'WARN';
    			className = 'build_warn';
    			break;
    		case 4:
    			node.build_txt = 'SKIP';
    			className = 'build_skip';
    			break;
    		}

    		switch (node.status) {
    		case 101:
    			node.status_txt = 'NEW';
        		className += ' status_new';
    			break;
    		case 102:
    			node.status_txt = 'PATCH';
        		className += ' status_patch';
    			break;
    		case 104:
    			node.status_txt = 'RENEW';
        		className += ' status_renew';
    			break;
    		case 105:
    			node.status_txt = 'REPORT';
        		className += ' status_report';
    			break;
    		case 201:
    			node.status_txt = 'READY';
        		className += ' status_pendding';
    			break;
    		case 301:
    			node.status_txt = 'MAILED';
        		className += ' status_mailed';
    			break;
    		case 401:
    			node.status_txt = 'FIXED';
        		className += ' status_fixed';
    			break;
    		case 402:
    			node.status_txt = 'REMOVED';
        		className += ' status_removed';
    			break;
    		case 403:
    			node.status_txt = 'IGNORED';
        		className += ' status_ignored';
    			break;
    		case 405:
    			node.status_txt = 'APPLIED';
        		className += ' status_applied';
    			break;
    		case 406:
    			node.status_txt = 'REJECTED';
        		className += ' status_rejected';
    			break;
    		case 407:
    			node.status_txt = 'ACCEPTED';
        		className += ' status_accepted';
    			break;
    		}
    		node.className = className;
    		node.date = node.date.substring(0, 10);
        }

        this.getClassName = function(node) {
            return (node.className || "")
                + (node.status == "loading" ? " loading" : "")
                + (node.error ? " watcherror" : "");
        };

    }).call(DataProvider.prototype);
 
    return DataProvider;
});
