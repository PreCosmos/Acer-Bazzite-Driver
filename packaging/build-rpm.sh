#!/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
release=${1:?Usage: packaging/build-rpm.sh 44|45}
case $release in 44|45) ;; *) echo 'Expected Fedora 44 or 45' >&2; exit 1;; esac
root=$(pwd)
mkdir -p dist
podman run --rm -v "$root:/source:ro,z" -v "$root/dist:/output:rw,z" \
    "registry.fedoraproject.org/fedora:$release" bash -euc '
    dnf -y install rpm-build systemd-rpm-macros
    mkdir -p /tmp/rpmbuild/{SOURCES,SPECS}
    tar -C /source --exclude=.git --exclude=dist --transform="s,^,acer-bazzite-driver-1.0.0/," -czf /tmp/rpmbuild/SOURCES/acer-bazzite-driver-1.0.0.tar.gz .
    rpmbuild -ba --define "_topdir /tmp/rpmbuild" /source/packaging/acer-bazzite-driver.spec
    cp /tmp/rpmbuild/RPMS/noarch/*.rpm /tmp/rpmbuild/SRPMS/*.rpm /output/
    '
