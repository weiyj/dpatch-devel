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
import re
import json
import tempfile
import subprocess

from rest_framework import status, viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import F
from django.utils import html

from dpatch.core.utils import execute_shell_unicode, execute_shell_unicode_noret
from dpatch.core.utils import find_remove_lines, commit_url
from dpatch.core.patchformater import PatchFormater
from dpatch.core.patchparser import PatchParser

from dpatch.repository.models import FileModule
from dpatch.mail.models import SMTPServer
from dpatch.repository.models import RepositoryTag
from .serializers import PatchSerializer, PatchDetailSerializer, PatchContentSerializer
from .models import Patch

class PatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

    def get_queryset(self):
        user = self.request.user
        return Patch.objects.filter(type__user=user).order_by('-id')

    def list(self, request):
        queryset = self.get_queryset()
        serializer = PatchSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            patch = Patch.objects.get(pk=pk, type__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = PatchDetailSerializer(patch)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            patch = Patch.objects.get(pk=pk, type__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PatchDetailSerializer(patch, data=request.data, partial=True)
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
            patch = Patch.objects.get(pk=pk, type__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        patch.tag.total = F('total') - 1
        patch.tag.save()
        patch.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class PatchTagViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

    def retrieve(self, request, pk=None):
        queryset = Patch.objects.filter(tag__id=pk, type__user=request.user).order_by('-id')
        serializer = PatchSerializer(queryset, many=True)
        return Response(serializer.data)

class DefectPatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

    def get_queryset(self):
        user = self.request.user
        return Patch.objects.filter(type__user=user).order_by('-id')

class PendingPatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

    def get_queryset(self):
        user = self.request.user
        return Patch.objects.filter(type__user=user).order_by('-id')

class ArchivePatchViewSet(viewsets.ModelViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchSerializer

    def get_queryset(self):
        user = self.request.user
        return Patch.objects.filter(type__user=user).order_by('-id')

class PatchContentViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):
    queryset = Patch.objects.all()
    serializer_class = PatchContentSerializer

    def _register_module(self, repo, file, name, newname):
        if len(newname) == 0 or name == newname:
            return False

        mlist = FileModule.objects.filter(repo = repo, file = file)
        if len(mlist) == 0:
            mname = FileModule(repo = repo, file = file, name = newname)
            mname.save()
        else:
            for mname in mlist:
                mname.name = newname
                mname.save()
        return True

    def get_queryset(self):
        user = self.request.user
        return Patch.objects.filter(type__user=user)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = PatchContentSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = self.request.user
        try:
            patch = Patch.objects.get(type__user=user, pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = PatchContentSerializer(patch)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            patch = Patch.objects.get(pk=pk)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if 'content' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        parser = PatchParser(request.data['content'])
        parser.parser()

        if len(parser.get_title()) == 0:
            return Response({
                'detail:' : 'bad title field'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(parser.get_description()) == 0:
            return Response({
                'detail:' : 'bad description field'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(parser.get_email_list()) == 0:
            return Response({
                'detail:' : 'bad email list field'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(parser.get_diff()) == 0:
            return Response({
                'detail:' : 'bad diff field'
            }, status=status.HTTP_400_BAD_REQUEST)

        # upgrade file module name if possible
        self._register_module(patch.tag.repo, patch.file, patch.module, parser.get_module_name())
    
        request.data['title'] = parser.get_title_full()
        request.data['description'] = parser.get_description()
        request.data['emails'] = parser.get_email_list()
        request.data['module'] = parser.get_module_name()
        if patch.diff != parser.get_diff():
            request.data['diff'] = parser.get_diff()
            request.data['build'] = 0

        serializer = PatchDetailSerializer(patch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({
                'code': 1,
                'detail': 'Bad format.'
            }, status=status.HTTP_400_BAD_REQUEST)

class PatchFileView(APIView):
    def _get_diff_and_revert(self, repo, fname):
        diff = subprocess.Popen("cd %s; LC_ALL=en_US git diff --patch-with-stat %s" % (repo, fname),
                                shell=True, stdout=subprocess.PIPE)
        diffOut = diff.communicate()[0]
        os.system("cd %s; git checkout %s" % (repo, fname))
        return diffOut

    def get(self, request, id):
        user = self.request.user
        try:
            patch = Patch.objects.get(type__user=user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        content = patch.filecontent()

        log = ''
        if patch.status in [Patch.PATCH_STATUS_PATCH, Patch.PATCH_STATUS_RENEW]:
            try:
                tmpsrcfname = tempfile.mktemp(dir = patch.tempdir())
                with open(tmpsrcfname, "w") as tmpsrcfile:
                    tmpsrcfile.write(content)
    
                tmpdiffname = tempfile.mktemp(dir = patch.tempdir())
                with open(tmpdiffname, "w") as tmpdiffile:
                    tmpdiffile.write(patch.diff)

                tmpdstfname = tempfile.mktemp(dir = patch.tempdir())
    
                ret, log = execute_shell_unicode('/usr/bin/patch %s -i %s -o %s' % (tmpsrcfname, tmpdiffname, tmpdstfname))
                if ret == 0:
                    with open(tmpdstfname, "r") as dstfile:
                        content = dstfile.read()

                os.unlink(tmpsrcfname)
                os.unlink(tmpdiffname)
                os.unlink(tmpdstfname)
            except:
                pass

        return Response({
            'id': patch.id,
            'filename': patch.file,
            'log': log,
            'content': unicode(content, 'utf-8')
        }, status=status.HTTP_200_OK)

    def put(self, request, id):
        user = self.request.user
        try:
            patch = Patch.objects.get(type__user=user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        sfile = patch.sourcefile()
        if not os.path.exists(sfile) or not os.path.isfile(sfile):
            return Response({
                'code': 1,
                'detail': 'Not found ' + patch.file
            }, status=status.HTTP_404_NOT_FOUND)

        content = request.data['content']
        try:
            with open(sfile, "w") as srcfile:
                try:
                    srcfile.write(content)
                except:
                    srcfile.write(unicode.encode(content, 'utf-8'))

            diff = self._get_diff_and_revert(patch.tag.repo.dirname(), patch.file)
            user = patch.username()
            email = patch.email()
            if re.search(r'{{[^}]*}}', patch.type.title):
                title = patch.type.title
            else:
                title = patch.title
            if re.search(r'{{[^}]*}}', patch.type.description) or len(patch.description) == 0:
                desc = patch.type.description
            else:
                desc = patch.description

            formater = PatchFormater(patch.tag.repo.dirname(), patch.file, user, email,
                                   title, desc, diff)
            patch.content = formater.format_patch()
            patch.title = formater.format_title()
            patch.description = formater.format_desc()
            patch.emails = unicode(formater.get_mail_list(), 'utf-8')
            if patch.diff != diff:
                patch.diff = diff
                patch.status = Patch.PATCH_STATUS_PATCH
                if patch.build != Patch.BUILD_STASTU_SKIP:
                    patch.build = 0
            patch.save()
        except:
            return Response({
                'code': 1,
                'detail': 'Error.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = PatchDetailSerializer(patch)
        return Response(serializer.data)

class PatchChangelogView(APIView):
    def _patch_format_gitinfo(self, repo, gitlog):
        lines = gitlog.split("\n")
        fileinfos = []
        for line in lines:
            if line.find('||||') == -1:
                continue
            subflds = line.split('||||')
            commit = subflds[-1]
            title = subflds[-2]
            line = '%s  %-20s' % (subflds[0], subflds[1])
            url = commit_url(repo.url, commit)
            fileinfos.append('%s <a href="%s" target="__blank">%s</a>' % (line, url, html.escape(title)))

        return '\n'.join(fileinfos)

    def get(self, request, id):
        user = self.request.user
        try:
            patch = Patch.objects.get(type__user=user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found ' + id
            }, status=status.HTTP_404_NOT_FOUND)

        sfile = patch.sourcefile()
        if not os.path.exists(sfile):
            return Response({
                'code': 1,
                'detail': 'Not found ' + sfile
            }, status=status.HTTP_404_NOT_FOUND)

        rdir = patch.tag.repo.dirname()
        gitlog = execute_shell_unicode_noret("cd %s; git log -n 20 --pretty=format:'%%ci||||%%an||||%%s||||%%H' %s" % (rdir, patch.file))
        fileinfo = '# git log -n 20 %s\n' % patch.file
        fileinfo += self._patch_format_gitinfo(patch.tag.repo, gitlog)
        if patch.status in [Patch.PATCH_STATUS_PATCH, Patch.PATCH_STATUS_RENEW, Patch.PATCH_STATUS_PENDDING]:
            count = 0
            for line in find_remove_lines(patch.diff):
                gitlog = execute_shell_unicode_noret("cd %s; git log -n 1 -S '%s' --pretty=format:'%%ci||||%%an||||%%s||||%%H' %s" % (rdir, line, patch.file))
                fileinfo += '\n\n# git log -n 1 -S \'%s\' %s\n' % (html.escape(line), patch.file)
                fileinfo += self._patch_format_gitinfo(patch.tag.repo, gitlog)
                count += 1
                if count > 4:
                    break
        elif patch.status in [Patch.PATCH_STATUS_NEW]:
            count = 0
            for line in find_remove_lines(patch.report):
                gitlog = execute_shell_unicode_noret("cd %s; git log -n 1 -S '%s' --pretty=format:'%%ci||||%%an||||%%s||||%%H' %s" % (rdir, line, patch.file))
                fileinfo += '\n\n# git log -n 1 -S \'%s\' %s\n' % (html.escape(line), patch.file)
                fileinfo += self._patch_format_gitinfo(patch.tag.repo, gitlog)
                count += 1
                if count > 4:
                    break

        gitlog = execute_shell_unicode_noret("cd %s; /usr/bin/perl ./scripts/get_maintainer.pl -f %s --remove-duplicates --scm" % (rdir, patch.file))
        fileinfo += '\n\n# ./scripts/get_maintainer.pl -f %s --scm\n' % patch.file
        fileinfo += html.escape(gitlog)

        return Response({
            'id': id,
            'file': patch.file,
            'changlog': fileinfo
        }, status=status.HTTP_200_OK)

class PatchWhiteListView(APIView):
    def get(self, request, id):
        try:
            patch = Patch.objects.get(id=id, type__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            data = json.loads(patch.type.excludes)
        except:
            data = []
        return Response(data)

    def put(self, request, id):
        try:
            patch = Patch.objects.get(id=id, type__user=request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if 'file' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        wlist = json.loads(patch.type.excludes)
        fname = request.data['file']

        # this file name to the excludes
        if not fname in wlist:
            wlist.append(fname)
            patch.type.excludes = json.dumps(wlist)
            patch.type.save()

        # decrease the total patch count of tag
        patch.tag.total = F('total') - 1
        patch.tag.save()

        # delete this patch
        patch.delete()

        return Response(wlist)

class PatchSendWizardView(APIView):
    def check_patch(self, patch):
        repodir = patch.tag.repo.dirname()
        chkpatchbin = os.path.join(repodir, 'scripts/checkpatch.pl')

        temp = patch.fullpath()
        with open(patch.fullpath(), "w") as cfg:
            try:
                cfg.write(patch.content + '\n\n')
            except:
                cfg.write(unicode.encode(patch.content + '\n\n', 'utf-8'))

        ret1, chkpatch = execute_shell_unicode('/usr/bin/perl %s %s' % (chkpatchbin, temp))
        chkpatch = chkpatch.replace(temp, 'patch')
        ret2, apatch = execute_shell_unicode('cd %s && git apply --check %s' % (repodir, temp))
        if ret2 == 0:
            apatch = 'patch can be apply succeed'

        apatch3 = ''
        ndir = os.path.join(os.path.dirname(repodir), 'linux-next')
        if patch.tag.repo.name == 'linux.git' and os.path.exists(ndir):
            ret3, apatch3 = execute_shell_unicode('cd %s && git apply --check %s' % (ndir, temp))
            if ret3 == 0:
                apatch3 = 'patch can be apply succeed'

        ctx = '<pre># scripts/checkpatch.pl %s\n\n%s\n# git apply --check %s\n\n%s' \
                % (temp, chkpatch, temp, apatch)

        if apatch3 != '':
            ctx += '\n\n# cd ../linux-next\n# git apply --check %s\n\n%s' % (temp, apatch3)

        ctx += '</pre>'
        ctx = ctx.replace(patch.dirname() + '/', '')
        if ret1 != 0 or ret2 != 0:
            ctx += '<div><font color=red>Please correct above errors first!</font></div>'

        return Response({
                'id': patch.id,
                'code': (ret1 != 0 or ret2 != 0),
                'detail': ctx
        }, status=status.HTTP_200_OK)

    def _parser_email(self, maillist):
        email = maillist.replace('To:', '')
        email = email.replace('Cc:', '')
        email = email.replace(',', '')
        emails = email.split("\n")

        for addr in emails:
            if len(addr.strip()) != 0:
                return addr.strip(), emails

        return '', emails

    def check_send_email(self, patch):
        to, emails = self._parser_email(patch.emails)
        to = to.replace('"', '')
        ret, drun = execute_shell_unicode('/usr/bin/git send-email --dry-run --no-thread --to="%s" %s' \
                                % (to, patch.fullpath()))
        drun = drun.replace(patch.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % drun
            ctx += '<div><font color=red>Your SMTP setting is not correctly!</font></div>'
            return Response({
                    'id': patch.id,
                    'code': 1,
                    'detail': ctx
            }, status=status.HTTP_200_OK)

        return Response({
            'id': patch.id,
            'code': 0,
            'emails': emails,
            'to': to,
        }, status=status.HTTP_200_OK)

    def send_email(self, patch):
        try:
            smtp = SMTPServer.objects.get(active=True, user = self.request.user)
        except:
            return Response({
                'code': 1,
                'detail': 'SMTP Server not configured'
            }, status=status.HTTP_404_NOT_FOUND)

        to, emails = self._parser_email(patch.emails)
        to = to.replace('"', '')
        cmd = '/usr/bin/git send-email --no-thread '
        cmd += '--confirm=never --to="%s" ' % to
        cmd += '--smtp-server %s ' % smtp.server
        cmd += '--smtp-server-port %s ' % smtp.port
        cmd += '--smtp-encryption %s ' % smtp.encryption
        cmd += '--smtp-user %s ' % smtp.username
        cmd += '--smtp-pass %s ' % smtp.password
        if smtp.flags & SMTPServer.SMTP_SSL_VERIFY_NONE:
            cmd += '--smtp-ssl-cert-path "" '
        if len(smtp.alias) > 0:
            cmd += '--from "%s <%s>" ' % (smtp.alias, smtp.email)
        else:
            cmd += '--from %s ' % smtp.email
        if not patch.msgid is None and len(patch.msgid) > 0:
            cmd += '--in-reply-to %s ' % patch.msgid
        cmd += patch.fullpath()

        print cmd
        ret, drun = execute_shell_unicode(cmd)
        drun = drun.replace(patch.dirname(), '')
        if ret != 0:
            ctx = '<pre>%s</pre>' % (html.escape(drun))
            ctx += '<div id="steperrors"><font color=red>Your SMTP setting is not correctly!</font></div>'
            return Response({
                'id': patch.id,
                'code': 0,
                'detail': ctx
            }, status=status.HTTP_400_BAD_REQUEST)

        for line in drun.split('\n'):
            if line.find("Message-Id: ") == 0:
                line = line.replace("Message-Id: ", "")
                line = line.lstrip('<')
                patch.msgid = line.rstrip('>')
                break

        patch.status = Patch.PATCH_STATUS_MAILED
        patch.save()

        return Response({
            'id': patch.id,
            'code': 0,
            'detail': '<pre>Patch has been sent succeed!</pre>'
        }, status=status.HTTP_200_OK)

    def put(self, request, id, step):
        try:
            patch = Patch.objects.get(type__user=self.request.user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if patch.status != Patch.PATCH_STATUS_PENDDING:
            return Response({
                'code': 1,
                'detail': 'Wrong status %d ' % patch.status
            }, status=status.HTTP_400_BAD_REQUEST)

        if step == 'checkpatch':
            return self.check_patch(patch)
        elif step == 'checkemail':
            return self.check_send_email(patch)
        elif step == 'sendemail':
            return self.send_email(patch)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class PatchRepoLatestView(APIView):
    def put(self, request, id):
        try:
            patch = Patch.objects.get(type__user=self.request.user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        ntag = RepositoryTag.objects.filter(repo__name = patch.tag.repo.name).order_by("-id")
        if len(ntag) == 0:
            return Response({
                'code': 1,
                'detail': 'linux.git Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        patch.tag.total = F('total') - 1
        patch.tag.save()
        patch.tag = ntag[0]
        patch.save()
        patch.tag.total = F('total') + 1
        patch.tag.save()

        return Response({
            'id': patch.id,
            'detail': 'success'
        }, status=status.HTTP_200_OK)

class PatchRepoStableView(APIView):
    def put(self, request, id):
        try:
            patch = Patch.objects.get(type__user=self.request.user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        ntag = RepositoryTag.objects.filter(repo__name = 'linux.git').order_by("-id")
        if len(ntag) == 0:
            return Response({
                'code': 1,
                'detail': 'linux.git Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        patch.tag.total = F('total') - 1
        patch.tag.save()
        patch.tag = ntag[0]
        patch.save()
        patch.tag.total = F('total') + 1
        patch.tag.save()

        return Response({
            'id': patch.id,
            'detail': 'success'
        }, status=status.HTTP_200_OK)

class PatchRepoNextView(APIView):
    def put(self, request, id):
        try:
            patch = Patch.objects.get(type__user=self.request.user, id=id)
        except:
            return Response({
                'code': 1,
                'detail': 'Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        ntag = RepositoryTag.objects.filter(repo__name = 'linux-next.git').order_by("-id")
        if len(ntag) == 0:
            return Response({
                'code': 1,
                'detail': 'linux-next.git Not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        patch.tag.total = F('total') - 1
        patch.tag.save()
        patch.tag = ntag[0]
        patch.save()
        patch.tag.total = F('total') + 1
        patch.tag.save()

        return Response({
            'id': patch.id,
            'detail': 'success'
        }, status=status.HTTP_200_OK)
