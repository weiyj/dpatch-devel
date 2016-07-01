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
import subprocess

class CocciKernelParser(object):
    def __init__(self, lines):
        self._lines = lines
        self._title = ''
        self._options = ''
        self._description = ''
        self._comment = ''
        self._content = ''

    def parser(self):
        description = []
        _desc = []
        comment = []
        content = []
        is_content = False
        for i in range(len(self._lines)):
            line = self._lines[i]
            if is_content is True:
                content.append(line)
                continue

            if line.find('/// TITLE: ') == 0:
                self._title = line.replace('/// TITLE: ', '').strip()
            elif line.find('/// DESC: ') == 0:
                _desc.append(line.replace('/// DESC:', '').strip())
            elif line.find('/// ') == 0:
                content.append(line)
                descline = line.replace('///', '').strip()
                if i ==0 and len(descline) == 0:
                    continue
                description.append(descline)
                continue
            elif line.find('// ') == 0:
                content.append(line)
                if line.find("// Options:") == 0:
                    self._options = line.replace('// Options:', '').strip()
            elif line.find('//# ') == 0:
                content.append(line)
                comment.append(line.replace('//# ', '').strip())
            elif line.find('//') == 0:
                content.append(line)
                continue
            else:
                is_content = True
                content.append(line)

        if len(description) and len(description[-1]) == 0:
            description = description[:-1]

        if len(self._title) == 0:
            if len(description) == 1:
                self._title = description[0]
            else:
                self._title = "FIXME: fix coccinelle warning"

        if len(_desc) == 0:
            self._description = '\n'.join(description)
        else:
            self._description = '\n'.join(_desc)
        self._content = '\n'.join(content)
        self._comment = '\n'.join(comment)

    def get_title(self):
        return self._title

    def get_options(self):
        return self._options

    def get_description(self):
        return self._description

    def get_content(self):
        return self._content

    def get_comment(self):
        return self._comment

if __name__ == '__main__':
    findlog = subprocess.Popen("find %s -type f -name *.cocci" % (sys.argv[1]),
                                  shell=True, stdout=subprocess.PIPE)
    findOut = findlog.communicate()[0]

    files = findOut.split("\n")
    files = files[0:-1]

    for sfile in files:
        with open(sfile, "r") as fp:
            cocci = CocciKernelParser(fp.readlines())
            cocci.parser()
            print "=== parse file %s ===" % sfile
            print "TITLE: %s" % cocci.get_title()
            print "DESC: %s" % cocci.get_description()
            print "OPTIONS: %s" % cocci.get_options()
            print "COMMENT: %s" % cocci.get_comment()

