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

import json

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SystemSetting

class SystemSettingView(APIView):
    def get(self, request, name):
        user = self.request.user
        try:
            setting = SystemSetting.objects.get(user=user, name=name)
        except:
            return Response({}, status=status.HTTP_200_OK)

        try:
            return Response(json.loads(setting.content), status=status.HTTP_200_OK)
        except:
            return Response(setting.content, status=status.HTTP_200_OK)

    def put(self, request, name):
        user = self.request.user
        content = request.stream.read()
        
        try:
            setting = SystemSetting.objects.get(user=user, name=name)
        except:
            setting = SystemSetting(user=user, name=name)
            
        setting.content = content
        setting.save()

        return Response(setting.content, status=status.HTTP_200_OK)

    def delete(self, request, name):
        user = self.request.user
        try:
            setting = SystemSetting.objects.get(user=user, name=name)
        except:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        setting.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
