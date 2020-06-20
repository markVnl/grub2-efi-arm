%undefine _hardened_build

%ifarch aarch64
%global grubefiarch arm64-efi
%global grubefiname grubaa64.efi
%global grubeficdname gcdaa64.efi
%global grububootname BOOTAA64.EFI
%endif
%ifarch armv7hl
%global grubefiarch arm-efi
%global grubefiname grubarm.efi
%global grubeficdname gcdarm.efi
%global grububootname BOOTARM.EFI
%endif

# Figure out the right file path to use
%global efidir %(eval echo $(grep ^ID= /etc/os-release | sed -e 's/^ID=//'))

%global githash na
%undefine _missing_build_ids_terminate_build

Name:           grub2
Epoch:          1
Version:        2.04
Release:        %mkrel 1
Summary:        Bootloader with support for Linux, Multiboot and more

Group:          System Environment/Base
License:        GPLv3+
URL:            http://www.gnu.org/software/grub/
Source0:        https://ftp.gnu.org/gnu/grub/grub-%{version}.tar.xz

Patch1:        0001-Fix-bad-test-on-GRUB_DISABLE_SUBMENU.patch
Patch2:        0002-Honor-a-symlink-when-generating-configuration-by-gru.patch
Patch3:        0003-Don-t-say-GNU-Linux-in-generated-menus.patch
# mageia DejaVuSans.ttf location
Patch9991:     9991-Fix-DejaVuSans.ttf-location.patch

BuildRequires: flex bison binutils python
BuildRequires: ncurses-devel xz-devel bzip2-devel
BuildRequires: freetype-devel libusb-devel
BuildRequires: rpm-devel
BuildRequires: glibc-devel glibc-static-devel
BuildRequires:  autoconf automake autogen device-mapper-devel
BuildRequires:  freetype-devel gettext-devel git
BuildRequires:  texinfo
#BuildRequires:  dejavu-sans-fonts
BuildRequires:  fonts-ttf-dejavu
BuildRequires:  help2man

Requires:       gettext which file
Requires:       %{name}-common = %{epoch}:%{version}-%{release}
Requires:       os-prober >= 1.58-11
Requires(pre):  dracut
Requires(post): dracut


%description
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides support for PC BIOS systems.

%package efi
Summary:       GRUB for EFI systems.
Group:         System Environment/Base
Requires:      %{name}-common = %{epoch}:%{version}-%{release}

%description efi
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides support for EFI systems.

%package common
Summary:       Support common for GRUB.
Group:         System Environment/Base
# FIXME quick mitigation for mageia
#Requires:      gettext os-prober which file system-logos
#Requires:     grubby-deprecated
Requires:      gettext os-prober which file
Provides:      %{name}-common = %{epoch}:%{version}-%{release}
Provides:      %{name}-common-minimal = %{epoch}:%{version}-%{release}
Provides:      %{name}bootloader = %{epoch}:%{version}-%{release}

%description common
The GRand Unified Bootloader (GRUB) is a highly configurable and customizable
bootloader with modular architecture.  It support rich varietyof kernel formats,
file systems, computer architectures and hardware devices.  This subpackage
provides common for support of all platforms.

%prep
%setup -q -n grub-%{version}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch9991 -p1

%build
./autogen.sh
%configure                     \
   CFLAGS="-Os -g"             \
   TARGET_LDFLAGS=-static      \
        --with-platform=efi    \
        --with-grubdir=%{name} \
        --program-transform-name=s,grub,%{name}, \
        --disable-grub-mount   \
        --disable-werror

make %{?_smp_mflags}

sed -i -e 's,(grub),(%{name}),g' \
   -e 's,grub.info,%{name}.info,g' \
   -e 's,\* GRUB:,* GRUB2:,g' \
   -e 's,/boot/grub/,/boot/%{name}/,g' \
   -e 's,\([^-]\)grub-\([a-z]\),\1%{name}-\2,g' \
   docs/grub.info
sed -i -e 's,grub-dev,%{name}-dev,g' docs/grub-dev.info

