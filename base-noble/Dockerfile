# rebrew/base-noble — the Ubuntu-noble layer for toolchains Debian cannot host.
#
# Two families need a newer/other userland than `base/` (Debian bookworm):
# the 16-bit DOS toolchains (dosemu2 + dj64 are packaged only for Ubuntu —
# see base-dosemu) and the IRIX IDO images whose bundled `qemu-irix-4.0` needs
# GLIBC_2.38 (bookworm ships 2.36 and the loader aborts when trixie's libc is
# mixed in).  Both inherit this layer so the shared wrapper helpers and the
# unprivileged `rebrew` user exist in exactly one place.
#
# It deliberately installs nothing beyond the wrapper-common prerequisites:
# a family adds what *it* needs (dosemu2, libglib2.0 + python3, ...) so an
# image never carries a runtime it does not use.
#
# Build:  docker build -t rebrew/base-noble:1.0 base-noble

ARG HELPER_IMAGE=rebrew/base:1.0
# ubuntu:noble-20261110.1 (amd64 rootfs diff_id 369ede38a92d...), pinned by its
# index digest. The package index comes from snapshot.ubuntu.com at UBUNTU_SNAPSHOT,
# and the sources stay there, so an image built on this base (base-dosemu, the
# IDO images) installs from the same archive state rather than the live mirror.
# Ubuntu's image names no snapshot of its own, so nothing ties the two values
# together; the exact package versions below fail the build if the snapshot
# lacks them. Bump UBUNTU_DIGEST, UBUNTU_SNAPSHOT and the versions together.
ARG UBUNTU_DIGEST=sha256:882e1e56091c9ffbc70c026ff5935fe85d3c91ad155917865ba2ffa23ede1560
ARG UBUNTU_SNAPSHOT=20261121T180000Z

FROM ${HELPER_IMAGE} AS helper

FROM ubuntu:noble@${UBUNTU_DIGEST}
ARG UBUNTU_SNAPSHOT

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base-noble (Ubuntu 24.04 + wrapper helpers)" \
      org.opencontainers.image.description="Ubuntu-noble layer for toolchains that need a newer glibc or non-Debian runtime packages"

COPY --from=helper /usr/local/lib/rebrew /usr/local/lib/rebrew
COPY --from=helper /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt

# Same unprivileged runtime user as base/ (uid/gid 1000, /work owned), so
# images built on any base behave identically for volumes and `USER rebrew`.
# Ubuntu's image already owns uid/gid 1000 as `ubuntu`, so rename it rather
# than adding a second account.
# Only the dated snapshot supplies indexes. The Ubuntu archive can serve a .deb
# when its bytes match the hash in that index.
RUN groupmod -n rebrew ubuntu \
    && usermod -l rebrew -d /home/rebrew -m ubuntu \
    && sources=/etc/apt/sources.list.d/ubuntu.sources \
    && printf 'https://archive.ubuntu.com/ubuntu/\ttype:deb priority:1\nhttps://snapshot.ubuntu.com/ubuntu/%s/\n' \
        "$UBUNTU_SNAPSHOT" > /etc/apt/ubuntu-mirrors.list \
    && sed -Ei 's#^URIs: http://(archive|security)\.ubuntu\.com/ubuntu/$#URIs: mirror+file:/etc/apt/ubuntu-mirrors.list#' "$sources" \
    && ! grep -Eq "(archive|security)\.ubuntu\.com" "$sources" \
    && printf '%s\n' 'Acquire::Check-Valid-Until "false";' 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/99snapshot \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates=20260816ubuntu0.24.04.2 curl=8.5.0-2ubuntu10.16 \
        gzip=1.12-1ubuntu3.2 tar=1.35+dfsg-3ubuntu0.4 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /work \
    && chown -R rebrew:rebrew /home/rebrew /work

ENV HOME=/home/rebrew
