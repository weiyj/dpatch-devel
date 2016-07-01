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

import sys
import django

django.setup()

from django.db.models import Q
from dpatch.patch.models import Patch
from dpatch.taskqueue.models import StatusTaskQueue

def main(args):

    patchs = Patch.objects.filter(Q(status = Patch.PATCH_STATUS_NEW) |
                                Q(status = Patch.PATCH_STATUS_PATCH) |
                                Q(status = Patch.PATCH_STATUS_RENEW) |
                                Q(status = Patch.PATCH_STATUS_PENDDING) |
                                Q(status = Patch.PATCH_STATUS_MAILED) |
                                Q(status = Patch.PATCH_STATUS_ACCEPTED))
    for patch in patchs:
        if StatusTaskQueue.objects.filter(status = 0, patch = patch).count() > 0:
            continue

        task = StatusTaskQueue(status = 0, patch = patch)
        task.save()

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
