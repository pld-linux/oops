# TODO
# - create separate user for this daemon?
Summary:	Oops! is an HTTP-1.1/FTP proxy server
Summary(pl.UTF-8):	Oops! jest serwerem proxy HTTP-1.1/FTP
Name:		oops
Version:	1.5.23
Release:	0.13
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://zipper.paco.net/~igor/oops/%{name}-%{version}.tar.gz
# Source0-md5:	bfa19752af517bb5a6cd746acf61064c
Source1:	%{name}.logrotate
Source2:	%{name}.sysconfig
Source3:	%{name}.init
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-config.patch
Patch2:		%{name}-ac.patch
Patch3:		%{name}-build.patch
Patch4:		%{name}-socket.patch
Patch5:		%{name}-CVE-2005-1121.patch
URL:		http://zipper.paco.net/~igor/oops.eng/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	db-devel
BuildRequires:	flex
BuildRequires:	mysql-devel
BuildRequires:	pam-devel
BuildRequires:	pcre-devel
BuildRequires:	postgresql-devel
BuildRequires:	rpmbuild(macros) >= 1.177
BuildRequires:	sed >= 4.0
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
Conflicts:	logrotate < 3.7-4
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

%description -l pl.UTF-8
Oops! jest serwerem proxy; główne cele przyświecające jego tworzeniu
to stabilna praca, szybkość, obsługa podstawowych protokołów,
modularność, łatwość użycia. Po co jeszcze jeden serwer, skoro już
jest Squid? Autor Oopsa nie był usatysfakcjonowany Squidem w
niektórych punktach, dlatego napisał własny program. Podstawowe
różnice w stosunku do Squida:
- Każde żądanie jest obsługiwane przez oddzielny wątek, co pozwala na
  wykorzystanie wszystkich dostępnych procesorów w maszynach
  wieloprocesorowych.
- Buforowane dokumenty są przechowywane w jednym lub kilku dużych
  plikach; umożliwia to uniknięcie obciążenia systemu przy operacjach na
  katalogach i przyspieszenie dostępu do dokumentów, oraz na używanie
  surowych urządzeń do przechowywania buforowanych obiektów.
- Modularna struktura programu udostępnia rozszerzanie funkcjonalności
  bez potrzeby zmian w kodzie źródłowym.
- Szczególną uwagę zwrócono na zapewnienie stabilnej, ciągłej, nie
  przerwanej pracy oraz łatwą i prostą konfigurację/rekonfigurację. Na
  przykład rekonfiguracja w locie nie powoduje zerwania już
  ustanowionych połączeń.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
cp -f /usr/share/automake/config.sub .
%{__autoconf}
%{__autoheader}
CFLAGS="-D_XOPEN_SOURCE=600 -D_GNU_SOURCE=1"
%configure \
	--enable-large-files \
	--enable-oops-user=daemon \
	--with-regexp=pcre \
	--with-zlib="-lz" \
	--with-MYSQL=%{_prefix} \
	--with-PGSQL=%{_prefix} \
	--libdir=%{_libdir}/oops \
	--sysconfdir=%{_sysconfdir}/oops

:> src/rwlock.c

%{__make} -j1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d,logrotate.d},/var/{run/oops,log/{archive/oops,oops},spool/oops}} \
	$RPM_BUILD_ROOT%{_mandir}/man8

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1}	$RPM_BUILD_ROOT/etc/logrotate.d/oops
install %{SOURCE2}	$RPM_BUILD_ROOT/etc/sysconfig/oops
install %{SOURCE3}	$RPM_BUILD_ROOT/etc/rc.d/init.d/oops
install doc/*.8		$RPM_BUILD_ROOT%{_mandir}/man8

# SECURITY: disable the password(s) there
sed -i -e 's,:,:!,;s,^,#,' $RPM_BUILD_ROOT%{_sysconfdir}/oops/passwd

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add oops
if [ -f /var/lock/subsys/oops ]; then
	/etc/rc.d/init.d/oops restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/oops start\" to start Oops!."
fi

if [ "$1" = "1" ]; then
%banner %{name} -e <<EOF
Don't forget to initialize oops storages, by running:

/etc/rc.d/init.d/oops init

EOF
#' vim stupidity.
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
%doc ChangeLog FAQ INSTALL README SERVICES TODO doc/*.html contrib
%dir %{_sysconfdir}/oops
%attr(644,root,daemon) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/oops/[!p]*
%attr(640,root,daemon) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/oops/passwd
%attr(754,root,root) /etc/rc.d/init.d/oops
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/oops
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/oops
%attr(755,root,root) %{_sbindir}/*
%dir %{_libdir}/oops
%attr(755,root,root) %{_libdir}/oops/*
%dir %attr(770,root,daemon) /var/run/oops
%dir %attr(755,daemon,daemon) /var/log/oops
%dir /var/log/archive/oops
%dir %attr(755,daemon,daemon) /var/spool/oops
%{_mandir}/man8/*
