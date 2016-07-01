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
import tarfile
import django

django.setup()

from django.contrib.auth.models import User
from django.db.models import F
from dpatch.engine.models import PatchType, PatchEngine
from dpatch.core.cocciparser import CocciParser
from dpatch.core.coccikernelparser import CocciKernelParser

def INFO(msg):
    print "INFO: %s" % msg

def ERROR(msg):
    print "ERROR: %s" % msg
    
def usage(prog):
    print 'Usage: python %s username patch|report|kpatch|kreport file...' % prog

def import_cocci_patch(user, fname, lines, cocci):
    INFO('import coccinelle patch file %s' % fname)

    if PatchType.objects.filter(filename = fname, user = user).count() != 0:
        INFO('skip %s, already exists' % fname)
        return False

    name = os.path.splitext(fname)[0]
    title = cocci.get_title()
    fixed = cocci.get_fixed()
    options = cocci.get_options()
    description = cocci.get_description()
    content = cocci.get_content()
    efiles = cocci.get_efiles()

    try:
        engine = PatchEngine.objects.get(name='checkcoccinelle')
    except:
        ERROR("checkcoccinelle is not supported!!!")
        sys.exit(0)

    etype = PatchType(engine = engine, user = user, name = name,
                      filename = fname, title = title,
                      description = description, content = content,
                      options = options, fixed = fixed,
                      excludes = json.dumps(efiles))

    try:
        path = os.path.dirname(etype.fullpath())
        if not os.path.exists(path):
            os.makedirs(path)
        with open(etype.fullpath(), "w") as cocci:
            cocci.writelines(lines)
    except:
        ERROR("failed to write file %s" % etype.fullpath())
        return False

    etype.save()

    engine.total = F('total') + 1
    engine.save()

    return True

def import_cocci_report(user, fname, lines, cocci):
    INFO('import coccinelle report file %s' % fname)

    if PatchType.objects.filter(filename = fname, user = user).count() != 0:
        INFO('skip %s, already exists' % fname)
        return False

    name = os.path.splitext(fname)[0]
    title = cocci.get_title()
    fixed = cocci.get_fixed()
    options = cocci.get_options()
    description = cocci.get_description()
    content = cocci.get_content()
    efiles = cocci.get_efiles()

    try:
        engine = PatchEngine.objects.get(name='checkcoccinelle')
    except:
        ERROR("checkcoccinelle is not supported!!!")
        sys.exit(0)

    etype = PatchType(engine = engine, user = user, name = name,
                      filename = fname, title = title,
                      description = description, content = content,
                      options = options, fixed = fixed,
                      excludes = json.dumps(efiles), reportonly = True)

    try:
        path = os.path.dirname(etype.fullpath())
        if not os.path.exists(path):
            os.makedirs(path)
        with open(etype.fullpath(), "w") as cocci:
            cocci.writelines(lines)
    except:
        ERROR("failed to write file %s" % etype.fullpath())
        return False

    etype.save()

    engine.total = F('total') + 1
    engine.save()

    return True

def import_cocci_kernel_patch(user, fname, lines, kcocci):
    INFO('import coccinelle kernel patch file %s' % fname)

    if PatchType.objects.filter(filename = fname, user = user).count() != 0:
        INFO('skip %s, already exists' % fname)
        return False

    name = os.path.splitext(fname)[0]
    title = kcocci.get_title()
    options = kcocci.get_options()
    description = kcocci.get_description()
    content = "".join(lines)
    options = "-D patch %s" % options

    try:
        engine = PatchEngine.objects.get(name='checkcoccinelle')
    except:
        ERROR("checkcoccinelle is not supported!!!")
        sys.exit(0)

    etype = PatchType(engine = engine, user = user, name = name,
                      filename = fname, title = title,
                      source = PatchType.SOURCE_KERNEL,
                      description = description, content = content,
                      options = options, excludes = json.dumps([]))

    try:
        path = os.path.dirname(etype.fullpath())
        if not os.path.exists(path):
            os.makedirs(path)
        with open(etype.fullpath(), "w") as cocci:
            cocci.writelines(lines)
    except:
        ERROR("failed to write file %s" % etype.fullpath())
        return False

    etype.save()

    engine.total = F('total') + 1
    engine.save()

    return True

