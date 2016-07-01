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

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from dpatch.repository.models import RepositoryTag
from dpatch.engine.models import PatchType

class Patch(models.Model):
    PATCH_STATUS_NEW = 101
    PATCH_STATUS_PATCH = 102
    PATCH_STATUS_MERGED = 103
    PATCH_STATUS_RENEW = 104
    PATCH_STATUS_REPORT = 105
    PATCH_STATUS_PENDDING = 201
    PATCH_STATUS_MAILED = 301
    PATCH_STATUS_FIXED = 401
    PATCH_STATUS_REMOVED = 402
    PATCH_STATUS_IGNORED = 403
    PATCH_STATUS_OBSOLETED = 404
    PATCH_STATUS_APPLIED = 405
    PATCH_STATUS_REJECTED = 406
    PATCH_STATUS_ACCEPTED = 407

    PATCH_STATUS_CHOICES = (
        (PATCH_STATUS_NEW, 'NEW'),
        (PATCH_STATUS_PATCH, 'PATCH'),
        (PATCH_STATUS_MERGED, 'MERGED'),
        (PATCH_STATUS_RENEW, 'RENEW'),
        (PATCH_STATUS_REPORT, 'REPORT'),
        (PATCH_STATUS_PENDDING, 'PENDDING'),
        (PATCH_STATUS_MAILED, 'MAILED'),
        (PATCH_STATUS_FIXED, 'FIXED'),
        (PATCH_STATUS_REMOVED, 'REMOVED'),
        (PATCH_STATUS_IGNORED, 'IGNORED'),
        (PATCH_STATUS_OBSOLETED, 'OBSOLETED'),
        (PATCH_STATUS_APPLIED, 'APPLIED'),
        (PATCH_STATUS_REJECTED, 'REJECTED'),
        (PATCH_STATUS_ACCEPTED, 'ACCEPTED'),
    )

    BUILD_STASTU_TBD = 0
    BUILD_STASTU_PASS = 1
    BUILD_STASTU_FAIL = 2
    BUILD_STASTU_WARN = 3
    BUILD_STASTU_SKIP = 4

    BUILD_STATUS_CHOICES = (
        (BUILD_STASTU_TBD, 'TBD'),
        (BUILD_STASTU_PASS, 'PASS'),
        (BUILD_STASTU_FAIL, 'FAIL'),
        (BUILD_STASTU_WARN, 'WARN'),
        (BUILD_STASTU_SKIP, 'SKIP'),
    )

    id = models.AutoField(
        primary_key = True,
        verbose_name=_('ID'),
    )

    tag = models.ForeignKey(
        RepositoryTag,
        verbose_name=_('Tag')
    )

    type = models.ForeignKey(
        PatchType,
        verbose_name=_('Type')
    )

    status = models.IntegerField(
        choices = PATCH_STATUS_CHOICES,
        default = PATCH_STATUS_NEW,
        verbose_name=_('Status')
    )

    file = models.CharField(
        max_length = 256,
        verbose_name=_('File Name')
    )

    date = models.DateTimeField(
        auto_now = True,
        verbose_name=_('Date')
    )

    mergered = models.IntegerField(
        default = 0,
        verbose_name=_('Mergered')
    )

    mglist = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name=_('Mergered Patch')
    )

    commit = models.CharField(
        max_length = 60,
        blank = True,
        verbose_name=_('Commit in Git')
    )

    module = models.CharField(
        max_length = 60,
        blank = True,
        verbose_name=_('Module Name')        
    )

    report = models.TextField(
        blank = True,
        verbose_name=_('Report')        
    )

    diff = models.TextField(
        blank = True,
        verbose_name=_('Diff')        
    )

    title = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name=_('Title')        
    )

    description = models.TextField(
        max_length = 1024,
        blank = True,
        verbose_name=_('Description')        
    )

    version = models.IntegerField(
        default = 1,
        verbose_name=_('Version')        
    )

    emails = models.CharField(
        max_length = 512,
        blank = True,
        verbose_name=_('Emails')        
    )

    comment = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name=_('Comment')        
    )

    content = models.TextField(
        blank = True,
        verbose_name=_('Content')        
    )

    build = models.IntegerField(
        choices = BUILD_STATUS_CHOICES,
        default = BUILD_STASTU_TBD,
        verbose_name=_('Build Status')        
    )

    buildlog = models.TextField(
        blank = True,
        verbose_name=_('Build Log')        
    )

    msgid = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name=_('Message ID')        
    )

    def __unicode__(self):
        return u'%s %s' %(self.tag, self.file)

    def filename(self, prefix = 1):
        fname = re.sub(r'\[[^\]]*\]', '', self.title)
        fname = re.sub(r'\W+', '-', fname.strip())
        if len(fname) > 52:
            fname = fname[:52]
        return "%04d-%s.patch" % (prefix, fname)

    def dirname(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'PATCH')

    def tempdir(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'TEMP')

    def fullpath(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'PATCH', self.filename())

    def username(self):
        if len(self.type.username) == 0:
            return self.tag.repo.username
        else:
            return self.type.username

    def email(self):
        if len(self.type.email) == 0:
            return self.tag.repo.email
        else:
            return self.type.email

    def sourcefile(self):
        return os.path.join(self.tag.repo.dirname(), self.file)

    def filecontent(self):
        sfile = self.sourcefile()
        if os.path.exists(sfile) and os.path.isfile(sfile):
            with open(sfile, 'r') as f:
                return f.read()
        return ""
