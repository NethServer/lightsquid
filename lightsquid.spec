#===== Generic Info ======
%define apache_confdir %{_sysconfdir}/httpd/conf.d
%define lightsquid_confdir %{_sysconfdir}/lightsquid
%define lightsquid_reportdir %{_localstatedir}/lightsquid
%define srcname lightsquid-%{version}
%define ip2namepath %{_datadir}/%{name}/ip2name

Summary: Light, small, and fast log analyzer for squid proxy
Name: lightsquid
Version: 1.8
Release: 11%{?dist}
License: GPLv2+

Url: http://lightsquid.sourceforge.net/

Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tgz
Patch0: shebang-and-thanks.patch
Requires: perl-GDGraph3d perl-GD perl-GDGraph
BuildRequires: sed
BuildArch: noarch

%if 0%{?el5}
BuildRequires: util-linux
%else
BuildRequires: util-linux-ng
%endif


%description
%{name} is a small and fast Squid log analyzer.

%prep
%setup -q -n %{srcname}
%patch0 -p1

%{__sed} -i 's|/var/www/html/lightsquid/lang|%{_datadir}/%{name}/lang|' lightsquid.cfg
%{__sed} -i 's|/var/www/html/lightsquid/tpl|%{_datadir}/%{name}/tpl|' lightsquid.cfg
%{__sed} -i 's|/var/www/html/lightsquid/ip2name|%{_datadir}/%{name}/ip2name|' lightsquid.cfg
%{__sed} -i 's|/var/www/html/lightsquid/report|%{lightsquid_reportdir}|' lightsquid.cfg
%{__sed} -i 's|/var/www/html/lightsquid|%{lightsquid_confdir}|' lightsquid.cfg
%{__sed} -i 's|require "ip2name|require "%{ip2namepath}|' lightparser.pl
%{__sed} -i 's|lightsquid.cfg|%{lightsquid_confdir}/lightsquid.cfg|' *.cgi *.pl
%{__sed} -i 's|common.pl|%{_datadir}/%{name}/common.pl|' *.cgi *.pl
%{__sed} -i 's|/etc/squid/users.txt|/etc/lightsquid/users.txt|' ip2name/ip2name.*list*
%{__sed} -i 's|"../lightsquid.cfg"|"%{lightsquid_confdir}/lightsquid.cfg"|' tools/fixreport.pl
%{__sed} -i 's|#/bin/perl|#!/usr/bin/perl|' tools/fixreport.pl
%{__sed} -i 's|#/bin/perl|#!/usr/bin/perl|' lang/check_tpl_lng.pl
col -bx <lang/check_tpl_lng.pl> lang/check_tpl_lng.pl.tmp
%{__mv} -f lang/check_tpl_lng.pl.tmp lang/check_tpl_lng.pl
col -bx <doc/thanks.txt> doc/thanks.txt.tmp
%{__mv} -f doc/thanks.txt.tmp doc/thanks.txt
%{__sed} -i 's|../../lightsquid.cfg|%{lightsquid_confdir}/lightsquid.cfg|' tools/SiteAggregator/ReportExplorer.pl
%{__sed} -i 's|../../lightsquid.cfg|%{lightsquid_confdir}/lightsquid.cfg|' tools/SiteAggregator/SiteAgregator.pl
iconv -f WINDOWS-1251 -t UTF8 lang/ru.lng > lang/ru-utf8.lng
%{__sed} -i 's|windows-1251|utf8|' lang/ru-utf8.lng

%install
%{__rm} -rf %{buildroot}

install -m 755 -d %{buildroot}%{_sbindir}
install -m 755 -d %{buildroot}%{_sysconfdir}/cron.daily
install -m 755 -d %{buildroot}%{apache_confdir}
install -m 755 -d %{buildroot}%{lightsquid_reportdir}
install -m 755 -d %{buildroot}%{_datadir}/%{name}/{tools,lang,ip2name,tpl,cgi}
install -m 755 -d %{buildroot}%{_datadir}/%{name}/tools/SiteAggregator
install -m 755 lightparser.pl %{buildroot}%{_sbindir}/
install -pD -m 644 lightsquid.cfg %{buildroot}%{lightsquid_confdir}/lightsquid.cfg
install -pD -m 644 group.cfg.src %{buildroot}%{lightsquid_confdir}/group.cfg
install -pD -m 644 realname.cfg %{buildroot}%{lightsquid_confdir}/realname.cfg

%{__cat} << EOF > %{buildroot}%{_sysconfdir}/cron.daily/lightsquid
#!/bin/bash
%{_sbindir}/lightparser.pl yesterday
EOF
%__chmod 0755 %{buildroot}%{_sysconfdir}/cron.daily/lightsquid

