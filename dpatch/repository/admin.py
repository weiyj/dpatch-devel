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

from django.contrib import admin
from .models import Repository, RepositoryTag, RepositoryHistory, FileModule, FileChecksum

class RepositoryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(RepositoryAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    list_display = (
        'id',
        'name',
        'url',
        'username',
        'email',
        'devel',
        'developing',
        'build',
        'commit',
        'stable',
        'includes',
        'excludes',
        'update',
        'status'
    )

class RepositoryTagAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(RepositoryTagAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(repo__user=request.user)

    list_display = (
        'id',
        'repo',
        'name',
        'total',
        'changelist',
        'running'
    )

class RepositoryHistoryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(RepositoryHistoryAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(repo__user=request.user)

    list_display = (
        'id',
        'repo',
        'changes',
        'date'
    )

    list_filter = (
        'repo',
    )

class FileModuleAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(FileModuleAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(repo__user=request.user)

    list_display = (
        'id',
        'name',
        'file',
        'repo'
    )

class FileChecksumAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(FileChecksumAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(repo__user=request.user)

    list_display = (
        'id',
        'file',
        'checksum',
        'repo',
        'date'
    )

admin.site.register(Repository, RepositoryAdmin)
admin.site.register(RepositoryTag, RepositoryTagAdmin)
admin.site.register(RepositoryHistory, RepositoryHistoryAdmin)
admin.site.register(FileModule, FileModuleAdmin)
admin.site.register(FileChecksum, FileChecksumAdmin)
