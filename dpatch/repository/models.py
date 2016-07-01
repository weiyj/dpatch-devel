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

class Repository(models.Model):

    KERNEL = 0

    REPOSITORY_TYPE_CHOICES = (
        (KERNEL, 'kernel'),
    )

    PROTO_GIT = 0

    REPOSITORY_PROTO_CHOICES = (
        (PROTO_GIT, 'git'),
    )

    id = models.AutoField(
        primary_key = True,
        verbose_name = _('ID'),
    )

    type = models.IntegerField(
        choices = REPOSITORY_TYPE_CHOICES,
        default = KERNEL,
        verbose_name = _('Type')
    )

    user = models.ForeignKey(
        User,
        verbose_name=_('User')
    )

    name = models.CharField(
        max_length = 60,
        verbose_name=_('Name'),
    )

    url = models.CharField(
        max_length = 256,
        verbose_name=_('URL'),
    )

    protocol = models.IntegerField(
        choices = REPOSITORY_PROTO_CHOICES,
        default = PROTO_GIT,
        verbose_name = _('Protocol')
    )

    username = models.CharField(
        max_length = 60,
        verbose_name=_('Username'),
    )

    email = models.CharField(
        max_length = 256,
        verbose_name=_('Email'),
    )

    developing = models.BooleanField(
        default = False,
        verbose_name=_('Developing'),
    )

    devel = models.CharField(
        max_length = 60,
        blank = True,
        verbose_name=_('Development Tree'),
    )

    build = models.BooleanField(
        default = True,
        verbose_name=_('Enable Build'),
    )

    commit = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name=_('Last Commit'),
    )

    stable = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name=_('Stable Commit'),
    )

    update = models.DateTimeField(
        auto_now = True,
        verbose_name=_('Last Update'),
    )

    includes = models.TextField(
        blank = True,
        verbose_name = _('Include Paths'),
    )

    excludes = models.TextField(
        blank = True,
        verbose_name = _('Exclude Paths'),
    )

    status = models.BooleanField(
        default = False,
        verbose_name = _('Enabled'),
    )

    def __unicode__(self):
        return u'%s' %(self.name)

    def dirname(self):
        dname = os.path.basename(self.url).replace('.git', '')
        return os.path.join(settings.DATA_DIR, 'repo', str(self.user.id), dname)

    def builddir(self):
        dname = os.path.basename(self.url).replace('.git', '')
        return os.path.join(settings.DATA_DIR, 'build', str(self.user.id), dname)


class RepositoryTag(models.Model):

    id = models.AutoField(
        primary_key = True,
        verbose_name = _('ID'),
    )

    repo = models.ForeignKey(
        Repository,
        verbose_name = _('Repository'),
    )

    name = models.CharField(
        max_length = 60,
        verbose_name = _('Name'),
    )

    total = models.IntegerField(
        default = 0,
        verbose_name = _('Total Patchs'),
    )

    changelist = models.TextField(
        blank = True,
        verbose_name = _('Changed Files'),
    )

    running = models.BooleanField(
        default = False,
        verbose_name = _('Running'),
    )

    def __unicode__(self):
        return u'%s' %(self.name)

class RepositoryHistory(models.Model):

    id = models.AutoField(
        primary_key = True,
        verbose_name = _('ID'),
    )

    repo = models.ForeignKey(
        Repository,
        verbose_name = _('Repository'),
    )

    changes = models.IntegerField(
        default = 0,
        verbose_name = _('Change'),
    )

    date = models.DateField(
        auto_now_add = True,
        verbose_name = _('Date')
    )

class FileChecksum(models.Model):

    id = models.AutoField(
        primary_key = True,
        verbose_name=_('ID'),
    )

    repo = models.ForeignKey(
        Repository,
        verbose_name=_('Repository'),
    )

    file = models.CharField(
        max_length = 256,
        verbose_name=_('File Name'),
    )

    checksum = models.CharField(
        max_length = 60,
        verbose_name=_('Checksum'),
    )

    date = models.DateTimeField(
        auto_now = True,
        verbose_name=_('Date')
    )

    def __unicode__(self):
        return u'%s' %(self.file)

class FileModule(models.Model):

    id = models.AutoField(
        primary_key = True,
        verbose_name=_('ID'),
    )

    name = models.CharField(
        max_length = 256,
        verbose_name=_('Module Name'),
    )

    file = models.CharField(
        max_length = 256,
        verbose_name=_('File Name'),
    )

    repo = models.ForeignKey(
        Repository,
        verbose_name=_('Repository'),
    )

    def __unicode__(self):
        return u'%s' %(self.name)

