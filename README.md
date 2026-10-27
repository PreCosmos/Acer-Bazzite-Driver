# Acer Bazzite Driver

**A fork of [Linuwu-Sense](https://github.com/0x7375646F/Linuwu-Sense), made specifically to install its Acer laptop driver on immutable Fedora systems, including Bazzite Nvidia Open.**

Target: **Acer Predator PHN16S-71**, x86_64, Fedora **44** and **45** based Bazzite images. Other upstream-supported Acer Predator/Nitro models remain in the source, but are not hardware-validated here. This is an unofficial, community driver; neither Acer nor Bazzite maintains this fork.

[Download RPMs and source RPMs](https://github.com/PreCosmos/Acer-Bazzite-Driver/releases/latest) · [Original usage documentation](README.upstream.md) · [GPL v3 license](LICENSE)

## Source and laptop support

This release starts from upstream commit [`4483b6c38b9bb963ac9ada9ca476578e0c63cc08`](https://github.com/0x7375646F/Linuwu-Sense/commit/4483b6c38b9bb963ac9ada9ca476578e0c63cc08). It includes the original PHN16S-71 support from [upstream PR #97](https://github.com/0x7375646F/Linuwu-Sense/pull/97), by **alltern**:

- [`6bee3af6f02d8adc00c1f70a88b8add0beaf29a8`](https://github.com/0x7375646F/Linuwu-Sense/commit/6bee3af6f02d8adc00c1f70a88b8add0beaf29a8): recognize `Acer` / `Predator PHN16S-71` through DMI.
- [`53e3eb37386635a1b68ad0e772df6f7fdff710dd`](https://github.com/0x7375646F/Linuwu-Sense/commit/53e3eb37386635a1b68ad0e772df6f7fdff710dd): select the model quirk with Predator v4 and four-zone keyboard capabilities.

These commits are already merged upstream and are retained in this fork's history. This fork adds the immutable Fedora RPM packaging and service. It preserves upstream authorship and GPL licensing. The original README is retained as `README.upstream.md`; its `make install` instructions are **not** the installation method for this package.

## What the RPM installs

The `acer-bazzite-driver` RPM ships driver **source**, helpers, and a systemd service. It builds a kernel-specific `linuwu_sense.ko` in `/var/lib/acer-bazzite-driver/build/<kernel>/`, then loads it from that writable location. It does not install a precompiled module into immutable `/usr/lib/modules`, run DKMS, alter the Nvidia driver, or rebase your Bazzite image.

There are separate `.fc44.noarch.rpm` and `.fc45.noarch.rpm` assets built inside the corresponding Fedora containers. `noarch` describes the source/service payload: **the actual driver supports x86_64 only**. Select the RPM matching `VERSION_ID` in `/etc/os-release`. The two RPMs are alternatives, not packages to install together.

The service rebuilds when the running kernel or packaged source changes. It requires the exact kernel's development tree at `/usr/src/kernels/$(uname -r)`. The RPM depends on `kernel-devel`, GCC, make, libelf development files, kmod, mokutil, OpenSSL, SELinux tools, systemd, and util-linux. A generic Fedora kernel-devel package cannot substitute for headers matching Bazzite's custom kernel. Bazzite Nvidia Open commonly includes its matching development package; check before installing.

On start, the service builds first, unloads `acer_wmi`, and loads `linuwu_sense`. If loading fails, it attempts to restore `acer_wmi`. On stop it unloads `linuwu_sense` and restores `acer_wmi`. No persistent `acer_wmi` blacklist is installed. The service does not choose Turbo mode, change fan settings, or set a power profile. Device features and any firmware side effects remain those of the upstream driver.

## Install on Bazzite Nvidia Open

1. Check the base Fedora version and the running kernel:

   ```bash
   cat /etc/os-release
   uname -r
   test -f "/usr/src/kernels/$(uname -r)/Makefile" && echo 'Matching kernel headers found'
   mokutil --sb-state
   ```

   If headers are missing, obtain the **exact matching kernel-devel** from the same kernel repository/image as your Bazzite kernel. If you have a pending system update, reboot first and recheck. Do not point the build at another kernel version.

2. Download the matching RPM and `SHA256SUMS` from the release. In the download directory, verify the RPM's hash against its entry in `SHA256SUMS`, for example:

   ```bash
   sha256sum acer-bazzite-driver-1.0.0-1.fc44.noarch.rpm
   grep 'acer-bazzite-driver-1.0.0-1.fc44.noarch.rpm$' SHA256SUMS
   ```

   These initial RPMs are not signed with a repository GPG key; the checksums detect corruption but are not an independent publisher signature.

3. Layer the RPM on the **host**, not inside Distrobox/Toolbox. For Fedora 44:

   ```bash
   sudo rpm-ostree install ./acer-bazzite-driver-1.0.0-1.fc44.noarch.rpm
   systemctl reboot
   ```

   For Fedora 45, substitute `acer-bazzite-driver-1.0.0-1.fc45.noarch.rpm`. Bazzite's [package layering documentation](https://docs.bazzite.gg/Installing_and_Managing_Software/rpm-ostree/) explains why a reboot is required.

4. After reboot, configure Secure Boot below if enabled, then explicitly start the driver:

   ```bash
   sudo acer-bazzite-driver --check
   sudo systemctl enable --now acer-bazzite-driver.service
   systemctl status acer-bazzite-driver.service --no-pager
   lsmod | grep -E 'linuwu_sense|acer_wmi'
   ```

   The first start compiles the module; allow several minutes. Installation alone does **not** enable or load it. A failed prerequisite check leaves the stock driver in place.

5. Optional: grant your account access to the supported sysfs controls:

   ```bash
   sudo usermod -aG linuwu_sense "$USER"
   ```

   Log out and back in. Root can use the controls without group membership. There is no bundled GUI. Upstream's optional GUIs are separate projects.

## Secure Boot and kernel lockdown

The release does not contain a private signing key. With Secure Boot or enforcing kernel lockdown, you must create a local key, enroll its certificate, and sign locally. Bazzite's built-in certificate does not automatically trust this custom module.

```bash
sudo install -d -m 0700 /var/lib/acer-bazzite-driver/keys
sudo openssl req -new -x509 -newkey rsa:3072 -nodes -days 3650 \
  -subj '/CN=Acer Bazzite Driver local module/' \
  -keyout /var/lib/acer-bazzite-driver/keys/MOK.priv \
  -outform DER -out /var/lib/acer-bazzite-driver/keys/MOK.der
sudo chmod 0600 /var/lib/acer-bazzite-driver/keys/MOK.priv
sudo mokutil --import /var/lib/acer-bazzite-driver/keys/MOK.der
systemctl reboot
```

Complete enrollment in the firmware MOK manager using the temporary password you chose. After reboot, run `sudo acer-bazzite-driver --check` and start the service. The helper uses the kernel's `scripts/sign-file` before loading the module. Never upload or share `MOK.priv`. Systems without working MOK enrollment need their own supported kernel trust mechanism. Secure Boot operation has not been hardware-tested for this release.

## Existing Linuwu Sense installations

Disable and remove any previous `linuwu-sense.service` or `linuwu_sense.service` before enabling this package. Do not run two loaders together. Remove old dedicated module-load/blacklist configuration only if it belongs to that previous installation. An old module loaded with `insmod` may need `sudo rmmod linuwu_sense`, since it is not indexed under `/usr/lib/modules`.

The earlier local installation on the target laptop used `/etc/systemd/system/linuwu-sense.service` and `/var/lib/linuwu-sense`. Those paths are distinct from this package's service and state directory. Package installation does not silently delete a previous setup.

## Controls and troubleshooting

Read [upstream usage](README.upstream.md) for thermal profiles, battery charge limiting, fans, and keyboard controls. Available files depend on the firmware and model. Typical paths are:

- `/sys/firmware/acpi/platform_profile` and `platform_profile_choices`
- `/sys/devices/platform/acer-wmi/predator_sense/`
- `/sys/devices/platform/acer-wmi/four_zoned_kb/`

Four-zone flags do not guarantee working RGB on every keyboard controller revision. Per-key RGB and ENEK5130 hardware may need other drivers. Fan and battery controls call reverse-engineered firmware methods: use settings appropriate to your hardware. A successful compile is not proof every control works.

```bash
sudo journalctl -u acer-bazzite-driver.service -b --no-pager
sudo dmesg | grep -Ei 'linuwu|acer|verification|key rejected'
sudo acer-bazzite-driver --check
```

Missing headers: obtain matching development files. `Key was rejected`: complete certificate enrollment. `Module in use`: stop the previous loader and close consumers of its devices; reboot if necessary. SELinux remains enabled; the helper labels the built module `modules_object_t` before loading. Do not disable SELinux to work around an uninvestigated denial.

## Updates and removal

A kernel update triggers a fresh build at the next service start, provided matching headers are installed. An upstream kernel API change can still require a driver update. Cached builds remain in `/var` and may be removed while the service is stopped. Locally layered release RPMs do **not** automatically receive project updates. Install a later RPM with `rpm-ostree` and reboot. Before changing between Fedora 44 and 45, uninstall this local RPM, complete the OS upgrade, then layer the matching release asset.

To restore the stock Acer driver and remove the package:

```bash
sudo systemctl disable --now acer-bazzite-driver.service
sudo rpm-ostree uninstall acer-bazzite-driver
systemctl reboot
```

After reboot, optional state/group cleanup:

```bash
sudo rm -rf /var/lib/acer-bazzite-driver
sudo gpasswd -d "$USER" linuwu_sense
sudo groupdel linuwu_sense
```

Only remove the group if no other Linuwu installation uses it. Removing the state directory also removes any local signing key; retain a secure backup first if desired. Enrolled MOK certificates are not automatically deleted; manage them through `mokutil` if no longer needed.

## Build and validation

From a checkout, with Podman installed:

```bash
packaging/build-rpm.sh 44
packaging/build-rpm.sh 45
```

Binary and source RPMs are written to `dist/`. The GitHub Actions workflow builds both variants and compiles the source against each Fedora container's available kernel development tree. Release notes record the checks actually completed. The initial release additionally compiled on the target laptop against `7.2.11-ogc4.1.fc44.x86_64`; BTF was skipped because the kernel's `vmlinux` was unavailable. **Live RPM installation, post-reboot behavior, hardware controls, and Secure Boot remain for the user to test. Fedora 45 Bazzite hardware operation is not claimed as tested.**
