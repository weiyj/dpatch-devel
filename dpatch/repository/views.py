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

from rest_framework import status, viewsets, mixins
from rest_framework.response import Response

from .serializers import RepositorySerializer, RepositoryHistorySerializer
from .serializers import RepositoryTagSerializer, FileModuleSerializer
from .models import Repository, RepositoryHistory, RepositoryTag, FileModule

class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer

    def get_queryset(self):
        user = self.request.user
        return Repository.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = RepositorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            repo = Repository.objects.get(id=pk, user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RepositorySerializer(repo)
        return Response(serializer.data)

    def create(self, request):
        return Response({
            'code': 1,
            'detail': 'Bad request.'
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            repo = Repository.objects.get(pk=pk, user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RepositorySerializer(repo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'code': 1,
                'detail': 'Bad format.'
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            repo = Repository.objects.get(pk=pk, user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        repo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class RepositoryTagViewSet(viewsets.ModelViewSet):
    queryset = RepositoryTag.objects.all()
    serializer_class = RepositoryTagSerializer

    def get_queryset(self):
        user = self.request.user
        return RepositoryTag.objects.filter(repo__user=user, total__gt=0).order_by('-id')

    def list(self, request):
        queryset = self.get_queryset()
        serializer = RepositoryTagSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            history = RepositoryTag.objects.get(pk=pk, repo__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RepositoryTagSerializer(history)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            history = RepositoryTag.objects.get(pk=pk, repo__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        history.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class RepositoryHistoryViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    queryset = RepositoryHistory.objects.all()
    serializer_class = RepositoryHistorySerializer

    def get_queryset(self):
        user = self.request.user
        return RepositoryHistory.objects.filter(repo__user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = RepositoryHistorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            history = RepositoryHistory.objects.get(pk=pk, repo__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = RepositoryHistorySerializer(history)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            history = RepositoryHistory.objects.get(pk=pk, repo__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        history.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class FileModuleViewSet(viewsets.ModelViewSet):
    queryset = FileModule.objects.all()
    serializer_class = FileModuleSerializer

    def get_queryset(self):
        user = self.request.user
        return FileModule.objects.filter(repo__user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = FileModuleSerializer(queryset, many=True)
        return Response(serializer.data)
