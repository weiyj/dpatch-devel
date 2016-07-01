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
import time
import django
import re

django.setup()

from time import localtime, strftime
from django.db.models import F

from dpatch.taskqueue.models import ScanTaskQueue, StatusTaskQueue
from dpatch.patch.models import Patch
from dpatch.engine.models import PatchType
from dpatch.repository.models import Repository

from dpatch.core.checkinclude import CheckIncludeEngine
from dpatch.core.checkrelease import CheckReleaseEngine
from dpatch.core.checkversion import CheckVersionEngine
from dpatch.core.checksparse import CheckSparseEngine
from dpatch.core.checkcoccinelle import CheckCocciPatchEngine
from dpatch.core.checkcoccinelle import CheckCocciReportEngine
from dpatch.core.patchformater import PatchFormater
from dpatch.core.utils import execute_shell, execute_shell_unicode
from dpatch.core.utils import is_c_file, is_white_black_list, execute_shell_full

def INFO(msg):
    print "%s [INFO] %s" %(strftime("%a, %d %b %Y %H:%M:%S", localtime()), msg)

def ERROR(msg):
    print "%s [ERROR] %s" %(strftime("%a, %d %b %Y %H:%M:%S", localtime()), msg)

def update_tag_total(tag):
    tag.total = F('total') + 1
    tag.save()

def check_patch(task, detector):
    patchs = Patch.objects.filter(file = task.filename, type = task.type)
    rpatchs = []

    PENDINGS = [
        Patch.PATCH_STATUS_NEW,
        Patch.PATCH_STATUS_REPORT,
        Patch.PATCH_STATUS_PATCH,
        Patch.PATCH_STATUS_RENEW,
        Patch.PATCH_STATUS_PENDDING,
        Patch.PATCH_STATUS_MAILED
    ]

    for p in patchs:
        if not p.status in PENDINGS:
            continue
        rpatchs.append(p)

    detector.set_filename(task.filename)
    # source file maybe removed
    if not os.path.exists(detector._get_file_path()):
        detector.debug("file removed")
        for p in rpatchs:
            p.status = Patch.PATCH_STATUS_REMOVED
            p.save()
        return False

    should_patch = detector.should_patch()
    if detector.has_error():
        detector.error("detect error!")
        return False

    # fixed ?
    if len(rpatchs) != 0 and should_patch == False:
        detector.info("detect no patch")
        for p in rpatchs:
            if p.status == Patch.PATCH_STATUS_MAILED:
                p.status = Patch.PATCH_STATUS_ACCEPTED
            elif p.mergered != 0:
                mpatch = Patch.objects.filter(id = p.mergered)
                if len(mpatch) != 0:
                    if mpatch[0].status == Patch.PATCH_STATUS_MAILED:
                        mpatch[0].status = Patch.PATCH_STATUS_ACCEPTED
                        p.status = Patch.PATCH_STATUS_ACCEPTED
                    else:
                        mpatch[0].status = Patch.PATCH_STATUS_FIXED
                        p.status = Patch.PATCH_STATUS_FIXED
                    mpatch[0].save()
                else:
                    p.status = Patch.PATCH_STATUS_FIXED
            else:
                p.status = Patch.PATCH_STATUS_FIXED
                p.save()
        return False

    # new patch should be added
    if should_patch == True and len(rpatchs) == 0:
        detector.info("detect new patch")
        text = detector.get_patch()
        patch = Patch(tag = task.tag, file = task.filename, type = task.type,
                      status = Patch.PATCH_STATUS_PATCH, diff = text)
        user = patch.username()
        email = patch.email()
        desc = detector.get_patch_description()
        title = detector.get_patch_title()
        if desc is None:
            desc = task.type.description
        if title is None:
            title = task.type.title

        formater = PatchFormater(task.tag.repo.dirname(), task.filename, user, email, title, desc, text)
        patch.content = formater.format_patch()
        patch.title = formater.format_title()
        patch.description = formater.format_desc()
        patch.emails = formater.get_mail_list()
        patch.module = formater.get_module()
        patch.save()

        update_tag_total(task.tag)

        return True

    return False

