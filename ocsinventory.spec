%if %{_use_internal_dependency_generator}
%define __noautoreq 'pear\\(dbconfig.inc.php\\)|pear\\(composants.php\\)|pear\\(dico.php\\)'
%else
%define _requires_exceptions pear(dbconfig.inc.php)\\|pear(composants.php)\\|pear(dico.php)
%endif

%define schema_version 2.0

Name:		ocsinventory
Version:	2.0.3
Release:	2
Summary:	Open Computer and Software Inventory Next Generation
License:	GPL
Group:		System/Servers
URL:		http://www.ocsinventory-ng.org/ 
Source0:	http://launchpad.net/ocsinventory-server/stable-1.3/server-release-1.3/+download/OCSNG_UNIX_SERVER-%{version}.tar.gz
BuildRequires: perl-devel
BuildArch:  noarch

%description
Open Computer and Software Inventory Next Generation is an application
designed to help a network or system administrator keep track of the
computers configuration and software that are installed on the network.

OCS Inventory is also able to detect all active devices on your network,
such as switch, router, network printer and unattended devices.

OCS Inventory NG includes package deployment feature on client computers

%package server
Group:      System/Servers
Summary:    Communication server
Requires:	apache-mod_perl
Requires:	perl(Apache::DBI)
Requires:   perl-DBD-mysql
Requires:   perl-Net-IP
Requires:   perl-SOAP-Lite
Obsoletes:  ocsng-linux-server

%description server
This package provides the Communication server, which will handle HTTP
communications between database server and agents.

%package reports
Group:      System/Servers
Summary:    Administration console
Requires:	apache-mod_php
Requires:	php-mysql
Requires:	php-xml
Requires:	php-zip
Obsoletes:  ocsng-linux-server

%description reports
This package provides the Administration console, which will allow 
administrators to query the database server through their favorite browser.

%prep
%setup -q -n OCSNG_UNIX_SERVER-%{version}

perl -pi -e 's/SCHEMA_VERSION/%{schema_version}/' ocsreports/index.php

%build
cd Apache
%{__perl} Makefile.PL INSTALLDIRS=vendor
%make

%install
# ocsinventory-server
pushd Apache
make pure_install PERL_INSTALL_ROOT=%{buildroot}
find %{buildroot} -type f -name .packlist -exec rm -f {} ';'
find %{buildroot} -type d -depth -exec rmdir {} 2>/dev/null ';' 

# To avoid bad dependency on perl(mod_perl)
rm -f %{buildroot}%{perl_vendorlib}/Apache/Ocsinventory/Server/Modperl1.pm 

popd

install -d -m 755 %{buildroot}%{_localstatedir}/log/ocsinventory-server

