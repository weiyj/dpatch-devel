#!/bin/sh
#
# Dailypatch - automated kernel patch create engine
# Copyright (C) 2012 - 2016 Wei Yongjun <weiyj.lk@gmail.com>
#
# This file is part of the Dailypatch package.
#
# Dailypatch is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Dailypatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dailypatch; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

version=`grep 'Version' dpatch.spec | sed -e 's/Version: //'`
if [ -e ".RELEASE" ]; then
	release=`cat .RELEASE`
else
	release=1
fi

commit=`git log -n 1 --pretty=format:%H`
ocommit=`cat .COMMIT_LATEST`
echo $commit > .COMMIT_LATEST
if [ "$commit" != "$ocommit" ]; then
	release=$((release+1))
	echo $release > .RELEASE
fi

git archive --format=tar --prefix="dpatch-${version}/" ${commit} | gzip > ~/rpmbuild/SOURCES/dpatch-${version}.tar.gz
rpmbuild -bb dpatch.spec --define="dpatch_release $release"