def check_report(task, detector):
    reports = Patch.objects.filter(file = task.filename, type = task.type)
    oreports = []

    PENDINGS = [
        Patch.PATCH_STATUS_NEW,
        Patch.PATCH_STATUS_REPORT,
        Patch.PATCH_STATUS_PATCH,
        Patch.PATCH_STATUS_RENEW,
        Patch.PATCH_STATUS_PENDDING,
        Patch.PATCH_STATUS_MAILED
    ]

    for r in reports:
        if not r.status in PENDINGS:
            continue
        oreports.append(r)

    detector.set_filename(task.filename)
    # source file maybe removed
    if not os.path.exists(detector._get_file_path()):
        detector.debug("file removed")
        for p in oreports:
            p.status = Patch.PATCH_STATUS_REMOVED
            p.save()
        return False

    should_report = detector.should_report()
    if detector.has_error():
        detector.error("detect error!")
        return False

    if should_report is False:
        for r in oreports:
            if r.status == Patch.PATCH_STATUS_MAILED:
                r.status = Patch.PATCH_STATUS_ACCEPTED
                r.save()
            else:
                if r.mergered == 0:
                    r.status = Patch.PATCH_STATUS_FIXED
                    r.save()
                else:
                    mreport = Patch.objects.filter(id = r.mergered)
                    if len(mreport) != 0:
                        if mreport[0].status == Patch.PATCH_STATUS_MAILED:
                            mreport[0].status = Patch.PATCH_STATUS_ACCEPTED
                            r.status = Patch.PATCH_STATUS_ACCEPTED
                        else:
                            mreport[0].status = Patch.PATCH_STATUS_FIXED
                            r.status = Patch.PATCH_STATUS_FIXED
                        mreport[0].save()
                    else:
                        r.status = Patch.PATCH_STATUS_FIXED
                    r.save()
        return False

    if len(oreports) > 0:
        return False

    text = detector.get_report()
    report = Patch(tag = task.tag, file = task.filename, type = task.type,
                    status = Patch.PATCH_STATUS_NEW, report = '\n'.join(text))
    report.title = task.type.title
    report.desc = task.type.description
    report.save()

    update_tag_total(task.tag)

    return True

def do_task_patch():
    # remove finished task first
    ScanTaskQueue.objects.filter(status=2).delete()

    tasks = ScanTaskQueue.objects.filter(status=0).order_by('id')[:20]
    for task in tasks:
        if task.type.engine.status is False or task.type.status is False:
            task.status = 2
        else:
            task.status = 1
        task.save()

    count = len(tasks)

    for task in tasks:
        if task.status != 1:
            continue

        INFO("start check file %s for %s" % (task.filename, task.type.name))
        stime = time.time()
        result = False
        repodir = task.tag.repo.dirname()
        repobuid = task.tag.repo.builddir()
        if task.type.engine.name == 'checkinclude':
            if task.type.name == 'checkinclude':
                detector = CheckIncludeEngine(repodir, repobuid)
                result = check_patch(task, detector)
            elif task.type.name == 'checkversion':
                detector = CheckVersionEngine(repodir, repobuid)
                result = check_patch(task, detector)
            elif task.type.name == 'checkrelease':
                detector = CheckReleaseEngine(repodir, repobuid)
                result = check_patch(task, detector)
        elif task.type.engine.name == 'checksparse':
            detector = CheckSparseEngine(repodir, repobuid)
            result = check_patch(task, detector)
        elif task.type.engine.name == 'checkcoccinelle':
            if task.type.reportonly is False:
                detector = CheckCocciPatchEngine(repodir, task.type, repobuid)
                result = check_patch(task, detector)
            else:
                detector = CheckCocciReportEngine(repodir, task.type, repobuid)
                result = check_report(task, detector)
        else:
            ERROR("unknow engine %s" % task.type.engine.name)
            continue

        ptime = time.time() - stime
        INFO("end check file %s, time %d, %s" %(task.filename, ptime, result))

        # save performance data
        task.type.totalfile = task.type.totalfile + 1
        task.type.totaltime = task.type.totaltime + ptime
        task.type.save()

        # change task status
        task.status = 2
        task.save()

    return count

def do_check_patch_disabled(patch):
    if patch.status == Patch.PATCH_STATUS_MAILED:
        return False

    patch.status = Patch.PATCH_STATUS_IGNORED
    patch.save()

    return True

