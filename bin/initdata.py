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

from django.contrib.auth.models import User
from dpatch.repository.models import Repository
from dpatch.engine.models import PatchEngine, PatchType
from django.db.models import F

def INFO(msg):
    print msg

def usage(prog):
    print 'Usage: python %s username all|engine|repository...' % prog

def do_init_repository(user):
    REPOSITORIES = [{
        'name': 'linux.git',
        'url': 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git',
        'status': True,
        'build': True,
        'type': Repository.KERNEL,
        'excludes': "[\"^Documentation/*\", \"^scripts/*\", \"^tools/\", \"^net/*\", \"^drivers/net/*\"]"
    }, {   
        'name': 'linux-next.git',
        'url': 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git',
        'status': True,
        'build': True,
        'type': Repository.KERNEL,
        'excludes': "[\"^Documentation/*\", \"^scripts/*\", \"^tools/\", \"^net/*\", \"^drivers/net/*\"]"
    }, {   
        'name': 'net.git',
        'url': 'https://git.kernel.org/pub/scm/linux/kernel/git/davem/net.git',
        'status': True,
        'build': True,
        'type': Repository.KERNEL,
        'excludes': "[\"^Documentation/*\", \"^scripts/*\", \"^tools/\"]"
    }, {   
        'name': 'net-next.git',
        'url': 'https://git.kernel.org/pub/scm/linux/kernel/git/davem/net-next.git',
        'status': True,
        'build': True,
        'type': Repository.KERNEL,
        'excludes': "[\"^Documentation/*\", \"^scripts/*\", \"^tools/\"]"
    }]

    INFO("Init default repositories...")

    for srepo in REPOSITORIES:
        if Repository.objects.filter(name = srepo["name"], user = user).count() > 0:
            INFO("repository %s exists already, skip" % srepo["name"])
            continue

        INFO("create repository %s" % srepo["name"])

        username = user.get_full_name()
        email = user.email
        if username is None or len(username) == 0:
            username = "Undefined"
        if email is None or len(email) == 0:
            email = "undefined@mail.com"

        repo = Repository(name = srepo["name"], url = srepo["url"],
                          status = srepo["status"], build = srepo["build"],
                          type = srepo["type"], excludes= srepo["excludes"],
                          username = username, email = email, user = user)
        repo.save()

def do_init_engine_type(user):
    ENGINES = [{
        'id': 1,
        'name': 'checkinclude',
        'types': [{
            'name': 'checkversion',
            'flags': 0,
            'title': 'remove unused including <linux/version.h>',
            'description': 'Remove including <linux/version.h> that don\'t need it.'
        }, {
            'name': 'checkrelease',
            'flags': 0,
            'title': 'remove unused including <generated/utsrelease.h>',
            'description': 'Remove including <generated/utsrelease.h> that don\'t need it.'
        }, {
            'name': 'checkinclude',
            'flags': 0,
            'title': 'remove duplicated include from {{file}}',
            'description': 'Remove duplicated include.'
        }]
    }, {
        'id': 2,
        'name': 'checksparse',
        'types': [{
            'name': 'checksparse',
            'flags': PatchType.TYPE_FLAG_BUILD_SPARSE | PatchType.TYPE_FLAG_DEV_ONLY,
            'title': 'fix sparse warnings',
            'description': 'Fix sparse warnings.'
        }]
    }, {
        'id': 3,
        'name': 'checkcoccinelle',
        'types': []
    }]

    INFO("Init default engine type...")
    
    for sengine in ENGINES:
        if PatchEngine.objects.filter(name=sengine["name"]).count() == 0:
            INFO("create engine type %s" % sengine["name"])
            engine = PatchEngine(id = sengine["id"], name = sengine["name"])
            engine.save()
        else:
            INFO("engine type %s exists" % sengine["name"])
            engine = PatchEngine.objects.get(name=sengine["name"])
            
        for stype in sengine["types"]:
            if PatchType.objects.filter(name = stype['name'], user = user).count() > 0:
                INFO('patch type %s exists' % stype['name'])
                continue

            INFO("create patch type %s" % stype['name'])
            ptype = PatchType(name = stype['name'], title = stype['title'],
                           description = stype['description'], flags = stype['flags'],
                           user = user, engine = engine)
            if sengine["name"] == 'checksparse':
                ptype.excludes = "[\"*.h\"]"
            else:
                ptype.excludes = "[]"
            ptype.save()

            engine.total = F('total') + 1
            engine.save()

def main(args):
    if len(args) < 3:
        usage(args[0])
        return 0

    rules = args[2:]
    for rule in rules:
        if not rule in ['all', 'engine', 'repository']:
            usage(args[0])
            return 0

    username = args[1]
    suser = User.objects.get(username = username)
    if suser is None:
        print 'user %s does not exists' % username
        sys.exit(1)

    if 'all' in rules or 'repository' in rules:
        do_init_repository(suser)

    if 'all' in rules or 'engine' in rules:
        do_init_engine_type(suser)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
