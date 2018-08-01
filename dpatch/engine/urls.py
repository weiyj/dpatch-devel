#!/usr/bin/python
#
# DailyPatch - Automated Linux Kernel Patch Generate Engine
# Copyright (C) 2012 - 2016 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the DailyPatch package.
#
# DailyPatch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# DailyPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DailyPatch; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from rest_framework.routers import DefaultRouter
from django.conf.urls import url

from .views import PatchEngineViewSet, PatchTypeViewSet
from .views import IncludeTypeViewSet, SparseTypeViewSet, BuildTypeViewSet, CoccinelleTypeViewSet
from .views import CoccinelleFileExportViewSet, CoccinelleFileView

router = DefaultRouter()
router.register(r'engine/engines', PatchEngineViewSet)
router.register(r'engine/types', PatchTypeViewSet)
router.register(r'engine/includes', IncludeTypeViewSet)
router.register(r'engine/sparses', SparseTypeViewSet)
router.register(r'engine/builds', BuildTypeViewSet)
router.register(r'engine/coccinelles', CoccinelleTypeViewSet)
router.register(r'engine/coccinelle/export', CoccinelleFileExportViewSet)

urlpatterns = router.urls

urlpatterns += [
    url(r'^engine/coccinelle/file/(?P<id>.+)/$', CoccinelleFileView.as_view()),
]
