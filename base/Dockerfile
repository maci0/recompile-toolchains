# rebrew/base — the shared OS + wine layer for every toolchain image.
#
# All toolchain Dockerfiles inherit FROM this image, so the OS, wine,
# dosbox and download tooling are built once and cached; each toolchain
# image only adds its compiler + an entrypoint wrapper.
#
# Build:  docker build -t rebrew/base:1.0 base
# Invoke: (base has no entrypoint — toolchain images set their own)
#
# Contents:
#   - wine + wine32 (32-bit PE compilers under wine, e.g. MSVC 6.0)
#   - wibo (minimal decompals PE loader — selectable per run via
#     REBREW_RUNNER=wibo for much faster compiles of plain console tools)
#   - dosbox (16-bit DOS compilers, e.g. MSVC 1.52, Delphi 1.0)
#   - dumb-init (PID-1 signal relay; no image entrypoint wraps with it —
#     available to callers who prepend it via --entrypoint)
#   - curl / ca-certificates / xz-utils (the pinned tarball downloads)
#   - /usr/local/lib/rebrew/wrapper-common.sh (shared wrapper helpers)
#   - common env: WINEDEBUG=-all, WINEPREFIX=/opt/wineprefix,
#     SDL_VIDEODRIVER=dummy (headless)
#   - REBREW_RUNNER (wine|wibo) selects the 32-bit PE runtime per run; the
#     wrapper-common rebrew_run helper dispatches on it
#
# The Debian filesystem is pinned by digest and every package comes from
# snapshot.debian.org at DEBIAN_SNAPSHOT: the archive state rebrew/base:1.0 was
# last built from (2026-11-12 18:06 UTC, from the live mirror), so a rebuild
# installs the packages the published images run. The image's debian.sources
# names the snapshot it was built from (20261005T000000Z); the build refuses an
# archive older than that. The sources stay on the snapshot, so a toolchain image's own
# `apt-get install` reads the same archive state rather than the live mirror.
# A snapshot's Release files expire like any other, so the images keep
# Acquire::Check-Valid-Until off (/etc/apt/apt.conf.d/99snapshot); signatures
# are still checked against the image's keyring. Bump DEBIAN_DIGEST,
# DEBIAN_SNAPSHOT and the package versions together, never one alone. Native
# compiler downloads remain sha256-pinned in each toolchain Dockerfile.

ARG DEBIAN_DIGEST=sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
ARG DEBIAN_SNAPSHOT=20261112T180000Z

# libfaketime 0.9.13 supports Wine's 32-bit time64 ABI. Debian's 0.9.10
# hangs before native LIB executes. Build both ELF ABIs without changing Wine.
FROM debian:bookworm-slim@${DEBIAN_DIGEST} AS clock-build
ARG DEBIAN_SNAPSHOT
RUN sources=/etc/apt/sources.list.d/debian.sources \
    && built=$(sed -n 's|^# http://snapshot.debian.org/archive/debian/\([0-9]\{8\}T[0-9]\{6\}Z\)$|\1|p' "$sources") \
    && grep -qx "# http://snapshot.debian.org/archive/debian-security/${built}" "$sources" \
    && [ "$(printf '%s\n' "$built" "$DEBIAN_SNAPSHOT" | sort | tail -n 1)" = "$DEBIAN_SNAPSHOT" ] \
    && sed -i \
        -e "s|^URIs: http://deb.debian.org/debian-security\$|URIs: http://snapshot.debian.org/archive/debian-security/${DEBIAN_SNAPSHOT}|" \
        -e "s|^URIs: http://deb.debian.org/debian\$|URIs: http://snapshot.debian.org/archive/debian/${DEBIAN_SNAPSHOT}|" \
        "$sources" \
    && ! grep -q "deb.debian.org" "$sources" \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99snapshot \
    && apt-get -o Acquire::Retries=3 update \
    && apt-get install -y --no-install-recommends \
        gcc=4:12.2.0-3 gcc-multilib=4:12.2.0-3 make=4.3-4.1 \
        curl=7.88.1-10+deb12u15 ca-certificates=20250419~deb12u2 \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/libfaketime.tar.gz \
        "https://codeload.github.com/wolfcw/libfaketime/tar.gz/86b37fde2fed7336ea2d0c17928e3015a55d9b4a" \
    && echo "d98aa7beeb21344b3612f60cbfe08196541a2ef25525b3774b11871493a4726e  /tmp/libfaketime.tar.gz" | sha256sum -c - \
    && mkdir /tmp/faketime && tar -xzf /tmp/libfaketime.tar.gz --no-same-owner -C /tmp/faketime --strip-components=1 \
    && make -C /tmp/faketime/src libfaketime.so.1 \
    && install -Dm0644 /tmp/faketime/src/libfaketime.so.1 /clock/lib/x86_64-linux-gnu/faketime/libfaketime.so.1 \
    && make -C /tmp/faketime/src clean \
    && make -C /tmp/faketime/src CC='gcc -m32' libfaketime.so.1 \
    && install -Dm0644 /tmp/faketime/src/libfaketime.so.1 /clock/lib/i386-linux-gnu/faketime/libfaketime.so.1 \
    && install -Dm0644 /tmp/libfaketime.tar.gz /clock/share/doc/libfaketime/source.tar.gz \
    && install -Dm0644 /tmp/faketime/COPYING /clock/share/doc/libfaketime/COPYING

