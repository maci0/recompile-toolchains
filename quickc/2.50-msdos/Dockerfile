# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: quickc-2.50

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Microsoft QuickC 2.50" \
      org.opencontainers.image.description="Microsoft QuickC 2.50 16-bit DOS compiler"

RUN apt-get update \
    && apt-get install -y --no-install-recommends p7zip-full gcc libmspack-dev libc6-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/quickc.7z \
        "https://dl-alt1.winworldpc.com/Microsoft%20QuickC%202.50%20(1990)%20(5.25-360k).7z" \
    && echo "922305575ba425158a7db1a49eceecd00481dc5a092db02eda3582d68447198a  /tmp/quickc.7z" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/mspack.tar.gz \
        "https://codeload.github.com/kyz/libmspack/tar.gz/55d501976171397ccd5d5a7a1ca7da065b1d9a06" \
    && echo "6268bcb52c1a54052766641bd4a64fa953bf1cd78d2535965d67d349dbaa49a0  /tmp/mspack.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/quickc2.50 /opt/quickc-media /tmp/quickc-disks /tmp/mspack \
    && tar xzf /tmp/mspack.tar.gz --no-same-owner --strip-components=1 -C /tmp/mspack \
    && gcc -I/tmp/mspack/libmspack/test /tmp/mspack/libmspack/examples/msexpand.c -lmspack -o /tmp/msexpand \
    && 7z x -y /tmp/quickc.7z -o/opt/quickc-media >/dev/null \
    && for disk in /opt/quickc-media/*/*.img; do 7z x -y "$disk" -o/tmp/quickc-disks >/dev/null; done \
    && cd /tmp/quickc-disks && find . -type f -name '*$' -exec sh -c 'for f do /tmp/msexpand "$f" "${f%?}_" || exit; done' sh {} + \
    && cp -a /tmp/quickc-disks/. /opt/quickc2.50/ && find /opt/quickc2.50 -type f -name '*_' -exec sh -c 'for f do case "$f" in *.EX_) mv "$f" "${f%?}E";; *.HL_) mv "$f" "${f%?}P";; *.ER_) mv "$f" "${f%?}R";; *.H_) mv "$f" "${f%?}";; *.C_) mv "$f" "${f%?}";; *.LI_) mv "$f" "${f%?}B";; esac; done' sh {} + \
    && rm -rf /tmp/quickc.7z /tmp/quickc-disks /tmp/mspack /tmp/mspack.tar.gz /tmp/msexpand \
    && test -f /opt/quickc2.50/QCL.EXE

COPY quickc-wrapper.sh /usr/local/bin/quickc
RUN chmod +x /usr/local/bin/quickc

ENTRYPOINT ["/usr/local/bin/quickc"]

USER rebrew
