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

from rest_framework import status, viewsets
from rest_framework.response import Response

from .serializers import SMTPServerSerializer, POPServerSerializer
from .models import SMTPServer, POPServer

class SMTPServerViewSet(viewsets.ModelViewSet):
    queryset = SMTPServer.objects.all()
    serializer_class = SMTPServerSerializer

    def get_queryset(self):
        user = self.request.user
        return SMTPServer.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = SMTPServerSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        return Response({
            'code': 1,
            'detail': 'Bad request.'
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            repo = SMTPServer.objects.get(pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = SMTPServerSerializer(repo)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            engine = SMTPServer.objects.get(pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = SMTPServerSerializer(engine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'code': 1,
                'detail': 'Bad format.'
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        return Response({
            'code': 1,
            'detail': 'Bad request.'
        }, status=status.HTTP_400_BAD_REQUEST)

class POPServerViewSet(viewsets.ModelViewSet):
    queryset = POPServer.objects.all()
    serializer_class = POPServerSerializer

    def get_queryset(self):
        user = self.request.user
        return POPServer.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = POPServerSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        return Response({
            'code': 1,
            'detail': 'Bad request.'
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            repo = POPServer.objects.get(pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = POPServerSerializer(repo)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            engine = POPServer.objects.get(pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = POPServerSerializer(engine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'code': 1,
                'detail': 'Bad format.'
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        return Response({
            'code': 1,
            'detail': 'Bad request.'
        }, status=status.HTTP_400_BAD_REQUEST)