FROM debian:bookworm-slim@${DEBIAN_DIGEST}
ARG DEBIAN_SNAPSHOT

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base (OS + wine/wibo + dosbox + wrapper helpers)" \
      org.opencontainers.image.description="base (OS + wine/wibo + dosbox + wrapper helpers) toolchain image"

RUN dpkg --add-architecture i386 \
    && sources=/etc/apt/sources.list.d/debian.sources \
    && built=$(sed -n 's|^# http://snapshot.debian.org/archive/debian/\([0-9]\{8\}T[0-9]\{6\}Z\)$|\1|p' "$sources") \
    && grep -qx "# http://snapshot.debian.org/archive/debian-security/${built}" "$sources" \
    && [ "$(printf '%s\n' "$built" "$DEBIAN_SNAPSHOT" | sort | tail -n 1)" = "$DEBIAN_SNAPSHOT" ] \
    && sed -i \
        -e "s|^URIs: http://deb.debian.org/debian-security\$|URIs: http://snapshot.debian.org/archive/debian-security/${DEBIAN_SNAPSHOT}|" \
        -e "s|^URIs: http://deb.debian.org/debian\$|URIs: http://snapshot.debian.org/archive/debian/${DEBIAN_SNAPSHOT}|" \
        "$sources" \
    && ! grep -q "deb.debian.org" "$sources" \
    && echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99snapshot \
    && apt-get -o Acquire::Retries=3 update \
    && apt-get install -y --no-install-recommends \
        wine=8.0~repack-4 wine32=8.0~repack-4 dosbox=0.74-3-4+b1 dumb-init=1.2.5-2 \
        curl=7.88.1-10+deb12u15 ca-certificates=20250419~deb12u2 xz-utils=5.4.1-1+deb12u2 \
    && rm -rf /var/lib/apt/lists/*

# wibo — the minimal decompals PE loader (github.com/decompals/wibo), static
# x86_64 build, sha256-pinned from the 1.2.0 release.  Runs 32-bit PE
# command-line tools (cl.exe, bcc32.exe, ...) without a wine prefix; wrappers
# use it when REBREW_RUNNER=wibo (they default to wine).
RUN curl -fsSL --retry 3 --retry-all-errors -o /usr/local/bin/wibo \
        "https://github.com/decompals/wibo/releases/download/1.2.0/wibo-x86_64" \
    && echo "13f86a2d618f0dbe67179d349625345eabf9b46450295cb4c904e49f6aff85af  /usr/local/bin/wibo" | sha256sum -c - \
    && chmod +x /usr/local/bin/wibo \
    && wibo --version >/dev/null

ENV WINEDEBUG=-all \
    WINEPREFIX=/opt/wineprefix \
    SDL_VIDEODRIVER=dummy \
    HOME=/home/rebrew

COPY wrapper-common.sh /usr/local/lib/rebrew/wrapper-common.sh
RUN chmod +x /usr/local/lib/rebrew/wrapper-common.sh
COPY --from=clock-build /clock/ /usr/
COPY clock.sh /usr/local/bin/rebrew-clock
RUN chmod +x /usr/local/bin/rebrew-clock

# Runtime runs as a non-root user (fixed uid/gid 1000): these images compile
# untrusted workdirs mounted at /work, so the compiler and its emulator never
# need root inside the container.  The wine prefix and HOME are pre-created
# and handed over because wine initializes its prefix lazily on the first PE
# run and DOSBox writes its primary config under $HOME/.dosbox.
RUN groupadd --gid 1000 rebrew \
    && useradd --uid 1000 --gid rebrew --create-home \
        --home-dir /home/rebrew --shell /usr/sbin/nologin rebrew \
    && mkdir -p /opt/wineprefix /work \
    && chown -R rebrew:rebrew /opt/wineprefix /home/rebrew /work

USER rebrew