def import_cocci_kernel_report(user, fname, lines, kcocci):
    INFO('import coccinelle kernel report file %s' % fname)

    if PatchType.objects.filter(filename = fname, user = user).count() != 0:
        INFO('skip %s, already exists' % fname)
        return False

    name = os.path.splitext(fname)[0]
    title = kcocci.get_title()
    options = kcocci.get_options()
    description = kcocci.get_description()
    content = "".join(lines)
    options = "-D context %s" % options

    try:
        engine = PatchEngine.objects.get(name='checkcoccinelle')
    except:
        ERROR("checkcoccinelle is not supported!!!")
        sys.exit(0)

    etype = PatchType(engine = engine, user = user, name = name,
                      filename = fname, title = title,
                      source = PatchType.SOURCE_KERNEL,
                      description = description, content = content,
                      options = options, excludes = json.dumps([]),
                      reportonly = True)

    try:
        path = os.path.dirname(etype.fullpath())
        if not os.path.exists(path):
            os.makedirs(path)
        with open(etype.fullpath(), "w") as cocci:
            cocci.writelines(lines)
    except:
        ERROR("failed to write file %s" % etype.fullpath())
        return False

    etype.save()

    engine.total = F('total') + 1
    engine.save()

    return True

def import_cocci_file(user, target, fname, lines):
    if len(lines) < 5:
        return False

    if target in ['patch', 'report']:
        cocci = CocciParser(lines)
        cocci.parser()
    
        if len(cocci.get_title()) == 0 or len(cocci.get_description()) == 0:
            return False
        if len(cocci.get_content()) == 0:
            return False
    
        if target == 'patch':
            return import_cocci_patch(user, fname, lines, cocci)
        elif target == 'report':
            return import_cocci_report(user, fname, lines, cocci)
    elif target in ['kpatch', 'kreport']:
        kcocci = CocciKernelParser(lines)
        kcocci.parser()

        if target == 'kpatch':
            return import_cocci_kernel_patch(user, fname, lines, kcocci)
        elif target == 'kreport':
            return import_cocci_kernel_report(user, fname, lines, kcocci)
    else:
        return False

def main(args):
    if len(args) < 4:
        usage(args[0])
        return 0

    if not args[2] in ['patch', 'report', 'kpatch', 'kreport']:
        usage(args[0])
        return 0

    suser = User.objects.get(username = args[1])
    if suser is None:
        sys.exit(1)

    target = args[2]
    for fname in args[3:]:
        if not os.path.isfile(fname):
            INFO('file %s does not exists or is not a file' % fname)
            continue

        if tarfile.is_tarfile(fname):
            tar = tarfile.open(fname, "r:gz")
            for tarinfo in tar:
                if os.path.splitext(tarinfo.name)[1] != ".cocci":
                    INFO("import fail: file %s is not a *.cocci file" % tarinfo.name)
                    continue
                if not tarinfo.isreg():
                    continue
                print tarinfo.name
                fp = tar.extractfile(tarinfo)
                if import_cocci_file(suser, target, tarinfo.name, fp.readlines()):
                    INFO('import succeed: %s' % tarinfo.name)
                else:
                    INFO('import fail: %s is not a cocci file' % tarinfo.name)
        else:
            if os.path.splitext(fname)[1] != ".cocci":
                INFO("import fail: file %s is not a *.cocci file" % fname)
                continue
            fp = open(fname, 'r')
            if import_cocci_file(suser, target, os.path.basename(fname), fp.readlines()):
                INFO('import succeed: %s' % fname)
            else:
                INFO('import fail: %s is not a cocci file' % fname)
            fp.close()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
