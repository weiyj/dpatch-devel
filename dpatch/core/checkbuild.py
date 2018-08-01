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
import subprocess

from patchengine import PatchEngine

class CheckBuildEngine(PatchEngine):
    def __init__(self, repo, build = None, logger = None):
        PatchEngine.__init__(self, repo, build, logger)
        self._nochk_dirs = ["arch", "Documentation", "include", "tools", "usr", "samples", "scripts"]
        self._diff = []
        self._includes = []
        self._recheck = False
        self._error = False

    def _execute_shell(self, args):
        if isinstance(args, basestring):
            shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            shelllog = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        shellOut = shelllog.communicate()[0]

        if shelllog.returncode != 0 and len(shellOut) > 0:
            self.warning(shellOut)

        lines = shellOut.split("\n")
        lines = lines[0:-1]

        return lines

    def name(self):
        return 'check build'

    def has_error(self):
        if self._error is True:
            return True

        for line in self._diff:
            if re.search('\s+Error\s+\d', line):
                return True
        return False

    def _get_patch_title(self):
        _cnt = {'total': 0, 'unused': 0}
        title = 'remove set but not used variable'
        _dubious_type = []
        for line in self._diff:
            if self._is_unused_but_set_variable(line): 
                _cnt['unused'] += 1
                _cnt['total'] += 1

        if _cnt['total'] > 1:
            title += 's'

        #if self._recheck is True:
        #    title = 'cHECK-' + title

        return title

    def _nowrap_description(self, line):
        return False

    def _get_patch_description(self):
        _desc = 'Fixes gcc \'-Wunused-but-set-variable\' warning:\n'
        _skip = False
        _prev = False
        idx = 0
        for line in self._diff:
            idx = idx + 1
            if not isinstance(line, unicode):
                nline = unicode(line, errors='ignore')
            else:
                nline = line

            if nline.startswith(self._fname):
                if self._is_unused_but_set_variable(nline):
                    _skip = False
                    _prev = True
                else:
                    _skip = True
            elif not nline.startswith(' '):
                _skip = True

            if _skip is True:
                continue

            if _prev is True:
                _desc += '\n' + self._diff[idx - 2]
                _prev = False

            if len(line) > 80:
                a = line.split(':')
                if len(a) > 4 and not self._nowrap_description(line):
                    _desc += '\n' + ':'.join(a[:4])
                    _desc += ':\n' + ':'.join(a[4:])
                else:
                    _desc += '\n' + line
            else:
                _desc += '\n' + line

        return _desc

    def _is_skip_type_list(self, line):
        _objname = re.sub("\.c$", ".o", self._fname)
        if re.search('make: \*\*\* \[%s\] Error' % _objname, line):
            return True
        return False

    def _is_fake_warning(self, line):
        try:
            __sfname = os.path.basename(self._fname)
            if __sfname != os.path.basename(line.split(':')[0]):
                return True
        except:
            return True
        return False

    def _is_unused_but_set_variable(self, line):
        if re.search("set but not used", line):
            return True
        return False

    def _get_variable_symbol(self, line):
        a = line.split(':')
        if len(a) < 5:
            return ""
        _nr = int(a[1])
        _sym = a[-1].strip().split(' ')[1]
        if _sym.find('\'') != -1:
            return re.sub("'", "", _sym)
        elif _sym.isalpha():
            return _sym
        else:
            return _sym[3:-3]

    def _fix_unused_but_set_variable(self, line):
        a = line.split(':')
        if len(a) < 5:
            return False
        _nr = int(a[1])
        _sym = a[-1].strip().split(' ')[1]
        if _sym.find('\'') != -1:
            _sym = re.sub("'", "", _sym)
        elif not _sym[0].isalpha():
            _sym = _sym[3:-3]
        #_sym = _sym[2:len(_sym)-2]
        try:
            lines = self._execute_shell("sed -n '%d,%dp' %s" % (_nr, _nr + 100, self._get_build_path()))
        except:
            return []

        if lines[0].find(',') != -1:
            self._execute_shell("sed -i '%ds/ %s, / /' %s" % (_nr, _sym, self._get_build_path()))
            self._execute_shell("sed -i '%ds/, %s / /' %s" % (_nr, _sym, self._get_build_path()))
            self._execute_shell("sed -i '%ds/, %s;/;/' %s" % (_nr, _sym, self._get_build_path()))

        _nrs = []
        for oline in lines[1:]:
            _nr = _nr + 1
            if re.match('\s+%s\s*=' % _sym, oline):
                _nrs.append(_nr)

        return _nrs

    def _modify_source_file(self):
        _rmlines = []
        try:
            for line in self._diff:
                if self._is_fake_warning(line):
                    continue
                if self._is_unused_but_set_variable(line): 
                    _rmlines.extend(self._fix_unused_but_set_variable(line))
            for _nr in sorted(_rmlines, reverse = True):
                self._execute_shell("sed -i '%dd' %s" % (_nr, self._get_build_path()))
        except:
            return False

    def _is_buildable(self):
        #_objname = re.sub("\.c$", ".o", self._fname)
        if not os.path.exists(self._build):
            self._error = True
            return False
        if not os.path.exists(os.path.join(self._build, 'vmlinux')):
            self._error = True
            return False
        #if not os.path.exists(os.path.join(self._build, _objname)):
        #    return False
        return True

    def _should_patch(self):
        if re.search(r"\.c$", self._fname) == None:
            return False
        if self._build is None:
            return False
        if not self._is_buildable():
            return False
        for _skip in self._nochk_dirs:
            if self._fname.find(_skip) == 0:
                return False

        if os.path.exists(os.path.join(self._build, self._fname)):
            self._execute_shell("cd %s; touch %s" % (self._build, self._fname))

        _objname = re.sub("\.c$", ".o", self._fname)
        args = "cd %s; make W=1 %s | grep '^%s'" % (self._build, _objname, self._fname)
        self._diff = self._execute_shell(args)
        self._recheck = False
        logresult = '\n'.join(self._diff)
        # make may error and need make allmodconfig
        if logresult.find('include/config/auto.conf') != -1:
            self._execute_shell("cd %s; make allmodconfig" % self._build)
            args = "cd %s; make W=1 %s | grep '^%s'" % (self._build, _objname, self._fname)
            self._diff = self._execute_shell(args)
        if len(os.path.dirname(self._fname).split(os.sep)) > 2:
            args = "cd %s; make W=1 M=%s" % (self._build, os.path.dirname(self._fname))
            _modresult = self._execute_shell(args)
        else:
            _modresult = None
        if self._is_skip_type_list('\n'.join(self._diff)):
            return
        for line in self._diff:
            # module build does not exists for this one?
            if not isinstance(line, unicode):
                line = unicode(line, errors='ignore')

            if not _modresult is None and not line in _modresult:
                self._recheck = True
            if self._is_fake_warning(line):
                continue
            if self._is_unused_but_set_variable(line):
                return True
            elif self._is_skip_type_list(line):
                return False
        return False

    def _revert_soure_file(self):
        os.system("cd %s ; git diff %s | patch -p1 -R > /dev/null" % (self._build, self._fname))

    def _get_diff(self):
        diff = subprocess.Popen("cd %s ; LC_ALL=en_US git diff --patch-with-stat %s" % (self._build, self._fname),
                                shell=True, stdout=subprocess.PIPE)
        diffOut = diff.communicate()[0]
        return diffOut

if __name__ == "__main__":
    repo = "/var/lib/dpatch/build/1/linux-next"
    files = ['net/ipv4/tcp_output.c']

    count = 0
    for sfile in files:
        detector = CheckBuildEngine("/var/lib/dpatch/build/1/linux-next", repo, None)
        detector.set_filename(sfile)
        #print detector._guess_mail_list()
        if detector.should_patch():
            count += 1
            print detector.get_patch_title()
            print detector.get_patch_description()
            print detector.get_patch()

    print "patch files: %d" % count
