# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: saturn-cygnus-2.7-96Q3-daze-0.3.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Saturn Cygnus 2.7-96Q3 (Daze 0.3.0)" \
      org.opencontainers.image.description="Cygnus 2.7-96Q3 (SH-2, Sega Saturn, DOS binaries under Daze 0.3.0 (Unicorn)) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils-sh-elf unzip cpp dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/saturn-cygnus /tmp/tools && curl -fsSL --retry 3 --retry-all-errors -o /tmp/tools/saturn.zip \
        "https://github.com/sozud/saturn-compilers/archive/af27f4aa6566c1b0fa5332b488e63d6ffd28bd48.zip" \
    && echo "f5460e3ea653a24fb011a94f2ce2c54b277877e60859ffc906b07dbbe6406595  /tmp/tools/saturn.zip" | sha256sum -c -

RUN mkdir -p /usr/local/bin && curl -fsSL --retry 3 --retry-all-errors -o /usr/local/bin/daze \
        "https://github.com/mkst/daze/releases/download/0.3.0/daze" \
    && echo "4b6f55e5813a0752eedd1462ef4e3877a7ab0d0a244d806f3fab495bcee2894c  /usr/local/bin/daze" | sha256sum -c -

RUN mkdir -p /opt/daze-notices && curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/BUILD-INFO.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/BUILD-INFO.txt" \
    && echo "34147e157731b3ba91ba492641dabe538567978349adfe4f1ce194355e62936e  /opt/daze-notices/BUILD-INFO.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/gcc-copyright \
        "https://github.com/mkst/daze/releases/download/0.3.0/gcc-copyright" \
    && echo "08c6f3dee4c19aa1e57eb7d4ad45829b2e99656313bd07fa0922e2553f500be5  /opt/daze-notices/gcc-copyright" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/glibc-copyright \
        "https://github.com/mkst/daze/releases/download/0.3.0/glibc-copyright" \
    && echo "d3c95b56fa33e28b57860580f0baf4e4f4de2a268a2b80f1d031a5191bade265  /opt/daze-notices/glibc-copyright" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/GPL-2.0.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/GPL-2.0.txt" \
    && echo "6f04ae8364d0079a192b14635f4b1da294ce18724c034c39a6a41d1b09df6100  /opt/daze-notices/GPL-2.0.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/GPL-3.0.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/GPL-3.0.txt" \
    && echo "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986  /opt/daze-notices/GPL-3.0.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/LGPL-2.1.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/LGPL-2.1.txt" \
    && echo "dc626520dcd53a22f727af3ee42c770e56c97a64fe3adb063799d8ab032fe551  /opt/daze-notices/LGPL-2.1.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/LICENSE.md \
        "https://github.com/mkst/daze/releases/download/0.3.0/LICENSE.md" \
    && echo "62ff9cf06bc8ce267b99735069eb307bc72879af5dbddda5c826344696c54171  /opt/daze-notices/LICENSE.md" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/THIRD_PARTY_NOTICES.md \
        "https://github.com/mkst/daze/releases/download/0.3.0/THIRD_PARTY_NOTICES.md" \
    && echo "bbe2d9f9528a2a6f3659921717104bbda950b5afa24272339adc3537b858be30  /opt/daze-notices/THIRD_PARTY_NOTICES.md" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/unicorn-glib.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/unicorn-glib.txt" \
    && echo "d245807f90032872d1438d741ed21e2490e1175dc8aa3afa5ddb6c8e529b58e5  /opt/daze-notices/unicorn-glib.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/unicorn-LGPL-2.0.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/unicorn-LGPL-2.0.txt" \
    && echo "b7993225104d90ddd8024fd838faf300bea5e83d91203eab98e29512acebd69c  /opt/daze-notices/unicorn-LGPL-2.0.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/unicorn-qemu.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/unicorn-qemu.txt" \
    && echo "139c64b7a9ae62858ff969aae622ecfcf4f1519655bd92d2e70a1a2fb615690e  /opt/daze-notices/unicorn-qemu.txt" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && unzip -q /tmp/tools/saturn.zip -d /tmp/tools \
    && cp -r /tmp/tools/saturn-compilers-af27f4aa6566c1b0fa5332b488e63d6ffd28bd48/cygnus-2.7-96Q3-bin/. /opt/saturn-cygnus/ \
    && rm -rf /tmp/tools \
    && chmod +x /opt/saturn-cygnus/*.EXE \
    && ls /opt/saturn-cygnus/OBJCOPY.EXE \
    && chmod +x /usr/local/bin/daze

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
