%define _requires_exceptions pear(dbconfig.inc.php)\\|pear(composants.php)\\|pear(dico.php)

Name:		ocsinventory
Version:	1.02.1
Release:	%mkrel 3
Summary:	Open Computer and Software Inventory Next Generation
License:	GPL
Group:		System/Servers
URL:		http://ocsinventory.sourceforge.net/
Source0:	http://downloads.sourceforge.net/ocsinventory/OCSNG_UNIX_SERVER-%{version}.tar.gz
Source6:	README.urpmi.server
Source7:	ocsng-server-rotate
Patch1:		apache_config.patch
BuildRequires:	rpm-helper >= 0.16
BuildRequires:	rpm-mandriva-setup >= 1.23
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

%build
cd Apache
%{__perl} Makefile.PL INSTALLDIRS=vendor
%make


%install
rm -rf  %{buildroot}

install -d -m 755 %{buildroot}%{_datadir}/ocsinventory
cp -pr ocsreports %{buildroot}%{_datadir}/ocsinventory


cd Apache
%makeinstall_std

install -d -m 755 %{buildroot}%{_sysconfdir}/ocsinventory
install -d -m 755 %{buildroot}%{_sysconfdir}/ocsinventory/ocsinventory-reports
mv %{buildroot}%{_datadir}/ocsinventory/ocsreports/dbconfig.inc.php \
    %{buildroot}%{_sysconfdir}/ocsinventory/ocsinventory-reports/dbconfig.inc.php
pushd %{buildroot}%{_datadir}/ocsinventory/ocsreports
ln -s ../../../..%{_sysconfdir}/ocsinventory/ocsinventory-reports/dbconfig.inc.php .
popd

install -d %{buildroot}%{_localstatedir}/log/ocsinventory-server

install -d %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/ocsinventory-server<<EOF
/var/log/ocsinventory-server/*.log {
    missingok
}
EOF

# apache configuration
install -d -m 755 %{buildroot}%{_webappconfdir}
install -m 644 etc/ocsinventory/ocsinventory-reports.conf %{buildroot}%{_webappconfdir}
install -m 644 etc/ocsinventory/ocsinventory-server.conf %{buildroot}%{_webappconfdir}

perl -pi \
    -e 's|VERSION_MP|2|;' \
    -e 's|PATH_TO_LOG_DIRECTORY|%{_localstatedir}/log/ocsinventory-server|;' \
    %{buildroot}%{_webappconfdir}/ocsinventory-server.conf 

perl -pi \
    -e 's|OCSREPORTS_ALIAS|/ocsinventory-reports|;' \
    -e 's|PATH_TO_OCSREPORTS_DIR|%{_datadir}/ocsinventory/ocsreports|;' \
    -e 's|PACKAGES_ALIAS|/ocsinventory-download|;' \
    -e 's|PATH_TO_PACKAGES_DIR|%{_localstatedir}/lib/ocsinventory-reports/download|;' \
    %{buildroot}%{_webappconfdir}/ocsinventory-reports.conf 

install -d -m 755 %{buildroot}%{_datadir}/ocsinventory/bin
install -m 755 binutils/*.pl %{buildroot}%{_datadir}/ocsinventory/bin

install -d -m 755 %{buildroot}%{_localstatedir}/lib/ocsinventory-reports
install -d -m 755 %{buildroot}%{_localstatedir}/lib/ocsinventory-reports/download

%post server
%_post_webapp

%post reports
%_post_webapp

%postun server
%_postun_webapp

%postun reports
%_postun_webapp

%clean
rm -rf %{buildroot}

%files server
%defattr(-,root,root)
%doc README LICENSE.txt ChangeLog
%{perl_vendorlib}/Apache
%attr(-,apache,apache) %{_var}/log/ocsinventory-server
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/ocsinventory-server.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/ocsinventory-server

%files reports
%doc README LICENSE.txt ChangeLog
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/ocsinventory-reports.conf
%{_datadir}/ocsinventory
%config(noreplace) %{_sysconfdir}/ocsinventory
%attr(-,apache,apache) %{_localstatedir}/lib/ocsinventory-reports
