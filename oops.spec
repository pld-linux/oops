# TODO:
# - use shared libs instead of static

Summary:	Oops! is an HTTP-1.1/FTP proxy server
Summary(pl):	Oops! jest serwerem proxy HTTP-1.1/FTP
Name:		oops
Version:	1.5.22
Release:	0.9
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://zipper.paco.net/~igor/oops/%{name}-%{version}.tar.gz
# Source0-md5:	bd6f743fb4abc6cf08ae310b1927b211
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
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
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

%description -l pl
Oops! jest serwerem proxy; g³ówne cele przy¶wiecaj±ce jego tworzeniu
to stabilna praca, szybko¶æ, obs³uga podstawowych protoko³ów,
modularno¶æ, ³atwo¶æ u¿ycia. Po co jeszcze jeden serwer, skoro ju¿
jest Squid? Autor Oopsa nie by³ usatysfakcjonowany Squidem w
niektórych punktach, dlatego napisa³ w³asny program. Podstawowe
ró¿nice w stosunku do Squida:
- Ka¿de ¿±danie jest obs³ugiwane przez oddzielny w±tek, co pozwala na
  wykorzystanie wszystkich dostêpnych procesorów w maszynach
  wieloprocesorowych.
- Buforowane dokumenty s± przechowywane w jednym lub kilku du¿ych
  plikach; umo¿liwia to unikniêcie obci±¿enia systemu przy operacjach
  na katalogach i przyspieszenie dostêpu do dokumentów, oraz na
  u¿ywanie surowych urz±dzeñ do przechowywania buforowanych obiektów.
- Modularna struktura programu udostêpnia rozszerzanie funkcjonalno¶ci
  bez potrzeby zmian w kodzie ¼ród³owym.
- Szczególn± uwagê zwrócono na zapewnienie stabilnej, ci±g³ej, nie
  przerwanej pracy oraz ³atw± i prost± konfiguracjê/rekonfiguracjê.
  Na przyk³ad rekonfiguracja w locie nie powoduje zerwania ju¿
  ustanowionych po³±czeñ.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__autoconf}
%{__autoheader}
%configure \
	--enable-oops-user=daemon \
	--libdir=/usr/lib/oops \
	--sysconfdir=%{_sysconfdir}/oops

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d,logrotate.d},/var/{log/{archiv/oops,oops},spool/oops}} \
	$RPM_BUILD_ROOT%{_mandir}/man8

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1}	$RPM_BUILD_ROOT/etc/logrotate.d/oops
install %{SOURCE2}	$RPM_BUILD_ROOT/etc/sysconfig/oops
install %{SOURCE3}	$RPM_BUILD_ROOT/etc/rc.d/init.d/oops
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
%dir %{_sysconfdir}/oops
%attr(644,root,daemon) %config(noreplace) %{_sysconfdir}/oops/*
%attr(754,root,root) /etc/rc.d/init.d/oops
%attr(640,root,root) %config(noreplace) /etc/sysconfig/oops
%attr(640,root,root) %config(noreplace) /etc/logrotate.d/oops
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/oops/*
%dir %{_libdir}/oops
%dir %attr(755,daemon,daemon) /var/log/oops
%dir /var/log/archiv/oops
%dir %attr(755,daemon,daemon) /var/spool/oops
%{_mandir}/man8/*
