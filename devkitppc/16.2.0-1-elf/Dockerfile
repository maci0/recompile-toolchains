# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: devkitppc-16.2.0-1

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew devkitPPC GCC 16.2.0-1" \
      org.opencontainers.image.description="devkitPPC GCC 16.2.0-1 native Linux cross compiler"

RUN apt-get update \
    && apt-get install -y --no-install-recommends zstd libmpc3 libmpfr6 libgmp10 zlib1g libzstd1 python3 \
    && rm -rf /var/lib/apt/lists/*

ENV DEVKITPRO=/opt/devkitpro \
    DEVKITPPC=/opt/devkitpro/devkitPPC

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/linux/x86_64/devkitppc-gcc-16.2.0-1-x86_64.pkg.tar.zst" /tmp/part0.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "d27ec75b8e309608495712f95357b68792cad9868aa2abe53e957c5538722549  /tmp/part0.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/linux/x86_64/devkitppc-binutils-2.47-2-x86_64.pkg.tar.zst" /tmp/part1.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "b2f7096da00e56be9752ada2453c8d4b538dbb0bad2315fb4a1416f01187ab77  /tmp/part1.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkitppc-newlib-4.6.0.20260123-4-any.pkg.tar.zst" /tmp/part2.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "2c5277c6b07a5558c9fd8e631d958c6d7784860aa55f5c320cb51371bc07e21b  /tmp/part2.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkitppc-rules-1.2.1-1-any.pkg.tar.zst" /tmp/part3.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "0c3394da451c9dfb3b428d9d61b044eb1eafb947b2b5090ff88525f55c785278  /tmp/part3.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkitppc-crtls-2.1.0-1-any.pkg.tar.zst" /tmp/part4.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "5a1144d515579eee73bb936ca36a8ea739b00d8cf32af3fa4dda21a039881bcd  /tmp/part4.pkg.tar.zst" | sha256sum -c -

RUN mkdir -p /opt/devkitpro \
    && for p in /tmp/part*.pkg.tar.zst; do tar --zstd --no-same-owner -xf "$p" -C / --exclude=.MTREE --exclude=.BUILDINFO --exclude=.PKGINFO; done \
    && rm /tmp/part*.pkg.tar.zst \
    && test -x /opt/devkitpro/devkitPPC/bin/powerpc-eabi-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