%{__cat} << EOF > %{buildroot}%{apache_confdir}/lightsquid.conf
Alias /lightsquid %{_datadir}/%{name}/cgi

<Directory %{_datadir}/%{name}/cgi>
    DirectoryIndex index.cgi
    Options ExecCGI
    AddHandler cgi-script .cgi
    AllowOverride None
</Directory>
EOF
%__chmod 0644 %{buildroot}%{apache_confdir}/lightsquid.conf

# install lib
install -p -m 755 {common.pl,check-setup.pl} %{buildroot}%{_datadir}/%{name}/
install -p -m 755 {lang/check_tpl_lng.pl,lang/check_lng.pl} %{buildroot}%{_datadir}/%{name}/lang
install -p -m 644 lang/*.lng %{buildroot}%{_datadir}/%{name}/lang/
install -p -m 644 ip2name/* %{buildroot}%{_datadir}/%{name}/ip2name/
install -p -m 755 tools/*.pl %{buildroot}%{_datadir}/%{name}/tools/
install -p -m 755 tools/SiteAggregator/* %{buildroot}%{_datadir}/%{name}/tools/SiteAggregator/

%{__cp} -aRf tpl/* %{buildroot}%{_datadir}/%{name}/tpl/

install -p -m 755 [^A-Z]*.cgi %{buildroot}%{_datadir}/%{name}/cgi/

%files
%defattr(-,root,root)
%doc doc/*
%_sbindir/*
%_datadir/%name/ip2name/*
%_datadir/%name/lang/*
%_datadir/%name/tools/*
%_datadir/%name/tpl/*
%_datadir/%name/check-setup.pl
%_datadir/%name/common.pl
%dir %{lightsquid_confdir}
%dir %{lightsquid_reportdir}
%config(noreplace) %{lightsquid_confdir}/*.cfg
%{_sysconfdir}/cron.daily/lightsquid

%package apache
Summary: Web Controls for %{name}
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}
Requires: httpd
%description apache
%{name} configuration files and scripts for Apache.


%files apache
%defattr(-,root,root)
%config(noreplace) %{apache_confdir}/lightsquid.conf
%_datadir/%name/cgi/*

%clean
%{__rm} -rf %{buildroot}

%changelog
* Wed Jun 8 2011 Popkov Aleksey <aleksey@psniip.ru> 1.8-11
- Rebuild of package.

* Wed Dec 1 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-10
- Adding el5 macros for util-linux package.

* Wed Nov 18 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-9
- Some fixed littles bugs wich Ruediger Landmann <r.landmann@redhat.com>.

* Wed Nov 17 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-8
- Fixed of grammatics errors wich Ruediger Landmann <r.landmann@redhat.com>.
- Some fixed littles bugs wich Ruediger Landmann <r.landmann@redhat.com>.

* Thu Jul 22 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-7
- Moved *.cgi file back to lightsquid-apache package.

* Thu Jul 20 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-6
- Some fixed by Andrey Lavrinenko lxlight@gmail.com.

* Thu Jul 20 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-5
- Some fixed littles bugs.
- Deleted SOURCE.redhat file.
- Deleted post directive with reports files.
- Moved *.cgi file from the lightsquid-apache package.
- Some cosmetics by Andrey Lavrinenko lxlight@gmail.com.

* Thu Jul 19 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-4
- Added of Requires: httpd wich Manuel Wolfshant <wolfy@nobugconsulting.ro>.
- Returned self package of lightsquid-apache.
- Some cosmetics edition wich Peter Lemenkov <lemenkov@gmail.com>.

* Thu Jul 16 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-3
- Fixed some the littles errors with Manuel Wolfshant <wolfy@nobugconsulting.ro>.

* Thu Jul 16 2010 Popkov Aleksey <aleksey@psniip.ru> 1.8-2
- lightsquid.conf - moved from self package.
- Fixed some the littles bugs.
- Some cosmetics edition.

* Thu Jul 9 2009 Popkov Aleksey <aleksey@psniip.ru> 1.8-1
- Build version lightsquid 1.8
- Added patch for fixed some the littles bugs.

* Wed Jun 17 2009 Popkov Aleksey <aleksey@psniip.ru> 1.7.1-1
- Some removed sed's
- Added BuildRoot directive
- lightsquid.conf - moved from main package to self package.

* Tue Jun 16 2009 Popkov Aleksey <aleksey@psniip.ru> 1.7.1-1
- Adapted for Fedora Group