/usr/bin/makeinfo --html --no-split -I docs -o grub-dev.html docs/grub-dev.texi
/usr/bin/makeinfo --html --no-split -I docs -o grub.html docs/grub.texi
sed -i -e 's,/boot/grub/,/boot/%{name}/,g' \
   -e 's,\([^-]\)grub-\([a-z]\),\1%{name}-\2,g' \
   grub.html

%install
make DESTDIR=$RPM_BUILD_ROOT install
find $RPM_BUILD_ROOT -iname "*.module" -exec chmod a-x {} \;

# Ghost config file
install -m 755 -d $RPM_BUILD_ROOT/boot/%{name}
touch $RPM_BUILD_ROOT//boot/%{name}/grub.cfg
ln -s ../boot/%{name}/grub.cfg $RPM_BUILD_ROOT%{_sysconfdir}/%{name}-efi.cfg

mv $RPM_BUILD_ROOT%{_infodir}/grub.info $RPM_BUILD_ROOT%{_infodir}/%{name}.info
mv $RPM_BUILD_ROOT%{_infodir}/grub-dev.info $RPM_BUILD_ROOT%{_infodir}/%{name}-dev.info
rm $RPM_BUILD_ROOT%{_infodir}/dir


%post common
if [ "$1" = 1 ]; then
   /sbin/install-info --info-dir=%{_infodir} %{_infodir}/%{name}.info.gz || :
   /sbin/install-info --info-dir=%{_infodir} %{_infodir}/%{name}-dev.info.gz || :
fi

%preun common
if [ "$1" = 0 ]; then
   /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/%{name}.info.gz || :
   /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/%{name}-dev.info.gz || :
fi

%files efi
%doc COPYING
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}-efi.cfg
%ghost %config(noreplace) /boot/%{name}/grub.cfg
# grub-efi-modules
%{_libdir}/grub/%{grubefiarch}

%files common
%defattr(-,root,root,-)
%dir %{_libdir}/grub/
%dir %{_datarootdir}/grub/
%dir %{_datarootdir}/grub/themes
%{_datarootdir}/grub/*
%{_sbindir}/%{name}-bios-setup
%{_sbindir}/%{name}-install
%{_sbindir}/%{name}-macbless
%{_sbindir}/%{name}-mkconfig
%{_sbindir}/%{name}-ofpathname
%{_sbindir}/%{name}-probe
%{_sbindir}/%{name}-reboot
%{_sbindir}/%{name}-set-default
%{_sbindir}/%{name}-sparc64-setup
%{_bindir}/%{name}-editenv
%{_bindir}/%{name}-file
%{_bindir}/%{name}-fstest
%{_bindir}/%{name}-glue-efi
%{_bindir}/%{name}-kbdcomp
%{_bindir}/%{name}-menulst2cfg
%{_bindir}/%{name}-mkfont
%{_bindir}/%{name}-mkimage
%{_bindir}/%{name}-mklayout
%{_bindir}/%{name}-mknetdir
%{_bindir}/%{name}-mkpasswd-pbkdf2
%{_bindir}/%{name}-mkrelpath
%ifnarch %{sparc}
%{_bindir}/%{name}-mkrescue
%endif
%{_bindir}/%{name}-mkstandalone
%{_bindir}/%{name}-render-label
%{_bindir}/%{name}-script-check
%{_bindir}/%{name}-syslinux2cfg
%{_sysconfdir}/bash_completion.d/grub
%attr(0700,root,root) %dir %{_sysconfdir}/grub.d
%config %{_sysconfdir}/grub.d/??_*
%{_sysconfdir}/grub.d/README
%attr(0644,root,root) %ghost %config(noreplace) %{_sysconfdir}/default/grub
%dir /boot/%{name}
%{_infodir}/%{name}*
%{_datadir}/man/man?/*
%doc COPYING INSTALL
%doc NEWS README
%doc THANKS TODO
%doc grub.html
%doc grub-dev.html docs/font_char_metrics.png
# locales
%dir %{_datarootdir}/locale
%{_datarootdir}/locale/*
