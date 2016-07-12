define(function(require, exports, module) {
    main.consumes = ["layout", "Editor", "editors", "ui", "patch", "tabManager",
        "dialog.error", "dialog.confirm", "dialog.patchinfo", "utils", "sendwizard",
        "menus", "commands"];
    main.provides = ["patch.editor"];
    return main;

    function main(options, imports, register) {
        var layout = imports.layout;
        var Editor = imports.Editor;
        var editors = imports.editors;
        var ui = imports.ui;
        var tabs = imports.tabManager;
        var menus = imports.menus;
        var commands = imports.commands;
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

        function setMenus() {
            menus.addItemByPath("Edit/~", new ui.divider(), 2000, handle);
            menus.addItemByPath("Edit/Patch/", null, 2100, handle);
            menus.addItemByPath("Edit/Patch/Rebuild Patch", new ui.item({
                command: "patchSkipBuild"}), 100, handle);
            menus.addItemByPath("Edit/Patch/Skip Build", new ui.item({
                command: "patchSkipBuild"}), 200, handle);
            menus.addItemByPath("Edit/Patch/~", new ui.divider(), 300, handle);
            menus.addItemByPath("Edit/Patch/Move to Renew Status", new ui.item({
                command: "patchSetStatusRenew"}), 400, handle);
            menus.addItemByPath("Edit/Patch/Move to Ready Status", new ui.item({
                command: "patchSetStatusPending"}), 500, handle);
            menus.addItemByPath("Edit/Patch/Move to Mailed Status", new ui.item({
                command: "patchSetStatusMailed"}), 600, handle);
            menus.addItemByPath("Edit/Patch/~", new ui.divider(), 700, handle);
            menus.addItemByPath("Edit/Patch/Merger Patchs", new ui.item({
                command: "patchMergerPatchs"}), 800, handle);
            menus.addItemByPath("Edit/Patch/UnMerger Patch", new ui.item({
                command: "patchUnMergerPatch"}), 900, handle);
        }

        function setCommands() {
            function checkAvailable(editor, action) {
                if (editor && tabs.focussedTab && tabs.focussedTab.editorType == "patcheditor")
                    return tabs.focussedTab.editor.checkAvailable(action);
                return false;
            }

            commands.addCommand({
                name: "patchRebuild",
                isAvailable: function(editor) { return checkAvailable(editor, "rebuild"); },
                exec: function() {
                    tabs.focussedTab.editor.rebuildSelectedPatch();
                },
                passEvent: true
            }, handle);

            commands.addCommand({
                name: "patchSkipBuild",
                isAvailable: function(editor){ return checkAvailable(editor, "skipbuild"); },
                exec: function() {
                    tabs.focussedTab.editor.skipBuildSelectedPatch();
                },
                passEvent: true
            }, handle);

            commands.addCommand({
                name: "patchSetStatusRenew",
                isAvailable: function(editor){ return checkAvailable(editor, "renew"); },
                exec: function() {
                    tabs.focussedTab.editor.movePatchToRenew();
                },
                passEvent: true
            }, handle);

            commands.addCommand({
                name: "patchSetStatusPending",
                isAvailable: function(editor){ return checkAvailable(editor, "pending"); },
                exec: function() {
                    tabs.focussedTab.editor.movePatchToPending();
                },
                passEvent: true
            }, handle);

            commands.addCommand({
                name: "patchSetStatusMailed",
                isAvailable: function(editor){ return checkAvailable(editor, "mailed"); },
                exec: function() {
                    tabs.focussedTab.editor.movePatchToMailed();
                },
                passEvent: true
            }, handle);
        }

        var loaded = false;
        function load() {
            if (loaded) return false;
            loaded = true;

            draw();

            setMenus();

            setCommands();
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
                        /*btnPatchBuild = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Rebuild",
                            onclick: rebuildSelectedPatch
                        }),*/
                        btnPatchPending = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Ready",
                            onclick: movePatchToPending
                        }),
                        /*btnPatchRenew = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Renew",
                            onclick: movePatchToRenew
                        }),*/
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
                    /*
                    if (item.status == 201 || item.status == 301) {
                        btnPatchRenew.enable();
                    } else {
                        btnPatchRenew.disable();
                    }*/

                    if ((item.build == 1 || item.build == 3 || item.build == 4) && item.status == 201) {
                        btnPatchSend.enable();
                    } else {
                        btnPatchSend.disable();
                    }

                    /*if ((item.status != 101 && item.status != 102 && item.status != 104) || item.build == 0) {
                        btnPatchBuild.disable();
                    } else {
                        btnPatchBuild.enable();
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

            function refreshPatchList() {
                updatePatchList(currentDocument);
            }

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

            function movePatchToMailed() {
                var item = datagrid.selection.getCursor();

                if (!item)
                    return;

                patch.patchs.put('patches/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'status': 301})
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

            function checkAvailable(action) {
                var item = datagrid.selection.getCursor();

                if (!item)
                    return false;

                if (action == 'rebuild') {
                    if ((item.status != 101 && item.status != 102 && item.status != 104) || item.build == 0)
                        return false;
                    else
                        return true;
                } else if (action == "skipbuild") {
                    if (item.build == 1 || item.build == 3)
                        return false;
                    else
                        return true;
                } else if (action == "renew") {
                    if (item.status == 201 || item.status == 301)
                        return true;
                    else
                        return false;
                } else if (action == "pending") {
                    if ((item.build == 1 || item.build == 3 || item.build == 4) && item.status == 102)
                        return true;
                    else
                        return false;
                } else if (action == "mailed") {
                    if (item.status == 201)
                        return true;
                    else
                        return false;
                }
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
                checkAvailable: checkAvailable,
                refreshPatchList: refreshPatchList,
                deleteSelectedPatch: deleteSelectedPatch,
                rebuildSelectedPatch: rebuildSelectedPatch,
                skipBuildSelectedPatch: skipBuildSelectedPatch,
                movePatchToPending: movePatchToPending,
                movePatchToRenew: movePatchToRenew,
                movePatchToMailed: movePatchToMailed,
                movePatchToWhiteList: movePatchToWhiteList,
                sendPatchWizard: sendPatchWizard
            });

            plugin.load(null, "patcheditor");
            
            return plugin;
        }

        register(null, {
            "patch.editor": handle
        });
    }
});