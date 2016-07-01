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
import tempfile
import subprocess

from .patchengine import PatchEngine
from .reportengine import ReportEngine

class CheckCocciPatchEngine(PatchEngine):
    def __init__(self, repo, ptype, build = None, logger = None):
        PatchEngine.__init__(self, repo, build, logger)
        self._diff = []
        self._cocci = ptype

    def name(self):
        return 'checkcoccinelle'

    def _execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if shelllog.returncode != 0:
            self.warning("cocci engine fail at %s" % (self._fname))
            self.warning(shellOut)

        lines = shellOut.split("\n")

        return lines

    def get_type(self):
        return self._cocci.id

    def _engine_fixed(self):
        cocci = self._cocci
        if cocci.fixed is None or len(cocci.fixed) == 0:
            return self._diff

        fixed = cocci.fixed.split('...')
        regexpr = fixed[0].strip()
        target = fixed[1].strip()
        cpl = re.compile(regexpr)
        diff = []
        for line in self._diff:
            line = cpl.sub(target, line)
            diff.append(line)
        return diff

    def has_error(self):
        for line in self._diff:
            if line.find('Fatal error: exception Common.Timeout') != -1:
                return True
        return False

    def _modify_source_file(self):
        # sometimes the engine give as a diff that does not pass
        # the checkpatch, we need fix it first.
        diff = self._engine_fixed()

        temp = tempfile.mktemp()
        cfg = open(temp, "w")
        cfg.write('\n'.join(diff))
        cfg.close()

        self._execute_shell('patch %s < %s' %(self._get_file_path(), temp))
        os.remove(temp)

    def _should_patch(self):
        cocci = self._cocci
        spfile = cocci.fullpath()
        if not os.path.exists(spfile):
            self.warning('sp_file %s does not exists' % spfile)
            return False

        timeout = 60
        args = '/usr/bin/spatch %s -I %s -timeout %d -very_quiet -sp_file %s %s' % (cocci.options,
                        os.path.join(self._repo, 'include'), timeout,
                        spfile, self._get_file_path())
        self._diff = self._execute_shell(args)
        if len(self._diff) > 1:
            if self._diff[0].find('diff ') == 0 or self._diff[0].find('--- ') == 0:
                return True
            else:
                self.warning('spatch output for %s' % self._fname)
                self.warning('\n'.join(self._diff))

        return False

class CheckCocciReportEngine(ReportEngine):
    def __init__(self, repo, ptype, build = None, logger = None):
        ReportEngine.__init__(self, repo, build, logger)
        self._cocci = ptype
        self._diff = []

    def name(self):
        return 'checkcoccinelle'

    def get_type(self):
        return self._cocci.id

    def has_error(self):
        for line in self._diff:
            if line.find('Fatal error: exception Common.Timeout') != -1:
                return True
        return False

    def _execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if shelllog.returncode != 0:
            self.warning("cocci engine fail at %s" % (self._fname))
            self.warning(shellOut)

        lines = shellOut.split("\n")

        return lines

    def _should_report(self):
        cocci = self._cocci
        spfile = cocci.fullpath()
        if not os.path.exists(spfile):
            self.warning('sp_file %s does not exists' % spfile)
            return False

        timeout = 60
        args = '/usr/bin/spatch %s -I %s -timeout %d -very_quiet -sp_file %s %s' % (cocci.options,
                        os.path.join(self._repo, 'include'), timeout,
                        spfile, self._get_file_path())
        self._diff = self._execute_shell(args)
        if len(self._diff) > 1:
            if self._diff[0].find('diff ') == 0 or self._diff[0].find('--- ') == 0:
                return True
            else:
                self.warning('spatch output for %s' % self._fname)
                self.warning('\n'.join(self._diff))

        return False

    def get_report(self):
        return self._diff
