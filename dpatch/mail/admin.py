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
from .models import SMTPServer, POPServer

class SMTPServerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(SMTPServerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    list_display = (
        'id',
        'active',
        'server',
        'encryption',
        'port',
        'username',
        'password',
        'email',
        'alias'
    )

class POPServerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super(POPServerAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    list_display = (
        'id',
        'active',
        'server',
        'encryption',
        'port',
        'username',
        'password',
        'email',
        'alias'
    )

admin.site.register(SMTPServer, SMTPServerAdmin)
admin.site.register(POPServer, POPServerAdmin)
