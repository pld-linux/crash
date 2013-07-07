# TODO:
# - memory_driver kernel module
# - eppic extension (wants to git pull from code.google.com)
#
Summary:	Core Analysis Suite
Summary(pl.UTF-8):	Zestaw narzędzi do analizy zrzutów pamięci
Name:		crash
Version:	7.0.1
Release:	1
License:	GPL v2+
Group:		Libraries
Source0:	http://people.redhat.com/anderson/%{name}-%{version}.tar.gz
# Source0-md5:	b59076aebaced87e9073328cb0a4f50a
URL:		http://people.redhat.com/anderson/
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
BuildRequires:	xz-devel
BuildRequires:	zlib-devel
ExclusiveArch:	%{ix86} %{x8664} alpha arm ia64 ppc64 s390 s390x
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The core analysis suite is a self-contained tool that can be used to
investigate either live systems, kernel core dumps created from the
netdump and diskdump packages offered by Red Hat, the LKCD kernel
patch or the mcore kernel patch available from Mission Critical Linux.

%description -l pl.UTF-8
Narzędzie do analizy zrzutów pamięci to samodzielny program służący do
badania systemów działających, zrzutów pamięci jądra utworzonych przez
pakiety Red Hata netdump lub diskdump, łatę jądra LKCD lub łatę jądra
mcore dostępną w Mission Critical Linuksie.

%package devel
Summary:	Header files for core analysis suite
Summary(pl.UTF-8):	Plik nagłówkowy narzędzia do analizy zrzutów pamięci
Group:		Development/Libraries
# doesn't require base

%description devel
Header files for core analysis suite.

%description devel -l pl.UTF-8
Plik nagłówkowy narzędzia do analizy zrzutów pamięci.

%prep
%setup -q

# TODO: download sources, disable git pull in eppic.mk
%{__mv} extensions/eppic.c{,.skip}

%build
export CPPFLAGS="%{rpmcppflags} -I/usr/include/ncurses"
%{__make} -j1 all extensions \
	ARCH="%{_target_cpu}" \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -I/usr/include/ncurses"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man8,%{_libdir}/crash/extensions,%{_includedir}/crash}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# omitted by make install
install extensions/*.so $RPM_BUILD_ROOT%{_libdir}/crash/extensions
cp -p crash.8 $RPM_BUILD_ROOT%{_mandir}/man8
cp -p defs.h $RPM_BUILD_ROOT%{_includedir}/crash

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/crash
%dir %{_libdir}/crash
%dir %{_libdir}/crash/extensions
%attr(755,root,root) %{_libdir}/crash/extensions/dminfo.so
%attr(755,root,root) %{_libdir}/crash/extensions/echo.so
#%attr(755,root,root) %{_libdir}/crash/extensions/eppic.so
%attr(755,root,root) %{_libdir}/crash/extensions/snap.so
%attr(755,root,root) %{_libdir}/crash/extensions/trace.so
%{_mandir}/man8/crash.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/crash
