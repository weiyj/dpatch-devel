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

from rest_framework import serializers

from .models import ScanTaskQueue, StatusTaskQueue

class ScanTaskQueueSerializer(serializers.ModelSerializer):

    class Meta:
        model = ScanTaskQueue

        fields = (
            'id',
            'status',
            'type',
            'tag',
            'filename',
            'date'
        )

        read_only_fields = (
            'id',
            'date'
        )

class StatusTaskQueueSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusTaskQueue

        fields = (
            'id',
            'status',
            'patch',
            'date'
        )

        read_only_fields = (
            'id',
            'date'
        )
