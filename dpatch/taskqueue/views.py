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

from rest_framework import viewsets
from rest_framework.response import Response

from .serializers import ScanTaskQueueSerializer, StatusTaskQueueSerializer
from .models import ScanTaskQueue, StatusTaskQueue

class ScanTaskQueueViewSet(viewsets.ModelViewSet):
    queryset = ScanTaskQueue.objects.all()
    serializer_class = ScanTaskQueueSerializer

    def get_queryset(self):
        user = self.request.user
        return ScanTaskQueue.objects.filter(type__user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ScanTaskQueueSerializer(queryset, many=True)
        return Response(serializer.data)

class StatusTaskQueueViewSet(viewsets.ModelViewSet):
    queryset = StatusTaskQueue.objects.all()
    serializer_class = StatusTaskQueueSerializer

    def get_queryset(self):
        user = self.request.user
        return StatusTaskQueue.objects.filter(patch__type__user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = StatusTaskQueueSerializer(queryset, many=True)
        return Response(serializer.data)
