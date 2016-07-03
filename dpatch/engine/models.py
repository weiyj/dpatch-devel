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

from django.db import models
from django.conf import settings

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class PatchEngine(models.Model):
    id = models.AutoField(
        primary_key = True,
        verbose_name = _('ID'),
    )

    name = models.CharField(
        max_length = 60,
        verbose_name = _('Name'),
    )

    status = models.BooleanField(
        default = False,
        verbose_name = _('Enabled'),
    )

    flags = models.IntegerField(
        default = 0,
        verbose_name = _('Flags'),
    )

    setting = models.TextField(
        blank = True,
        verbose_name = _('Setting'),
    )

    total = models.IntegerField(
        default = 0,
        verbose_name = _('Total Types'),
    )

    def __unicode__(self):
        return u'%s' %(self.name)

class PatchType(models.Model):
    TYPE_FLAG_DEV_ONLY = 1
    TYPE_FLAG_BUILD_SPARSE = 2
    TYPE_FLAG_SKIP_OBSOLETE = 4

    SOURCE_DEFINE = 0
    SOURCE_KERNEL = 1

    PATCH_TYPE_SRC_CHOICES = (
        (SOURCE_DEFINE, 'define'),
        (SOURCE_KERNEL, 'kernel'),
    )

    id = models.AutoField(
        primary_key = True,
        verbose_name = _('ID'),
    )

    user = models.ForeignKey(
        User,
        verbose_name = _('User')
    )

    name = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name = _('Name'),
    )

    engine = models.ForeignKey(
        PatchEngine,
        verbose_name = _('Engine'),
    )

    source = models.IntegerField(
        choices = PATCH_TYPE_SRC_CHOICES,
        default = SOURCE_DEFINE,
        verbose_name = _('Source')
    )

    title = models.CharField(
        max_length = 256,
        verbose_name = _('Title'),
    )

    description = models.TextField(
        blank = True,
        verbose_name = _('Description'),
    )

    comment = models.TextField(
        blank = True,
        verbose_name = _('Comment'),
    )

    flags = models.IntegerField(
        default = 0,
        verbose_name = _('Flags'),
    )

    username = models.CharField(
        max_length = 60,
        blank = True,
        verbose_name = _('Username'),
    )

    email = models.CharField(
        max_length = 60,
        blank = True,
        verbose_name = _('Email'),
    )

    filename = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name = _('FileName'),
    )

    options = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name = _('Options'),
    )

    fixed = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name = _('Fix Regex'),
    )

    content = models.TextField(
        blank = True,
        verbose_name = _('Content'),
    )

    bugfix = models.BooleanField(
        default = False,
        verbose_name = _('Bug Fix'),
    )

    reportonly = models.BooleanField(
        default = False,
        verbose_name = _('Report Only'),
    )

    includes = models.TextField(
        blank = True,
        verbose_name = _('Include Paths'),
    )

    excludes = models.TextField(
        blank = True,
        verbose_name = _('Exclude Paths'),
    )

    setting = models.TextField(
        blank = True,
        verbose_name = _('Setting'),
    )

    totalfile = models.IntegerField(
        default = 0,
        verbose_name = _('TotalFile'),
    )

    totaltime = models.IntegerField(
        default = 0,
        verbose_name = _('TotalTime'),
    )

    status = models.BooleanField(
        default = False,
        verbose_name = _('Enable'),
    )

    def __unicode__(self):
        return u'%s' %(self.name)

    def tempdir(self):
        return os.path.join(settings.DATA_DIR, 'repo', 'TEMP')

    def fullpath(self):
        if self.source == self.SOURCE_KERNEL:
            return os.path.join(settings.DATA_DIR, 'pattern', 'cocci', 'kernel', str(self.user.id), self.filename)
        else:
            return os.path.join(settings.DATA_DIR, 'pattern', 'cocci', 'defined', str(self.user.id), self.filename)
