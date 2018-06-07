define(function(require, exports, module) {
    main.consumes = ["layout", "Editor", "editors", "ui", "engine", "tabManager",
        "dialog.error", "dialog.confirm", "utils", "sendwizard"];
    main.provides = ["engine.editor"];
    return main;

    function main(options, imports, register) {
        var layout = imports.layout;
        var Editor = imports.Editor;
        var editors = imports.editors;
        var ui = imports.ui;
        var tabs = imports.tabManager;
        var engine = imports.engine;
        var utils = imports.utils;
        var showError = imports["dialog.error"].show;
        var confirm = imports["dialog.confirm"].show;
        var jQuery = require("jquery");

        var Tree = require("ace_tree/tree");
        var TreeData = require("./dataprovider");

        var handle = editors.register("engineeditor", "EngineEditor", EngineEditor, []);
        var emit = handle.getEmitter();
        var markup = require("text!./editor.html");

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

        function EngineEditor() {
            var plugin = new Editor("Ajax.org", main.consumes, []);
            
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
                            "initial-message": "Search"
                        }),
                        new ui.filler({}),
                        btnTypeNew = new ui.button({
                            skin: "btn-default-css3",
                            class: "btn-green",
                            caption: "New",
                            onclick: newPatchType
                        }),
                        /*btnTypeImport = new ui.button({
                            skin: "btn-default-css3",
                            class: "btn-green",
                            caption: "Import"
                        }),*/
                        btnTypeExport = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Export",
                            onclick: exportPatchType
                        }),
                        btnTypeDelete = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Delete",
                            class: "btn-red",
                            onclick: deletePatchType
                        }),
                        btnTypeEdit = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Edit",
                            onclick: editPatchType
                        }),
                        btnTypeReport = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Patch",
                            onclick: changePatchReport
                        }),
                        btnTypeBugFix = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Bug Fix",
                            onclick: changePatchTypeBugfix
                        }),
                        btnTypeStatus = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Enable",
                            class: "btn-green",
                            onclick: changePatchTypeStatus
                        }),
                        btnTypeRefresh = new ui.button({
                            skin: "btn-default-css3",
                            caption: "Refresh",
                            onclick: function() {
                            	updatePatchTypeList(currentDocument);
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
                        caption: "NAME",
                        value: "name",
                        width: "15%"
                    },{
                        caption: "TITLE",
                        value: "title",
                        width: "35%"
                    },{
                        caption: "BUGFIX",
                        value: "bugfix_txt",
                        width: "10%"
                    },{
                        caption: "REPORT ONLY",
                        value: "reportonly_txt",
                        width: "10%"
                    },{
                        caption: "PERFMANCE",
                        value: "perfmance",
                        width: "10%"
                    },{
                        caption: "STATUS",
                        value: "status_txt",
                        width: "10%"
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

                    if (item.engine == 'checkcoccinelle') {
                    	btnTypeNew.enable();
                    	//btnTypeImport.enable();
                    	btnTypeExport.enable();
                    	btnTypeEdit.enable();
                    	btnTypeBugFix.enable();
                    } else {
                    	btnTypeNew.disable();
                    	//btnTypeImport.disable();
                    	btnTypeExport.disable();
                    	btnTypeEdit.disable();
                    	btnTypeBugFix.disable();
                    }

                    if (item.status == true) {
                    	btnTypeStatus.setCaption("Disable");
                    	btnTypeStatus.setAttribute("class", "btn-red");
                    } else {
                    	btnTypeStatus.setCaption("Enable");
                    	btnTypeStatus.setAttribute("class", "btn-green");
                    }

                    if (item.bugfix == true) {
                    	btnTypeBugFix.setCaption("Cleanup");
                    } else {
                    	btnTypeBugFix.setCaption("Bug Fix");
                    }

                    if (item.reportonly == true) {
                    	btnTypeReport.setCaption("Patch");
                    } else {
                    	btnTypeReport.setCaption("Report");
                    }

                    emit("changeSelection", { node : item });
                });
            });

            function updateIncludeTypeList(doc) {
                engine.engines.get('includes/', {}, function (err, data, res) {
                    if (err) {
                        showError("Failed to get checkinclude list");
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

            function updateSparseTypeList(doc) {
                engine.engines.get('sparses/', {}, function (err, data, res) {
                    if (err) {
                        showError("Failed to get checksparse list");
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

            function updateCocciTypeList(doc) {
                engine.engines.get('coccinelles/', {}, function (err, data, res) {
                    if (err) {
                        showError("Failed to get checkcoccinelle list");
                    } else {
                        doc.value = data;
                        for (var idx in data) {
                            model.formatRowData(data[idx]);
                        }
                        model.setRoot({children : data});
                        datagrid.resize();
                        datagrid.select(datagrid.provider.getNodeAtIndex(0));
                    	btnTypeNew.enable();
                    }
                });
            }

            function updatePatchTypeList(doc) {
                if (!doc)
                    return;

                var eid = doc.meta.eid;
                
                if (eid == 1)
                	updateIncludeTypeList(doc);
                else if (eid == 2)
                	updateSparseTypeList(doc);
                else
                	updateCocciTypeList(doc);
            }

            function changePatchReport() {
                var item = datagrid.selection.getCursor();

                if (!item)
                    return;

                engine.engines.put('types/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'reportonly': !item.reportonly})
                }, function (err, data, res) {
                    if (!err) {
                        updatePatchTypeList(currentDocument);
                    } else {
                        showError("Failed to move patch to report");
                    }
                });
            }

            function changePatchTypeBugfix() {
                var item = datagrid.selection.getCursor();

                if (!item)
                    return;

                engine.engines.put('types/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'bugfix': !item.bugfix})
                }, function (err, data, res) {
                    if (!err) {
                        updatePatchTypeList(currentDocument);
                    } else {
                        showError("Failed to move patch type to bugfix");
                    }
                });
            }

            function changePatchTypeStatus() {
                var item = datagrid.selection.getCursor();

                if (!item)
                    return;

                engine.engines.put('types/' + item.id + '/', {
                    "body": JSON.stringify({'id': item.id, 'status': !item.status})
                }, function (err, data, res) {
                    if (!err) {
                        updatePatchTypeList(currentDocument);
                    } else {
                        showError("Failed to enable/disable patch type");
                    }
                });
            }

            function download(url, inputs) {
            	var form = '<form action="' + url + '" method="get">' + inputs + '</form>';
            	jQuery(form).appendTo('body').submit().remove();
            }

            function exportPatchType() {
            	download("/api/engine/coccinelle/export/", "");
            }

            function deletePatchType() {
                var item = datagrid.selection.getCursor();

                if (!item)
                    return;

                confirm("Delete Coccinelle Script",
                	"Are you sure to Delete this coccinelle script?",
                    item.name,
                    function() {
                	    engine.engines.delete('types/' + item.id + '/', {
                        	"body": JSON.stringify({'id': item.id})
                        }, function (err, data, res) {
                            if (!err) {
                            	updatePatchTypeList(currentDocument);
                            } else {
                                showError("Failed to delete coccinelle script");
                            }
                        });
                    }
                );
            }

            function newPatchType() {
                if (currentDocument.meta.eid <= 2)
                    return;

                var fn = function() {};
                var sample = "/// this is patch title line\n" +
			     "///\n" +
			     "/// Name: sample.cocci\n" +
			     "///\n" +
			     "/// The rest are patch desctiption lines, which can be\n" +
			     "/// multi-lines.\n" +
			     "///\n" +
			     "\n" +
			     "@@\n" +
			     "expression e,e1;\n" +
			     "@@\n" +
			     "* e ? e1 : e1\n";

                tabs.open({
                     patchid: "new",
                     path: "undef.cocci",
                     tabtype: "checkcoccinelle",
                     nofs: 1,
                     active: true,
                     value: sample,
                },fn);
            }

            function editPatchType() {
                var item = datagrid.selection.getCursor();

                if (!item)
                    return;

                engine.engines.get('coccinelle/file/' + item.id + '/', {
                }, function (err, data, res) {
                    if (!err) {
                        var fn = function() {};
                        tabs.open({
                            patchid: data.id,
                            path: data.filename,
                            tabtype: item.engine,
                            nofs: 1,
                            active: true,
                            value: data.content
                        },fn);
                    } else {
                        showError("Failed to get patch content");
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
                if (tab.options.eid !== undefined)
                    doc.meta.eid = tab.options.eid;
                updatePatchTypeList(doc);
            });

            plugin.freezePublicAPI({
                
            });

            plugin.load(null, "engineeditor");
            
            return plugin;
        }

        register(null, {
            "engine.editor": handle
        });
    }
});