# TODO:
# - use shared libs instead of static

Summary:	Oops! is an HTTP-1.1/FTP proxy server
Summary(pl):	Oops! jest serwerem proxy HTTP-1.1/FTP
Name:		oops
Version:	1.5.22
Release:	0.5
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://zipper.paco.net/~igor/oops/%{name}-%{version}.tar.gz
Source1:	%{name}.logrotate
Source2:	%{name}.sysconfig
Source3:	%{name}.init
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-config.patch
Patch2:		%{name}-parser_fix.patch
URL:		http://zipper.paco.net/~igor/oops.eng/
BuildRequires:	autoconf
BuildRequires:	db3-devel
BuildRequires:	pam-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Oops! is a proxy server; the main aims of its development being stable
operation, service speed, main protocols support, modularity, ease at
use. What is one more server for when there is already Squid? I
personally was not satisfied with Squid on some points, that is was
why I wished to get rid of it. And that was done. Basic differences
from Squid:
- Each request is served by a separate thread, which allows to use all
  available processors on multiprocessor machine.
- Cashed documents are stored in one or several big files. This makes
  it possible to remove from the operational system a load on operation
  with directories and to speed up access to the documents, and to use
  raw-devices as a storage of cashed objects either.
- The program modular structure provides extension of its function
  without any change of the source code.
- The special attention was paid to the point of providing a stable,
  continuous, unbreakable work, easy and simple configuration
  /reconfiguration. Thus, for example, the reconfiguration on the fly
  doesn't result in a breakaway of already established connections.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
autoconf
autoheader
%configure \
	--enable-oops-user=daemon \
	--libdir=/usr/lib/oops \
	--sysconfdir=%{_sysconfdir}/oops

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d,logrotate.d},/var/{log/oops,spool/oops}}
install -d $RPM_BUILD_ROOT%{_mandir}/man8

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1}	$RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/oops
install %{SOURCE2}	$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/oops
install %{SOURCE3}	$RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/oops
install doc/*.8		$RPM_BUILD_ROOT%{_mandir}/man8/

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add oops
if [ -f /var/lock/subsys/oops ]; then
	/etc/rc.d/init.d/oops restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/oops start\" to start Oops!."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/oops ]; then
		/etc/rc.d/init.d/oops stop 1>&2
	fi
	/sbin/chkconfig --del oops
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog FAQ INSTALL README SERVICES TODO doc/*.html contrib/*
%dir %{_sysconfdir}
%attr(644,daemon,daemon) %config(noreplace) %{_sysconfdir}/oops/*
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/oops
%attr(755,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/oops
%attr(755,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/oops
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/oops/*
%dir %attr(755,root,root)	%{_libdir}/oops/
%dir %attr(755,daemon,daemon)	/var/log/oops
%dir %attr(755,daemon,daemon)	/var/spool/oops
%{_mandir}/man8/*