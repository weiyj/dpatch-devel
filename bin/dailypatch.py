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
import sys
import json
import re
import hashlib
import django

django.setup()

from dpatch.core.utils import is_source_file

from dpatch.repository.models import Repository, RepositoryTag, RepositoryHistory
from dpatch.repository.models import FileChecksum
from dpatch.engine.models import PatchType
from dpatch.patch.models import Patch
from dpatch.taskqueue.models import ScanTaskQueue
from dpatch.core.repository import GitRepository

def DEBUG(msg):
    print "%s" % msg

def is_white_black_list(wblist, sfile):
    try:
        alist = json.loads(wblist)
        for p in alist:
            if re.match(p, sfile) or sfile == p:
                return True
    except:
        return False

    return False

def get_file_checksum(repo, sfile):
    rfile = os.path.join(repo.dirname(), sfile)
    with open(rfile, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()

def is_file_merge_changed(repo, sfile):
    nchksum = get_file_checksum(repo, sfile)
    ochksum = FileChecksum.objects.filter(file = sfile, checksum = nchksum)
    if len(ochksum) != 0:
        return True
    else:
        return True

def is_file_changed(repo, sfile):
    # removed file?
    if not os.path.exists(os.path.join(repo.dirname(), sfile)):
        return True

    if repo.name == 'linux.git':
        return is_file_merge_changed(repo, sfile)

    if repo.name != 'linux-next.git':
        return True

    nchksum = get_file_checksum(repo, sfile)
    ochksum = FileChecksum.objects.filter(repo = repo, file = sfile)
    if len(ochksum) != 0:
        if nchksum == ochksum[0].checksum:
            return False
        else:
            ochksum[0].checksum = nchksum;
            ochksum[0].save()
            return True
    else:
        chksum = FileChecksum(repo = repo, file = sfile, checksum = nchksum)
        chksum.save()
        return True

def remove_unchange_file(repo, changelists):
    rflists = []

    for sfile in changelists:
        # check file ext
        if not is_source_file(sfile):
            continue

        # check white/black list
        if len(repo.includes) != 0:
            # file not exists in white list
            if not is_white_black_list(repo.includes, sfile):
                continue
        elif len(repo.excludes) != 0:
            # file in black list
            if is_white_black_list(repo.excludes, sfile):
                continue

        # check file checksum
        if not is_file_changed(repo, sfile):
            continue

        rflists.append(sfile)

    return rflists

def check_patch(repo, git, rtag, flists, commit):
    tcount = 0
    for pt in PatchType.objects.filter(user=repo.user):
        if pt.engine.status is False:
            DEBUG("engine %s is disabled" % pt.engine.name)
            continue

        if pt.status is False:
            DEBUG("patch type %s is disabled" % pt.name)
            continue

        if pt.flags & PatchType.TYPE_FLAG_DEV_ONLY and repo.developing is False:
            DEBUG("patch type %s is skip for non-devel" % pt.name)
            continue

        for f in flists:
            # check white black list
            # file not exists in white list
            if len(pt.includes) != 0 and not is_white_black_list(pt.includes, f):
                DEBUG("file %s not in type %s's includes list" % (f, pt.name))
                continue

            # file in black list
            if len(pt.excludes) != 0 and is_white_black_list(pt.excludes, f):
                DEBUG("file %s in type %s's excludes list" % (f, pt.name))
                continue

            num = ScanTaskQueue.objects.filter(status = 0, type = pt, filename = f).count()
            if num > 0:
                DEBUG("same task exists for file %s" % f)
                continue

            # treat patch marked with Rejected as except file
            if Patch.objects.filter(file = f, type = pt, status = Patch.PATCH_STATUS_REJECTED).count() > 0:
                DEBUG("rejected patch exists for file %s" % f)
                continue

            # treat patch marked with Applied and commit is '' as EXISTS patch
            if Patch.objects.filter(file = f, type = pt, status = Patch.PATCH_STATUS_ACCEPTED).count() > 0:
                DEBUG("accepted patch exists for file %s" % f)
                continue

            task = ScanTaskQueue(status = 0, type = pt, filename = f, tag = rtag)
            task.save()

            tcount = tcount + 1

    return tcount

def main(args):
    for repo in Repository.objects.filter(status=True):
        print "Check repository %s" % repo.name
        repotree = GitRepository(repo.name, repo.dirname(), repo.url, repo.commit, repo.stable)
        if repotree.check_update() == False:
            tag = repotree.get_tag()
            rtags = RepositoryTag.objects.filter(repo = repo, name = tag)
            if len(rtags) > 0:
                rtag = rtags[0]
                rtag.changelist = ''
                rtag.save()
            history = RepositoryHistory(repo = repo, changes = 0)
            history.save()
            print "No update for repository %s" % repo.name
            continue

        # update build tree
        print "Update build repository for %s" % repo.name
        _burl = "file://%s" % repo.dirname()
        buildtree = GitRepository(repo.name, repo.builddir(), _burl, repo.commit, repo.stable)
        buildtree.check_update()

        tag = repotree.get_tag()
        commit = repotree.get_commit()

        # do not scan at the first time
        if repo.commit is None or len(repo.commit) == 0:
            print "Skip first time for repository %s" % repo.name
            # only linux-next.git need real stable commit
            if repotree.is_linux_next():
                repo.stable = repotree.get_remote_stable()
            else:
                repo.stable = commit
            repo.commit = commit
            repo.save()
            continue

        if repotree.is_linux_next() == True and commit == repotree.get_stable():
            print "update failed for repository %s" % repo.name
            continue

        changelists = repotree.changelist(repo.commit, commit)
        changelists = remove_unchange_file(repo, changelists)

        print "Total changed files %d" % len(changelists)

        tags = RepositoryTag.objects.filter(repo = repo, name = tag)
        rtag = None
        if tags.count() == 0:
            rtag = RepositoryTag(repo = repo, name = tag, total = 0)
            rtag.save()
        else:
            rtag = tags[0]

        print "Add tasks for repository %s" % os.path.basename(repo.name)
        tcount = 0
        try:
            tcount = check_patch(repo, repotree, rtag, changelists, commit)
        except:
            pass

        rtag.changelist = json.dumps(changelists)
        rtag.save()

        repo.commit = commit
        if repotree.is_linux_next():
            repo.stable = repotree.get_stable()
        repo.save()

        history = RepositoryHistory(repo = repo, changes=len(changelists))
        history.save()

        print "Total task %d" % tcount

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