install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/ocsinventory-server<<EOF
/var/log/ocsinventory-server/*.log {
    missingok
}
EOF

install -d -m 755 %{buildroot}%{webappconfdir}
install -m 644 etc/ocsinventory/ocsinventory-server.conf \
    %{buildroot}%{webappconfdir}
perl -pi \
    -e 's|DATABASE_SERVER|localhost|;' \
    -e 's|DATABASE_PORT|3306|;' \
    -e 's|VERSION_MP|2|;' \
    -e 's|PATH_TO_LOG_DIRECTORY|%{_localstatedir}/log/ocsinventory-server|;' \
    %{buildroot}%{_webappconfdir}/ocsinventory-server.conf 

# --- ocsinventory-reports

install -d -m 755 %{buildroot}%{_datadir}/ocsinventory
cp -pr ocsreports %{buildroot}%{_datadir}/ocsinventory

install -d -m 755 %{buildroot}%{_localstatedir}/lib/ocsinventory-reports
install -d -m 755 %{buildroot}%{_localstatedir}/lib/ocsinventory-reports/download
install -d -m 755 %{buildroot}%{_localstatedir}/lib/ocsinventory-reports/ipd

install -m 755 binutils/ipdiscover-util.pl %{buildroot}%{_datadir}/ocsinventory/ocsreports/ipdiscover-util.pl 

install -d -m 755 %{buildroot}%{_sysconfdir}/ocsinventory
install -d -m 755 %{buildroot}%{_sysconfdir}/ocsinventory/ocsreports

mv %{buildroot}%{_datadir}/ocsinventory/ocsreports/dbconfig.inc.php \
    %{buildroot}%{_sysconfdir}/ocsinventory/ocsreports/dbconfig.inc.php
pushd %{buildroot}%{_datadir}/ocsinventory/ocsreports
ln -s ../../../../%{_sysconfdir}/ocsinventory/ocsreports/dbconfig.inc.php .
popd

install -m 644 etc/ocsinventory/ocsinventory-reports.conf \
    %{buildroot}%{webappconfdir}
perl -pi \
    -e 's|OCSREPORTS_ALIAS|/ocsinventory-reports|;' \
    -e 's|PATH_TO_OCSREPORTS_DIR|%{_datadir}/ocsinventory/ocsreports|;' \
    -e 's|PACKAGES_ALIAS|/ocsinventory-download|;' \
    -e 's|PATH_TO_PACKAGES_DIR|%{_localstatedir}/lib/ocsinventory-reports/download|;' \
    %{buildroot}%{_webappconfdir}/ocsinventory-reports.conf 


%files server
%defattr(-,root,root)
%doc README LICENSE.txt Apache/Changes
%{perl_vendorlib}/Apache
%attr(-,apache,apache) %{_localstatedir}/log/ocsinventory-server
%config(noreplace) %{webappconfdir}/ocsinventory-server.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/ocsinventory-server

%files reports
%doc README LICENSE.txt
%{_datadir}/ocsinventory
%config(noreplace) %{webappconfdir}/ocsinventory-reports.conf
%dir %{_sysconfdir}/ocsinventory
%dir %{_sysconfdir}/ocsinventory/ocsreports
%attr(660,root,apache) %config(noreplace) %{_sysconfdir}/ocsinventory/ocsreports/dbconfig.inc.php
%attr(-,apache,apache) %{_localstatedir}/lib/ocsinventory-reports


%changelog
* Wed Nov 30 2011 Sergey Zhemoitel <serg@mandriva.org> 2.0.3-1mdv2012.0
+ Revision: 735761
- add new release 2.0.3

* Wed Nov 16 2011 Sergey Zhemoitel <serg@mandriva.org> 2.0.2-1
+ Revision: 730815
- new release 2.0.2

* Mon Oct 17 2011 Sergey Zhemoitel <serg@mandriva.org> 2.0.1-1
+ Revision: 704957
- new version 2.0.1

* Sat Nov 27 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.3-1mdv2011.0
+ Revision: 601849
- new version

* Wed Jun 16 2010 Oden Eriksson <oeriksson@mandriva.com> 1.3.2-1mdv2010.1
+ Revision: 548135
- 1.3.2
- drop one upstream added patch

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - perms for configuration files more consistent with other packages

* Tue Mar 02 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.1-1mdv2010.1
+ Revision: 513563
- new version
- improved schema patch
- ensure configuration file is writable by apache

* Mon Feb 08 2010 Guillaume Rousse <guillomovitch@mandriva.org> 1.3-1mdv2010.1
+ Revision: 502468
- new version
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise
- drop useless sources

* Mon Feb 01 2010 Oden Eriksson <oeriksson@mandriva.com> 1.02.2-1mdv2010.1
+ Revision: 499186
- 1.02.2

* Tue Nov 24 2009 Anne Nicolas <ennael@mandriva.org> 1.02.1-3mdv2010.1
+ Revision: 469641
- Fix missing requires (#55941)

* Thu Jun 25 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.02.1-2mdv2010.0
+ Revision: 389024
- fix invalid php-db dependency

* Sun Jun 07 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.02.1-1mdv2010.0
+ Revision: 383469
- fix download alias
- add php-gd dependency
- symlink ocsreports configuration file to proper place
- package renaming
- new version
- drop client (packaged distinctly) and doc (not distributed anymore)
- sanitized package names
- drop ipdiscover binary to keep the package noarch
- spec cleanup

* Fri Dec 21 2007 Olivier Blin <blino@mandriva.org> 1.0-0.3mdv2008.1
+ Revision: 136634
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Jun 25 2007 Oden Eriksson <oeriksson@mandriva.com> 1.0-0.3mdv2008.0
+ Revision: 43837
- fix deps

