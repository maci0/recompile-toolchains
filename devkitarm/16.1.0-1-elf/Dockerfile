# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: devkitarm-16.1.0-1

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew devkitARM GCC 16.1.0-1" \
      org.opencontainers.image.description="devkitARM GCC 16.1.0-1 native Linux cross compiler"

RUN apt-get update \
    && apt-get install -y --no-install-recommends zstd libmpc3 libmpfr6 libgmp10 zlib1g libzstd1 python3 \
    && rm -rf /var/lib/apt/lists/*

ENV DEVKITPRO=/opt/devkitpro \
    DEVKITARM=/opt/devkitpro/devkitARM

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/linux/x86_64/devkitarm-gcc-16.1.0-1-x86_64.pkg.tar.zst" /tmp/part0.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "289be1a7a42321e02d8dad037acfdfbbe73cfe283b685b4d3860a2e946ea92d0  /tmp/part0.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/linux/x86_64/devkitarm-binutils-2.46.0-1-x86_64.pkg.tar.zst" /tmp/part1.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "fbca692c5b30008bef6b54c6b6cb48b6a03a656d7cc07beafa4dc7fdaa5838cf  /tmp/part1.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkitarm-newlib-4.6.0.20260123-5-any.pkg.tar.zst" /tmp/part2.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "d314c644c143bd5b104bd82cdc27602f6449cf907cb9c37ccfb8c0707182f89d  /tmp/part2.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkitarm-rules-1.6.0-4-any.pkg.tar.zst" /tmp/part3.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "35023b2b5f07a2dcfb600063854c712206341fb5df3ffbaf8ff825d3cbc15fcc  /tmp/part3.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkitarm-crtls-1.2.6-1-any.pkg.tar.zst" /tmp/part4.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "65faf10f62c219a1a8a3a182b0c4c56da7992599035ea32b3d79e39e79f964bb  /tmp/part4.pkg.tar.zst" | sha256sum -c -

RUN mkdir -p /opt/devkitpro \
    && for p in /tmp/part*.pkg.tar.zst; do tar --zstd --no-same-owner -xf "$p" -C / --exclude=.MTREE --exclude=.BUILDINFO --exclude=.PKGINFO; done \
    && rm /tmp/part*.pkg.tar.zst \
    && test -x /opt/devkitpro/devkitARM/bin/arm-none-eabi-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
