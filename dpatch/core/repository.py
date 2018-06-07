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
import datetime

from .utils import execute_shell, find_remove_lines

class GitRepository(object):
    def __init__(self, name, path, url, commit, stable):
        self._name = name
        self._url = url
        self._path = path
        self._commit = commit
        self._stable = stable
        self._nstable = None

    def is_linux_next(self):
        if self._name == 'linux-next.git':
            return True
        else:
            return False

    def _get_remote_master(self):
        commits = execute_shell("git ls-remote -h %s master | awk '{print $1;}'" % self._url)
        if len(commits) == 0:
            return None
        return commits[0]

    def get_remote_stable(self):
        commits = execute_shell("git ls-remote -h %s stable | awk '{print $1;}'" % self._url)
        if len(commits) == 0:
            return None
        return commits[0]

    def get_stable(self):
        if not self._nstable is None:
            return self._nstable

        nstable = self.get_remote_stable()
        if nstable is None:
            # can not get remove stable, guess it
            cmd = "git log --author='Linus Torvalds' --pretty='format:%H %s' -n 50"
            for line in execute_shell("cd %s ; %s" % (self._path, cmd)):
                _commit = line.split(' ')
                if len(_commit) < 2:
                    continue
                if _commit[1] == 'Merge' or _commit[1] == 'Linux':
                    self._nstable = _commit[0]
        else:
            self._nstable = nstable

        # fake a stable to make build happy
        with open(os.path.join(self._path, '.git/refs/remotes/origin/stable'), "w") as fp:
            fp.write(self._nstable)

        return self._nstable

    def get_commit(self):
        commits = execute_shell('cd %s; git log -n 1 --pretty=format:%%H%%n' % self._path)
        return commits[-1]

    def get_tag(self):
        if not os.path.exists(self._path):
            return None
        tags = execute_shell('cd %s; git tag' % self._path)

        stag = tags[-1]
        if re.search(r'-rc\d+$', stag) != None:
            tag = re.sub('-rc\d+$', '', stag)
            if tags.count(tag) > 0:
                stag = tag

        for ltag in tags[::-1]:
            if re.search(r'v\d.\d\d+', ltag) != None:
                lversions = re.sub('-rc\d+$', '', ltag).split('.')
                sversions = re.sub('-rc\d+$', '', stag).split('.')
                if lversions[0] != sversions[0] or int(sversions[-1]) > int(lversions[-1]):
                    return stag
                else:
                    tag = re.sub('-rc\d+$', '', ltag)
                    if tags.count(tag) > 0:
                        ltag = tag
                    return ltag

        return stag

    def clone(self):
        rpath = os.path.dirname(self._path)
        if not os.path.exists(rpath):
            os.mkdir(rpath)
        execute_shell('cd %s; git clone %s' % (rpath, self._url))

    def reset(self, commit):
        execute_shell('cd %s; git reset --hard %s' % (self._path, commit))

    def pull(self):
        if self.is_linux_next():
            rmaster = self._get_remote_master()
            if rmaster is None or rmaster == self._commit:
                return False
            if self._stable is None or len(self._stable) == 0:
                self._stable = self.get_stable()
            self.reset(self._stable)
        execute_shell('cd %s; git pull' % self._path)
        execute_shell('cd %s; make allmodconfig' % self._path)

    def diff(self, scommit, ecommit):
        return execute_shell('cd %s; git diff --name-only %s...%s' % (self._path, scommit, ecommit))

    def check_update(self):
        if not os.path.exists(self._path):
            self.clone()
        else:
            self.pull()
        commit = self.get_commit()
        if commit == self._commit or commit == self._stable:
            return False
        else:
            return True

    def changelist(self, scommit, ecommit):
        if scommit == ecommit and len(scommit) != 0:
            return []
        if self.is_linux_next():
            scommit = self.get_stable()
            return self.diff(scommit, ecommit)
        else:
            if len(scommit) == 0 or scommit is None:
                scommit = '1da177e4c3f41524e886b7f1b8a0c1fc7321cac2'
            return self.diff(scommit, ecommit)

    def is_change_obsoleted(self, fname, diff, days = 180):
        dates = []
        try:
            for line in find_remove_lines(diff):
                dates = execute_shell("cd %s; git log -n 1 -S '%s' --pretty=format:%%ci%%n %s" % (self._path, line, fname))
                if len(dates) == 0:
                    continue
                dt = datetime.datetime.strptime(' '.join(dates[0].split(' ')[:-1]), "%Y-%m-%d %H:%M:%S")
                delta = datetime.datetime.now() - dt
                if delta.days < days:
                    return False
            return True
        except:
            return True
