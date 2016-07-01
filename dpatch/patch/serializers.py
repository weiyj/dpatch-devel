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
from .models import Patch

class PatchSerializer(serializers.ModelSerializer):
    repo = serializers.ReadOnlyField(source="tag.repo.name")
    tag = serializers.ReadOnlyField(source="tag.name")
    type = serializers.ReadOnlyField(source="type.name")

    class Meta:
        model = Patch

        fields = (
            'id',
            'tag',
            'repo',
            'type',
            'status',
            'file',
            'date',
            'commit',
            'title',
            'description',
            'build'
        )

        read_only_fields = (
            'id',
            'date'
        )

class PatchSummarySerializer(serializers.ModelSerializer):
    repo = serializers.ReadOnlyField(source="tag.repo.name")
    tag = serializers.ReadOnlyField(source="tag.name")
    type = serializers.ReadOnlyField(source="type.name")

    class Meta:
        model = Patch

        fields = (
            'id',
            'tag',
            'repo',
            'type',
            'status',
            'file',
            'date',
            'commit',
            'title',
            'description',
            'build'
        )

        read_only_fields = (
            'id',
            'date'
        )

class PatchDetailSerializer(serializers.ModelSerializer):
    repo = serializers.ReadOnlyField(source="tag.repo.name")
    tag = serializers.ReadOnlyField(source="tag.name")
    type = serializers.ReadOnlyField(source="type.name")

    class Meta:
        model = Patch

        fields = (
            'id',
            'tag',
            'repo',
            'type',
            'status',
            'file',
            'date',
            'commit',
            'report',
            'diff',
            'title',
            'description',
            'emails',
            'content',
            'build',
            'buildlog'
        )

        read_only_fields = (
            'id',
            'date',
            'report'
        )

class PatchContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patch

        fields = (
            'id',
            'title',
            'content'
        )

        read_only_fields = (
            'id'
        )