def do_check_patch_applied(patch):
    if not os.path.exists(os.path.join(patch.tag.repo.dirname(), patch.file)):
        return False

    ptitle = re.sub('Subject: \[PATCH[^\]]*]', '', patch.title).strip()
    ptitle = re.sub('^.*:', '', ptitle).strip()
    if len(ptitle) > 2:
        ptitle = ptitle[1:]
    cmds = 'cd %s; git log --author="%s" --pretty="format:%%H|%%s" %s' % (patch.tag.repo.dirname(), patch.username(), patch.file)
    for line in execute_shell_full(cmds)[::-1]:
        if line.find('|') == -1:
            continue

        rtitle = line.split('|')[1]
        if line.upper().find(ptitle.upper()) == -1 and ptitle.upper().find(rtitle.upper()) == -1:
            continue

        commit = line.split('|')[0]
        if Patch.objects.filter(commit = commit).count() != 0:
            continue

        patch.status = Patch.PATCH_STATUS_APPLIED
        patch.commit = commit
        patch.save()
        return True

    return False

def check_patch_status(patch, detector):
    detector.set_filename(patch.file)

    # we have checked this, file remove in devel tree?
    if not os.path.exists(detector._get_file_path()):
        patch.status = Patch.PATCH_STATUS_REMOVED
        patch.save()
        return False

    should_patch = detector.should_patch()
    if detector.has_error():
        detector.error("detect error!")
        return False

    if should_patch is False:
        return True

    return False

def check_report_status(patch, detector):
    detector.set_filename(patch.file)

    # we have checked this, file remove in devel tree?
    if not os.path.exists(detector._get_file_path()):
        patch.status = Patch.PATCH_STATUS_REMOVED
        patch.save()
        return False

    should_report = detector.should_report()
    if detector.has_error():
        detector.error("detect error!")
        return False

    if should_report is False:
        return True

    return False

def _do_check_patch_fixed(repodir, repobuid, patch):
    etype = patch.type
    if etype.engine.name == 'checkinclude':
        if etype.name == 'checkinclude':
            detector = CheckIncludeEngine(repodir, repobuid)
            return check_patch_status(patch, detector)
        elif etype.name == 'checkversion':
            detector = CheckVersionEngine(repodir, repobuid)
            return check_patch_status(patch, detector)
        elif etype.name == 'checkrelease':
            detector = CheckReleaseEngine(repodir, repobuid)
            return check_patch_status(patch, detector)
    elif etype.engine.name == 'checksparse':
        detector = CheckSparseEngine(repodir, repobuid)
        return check_patch_status(patch, detector)
    elif etype.engine.name == 'checkcoccinelle':
        if etype.reportonly is False:
            detector = CheckCocciPatchEngine(repodir, etype, repobuid)
            return check_patch_status(patch, detector)
        else:
            detector = CheckCocciReportEngine(repodir, etype, repobuid)
            return check_report_status(patch, detector)
    else:
        ERROR("unknow engine %s" % etype.engine.name)
        return False

def do_check_patch_changes(patch):
    #patch.PATCH_STATUS_NEW
    #patch.PATCH_STATUS_PATCH
    #patch.PATCH_STATUS_RENEW
    #patch.PATCH_STATUS_REPORT
    #patch.PATCH_STATUS_PENDDING
    #patch.PATCH_STATUS_MAILED
    repodir = patch.tag.repo.dirname()
    repobuid = patch.tag.repo.builddir()

    if not os.path.exists(os.path.join(repodir, patch.file)):
        patch.status = Patch.PATCH_STATUS_REMOVED
        patch.save()
        return True

    # check whether file exists in the excludes list
    if is_white_black_list(patch.type.excludes, patch.file):
        patch.status = Patch.PATCH_STATUS_IGNORED
        patch.save()
        return True

    fixed = _do_check_patch_fixed(repodir, repobuid, patch)

    # check whether patch is fixed in the development tree
    if fixed is False and len(patch.tag.repo.devel) > 0:
        try:
            repo = Repository.objects.get(name=patch.tag.repo.devel)
            repodir = repo.dirname()
            repobuid = repo.builddir()
            fixed = _do_check_patch_fixed(repodir, repobuid, patch)
        except:
            ERROR("development repository %s not exists?" % patch.tag.repo.devel)

    if fixed is True:
        if patch.status == patch.PATCH_STATUS_MAILED:
            patch.status = patch.PATCH_STATUS_ACCEPTED
            do_check_patch_applied(patch)
            return True
        else:
            patch.status = Patch.PATCH_STATUS_FIXED
            patch.save()
            return True

    return False

