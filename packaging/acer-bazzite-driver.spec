Name:           acer-bazzite-driver
Version:        1.0.0
Release:        1%{?dist}
Summary:        Acer Linuwu Sense driver for Bazzite and immutable Fedora
License:        GPL-3.0-only
URL:            https://github.com/PreCosmos/Acer-Bazzite-Driver
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
ExclusiveArch:  x86_64 noarch
BuildRequires:  systemd-rpm-macros
Requires:       bash
Requires:       coreutils
Requires:       gcc
Requires:       make
Requires:       elfutils-libelf-devel
Requires:       kernel-devel
Requires:       kmod
Requires:       mokutil
Requires:       openssl
Requires:       policycoreutils
Requires:       util-linux
Requires:       systemd

%description
Linuwu-Sense fork for Acer Predator/Nitro laptops on Bazzite Nvidia Open
and immutable Fedora 44/45. Includes Predator PHN16S-71 support.
Ships source and an explicitly enabled systemd service that builds for the
running kernel in /var and loads the module without writing to /usr.
Matching kernel-devel is required. Secure Boot needs a locally enrolled key.

%prep
%autosetup

%build
# The module is built for the running host kernel after installation.

%install
install -Dpm 0755 packaging/acer-bazzite-driver %{buildroot}%{_sbindir}/acer-bazzite-driver
install -Dpm 0755 packaging/acer-bazzite-driver-stop %{buildroot}%{_libexecdir}/acer-bazzite-driver-stop
install -Dpm 0644 packaging/acer-bazzite-driver.service %{buildroot}%{_unitdir}/acer-bazzite-driver.service
install -Dpm 0644 src/linuwu_sense.c %{buildroot}%{_datadir}/acer-bazzite-driver/source/src/linuwu_sense.c
printf 'obj-m := src/linuwu_sense.o\n' > %{buildroot}%{_datadir}/acer-bazzite-driver/source/Makefile
install -d %{buildroot}%{_sysusersdir}
printf 'g linuwu_sense -\n' > %{buildroot}%{_sysusersdir}/acer-bazzite-driver.conf

%check
bash -n packaging/acer-bazzite-driver packaging/acer-bazzite-driver-stop

%files
%license LICENSE
%doc README.md README.upstream.md
%{_sbindir}/acer-bazzite-driver
%{_libexecdir}/acer-bazzite-driver-stop
%{_unitdir}/acer-bazzite-driver.service
%{_sysusersdir}/acer-bazzite-driver.conf
%{_datadir}/acer-bazzite-driver/

%changelog
* Tue Oct 27 2026 PreCosmos <85321958+PreCosmos@users.noreply.github.com> - 1.0.0-1
- Initial immutable Fedora 44/45 packaging with PHN16S-71 support
