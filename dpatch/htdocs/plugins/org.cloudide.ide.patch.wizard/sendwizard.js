define(function(require, module, exports) {
    main.consumes = [
        "Plugin", "Wizard", "WizardPage", "ui", "dialog.error", "utils", "patch"
    ];
    main.provides = ["sendwizard"];
    return main;

    function main(options, imports, register) {
        var Wizard = imports.Wizard;
        var WizardPage = imports.WizardPage;
        var showError = imports["dialog.error"].show;
        var ui = imports.ui;
        var utils = imports.utils;
        var patch = imports.patch;

        var plugin = new Wizard("Ajax.org", main.consumes, {
            name: "sendwizard",
            title: "Send Patch",
            allowClose: true,
            class: "sendwizard",
            resizable: true,
            height: 600,
            width: 800
        });
        var emit = plugin.getEmitter();
        
        var showpatch, overview;
        var id;

        plugin.setId = function(pid) {
        	id = pid;
        }

        function load() {
            
        }

        var drawn;
        var showPatchNode, checkPatchNode, checkEmailNode, sendEmailNode;
        function draw(){
            if (drawn) return;
            drawn = true;

            showpatch = new WizardPage({ name: "showpatch" }, plugin);
            showpatch.on("draw", function(e) {
                ui.insertHtml(e.html, require("text!./pages/showpatch.html"), showpatch);

                showPatchNode = e.html.querySelector("pre");
                
            });

            showpatch.on("show", function() {
                patch.patchs.get('patches/' + id + '/', {}, function (err, data, res) {
                    if (err) {
                      	showError("Failed to get patch info");
                      	showPatchNode.innerHTML = "";
                    } else {
                    	var payload = utils.escapeHTML(data.content);
                    	showPatchNode.innerHTML = payload;
                    }
                });
            });

            checkpatch = new WizardPage({ name: "checkpatch" }, plugin);
            checkpatch.on("draw", function(e) {
                ui.insertHtml(e.html, require("text!./pages/checkpatch.html"), checkpatch);

                checkPatchNode = e.html.querySelector("pre");
            });

            checkpatch.on("show", function() {
                patch.patchs.put('sendwizard/' + id + '/checkpatch/', {
                    "body": JSON.stringify({'id': id})
                }, function (err, data, res) {
                    if (err) {
                      	showError("Failed to get patch info");
                      	checkPatchNode.innerHTML = "";
                    } else {
                    	var payload = utils.escapeHTML(data.detail);
                    	checkPatchNode.innerHTML = data.detail;
                    }
                });
            });

            checkemail = new WizardPage({ name: "checkemail" }, plugin);
            checkemail.on("draw", function(e) {
                ui.insertHtml(e.html, require("text!./pages/checkemail.html"), checkemail);

                checkEmailNode = e.html.querySelector("div.maillist");
                
            });

            checkemail.on("show", function(e) {
                patch.patchs.put('sendwizard/' + id + '/checkemail/', {
                    "body": JSON.stringify({'id': id})
                }, function (err, data, res) {
                    if (err) {
                      	showError("Failed to get patch info");
                      	checkEmailNode.innerHTML = "";
                    } else {
                    	var emails = "";
                    	for (var idx in data.emails) {
                    		emails += "<br>&nbsp;&nbsp;&nbsp;&nbsp;<font color=green><b>";
                    		emails += utils.escapeHTML(data.emails[idx]) + "</b></font>";
                    	}
                    	checkEmailNode.innerHTML = emails;
                    }
                });
            });

            sendemail = new WizardPage({ name: "sendemail" }, plugin);
            sendemail.on("draw", function(e) {
                ui.insertHtml(e.html, require("text!./pages/sendemail.html"), sendemail);

                sendEmailNode = e.html.querySelector("div");
            });

            sendemail.on("show", function(e) {
            	sendEmailNode.innerHTML = "<font color=green>Mail sending, please waiting...</font>"
                patch.patchs.put('sendwizard/' + id + '/sendemail/', {
                	"body": JSON.stringify({'id': id})
                }, function (err, data, res) {
                    if (err) {
                    	sendEmailNode.innerHTML = "<font color=red>Error send patch, please check your SMTP setting!</font>";
                    } else {
                    	sendEmailNode.innerHTML = data.detail;
                    }
                });
            });

            plugin.on("previous", function(e) {
                var page = e.activePage;
                if (page.name == "checkpatch") {
                     return showpatch;
                } else if (page.name == "checkemail") {
                	return checkpatch;
                } else if (page.name == "sendemail") {
                	return checkemail;
                }
            });

            plugin.on("next", function(e) {
                var page = e.activePage;
                
                if (page.name == "showpatch") {
                	return checkpatch;
                } else if (page.name == "checkpatch") {
                	return checkemail;
                } else if (page.name == "checkemail") {
                    plugin.showFinish = true;
                    plugin.showPrevious = false;
                    plugin.showNext = false;
                	return sendemail;
                }	
            }, plugin);

            plugin.on("finish", function(e){
            });

            plugin.startPage = showpatch;
        }

        plugin.on("draw", function() {
            draw();
        });
        
        plugin.on("load", function() {
            load();
        });
        
        plugin.on("unload", function() {
        });
        
        plugin.on("hide", function() {
        });
        
        plugin.on("show", function() {
            plugin.showFinish = false;
            plugin.showPrevious = false;
            plugin.showNext = true;
        });

        register(null, {
        	sendwizard: plugin
        });
    }
});