def do_task_status():
    # remove finished task first
    StatusTaskQueue.objects.filter(status=2).delete()

    IGNORES = [
        Patch.PATCH_STATUS_MERGED,
        Patch.PATCH_STATUS_FIXED,
        Patch.PATCH_STATUS_REMOVED,
        Patch.PATCH_STATUS_IGNORED,
        Patch.PATCH_STATUS_OBSOLETED,
        Patch.PATCH_STATUS_APPLIED,
        Patch.PATCH_STATUS_REJECTED
    ]

    tasks = StatusTaskQueue.objects.filter(status=0).order_by('id')[:20]
    #for task in tasks:
    #    task.status = 1
    #    task.save()

    for task in tasks:
        if task.patch.status in IGNORES:
            task.status = 2
            task.save()
            continue

        etype = task.patch.type
        if etype.engine.status is False or etype.status is False:
            if do_check_patch_disabled(task.patch):
                task.status = 2
                task.save()
                continue

        if task.patch.status == Patch.PATCH_STATUS_ACCEPTED:
            do_check_patch_applied(task.patch)
            task.status = 2
            task.save()
            continue

        do_check_patch_changes(task.patch)
        task.status = 2
        task.save()

    return len(tasks)

def commit_from_stable(repo):
    commits = execute_shell('cd %s; cat .git/refs/remotes/origin/master' % repo.builddir())
    return commits[-1]

def commit_from_repo(repo):
    commits = execute_shell('cd %s; git log -n 1 --pretty=format:%%H%%n' % repo.builddir())
    return commits[-1]

def is_module_build(filename, output):
    if not isinstance(output, unicode):
        output = unicode(output, errors='ignore')

    if output.find('LD [M]') == -1:
        return False

    objfile = "%s.o" % filename[:-2]
    if filename[-2:] == '.c' and output.find(objfile) != -1:
        return True
    else:
        return False

def should_build_sparse(patch):
    if patch.type.flags & PatchType.TYPE_FLAG_BUILD_SPARSE:
        return True
    if patch.type.engine.name == "checksparse":
        return True
    return False

