define(function(require, exports, module) {
    main.consumes = ["layout", "Editor", "editors", "ui", "patch", "tabManager",
        "dialog.error", "dialog.confirm", "dialog.patchinfo", "utils", "sendwizard"];
    main.provides = ["patch.editor"];
    return main;

    function main(options, imports, register) {
        var layout = imports.layout;
        var Editor = imports.Editor;
        var editors = imports.editors;
        var ui = imports.ui;
        var tabs = imports.tabManager;
        var patch = imports.patch;
        var utils = imports.utils;
        var showError = imports["dialog.error"].show;
        var confirm = imports["dialog.confirm"].show;
        var showPatchInfo = imports["dialog.patchinfo"].show;
        var sendWizard = imports.sendwizard;

        var Tree = require("ace_tree/tree");
        var TreeData = require("./dataprovider");

        var handle = editors.register("patcheditor", "PatchEditor", PatchEditor, []);
        var emit = handle.getEmitter();
        var markup = require("text!./editor.html");
        var apiPrefix = options.apiPrefix || "";

        var loaded = false;
        function load() {
            if (loaded) return false;
            loaded = true;
            
            draw();
        }

        var drawn = false;
        function draw() {
            if (drawn) return;
            drawn = true;

            // Create UI elements
            ui.insertCss(require("text!./style.css"), handle);
        };

        handle.on("load", load);

        function PatchEditor() {
            var plugin = new Editor("Ajax.org", main.consumes, []);
            //var emit = plugin.getEmitter();
            
            var container;
            var model, datagrid, filterbox;
            var currentDocument;

            plugin.on("draw", function(e) {
                draw();

                container = e.htmlNode;

                var nodes = ui.insertHtml(container, markup, plugin);
                var node = nodes[0];

                var hbox = new ui.hbox({
                    htmlNode: node,
                    padding: 5,
                    edge: "10 10 0 10",
                    childNodes: [
                        filterbox = new apf.codebox({
                            realtime: true,
                            skin: "codebox",
                            "class": "",
                            clearbutton: true,
                            focusselect: true,
                            height: 27,
                            width: 240,
                            singleline: true,
                            "initial-message": ""
                        }),
                        new ui.filler({}),
                        btnPatchNew = new ui.button({
                            skin: "btn-default-css3",
                            class: "btn-green",
                            caption: "New"
                        }),
                        btnPatchDelete = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Delete",
                            class: "btn-red",
                            onclick: deleteSelectedPatch
                        }),
                        btnPatchEdit = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Edit",
                            onclick: editSelectedPatch
                        }),
                        btnPatchEditFile = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Edit File",
                            onclick: editSelectedPatchFile
                        }),
                        btnPatchWhiteList = new ui.button({
                            skin: "btn-default-css3",
                            caption: "WhiteList",
                            class: "btn-red",
                            onclick: movePatchToWhiteList
                        }),
                        btnPatchBuild = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Rebuild",
                            onclick: rebuildSelectedPatch
                        }),
                        /*
                        btnNotBuild = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Notbuild",
                            onclick: skipBuildSelectedPatch
                        }),*/
                        btnPatchPending = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Pending",
                            onclick: movePatchToPending
                        }),
                        btnPatchRenew = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Renew",
                            onclick: movePatchToRenew
                        }),
                        btnPatchSend = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Send",
                            class: "btn-green",
                            onclick: sendPatchWizard
                        }),
                        btnPatchChangeList = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Change List",
                            class: "btn-green",
                            onclick: showFileChangeList
                        }),
                        btnPatchRefresh = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Refresh",
                            onclick: function() {
                                    updatePatchList(currentDocument);
                            }
                        })
                    ]
                });

                model = new TreeData();
                model.emptyMessage = "No data found";

                model.columns = [
                    {
                        caption: "ID",
                        value: "id",
                        width: "60"
                    },{
                        caption: "TITLE",
                        value: "title",
                        width: "40%"
                    },{
                        caption: "FILENAME",
                        value: "file",
                        width: "20%"
                    },{
                        caption: "TYPE",
                        value: "type",
                        width: "10%"
                    },{
                        caption: "GIT",
                        value: "repo",
                        width: "10%"
                    },{
                        caption: "TAG",
                        value: "tag",
                        width: "5%"
                    },{
                        caption: "DATE",
                        value: "date",
                        width: "5%"
                    },{
                        caption: "STATUS",
                        value: "status_txt",
                        width: "5%"
                    },{
                        caption: "BUILD",
                        value: "build_txt",
                        width: "5%"
                    }
                ];

                var div = node.appendChild(document.createElement("div"));
                div.style.position = "absolute";
                div.style.left = "10px";
                div.style.right = "10px";
                div.style.bottom = "10px";
                div.style.top = "50px";
                
                datagrid = new Tree(div);
                datagrid.setTheme({ cssClass: "blackdg" });
                datagrid.setDataProvider(model);
                
                var nodes = [];
                model.setRoot({children : nodes});

                layout.on("resize", function(){ datagrid.resize() }, plugin);

                datagrid.on("changeSelection", function (e){
                    var item = datagrid.selection.getCursor();

                    if (!item)
                        return;

                    if (item.status == 201 || item.status == 301 ||
                    	item.status == 405 || item.status == 407) {
                    	btnPatchDelete.disable();
                    } else {
                    	btnPatchDelete.enable();
                    }

                    if ((item.build == 1 || item.build == 3 || item.build == 4) && item.status == 102) {
                    	btnPatchPending.enable();
                    } else {
                    	btnPatchPending.disable();
                    }

                    if (item.status == 201 || item.status == 301) {
                    	btnPatchRenew.enable();
                    } else {
                    	btnPatchRenew.disable();
                    }

                    if ((item.build == 1 || item.build == 3 || item.build == 4) && item.status == 201) {
                    	btnPatchSend.enable();
                    } else {
                    	btnPatchSend.disable();
                    }

                    if ((item.status != 101 && item.status != 102 && item.status != 104) || item.build == 0) {
                    	btnPatchBuild.disable();
                    } else {
                    	btnPatchBuild.enable();
                    }

                    /*
                    if (item.build == 1 || item.build == 3) {
                    	btnNotBuild.disable();
                    } else {
                    	btnNotBuild.enable();
                    }*/

                    if (item.status != 102 && item.status != 104) {
                	    btnPatchEdit.disable();
                    } else {
                    	btnPatchEdit.enable();
                    }

                    if (item.status != 101 && item.status != 102 && item.status != 104 && item.status != 105) {
                    	btnPatchEditFile.disable();
                    } else {
                    	btnPatchEditFile.enable();
                    }

                    patch.patchs.get('patches/' + item.id + '/', {}, function (err, data, res) {
                        if (!err)
                            emit("changeSelection", { node : data });
                    });

                });
            });

            function updatePatchList(doc) {
                if (!doc)
                    return;

                var tag = doc.meta.tagid;
                
                patch.patchs.get('tags/' + tag + '/', {}, function (err, data, res) {
                    if (err) {
                        showError("Failed to get patch list");
                    } else {
                        doc.value = data;
                        for (var idx in data) {
                            model.formatRowData(data[idx]);
                        }
                        model.setRoot({children : data});
                        datagrid.resize();
                        datagrid.select(datagrid.provider.getNodeAtIndex(0));
                    }
                });
            }

            function deleteSelectedPatch() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                confirm("Delete Patch", "Are you sure to Delete this patch?",
                    item.title,
                    function() {
                        patch.patchs.delete('patches/' + item.id + '/', {
                        	"body": JSON.stringify({'id': item.id})
                        }, function (err, data, res) {
                            if (!err) {
                                updatePatchList(currentDocument);
                            } else {
                                showError("Failed to delete patch");
                            }
                        });
                    }
                );
            }

            function editSelectedPatch() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                patch.patchs.get('patches/' + item.id + '/', {
                }, function (err, data, res) {
                    if (!err) {
                        var fn = function() {};
                        tabs.open({
                            patchid: data.id,
                            path: "PATCH-" + data.id + ".patch",
                            tabtype: 'patch',
                            nofs: 1,
                            active: true,
                            value: data.content
                        },fn);
                    } else {
                        showError("Failed to get patch content");
                    }
                });
            }

            function editSelectedPatchFile() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                patch.patchs.get('file/' + item.id + '/', {
                }, function (err, data, res) {
                    if (!err) {
                        var fn = function() {};

                        tabs.open({
                            patchid: item.id,
                            tabtype: 'file',
                            path: apiPrefix + item.file,
                            nofs: 1,
                            active: true,
                            value: data.content
                        },fn);
                    } else {
                        showError("Failed to get patch file content");
                    }
                });
            }
            
            function rebuildSelectedPatch() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                patch.patchs.put('patches/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'build': 0})
                }, function (err, data, res) {
                    if (!err) {
                        updatePatchList(currentDocument);
                    } else {
                        showError("Failed to mark patch for rebuild");
                    }
                });
            }

            function skipBuildSelectedPatch() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                patch.patchs.put('patches/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'build': 4})
                }, function (err, data, res) {
                    if (!err) {
                        updatePatchList(currentDocument);
                    } else {
                        showError("Failed to mark patch for skip build");
                    }
                });
            }

            function movePatchToWhiteList() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;
                confirm("White List", "Are you sure to add this file to whitelist of " + item.type + "?",
                    item.file,
                    function() {
                        patch.patchs.put('whitelist/' + item.id + '/', {
                            "body": JSON.stringify({
                                'file': item.file,
                                'reason': 'false positive'
                            })
                        }, function (err, data, res) {
                            if (!err) {
                                updatePatchList(currentDocument);
                            } else {
                                showError("Failed to mark patch for rebuild");
                            }
                        });
                    }
                );
            }

            function movePatchToPending() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                patch.patchs.put('patches/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'status': 201})
                }, function (err, data, res) {
                    if (!err) {
                        updatePatchList(currentDocument);
                    } else {
                        showError("Failed to save patch status");
                    }
                });
            }

            function movePatchToRenew() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                patch.patchs.put('patches/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'status': 102})
                }, function (err, data, res) {
                    if (!err) {
                        updatePatchList(currentDocument);
                    } else {
                        showError("Failed to save patch status");
                    }
                });
            }

            function sendPatchWizard() {
            	var item = datagrid.selection.getCursor();
            	
            	if (!item)
            		return;

            	sendWizard.setId(item.id);
            	sendWizard.show(true);
            }

            function showFileChangeList() {
                var item = datagrid.selection.getCursor();
                
                if (!item)
                    return;

                patch.patchs.get('changelog/' + item.id + '/', {
                }, function (err, data, res) {
                    if (!err) {
                        showPatchInfo("Change List", "<pre>" + data.changlog + "</pre>", 1, 960);
                    } else {
                        showError("Failed to get patch file change list");
                    }
                });
            }

            plugin.on("documentActivate", function(e) {
                currentDocument = e.doc;
                model.setRoot({children : e.doc.value});
                datagrid.resize();
            });

            plugin.on("documentLoad", function(e) {
                var doc = e.doc;
                var tab = doc.tab;
                
                tab.backgroundColor = '#F0F0F0';
                doc.title = tab.name;
                if (tab.options.tagid !== undefined)
                    doc.meta.tagid = tab.options.tagid;
                updatePatchList(doc);
            });

            plugin.freezePublicAPI({
                
            });

            plugin.load(null, "patcheditor");
            
            return plugin;
        }

        register(null, {
            "patch.editor": handle
        });
    }
});