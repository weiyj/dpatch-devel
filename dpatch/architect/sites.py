import os
import re
import json

from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.static import serve

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ArchitectSite(object):
    def __init__(self, name='architect'):
        self._registry = {}
        self.name = name
        
        self._prefix = settings.ARCHITECT_URL

        self._plugins = []
        self._requirejs = {
            "paths": {},
            "packages": [],
            "baseUrl": os.path.join(self._prefix, 'lib'),
            "useCache": False
        }

    def architect_dirname(self, name):
        if settings.ARCHITECT_PLUGINS.has_key(name):
            return os.path.join(BASE_DIR, settings.ARCHITECT_PLUGINS[name])
        else:
            return None

    def staticfile(self, prefix, name, view=serve, **kwargs):
        return [
            url(r'^%s(%s)$' % (re.escape(prefix.lstrip('/')), re.escape(name)), view, kwargs=kwargs),
        ]

    def register_library(self, name, plugin, path):
        urlpatterns = []
        root = os.path.join(path, plugin["path"])
        prefix = os.path.join(self._prefix, plugin["mount"])
        if plugin.has_key('rjs'):
            rjs = plugin['rjs']
            if isinstance(rjs, list):
                for lib in rjs:
                    self._requirejs["packages"].append(lib)
            elif isinstance(rjs, dict):
                for name in rjs:
                    self._requirejs["paths"][name] = os.path.join(self._prefix, rjs[name].lstrip('/'))
        for fname in os.listdir(root):
            fpath = os.path.join(root, fname)
            #print fpath
            if os.path.isfile(fpath):
                urlpatterns += self.staticfile(prefix, fname, document_root=root)
            elif os.path.isdir(fpath):
                urlpatterns += static(os.path.join(prefix, fname + '/'), document_root=fpath)
        return urlpatterns

    def register_libraries(self, path):
        urlpatterns = []
        with open(os.path.join(path, 'package.json'), 'r') as fp:
            config = json.load(fp)
        if not config.has_key("plugins"):
            return urlpatterns
        for name in config["plugins"]:
            plugin = config["plugins"][name]
            urlpatterns += self.register_library(name, plugin, path)
        return urlpatterns

    def register_plugin(self, name, path, prefix, options):
        bpath = os.path.basename(path)
        plugin = {
            "packagePath": "plugins/" + bpath + "/" + name,
            "staticPrefix": os.path.join(self._prefix, prefix, bpath)
        }

        if isinstance(options, dict):
            plugin.update(options)

        # allow disable plugin
        if not plugin.has_key('enable') or plugin['enable'] is True:
            self._plugins.append(plugin)

    def register_plugins(self, path):
        prefix = "lib/plugins/"
        bpath = os.path.basename(path)
        if not os.path.exists(os.path.join(path, 'package.json')):
            name = os.path.basename(path).split(".")[-1]
            if os.path.exists(os.path.join(path, name + ".js")):
                self.register_plugin(name, path, prefix, {})
        else:
            with open(os.path.join(path, 'package.json'), 'r') as fp:
                config = json.load(fp)
            for name in config["plugins"]:
                options = config["plugins"][name]
                self.register_plugin(name, path, prefix, options)
        return static(os.path.join(self._prefix, prefix, bpath + '/'), document_root=path)

    def libs_urlpatterns(self):
        urlpatterns = []
        path = self.architect_dirname('libs')
        if not path is None and os.path.exists(path):
            for name in os.listdir(path):
                dpath = os.path.join(path, name)
                if not os.path.isdir(dpath):
                    continue
                if not os.path.exists(os.path.join(dpath, 'package.json')):
                    continue
                urlpatterns += self.register_libraries(dpath)
        return urlpatterns

    def plugins_urlpatterns(self):
        urlpatterns = []
        path = self.architect_dirname('plugins')
        if not path is None and os.path.exists(path):
            for name in os.listdir(path):
                dpath = os.path.join(path, name)
                if not os.path.isdir(dpath):
                    continue
                urlpatterns += self.register_plugins(dpath)
        return urlpatterns

    def get_urls(self):
        urlpatterns = [
            url(r'^configs/require_config.js$', self.requirejs_config, name='requirejs_config'),
            url(r'^configs/plugins_config.js$', self.plugins_config, name='plugins_config'),
        ]

        urlpatterns += self.libs_urlpatterns()
        urlpatterns += self.plugins_urlpatterns()

        return urlpatterns

    def requirejs_config(self, request):
        return HttpResponse("requirejs.config(" + json.dumps(self._requirejs) + ");")
    
    def plugins_config(self, request):
        return HttpResponse("var plugins = " + json.dumps(self._plugins) + ";")

    @property
    def urls(self):
        return self.get_urls(), 'architect', self.name

    @property
    def requirejs(self):
        return self._requirejs

    @property
    def plugins(self):
        return self._plugins
        
site = ArchitectSite()

