%define _requires_exceptions pear(dbconfig.inc.php)\\|pear(composants.php)\\|pear(dico.php)
%define schema_version 2.0

Name:		ocsinventory
Version:	2.0.4
Release:	%mkrel 1
Summary:	Open Computer and Software Inventory Next Generation
License:	GPL
Group:		System/Servers
URL:		http://www.ocsinventory-ng.org/ 
Source0:	http://launchpad.net/ocsinventory-server/stable-1.3/server-release-1.3/+download/OCSNG_UNIX_SERVER-%{version}.tar.gz
%if %mdkversion < 201010
Requires(post):   rpm-helper
Requires(postun):   rpm-helper
%endif
BuildArch:  noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}

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
rm -rf  %{buildroot}


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

%post server
%if %mdkversion < 201010
%_post_webapp
%endif

%post reports
%if %mdkversion < 201010
%_post_webapp
%endif

%postun server
%if %mdkversion < 201010
%_postun_webapp
%endif

%postun reports
%if %mdkversion < 201010
%_postun_webapp
%endif

%clean
rm -rf %{buildroot}

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
