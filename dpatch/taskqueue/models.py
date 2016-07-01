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

from django.db import models
from dpatch.engine.models import PatchType
from dpatch.repository.models import RepositoryTag
from dpatch.patch.models import Patch

from django.utils.translation import ugettext_lazy as _

class ScanTaskQueue(models.Model):
    id = models.AutoField(
        primary_key = True,
        verbose_name=_('ID'),
    )

    #0: new, 1: running, 2: finish
    status = models.IntegerField(
        default = 0,
        verbose_name=_('Status'),
    )

    priority = models.IntegerField(
        default = 0,
        verbose_name=_('Priority'),
    )

    type = models.ForeignKey(
        PatchType,
        verbose_name=_('Patch Type')
    )

    tag = models.ForeignKey(
        RepositoryTag,
        verbose_name=_('Repository Tag')
    )

    filename = models.CharField(
        max_length = 256,
        blank = True,
        verbose_name=_('File Name'),
    )

    date = models.DateTimeField(
        auto_now_add = True,
        verbose_name=_('Date'),
    )

    def __unicode__(self):
        return u'%s' %(self.id)

class StatusTaskQueue(models.Model):
    id = models.AutoField(
        primary_key = True,
        verbose_name=_('ID'),
    )

    #0: new, 1: running, 2: finish
    status = models.IntegerField(
        default = 0,
        verbose_name=_('Status'),
    )

    priority = models.IntegerField(
        default = 0,
        verbose_name=_('Priority'),
    )

    patch = models.ForeignKey(
        Patch,
        verbose_name=_('Patch')
    )

    date = models.DateTimeField(
        auto_now_add = True,
        verbose_name=_('Date'),
    )

    def __unicode__(self):
        return u'%s' %(self.id)
