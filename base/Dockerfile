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
# The Debian filesystem is pinned by digest; apt still reads current
# Bookworm package indexes. Native compiler downloads remain sha256-pinned
# in each toolchain Dockerfile.

# libfaketime 0.9.13 supports Wine's 32-bit time64 ABI. Debian's 0.9.10
# hangs before native LIB executes. Build both ELF ABIs without changing Wine.
FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587 AS clock-build
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc gcc-multilib make curl ca-certificates && rm -rf /var/lib/apt/lists/*
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

# debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587
FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587

# OCI provenance labels (org.opencontainers.image).
LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base (OS + wine/wibo + dosbox + wrapper helpers)" \
      org.opencontainers.image.description="base (OS + wine/wibo + dosbox + wrapper helpers) toolchain image"

RUN dpkg --add-architecture i386 \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        wine wine32 dosbox dumb-init curl ca-certificates xz-utils \
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
