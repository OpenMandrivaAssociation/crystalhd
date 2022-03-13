%define snap 20121105
%define major 3
%define libname %mklibname crystalhd %{major}
%define devname %mklibname crystalhd -d

Summary:	Broadcom Crystal HD decoder driver and library
Name:		crystalhd
Version:	20170515
Release:	0.%{snap}.7
License:	GPLv2 and LGPLv2
Group:		System/Kernel and hardware
Url:		http://www.broadcom.com/support/crystal_hd/
# http://git.linuxtv.org/jarod/crystalhd.git
Source0:	%{name}-%{snap}.tar.xz
Source1:	%{name}.rpmlintrc
Patch0:         crystalhd-remove-msse2-gcc.patch
Patch1:		crystalhd-no-sse2.patch
# Uses emmintrin.h
#ExclusiveArch:	%{ix86} %{x86_64}

%description
Driver and support library for Broadcom Crystal HD hardware video
decoder.

To use the device, you need to copy the appropriate firmware file to
the /lib/firmware directory:
- BCM70012 devices: bcm70012fw.bin
- BCM70015 devices: bcm70015fw.bin

%package -n dkms-%{name}
Summary:	Broadcom Crystal HD decoder driver
Group:		System/Kernel and hardware
License:	GPLv2
Requires:	dkms
Requires(post,preun):	dkms
Requires(post,preun):	rpm-helper

%description -n dkms-%{name}
DKMS driver for Broadcom Crystal HD hardware video decoder.

To use the device, you need to copy the appropriate firmware file to
the /lib/firmware directory:
- BCM70012 devices: bcm70012fw.bin
- BCM70015 devices: bcm70015fw.bin

%package -n lib%{name}-common
Summary:	udev rules for Broadcom Crystal HD decoder
Group:		System/Libraries
License:	LGPLv2

%description -n lib%{name}-common
udev rules for Broadcom Crystal HD hardware video decoder.

To use the device, you need to copy the appropriate firmware file to
the /lib/firmware directory:
- BCM70012 devices: bcm70012fw.bin
- BCM70015 devices: bcm70015fw.bin

%package -n %{libname}
Summary:	Broadcom Crystal HD decoder library
Group:		System/Libraries
License:	LGPLv2
Provides:	%{name} = %{version}-%{release}
Requires:	lib%{name}-common >= %{version}-%{release}

%description -n %{libname}
Support library for Broadcom Crystal HD hardware video decoder.

To use the device, you need to copy the appropriate firmware file to
the /lib/firmware directory:
- BCM70012 devices: bcm70012fw.bin
- BCM70015 devices: bcm70015fw.bin

%package -n %{devname}
Summary:	Headers for libcrystalhd development
Group:		Development/C
License:	LGPLv2
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
This package contains the headers that are needed to compile
applications that use libcrystalhd.

%prep
%setup -qn %{name}-%{snap}
%ifarch %{armx}
# Should we also disable sse2 on i586?
%autopatch -p1
%endif

# for install target
mkdir -p firmware/fwbin/70012
touch firmware/fwbin/70012/bcm70012fw.bin

sed -i 's,\$(CRYSTALHD_ROOT),\$(src),g' driver/linux/Makefile.in

%build
%setup_compile_flags
%make -C linux_lib/libcrystalhd BCGCC="$CXX %{optflags} %{?ldflags}"

mkdir -p firmware/fwbin/70015
touch firmware/fwbin/70015/bcm70015fw.bin

%install
%makeinstall_std -C linux_lib/libcrystalhd LIBDIR=%{_libdir}
rm %{buildroot}/lib/firmware/bcm7001[25]fw.bin

install -d -m755 %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/driver/linux
install -m644 driver/linux/*.[ch] %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/driver/linux
# no thanks to autoconf:
install -m644 driver/linux/Makefile.in %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/driver/linux/Makefile
cp -pr include %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/

cat > %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}/dkms.conf <<EOF
PACKAGE_NAME="%{name}"
PACKAGE_VERSION="%{version}-%{release}"
AUTOINSTALL="yes"
MAKE[0]="make -C \${kernel_source_dir} M=\\\$(pwd)/driver/linux"
CLEAN="make -C \${kernel_source_dir} M=\\\$(pwd)/driver/linux clean"
BUILT_MODULE_NAME[0]="crystalhd"
BUILT_MODULE_LOCATION[0]="driver/linux"
DEST_MODULE_LOCATION[0]="/kernel"
EOF

install -d -m755 %{buildroot}%{_sysconfdir}/udev/rules.d
cat > %{buildroot}%{_sysconfdir}/udev/rules.d/65-crystalhd.rules <<EOF
KERNEL=="crystalhd", GROUP="video", ENV{ACL_MANAGE}="1"
EOF

%post -n dkms-%{name}
dkms add     -m %{name} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms build   -m %{name} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --force
true

%preun -n dkms-%{name}
dkms remove  -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all
true


%files -n dkms-%{name}
%dir %{_usrsrc}/%{name}-%{version}-%{release}
%dir %{_usrsrc}/%{name}-%{version}-%{release}/driver
%{_usrsrc}/%{name}-%{version}-%{release}/driver/linux
%{_usrsrc}/%{name}-%{version}-%{release}/include
%{_usrsrc}/%{name}-%{version}-%{release}/dkms.conf

%files -n lib%{name}-common
%{_sysconfdir}/udev/rules.d/65-crystalhd.rules

%files -n %{libname}
%{_libdir}/libcrystalhd.so.%{major}*

%files -n %{devname}
%doc examples
%{_libdir}/libcrystalhd.so
%dir %{_includedir}/lib%{name}
%{_includedir}/lib%{name}/*.h
