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

import re
import subprocess
import json

def is_source_file(sfile):
    if re.search(r"\.c$", sfile) != None:
        return True
    if re.search(r"\.h$", sfile) != None:
        return True
    return False

def is_c_file(filename):
    if filename.find('include/') != 0 and filename.find('tools/') != 0 and filename[-2:] == '.c':
        return True
    else:
        return False

def execute_shell(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")
    lines = lines[0:-1]

    return lines

def execute_shell_full(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE)
    shellOut = shelllog.communicate()[0]

    lines = shellOut.split("\n")

    return lines

def execute_shell_unicode(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    shellOut = shelllog.communicate()[0]
    if not isinstance(shellOut, unicode):
        shellOut = unicode(shellOut, errors='ignore')

    return shelllog.returncode, shellOut

def execute_shell_unicode_noret(args):
    if isinstance(args, basestring):
        shelllog = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    else:
        shelllog = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    shellOut = shelllog.communicate()[0]
    if not isinstance(shellOut, unicode):
        shellOut = unicode(shellOut, errors='ignore')

    return shellOut

def find_remove_lines(diff):
    if diff is None:
        return []
    is_source = False
    lines = []
    for line in diff.split("\n"):
        if is_source is False:
            if re.search('@@[^@]*@@', line):
                is_source = True
            continue
        if line.find('-') == 0 and re.search('\w+', line):
            lines.append(line[1:])
    return lines

def commit_url(url, commit):
    _weburl = url
    if url.find('gitorious.org') != -1:
        _weburl = re.sub(".git$", '', url)
        _weburl = "%s/commit/%s" % (_weburl, commit)
        _weburl = re.sub("git://", "https://", _weburl)
    else:
        _weburl = "%s/commit/?id=%s" % (url, commit)
        _weburl = re.sub("git://git.kernel.org/pub/scm/", "http://git.kernel.org/?p=", _weburl)
    return _weburl

def is_white_black_list(wblist, sfile):
    if len(wblist) == 0:
        return False

    try:
        alist = json.loads(wblist)
        if sfile in alist:
            return True
        for p in alist:
            if re.match(p, sfile) or sfile == p:
                return True
    except:
        return False

    return False
