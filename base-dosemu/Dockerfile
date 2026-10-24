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

# dosemu2's runtime libraries come from Ubuntu's archive (they are ordinary
# distro packages); only the PPA-only packages below are pinned.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates cpp curl dos2unix gzip libao4 libasound2t64 libb64-0d \
        libelf1t64 libfluidsynth3 libfontconfig1 libglib2.0-0t64 libgpm2 \
        libieee1284-3t64 libjansson4 libjson-c5 libreadline8t64 libsdl2-2.0-0 \
        libsdl2-ttf-2.0-0 libsearpc1t64 libseccomp2 libslang2 libslirp0 \
        libstdc++6 libx11-6 libxext6 python3 tar \
    && rm -rf /var/lib/apt/lists/*

# dosemu2 + the FreeDOS++ kernel (fdpp) + the dj64 DPMI host, from the two
# PPAs decomp.me's own backend uses.  apt installs the local files so their
# handful of Ubuntu-native dependencies resolve from the archive (the lists
# removed by the layer above are refreshed first).
RUN apt-get update \
    && mkdir -p /tmp/debs \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/dosemu2.deb \
        "https://launchpadlibrarian.net/880873282/dosemu2_2.0~pre9-10377-b683aeb53+202610131505~ubuntu24.04.1_amd64.deb" \
    && echo "aebb1f5b3eba515e0b2d49f897bbf2b225a2f9a4179c79cb2d814ef569d1ea5b  /tmp/debs/dosemu2.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/fdpp.deb \
        "https://launchpadlibrarian.net/860512428/fdpp_1.10-10002-1671-9282d8c+202605091902~ubuntu24.04.1_amd64.deb" \
    && echo "e1b2c238ef79c97ac588dfeec54cc8598890cd97e2e344dc4627258948d09d8d  /tmp/debs/fdpp.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libfdldr35.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/f/fdpp/libfdldr35_1.11-10003-1716-2f10d8a+202610122230~ubuntu24.04.1_amd64.deb" \
    && echo "2521bd466c5e0b5ae0a2d2ca855f7bdc4f60b814677231daf06f559c3a646c3a  /tmp/debs/libfdldr35.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libfdpp35.deb \
        "https://ppa.launchpadcontent.net/dosemu2/ppa/ubuntu/pool/main/f/fdpp/libfdpp35_1.11-10003-1716-2f10d8a+202610122230~ubuntu24.04.1_amd64.deb" \
    && echo "7299e263d0b5213e2bd5bf7f63389e9d7cd4901fef1483062a9361b16f173991  /tmp/debs/libfdpp35.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/comcom64.deb \
        "https://launchpadlibrarian.net/879631907/comcom64_0.5-0~202610040914+202610052207~ubuntu24.04.1_amd64.deb" \
    && echo "88deb90bc01279da57da12d131ff1a8fa7c9d4e2779c54aba8c624d085633357  /tmp/debs/comcom64.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/comcom32.deb \
        "https://launchpadlibrarian.net/879631904/comcom32_0.5-0~202610040914+202610052207~ubuntu24.04.1_all.deb" \
    && echo "f7b6ef20b573be739d81abc6ab282663f610755c4be4197d62c46bce8f17a873  /tmp/debs/comcom32.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/dj64.deb \
        "https://launchpadlibrarian.net/879631484/dj64_0.5-0~202610031149+202610052030~ubuntu24.04.1_amd64.deb" \
    && echo "a59151ebc5c6201544f9870095397e417dbac7b8f4fdef522fa6fda684c77476  /tmp/debs/dj64.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/djstub.deb \
        "https://launchpadlibrarian.net/878048879/djstub_0.9-0~202609240014+202609240117~ubuntu24.04.1_all.deb" \
    && echo "207f8a28e7be896f256c1519a69269ae1dfcbc9667bf2eecbbf976e88e122033  /tmp/debs/djstub.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libdjstub64-0.deb \
        "https://launchpadlibrarian.net/878032061/libdjstub64-0_0.5-0~202609232118~ubuntu24.04.1_amd64.deb" \
    && echo "62ccf36ab4ce966f7917772eff3d66d5c4ca5d9702b4c4bf85fc7e6987c29217  /tmp/debs/libdjstub64-0.deb" | sha256sum -c - \
    && curl -fsSL --retry 3 --retry-all-errors -o /tmp/debs/libdjdev64-0.deb \
        "https://launchpadlibrarian.net/878032060/libdjdev64-0_0.5-0~202609232118~ubuntu24.04.1_amd64.deb" \
    && echo "0b286a3f2c7639a2b5bcaf4641d5a8cf06e81c4998f1f809f2ace44021de5756  /tmp/debs/libdjdev64-0.deb" | sha256sum -c - \
    && apt-get install -y --no-install-recommends /tmp/debs/dosemu2.deb /tmp/debs/fdpp.deb \
        /tmp/debs/libfdldr35.deb /tmp/debs/libfdpp35.deb /tmp/debs/comcom64.deb \
        /tmp/debs/comcom32.deb /tmp/debs/dj64.deb /tmp/debs/djstub.deb \
        /tmp/debs/libdjstub64-0.deb /tmp/debs/libdjdev64-0.deb \
    && rm -rf /tmp/debs /var/lib/apt/lists/* \
    && dpkg -s dosemu2 dj64 fdpp > /dev/null \
    && /usr/libexec/dosemu2/dosemu2.bin --version
