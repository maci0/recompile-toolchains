# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: devkita64-16.1.0-1

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew devkitA64 GCC 16.1.0-1" \
      org.opencontainers.image.description="devkitA64 GCC 16.1.0-1 native Linux cross compiler"

RUN apt-get update \
    && apt-get install -y --no-install-recommends zstd libmpc3 libmpfr6 libgmp10 zlib1g libzstd1 python3 \
    && rm -rf /var/lib/apt/lists/*

ENV DEVKITPRO=/opt/devkitpro \
    DEVKITA64=/opt/devkitpro/devkitA64

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/linux/x86_64/devkita64-gcc-16.1.0-1-x86_64.pkg.tar.zst" /tmp/part0.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "8192b899f0a5fcfe10d11fa63a631b45310c0c8f0b98d88c7c283c16e9d6b0fa  /tmp/part0.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/linux/x86_64/devkita64-binutils-2.46.0-1-x86_64.pkg.tar.zst" /tmp/part1.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "0d61ad4946eb1080c6e645c41f0cfaac0a2eba5fec88426fef8f03363e933b5a  /tmp/part1.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkita64-newlib-4.6.0.20260123-4-any.pkg.tar.zst" /tmp/part2.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "fc97ba1009a94b68f8714c3cc548ef697ca82687b72fe0c05a7ca3df81beb53e  /tmp/part2.pkg.tar.zst" | sha256sum -c -

RUN python3 -c 'import sys,shutil,urllib.request; r=urllib.request.urlopen(urllib.request.Request(sys.argv[1],headers={"User-Agent":sys.argv[3]}),timeout=120); shutil.copyfileobj(r,open(sys.argv[2],"wb"))' "https://downloads.devkitpro.org/packages/devkita64-rules-1.1.1-1-any.pkg.tar.zst" /tmp/part3.pkg.tar.zst 'dkp-pacman/6.0.2' \
    && echo "2649cf7827243447070073acc2aa2fee152a0592fc30e827ceed803c565a1ede  /tmp/part3.pkg.tar.zst" | sha256sum -c -

RUN mkdir -p /opt/devkitpro \
    && for p in /tmp/part*.pkg.tar.zst; do tar --zstd --no-same-owner -xf "$p" -C / --exclude=.MTREE --exclude=.BUILDINFO --exclude=.PKGINFO; done \
    && rm /tmp/part*.pkg.tar.zst \
    && test -x /opt/devkitpro/devkitA64/bin/aarch64-none-elf-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
