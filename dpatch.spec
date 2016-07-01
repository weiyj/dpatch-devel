%define debug_package %{nil}

%global  dpatch_user      dpatch
%global  dpatch_group     %{dpatch_user}
%global  dpatch_home      %{_localstatedir}/lib/dpatch
%global  dpatch_confdir   %{_sysconfdir}/dpatch
%global  dpatch_datadir   %{_datadir}/dpatch
%global  dpatch_logdir    %{_localstatedir}/log/dpatch
%global  dpatch_webroot   %{dpatch_datadir}/html

%{!?dpatch_release: %{expand: %%define dpatch_release   1}}

Summary: Automated Linux Kernel Patch Generate Engine
Name: dpatch
Version: 2.0
Release: %{dpatch_release}%{?dist}
License: GPLv2
Group: System Environment/Base
URL: https://github.com/weiyj/dpatch
Source0: https://github.com/weiyj/dpatch/archive/dpatch-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
ExcludeArch: ppc64 s390 s390x

Requires: git
Requires: Django
Requires: supervisor
Requires: python-django-rest-framework
Requires: httpd mod_wsgi
Requires: git-email

Requires: coccinelle
# we need to build sparse for fedora
#Requires: sparse
Requires: gcc gcc-plugin-devel make patch

%description
Automated Linux Kernel Patch Generate Engine

%prep
%setup -q

%build

%install
%{__install} -d %{buildroot}/%{dpatch_datadir}
%{__install} -d %{buildroot}/%{dpatch_datadir}/bin
%{__install} -d %{buildroot}/%{dpatch_datadir}/dpatch
%{__install} -D manage.py %{buildroot}/%{dpatch_datadir}
%{__install} -D bin/*.py %{buildroot}/%{dpatch_datadir}/bin/
%{__install} -D bin/*.sh %{buildroot}/%{dpatch_datadir}/bin/
%{__install} -D dpatch/*.py %{buildroot}/%{dpatch_datadir}/dpatch/
cp -rf dpatch/* %{buildroot}/%{dpatch_datadir}/dpatch/
sed -i "s%DATA_DIR = HOME_DIR%DATA_DIR = '%{dpatch_home}'%" $RPM_BUILD_ROOT/usr/share/dpatch/dpatch/settings.py

%{__install} -d %{buildroot}/%{dpatch_home}
%{__install} -d %{buildroot}/%{dpatch_home}/repo
%{__install} -d %{buildroot}/%{dpatch_home}/repo/PATCH
%{__install} -d %{buildroot}/%{dpatch_home}/repo/TEMP
%{__install} -d %{buildroot}/%{dpatch_home}/build
%{__install} -d %{buildroot}/%{dpatch_home}/pattern
%{__install} -d %{buildroot}/%{dpatch_home}/pattern/cocci
%{__install} -d %{buildroot}/%{dpatch_home}/database
%{__install} -D pattern/cocci/empty.iso %{buildroot}/%{dpatch_home}/pattern/cocci/

%{__install} -D -m 644 config/dpatch.wsgi.conf %{buildroot}/etc/httpd/conf.d/dpatch.conf
%{__install} -D config/dpatch.cron.conf %{buildroot}/etc/cron.d/dpatch
%{__install} -D -m 644 config/dpatch.supervisor.ini %{buildroot}/etc/supervisord.d/dpatch.ini
%{__install} -D -m 644 config/dpatch.firewall.xml %{buildroot}/usr/lib/firewalld/services/dpatch.xml

%{__install} -d %{buildroot}/%{dpatch_logdir}

%clean

%files
%defattr(-,dpatch,dpatch)
%attr(0644,root,root)/etc/cron.d/dpatch
%config /etc/httpd/conf.d/dpatch.conf
%config /etc/supervisord.d/dpatch.ini
%config /usr/lib/firewalld/services/dpatch.xml
%{dpatch_datadir}/
%{dpatch_home}/
%{dpatch_logdir}/

%pre
/usr/sbin/groupadd -r dpatch &>/dev/null || :
/usr/sbin/useradd -s /sbin/nologin \
        -c 'Dailypatch User' -s /bin/sh -g dpatch dpatch &>/dev/null || :
if [ -e /var/lib/dpatch/database/sqlite.db ]; then
	cp -rf /var/lib/dpatch/database/sqlite.db /var/lib/dpatch/database/sqlite.db.save
	chown dpatch:dpatch /var/lib/dpatch/database/sqlite.db.save
fi

%post

chcon -R --type=httpd_sys_rw_content_t %{dpatch_home}/repo
chcon -R --type=httpd_sys_rw_content_t %{dpatch_home}/build
chcon -R --type=httpd_sys_rw_content_t %{dpatch_home}/pattern

/bin/systemctl restart crond.service
/bin/systemctl restart supervisord.service
/bin/systemctl restart httpd.service

%preun
if [ -e /var/lib/dpatch/database/sqlite.db ]; then
	cp -rf /var/lib/dpatch/database/sqlite.db /var/lib/dpatch/database/sqlite.db.save
	chown dpatch:dpatch /var/lib/dpatch/database/sqlite.db.save
fi

%postun
/bin/systemctl restart crond.service
/bin/systemctl restart supervisord.service
/bin/systemctl restart httpd.service

%changelog
* Mon Mar 7 2016 Wei Yongjun <weiyj.lk@gmail.com>
- Initial build.
