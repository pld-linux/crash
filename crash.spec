# TODO:
# - libeppic if anything else (but crash extension) wants to use it
#
# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose kernel module build (V=1)

# The goal here is to have main, userspace, package built once with
# simple release number, and only rebuild kernel packages with kernel
# version as part of release number, without the need to bump release
# with every kernel change.
%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel		1
%define		pname		crash
Summary:	Core Analysis Suite
Summary(pl.UTF-8):	Zestaw narzędzi do analizy zrzutów pamięci
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	7.2.3
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	GPL v2+
Group:		Libraries
Source0:	http://people.redhat.com/anderson/%{pname}-%{version}.tar.gz
# Source0-md5:	f394b1854112239c1c2e4dcf11cfbab3
# git clone https://code.google.com/p/eppic
Source1:	eppic.tar.xz
# Source1-md5:	a9f80ad71de9d6f5b77534a7ebdbed8e
Patch0:		%{pname}-x32.patch
URL:		http://people.redhat.com/anderson/
BuildRequires:	rpmbuild(macros) >= 1.701
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:2.6.20.2}}
%if %{with userspace}
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
BuildRequires:	xz-devel
BuildRequires:	zlib-devel
%endif
ExclusiveArch:	%{ix86} %{x8664} x32 alpha arm ia64 ppc64 s390 s390x
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

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-char-crash\
Summary:	Memory driver for live system crash sessions\
Summary(pl.UTF-8):	Sterownik pamięci dla sesji crash na żywym systemie\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-char-crash\
This package contains /dev/crash memory driver for live system crash\
sessions, which may be used when /dev/mem and /proc/kcore are\
unavailable.\
\
%description -n kernel%{_alt_kernel}-char-crash -l pl.UTF-8\
Ten pakiet zawiera sterownik pamięci /dev/crash do sesji crash na\
żywym systemie. Może być używany do analizy, kiedy /dev/mem i\
/proc/kcore nie są dostępne.\
\
%if %{with kernel}\
%files -n kernel%{_alt_kernel}-char-crash\
%defattr(644,root,root,755)\
%doc memory_driver/README\
/lib/modules/%{_kernel_ver}/kernel/drivers/char/crash.ko*\
%endif\
\
%post	-n kernel%{_alt_kernel}-char-crash\
%depmod %{_kernel_ver}\
\
%postun	-n kernel%{_alt_kernel}-char-crash\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
%build_kernel_modules -C memory_driver -m crash\
%install_kernel_modules -D installed -m memory_driver/crash -d kernel/drivers/char\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -a1 -n %{pname}-%{version}
%patch0 -p1

%{__mv} eppic extensions

%build
%{?with_kernel:%{expand:%build_kernel_packages}}

%if %{with userspace}
export CPPFLAGS="%{rpmcppflags} -I/usr/include/ncurses"
%{__make} -j1 all extensions \
	ARCH="%{_target_cpu}" \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -I/usr/include/ncurses"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT
cp -a installed/* $RPM_BUILD_ROOT
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man8,%{_libdir}/crash/extensions,%{_includedir}/crash}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# omitted by make install
install extensions/*.so $RPM_BUILD_ROOT%{_libdir}/crash/extensions
cp -p crash.8 $RPM_BUILD_ROOT%{_mandir}/man8
cp -p defs.h $RPM_BUILD_ROOT%{_includedir}/crash
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/crash
%dir %{_libdir}/crash
%dir %{_libdir}/crash/extensions
%attr(755,root,root) %{_libdir}/crash/extensions/dminfo.so
%attr(755,root,root) %{_libdir}/crash/extensions/echo.so
%attr(755,root,root) %{_libdir}/crash/extensions/eppic.so
%attr(755,root,root) %{_libdir}/crash/extensions/snap.so
%attr(755,root,root) %{_libdir}/crash/extensions/trace.so
%{_mandir}/man8/crash.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/crash
%endif
