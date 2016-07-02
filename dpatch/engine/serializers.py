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
from .models import PatchEngine, PatchType

class PatchEngineSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatchEngine

        fields = (
            'id',
            'name',
            'status',
            'flags',
            'setting',
            'total'
        )

        read_only_fields = (
            'id',
            'total'
        )

class PatchTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PatchType

        fields = (
            'id',
            'name',
            'engine',
            'source',
            'title',
            'description',
            'comment',
            'flags',
            'filename',
            'options',
            'fixed',
            'content',
            'bugfix',
            'reportonly',
            'includes',
            'excludes',
            'setting',
            'totalfile',
            'totaltime',
            'status'
        )

        read_only_fields = (
            'id',
            'totalfile',
            'totaltime',
        )

class IncludeTypeSerializer(serializers.ModelSerializer):
    engine = serializers.ReadOnlyField(source="engine.name")

    class Meta:
        model = PatchType

        fields = (
            'id',
            'name',
            'engine',
            'title',
            'description',
            'includes',
            'excludes',
            'totalfile',
            'totaltime',
            'status'
        )

        read_only_fields = (
            'id',
            'totalfile',
            'totaltime',
        )

class SparseTypeSerializer(serializers.ModelSerializer):
    engine = serializers.ReadOnlyField(source="engine.name")

    class Meta:
        model = PatchType

        fields = (
            'id',
            'name',
            'engine',
            'title',
            'description',
            'includes',
            'excludes',
            'totalfile',
            'totaltime',
            'status'
        )

        read_only_fields = (
            'id',
            'totalfile',
            'totaltime',
        )

class CoccinelleTypeSerializer(serializers.ModelSerializer):
    engine = serializers.ReadOnlyField(source="engine.name")

    class Meta:
        model = PatchType

        fields = (
            'id',
            'name',
            'filename',
            'engine',
            'title',
            'description',
            'comment',
            'flags',
            'bugfix',
            'reportonly',
            'options',
            'fixed',
            'content',
            'includes',
            'excludes',
            'totalfile',
            'totaltime',
            'status'
        )

        read_only_fields = (
            'id',
            'name',
            'filename',
            'totalfile',
            'totaltime',
        )
