# rebrew/base-dosemu — the dosemu2 runtime layer for 16-bit DOS toolchains.
#
# Inherits base-noble (Ubuntu 24.04 + the shared wrapper helpers and user) and
# adds only what the DOS toolchains need; see base-noble for why a non-Debian
# base exists.
#
# The DOS-extended compilers of the early 1990s (PSY-Q 3.x's CC1PSX.EXE, Saturn
# Cygnus's CPP/CC1/AS) are DJGPP `go32` binaries.  DOSBox cannot load their
# stub — they exit silently with no object — so they need dosemu2 with the
# dj64 DPMI host, which is what decomp.me uses too.  Those packages exist only
# in Ubuntu PPAs (dosemu2/ppa and stsp-0/dj64), so this base is Ubuntu while
# `base/` is Debian; the shared wrapper helpers are copied out of `base/` so
# there is exactly one implementation of argument handling and error reporting.
#
# Every PPA package is pinned by a versioned PPA or Launchpad URL and sha256.
# Superseded files can disappear, so a failed download requires an explicit
# pin refresh and compiler smoke verification. The build never reads a PPA
# index and never substitutes an unverified newer package.
#
# NOTE: dosemu2 runs the guest CPU under KVM, so containers built FROM this
#       base must be run with `--device /dev/kvm`; rebrew_dosemu_run says so
#       if the device is missing.
#
# Build:  docker build -t rebrew/base-dosemu:1.0 base-dosemu

# Overridable so `PREFIX=registry/ ./build.sh` builds against the matching
# base-noble rather than the default namespace.
ARG NOBLE_IMAGE=rebrew/base-noble:1.0

FROM ${NOBLE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew base-dosemu (dosemu2 + dj64 runtime layer)" \
      org.opencontainers.image.description="dosemu2/dj64 runtime base for 16-bit DOS toolchain images (needs --device /dev/kvm)"

# dosemu2's runtime libraries are ordinary Ubuntu packages, installed at exact
# versions from the snapshot base-noble's sources name; the PPA-only packages
# below are pinned by URL and sha256. The dosemu2, FreeDOS++ kernel and dj64 DPMI
# host builds come from the two PPAs used by decomp.me. archaic-toolchains/dosemu2-noble
# keeps copies because the PPAs delete superseded builds.
# A retry reuses indexes already downloaded if the snapshot service returns 503.
# Keep the signed lists through both installs, then remove them in this layer.
RUN (apt-get --error-on=any update || apt-get --error-on=any update) \
    && apt-get install -y --no-install-recommends \
        ca-certificates=20260816ubuntu0.24.04.2 cpp=4:13.2.0-7ubuntu1 \
        curl=8.5.0-2ubuntu10.16 dos2unix=7.5.1-1 gzip=1.12-1ubuntu3.2 \
        libao4=1.2.2+20180113-1.1ubuntu4 libasound2t64=1.2.11-1ubuntu0.3 \
        libb64-0d=1.2-5 libelf1t64=0.190-1.1ubuntu0.1 libfluidsynth3=2.3.4-1build3 \
        libfontconfig1=2.15.0-1.1ubuntu2 libglib2.0-0t64=2.80.0-6ubuntu3.10 \
        libgpm2=1.20.7-11 libieee1284-3t64=0.2.11-14.1build1 libjansson4=2.14-2build2 \
        libjson-c5=0.17-1build1 libreadline8t64=8.2-4build1 \
        libsdl2-2.0-0=2.30.0+dfsg-1ubuntu3.1 libsdl2-ttf-2.0-0=2.22.0+dfsg-1 \
        libsearpc1t64=3.3.0+really3.3+git20230527.783141f-3.2 \
        libseccomp2=2.5.5-1ubuntu3.1 libslang2=2.3.3-3build2 \
        libslirp0=4.7.0-1ubuntu3.1 libstdc++6=14.2.0-4ubuntu2~24.04.1 \
        libx11-6=2:1.8.7-1ubuntu0.1 libxext6=2:1.3.4-1build2 python3=3.12.3-0ubuntu2.1 \
        tar=1.35+dfsg-3ubuntu0.4 \
    && mkdir -p /tmp/debs \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/dosemu2.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/dosemu2.deb" \
    && echo "030f19f2e60a39b93411fb689bec732ef7fc7b2021af1f7f200166ad215b6cea  /tmp/debs/dosemu2.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/fdpp.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/fdpp.deb" \
    && echo "e1b2c238ef79c97ac588dfeec54cc8598890cd97e2e344dc4627258948d09d8d  /tmp/debs/fdpp.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libfdldr35.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/libfdldr35.deb" \
    && echo "3eae90ee8f0d2f44f1c6b23bc5025ab29438fc11ff7cbd68e12ff331855239a0  /tmp/debs/libfdldr35.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libfdpp35.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/libfdpp35.deb" \
    && echo "096d98ba5730dfd6e4030381e28f7ebd335e11579660765abf75dd549443af07  /tmp/debs/libfdpp35.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/comcom64.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/comcom64.deb" \
    && echo "a936b0cd6bb277b1390c69b446d1c40aaae66b709214d7d84b7af39fea21598b  /tmp/debs/comcom64.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/comcom32.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/comcom32.deb" \
    && echo "59908a1a15fa1b588fa2f02535ac6c956872d6cc6ccead1d283f8297f64d0f33  /tmp/debs/comcom32.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/dj64.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/dj64.deb" \
    && echo "a59151ebc5c6201544f9870095397e417dbac7b8f4fdef522fa6fda684c77476  /tmp/debs/dj64.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/djstub.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/djstub.deb" \
    && echo "7fe066839810615a6c0a1b3e761006e1f4fecc6a711de131b37bc6f0058a7d6c  /tmp/debs/djstub.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libdjstub64-0.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/libdjstub64-0.deb" \
    && echo "4c978839c9cf37fb3ed010febeed4f01f0e737296a5f6901f134aeab47cd37da  /tmp/debs/libdjstub64-0.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libdjdev64-0.deb \
        "https://github.com/archaic-toolchains/dosemu2-noble/releases/download/2026-11-10/libdjdev64-0.deb" \
    && echo "7b5c53170e2445884d83de0e5d7462daab09398473fd1dda929beafedb4245cd  /tmp/debs/libdjdev64-0.deb" | sha256sum -c - \
    && apt-get install -y --no-install-recommends /tmp/debs/dosemu2.deb /tmp/debs/fdpp.deb \
        /tmp/debs/libfdldr35.deb /tmp/debs/libfdpp35.deb /tmp/debs/comcom64.deb \
        /tmp/debs/comcom32.deb /tmp/debs/dj64.deb /tmp/debs/djstub.deb \
        /tmp/debs/libdjstub64-0.deb /tmp/debs/libdjdev64-0.deb \
    && rm -rf /tmp/debs /var/lib/apt/lists/* \
    && dpkg -s dosemu2 dj64 fdpp > /dev/null \
    && /usr/libexec/dosemu2/dosemu2.bin --version
