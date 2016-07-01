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

from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class SMTPServer(models.Model):

    id = models.AutoField(
        primary_key = True,
        verbose_name = _('ID'),
    )

    user = models.ForeignKey(
        User,
        verbose_name = _('User')
    )

    active = models.BooleanField(
        default = False,
        verbose_name = _('Active'),
    )

    server = models.CharField(
        max_length = 256,
        verbose_name = _('Server'),
    )

    encryption = models.CharField(
        max_length = 256,
        verbose_name = _('Encryption'),
    )

    port = models.CharField(
        max_length = 20,
        verbose_name = _('Port'),
    )

    username = models.CharField(
        max_length = 256,
        verbose_name = _('Username'),
    )

    password = models.CharField(
        max_length = 256,
        verbose_name = _('Password'),
    )

    email = models.CharField(
        max_length = 256,
        verbose_name = _('Email'),
    )

    alias = models.CharField(
        max_length = 256,
        verbose_name = _('Alias'),
    )

class POPServer(models.Model):

    id = models.AutoField(
        primary_key = True,
        verbose_name = _('ID'),
    )

    user = models.ForeignKey(
        User,
        verbose_name = _('User')
    )

    active = models.BooleanField(
        default = False,
        verbose_name = _('Active'),
    )

    server = models.CharField(
        max_length = 256,
        verbose_name = _('Server'),
    )

    encryption = models.CharField(
        max_length = 256,
        verbose_name = _('Encryption'),
    )

    port = models.CharField(
        max_length = 20,
        verbose_name = _('Port'),
    )

    username = models.CharField(
        max_length = 256,
        verbose_name = _('Username'),
    )

    password = models.CharField(
        max_length = 256,
        verbose_name = _('Password'),
    )

    email = models.CharField(
        max_length = 256,
        verbose_name = _('Email'),
    )

    alias = models.CharField(
        max_length = 256,
        verbose_name = _('Alias'),
    )