def do_task_build():
    patchs = Patch.objects.filter(status=Patch.PATCH_STATUS_PATCH, build=0)[:5]

    for patch in patchs:
        buildlog = ''

        if patch.file.find('arch/') == 0 and patch.file.find('arch/x86') != 0:
            patch.build = Patch.BUILD_STASTU_SKIP
            patch.save()
            continue

        fname = os.path.join(patch.dirname(), patch.filename())
        with open(fname, "w") as pdiff:
            try:
                pdiff.write(patch.content + '\n\n')
            except:
                pdiff.write(unicode.encode(patch.content + '\n\n', 'utf-8'))

        INFO("build for patch %s..." % os.path.basename(fname))
        repo = patch.tag.repo
        commit = commit_from_stable(patch.tag.repo)
        if commit is None or len(commit) == 0:
            commit = commit_from_repo(patch.tag.repo)
        execute_shell("cd %s; git reset --hard %s" % (patch.tag.repo.builddir(), commit))
        if os.path.exists(os.path.join(patch.tag.repo.builddir(), '.git/rebase-apply')):
            execute_shell("cd %s; rm -rf .git/rebase-apply" % patch.tag.repo.builddir())

        objfile = "%s.o" % patch.file[:-2]

        if should_build_sparse(patch):
            if not os.path.isdir(os.path.join(repo.builddir(), patch.file)):
                buildlog += '# make C=2 %s\n' % objfile
                ret, log = execute_shell_unicode("cd %s; make C=2 %s" % (repo.builddir(), objfile))
                buildlog += log
                buildlog += '\n'

            dname = os.path.dirname(patch.file)
            if len(dname.split(os.sep)) > 2:
                buildlog += '# make C=2 M=%s\n' % dname
                ret, log = execute_shell_unicode("cd %s; make C=2 M=%s" % (repo.builddir(), dname))
                buildlog += log
                buildlog += '\n'

        ret, log = execute_shell_unicode("cd %s; git am %s" % (repo.builddir(), fname))
        buildlog += '# git am %s\n' % os.path.basename(fname)
        buildlog += log
        if ret != 0:
            INFO("build failed")
            patch.build = Patch.BUILD_STASTU_FAIL
            patch.buildlog = buildlog
            patch.save()
            continue

        if patch.file.find('tools/') == 0:
            dname = os.path.dirname(patch.file)
            while len(dname) != 0 and not os.path.exists(os.path.join(repo.builddir(), dname, 'Makefile')):
                dname = os.path.dirname(dname)
            if len(dname) != 0:
                buildlog += '\n# cd %s; make\n' % dname
                ret, log = execute_shell_unicode("cd %s; make" % (os.path.join(repo.builddir(), dname)))
                buildlog += log
                if ret != 0:
                    INFO("build failed")
                    patch.build = Patch.BUILD_STASTU_FAIL
                    patch.buildlog = buildlog
                    patch.save()
                    continue
            else:
                buildlog += 'do not known how to build\n'
            log += '\nLD [M] %s\n' % objfile

        if patch.file.find('include/') != 0 and patch.file.find('tools/') != 0:
            dname = os.path.dirname(patch.file)
            while len(dname) != 0 and not os.path.exists(os.path.join(repo.builddir(), dname, 'Makefile')):
                dname = os.path.dirname(dname)
            if len(dname) != 0:
                buildlog += '\n# make M=%s\n' % dname
                ret, log = execute_shell_unicode("cd %s; make M=%s" % (repo.builddir(), dname))
                buildlog += log
                if ret != 0:
                    INFO("build failed")
                    patch.build = Patch.BUILD_STASTU_FAIL
                    patch.buildlog = buildlog
                    patch.save()
                    continue

        output = log
        if is_c_file(patch.file) and is_module_build(patch.file, output) == False:
            buildlog += '\n# make %s\n' % objfile
            ret, log = execute_shell_unicode("cd %s; make %s" % (repo.builddir(), objfile))
            buildlog += log
            if ret != 0:
                INFO("build failed")
                patch.build = Patch.BUILD_STASTU_FAIL
                patch.buildlog = buildlog
                patch.save()
                if buildlog.find("Run 'make oldconfig' to update configuration.") != -1:
                    os.system("cd %s; make allmodconfig" % repo.builddir())
                continue
            output = log
            if output.find(objfile) != -1:
                log += '\nLD [M] %s\n' % objfile

        output = log
        if patch.file.find('include/') == 0 or is_module_build(patch.file, output) == False:
            buildlog += '\n# make vmlinux\n'
            ret, log = execute_shell_unicode("cd %s; make vmlinux" % (repo.builddir()))
            buildlog += log
            if ret != 0:
                INFO("build failed")
                patch.build = Patch.BUILD_STASTU_FAIL
                patch.buildlog = buildlog
                patch.save()
                if buildlog.find("Run 'make oldconfig' to update configuration.") != -1:
                    os.system("cd %s; make allmodconfig" % repo.builddir())
                continue

        if should_build_sparse(patch):
            if not os.path.isdir(os.path.join(repo.builddir(), patch.file)):
                buildlog += '\n# make C=2 %s\n' % objfile
                ret, log = execute_shell_unicode("cd %s; make C=2 %s" % (repo.builddir(), objfile))
                buildlog += log
                buildlog += '\n'

            dname = os.path.dirname(patch.file)
            if len(dname.split(os.sep)) > 2:
                buildlog += '\n# make C=2 M=%s\n' % dname
                ret, log = execute_shell_unicode("cd %s; make C=2 M=%s" % (repo.builddir(), dname))
                buildlog += log
                buildlog += '\n'

        if buildlog.find(' Error ') != -1:
            patch.build = Patch.BUILD_STASTU_FAIL
        elif buildlog.find(': warning: ') != -1:
            patch.build = Patch.BUILD_STASTU_WARN
        else:
            patch.build = Patch.BUILD_STASTU_PASS
        patch.buildlog = buildlog
        patch.save()
        INFO("build success")

    return len(patchs)

def do_pending_task_reset():
    # reset scan tasks with status 1 to 0
    ScanTaskQueue.objects.filter(status=1).update(status=0)
    # reset status tasks with status 1 to 0
    StatusTaskQueue.objects.filter(status=1).update(status=0)

def main(args):
    # task remain in running state when system reboot or process crash
    do_pending_task_reset()

    while True:
        count = 0
        fuzzcnt = 0

        INFO("start patch task")
        count += do_task_patch()
        INFO("end patch task")

        INFO("start status task")
        count += do_task_status()
        INFO("end status task")

        INFO("start build task")
        count += do_task_build()
        INFO("end build task")

        # sleep for next check
        if count == 0:
            fuzzcnt = fuzzcnt + 1
            if fuzzcnt > 30:
                fuzzcnt = 1
            time.sleep(60 * fuzzcnt)
        else:
            fuzzcnt = 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
