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

from .views import DefectPatchViewSet, PendingPatchViewSet, ArchivePatchViewSet, PatchContentViewSet
from .views import PatchViewSet, PatchTagViewSet, PatchSendWizardView
from .views import PatchFileView, PatchChangelogView, PatchWhiteListView
from .views import PatchRepoLatestView, PatchRepoStableView, PatchRepoNextView

router = DefaultRouter()
router.register(r'patch/patches', PatchViewSet)
router.register(r'patch/detects', DefectPatchViewSet)
router.register(r'patch/pending', PendingPatchViewSet)
router.register(r'patch/archives', ArchivePatchViewSet)
router.register(r'patch/tags', PatchTagViewSet)
router.register(r'patch/content', PatchContentViewSet)

urlpatterns = router.urls

urlpatterns += [
    url(r'^patch/latest/(?P<id>.+)/$', PatchRepoLatestView.as_view()),
    url(r'^patch/stable/(?P<id>.+)/$', PatchRepoStableView.as_view()),
    url(r'^patch/next/(?P<id>.+)/$', PatchRepoNextView.as_view()),
    url(r'^patch/file/(?P<id>.+)/$', PatchFileView.as_view()),
    url(r'^patch/changelog/(?P<id>.+)/$', PatchChangelogView.as_view()),
    url(r'^patch/whitelist/(?P<id>.+)/$', PatchWhiteListView.as_view()),
    url(r'^patch/sendwizard/(?P<id>.+)/(?P<step>.+)/$', PatchSendWizardView.as_view()),
]