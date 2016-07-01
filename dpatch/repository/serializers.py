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
from .models import Repository, RepositoryTag, RepositoryHistory, FileModule

class RepositorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Repository

        fields = (
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

        read_only_fields = (
            'commit',
            'stable',
            'update'
        )

class RepositoryTagSerializer(serializers.ModelSerializer):
    reponame = serializers.ReadOnlyField(source="repo.name")

    class Meta:
        model = RepositoryTag

        fields = (
            'id',
            'repo',
            'reponame',
            'name',
            'total'
        )

        read_only_fields = (
            'id',
            'repo',
            'name',
            'total'
        )

class RepositoryHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = RepositoryHistory

        fields = (
            'id',
            'repo',
            'changes',
            'date'
        )

        read_only_fields = (
            'id',
            'repo',
            'changes',
            'date'
        )

class FileModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileModule

        fields = (
            'id',
            'name',
            'file',
            'repo'
        )

        read_only_fields = (
            'id',
            'file',
            'repo'
        )

