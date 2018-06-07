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

import os
import tarfile
import tempfile
import json

from rest_framework import status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponse
from time import gmtime, strftime

from dpatch.core.cocciparser import CocciParser
from dpatch.core.coccikernelparser import CocciKernelParser

from .serializers import PatchEngineSerializer, PatchTypeSerializer
from .serializers import IncludeTypeSerializer, SparseTypeSerializer, CoccinelleTypeSerializer
from .models import PatchEngine, PatchType

ENGINE_INCLUDE = 1
ENGINE_SPARSE = 2
ENGINE_COCCINELLE = 3

class PatchEngineViewSet(viewsets.ModelViewSet):
    queryset = PatchEngine.objects.all()
    serializer_class = PatchEngineSerializer

    def list(self, request):
        queryset = PatchEngine.objects.all()
        for engine in queryset:
            engine.total = PatchType.objects.filter(user=request.user, engine=engine).count()
        serializer = PatchEngineSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        return Response({
            'code': 1,
            'detail': 'Bad request.'
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            repo = PatchEngine.objects.get(pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = PatchEngineSerializer(repo)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            engine = PatchEngine.objects.get(pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PatchEngineSerializer(engine, data=request.data, partial=True)
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

class PatchTypeViewSet(viewsets.ModelViewSet):
    queryset = PatchType.objects.all()
    serializer_class = PatchTypeSerializer

    def get_queryset(self):
        user = self.request.user
        return PatchType.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = PatchTypeSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            ptype = PatchType.objects.get(pk=pk, user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': _('Not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PatchTypeSerializer(ptype)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            ptype = PatchType.objects.get(pk=pk, user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PatchTypeSerializer(ptype, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'code': 1,
                'detail': 'Bad format.'
            }, status=status.HTTP_400_BAD_REQUEST)

class IncludeTypeViewSet(viewsets.ModelViewSet):
    queryset = PatchType.objects.all()
    serializer_class = IncludeTypeSerializer

    def get_queryset(self):
        user = self.request.user
        return PatchType.objects.filter(user=user, engine__id=ENGINE_INCLUDE)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = IncludeTypeSerializer(queryset, many=True)
        return Response(serializer.data)

class SparseTypeViewSet(viewsets.ModelViewSet):
    queryset = PatchType.objects.all()
    serializer_class = SparseTypeSerializer

    def get_queryset(self):
        user = self.request.user
        return PatchType.objects.filter(user=user, engine__id=ENGINE_SPARSE)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = SparseTypeSerializer(queryset, many=True)
        return Response(serializer.data)

class CoccinelleTypeViewSet(viewsets.ModelViewSet):
    queryset = PatchType.objects.all()
    serializer_class = CoccinelleTypeSerializer

    def get_queryset(self):
        user = self.request.user
        return PatchType.objects.filter(user=user, engine__id=ENGINE_COCCINELLE)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CoccinelleTypeSerializer(queryset, many=True)
        return Response(serializer.data)

class CoccinelleFileView(APIView):
    def get(self, request, id):
        user = self.request.user
        try:
            ptype = PatchType.objects.get(user=user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found ' + id
            }, status=status.HTTP_404_NOT_FOUND)

        if ptype.source == PatchType.SOURCE_KERNEL:
            content = "/// TITLE: " + ptype.title + "\n"
            for line in ptype.description.split('\n'):
                content = content + "/// DESC: " + line + "\n"
            content = content + ptype.content
        else:
            content = ptype.content

        return Response({
            'id': ptype.id,
            'filename': ptype.filename,
            'content': content
        }, status=status.HTTP_200_OK)

    def _update_coccinelle_kernel(self, ptype, content):
        parser = CocciKernelParser(content.split('\n'))
        parser.parser()

        title = parser.get_title()
        if len(title) == 0:
            return Response({
                'detail:' : 'bad title field'
            }, status=status.HTTP_400_BAD_REQUEST)

        description = parser.get_description()
        if len(description) == 0:
            return Response({
                'detail:' : 'bad description field'
            }, status=status.HTTP_400_BAD_REQUEST)

        content = parser.get_content()
        if len(content) == 0:
            return Response({
                'detail:' : 'bad content field'
            }, status=status.HTTP_400_BAD_REQUEST)

        ptype.title = title
        ptype.description = description
        if content != ptype.content:
            ptype.content = content
            with open(ptype.fullpath(), "w") as fp:
                fp.write(content)

        ptype.save()

        return Response({
            'id': ptype.id,
            'filename': ptype.filename,
            'content': ptype.content
        }, status=status.HTTP_200_OK)

    def _update_coccinelle_defined(self, ptype, content):
        parser = CocciParser(content.split('\n'))
        parser.parser()

        title = parser.get_title()
        if len(title) == 0:
            return Response({
                'detail:' : 'bad title field'
            }, status=status.HTTP_400_BAD_REQUEST)

        description = parser.get_description()
        if len(description) == 0:
            return Response({
                'detail:' : 'bad description field'
            }, status=status.HTTP_400_BAD_REQUEST)

        content = parser.get_content()
        if len(content) == 0:
            return Response({
                'detail:' : 'bad content field'
            }, status=status.HTTP_400_BAD_REQUEST)

        ptype.title = title
        ptype.options = parser.get_options()
        ptype.description = description
        flags = parser.get_flags()
        if not flags is None:
            ptype.flags = flags

        if content != ptype.content:
            ptype.content = content
            with open(ptype.fullpath(), "w") as fp:
                fp.write(content)

        ptype.save()

        return Response({
            'id': ptype.id,
            'filename': ptype.filename,
            'content': ptype.content
        }, status=status.HTTP_200_OK)

    def put(self, request, id):
        user = self.request.user
        try:
            ptype = PatchType.objects.get(user=user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found ' + id
            }, status=status.HTTP_404_NOT_FOUND)

        if 'content' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if ptype.source == PatchType.SOURCE_KERNEL:
            return self._update_coccinelle_kernel(ptype, request.data['content'])
        else:
            return self._update_coccinelle_defined(ptype, request.data['content'])

class CoccinelleFileExportViewSet(mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  viewsets.GenericViewSet):
    queryset = PatchType.objects.all()
    serializer_class = CoccinelleTypeSerializer

    def get_queryset(self):
        user = self.request.user
        return PatchType.objects.filter(user=user, engine__id=ENGINE_COCCINELLE)

    def _archive_add(self, archive, ptype):
        tmpfname = tempfile.mktemp(dir = ptype.tempdir())
        with open(tmpfname, "w") as fp:
            serializer = PatchTypeSerializer(ptype)
            fp.write(json.dumps(serializer.data, indent=4))

        archive.add(tmpfname, arcname = "%s.json" % ptype.name)

        os.unlink(tmpfname)

    def _archive_add_content(self, archive, content):
        tmpfname = tempfile.mktemp()
        with open(tmpfname, "w") as fp:
            fp.write(content)

        archive.add(tmpfname, arcname = "coccinelle.json")

        os.unlink(tmpfname)

    def list(self, request):
        response = HttpResponse(content_type='application/x-gzip')
        response['Content-Disposition'] = 'attachment; filename=coccinelle-scripts-all-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
        archive = tarfile.open(fileobj=response, mode='w:gz')

        for etype in self.get_queryset():
            try:
                path = os.path.dirname(etype.fullpath())
                if not os.path.exists(path):
                    os.makedirs(path)
                with open(etype.fullpath(), "w") as cocci:
                    cocci.write(etype.content)
            except:
                pass

        serializer = PatchTypeSerializer(self.get_queryset(), many=True)

        self._archive_add_content(archive, json.dumps(serializer.data, indent=4))

        archive.close()

        return response

    def retrieve(self, request, pk=None):
        try:
            ptype = PatchType.objects.get(pk=pk, user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': _('Not found.')
            }, status=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(content_type='application/x-gzip')
        response['Content-Disposition'] = 'attachment; filename=coccinelle-scripts-%s.tar.gz' % strftime("%Y%m%d%H%M%S", gmtime())
        archive = tarfile.open(fileobj=response, mode='w:gz')

        self._archive_add(archive, ptype)

        archive.close()

        return response
