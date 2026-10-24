# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: vbcc-0.9h-p2-amiga

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew VBCC 0.9h patch 2 for Amiga m68k" \
      org.opencontainers.image.description="Commit-pinned VBCC VASM VLINK build with retained original archives and Amiga m68k target"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential p7zip-full \
    && rm -rf /var/lib/apt/lists/*

ENV VBCC=/opt/vbcc \
    PATH=/opt/vbcc/bin:$PATH

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/vbcc.tar.gz \
        "https://codeload.github.com/erique/vbcc_vasm_vlink/tar.gz/647720b664c0599a4b5b28b3232987673615fe11" \
    && echo "d9b4d46c27af0a98d5a49c5f6c494a40f21811caf877113bad8fc97dbf5c4a0e  /tmp/vbcc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/vbcc /opt/vbcc-sources \
    && tar xzf /tmp/vbcc.tar.gz --no-same-owner --strip-components=1 -C /opt/vbcc-sources \
    && cd /opt/vbcc-sources && tar xzf vbcc.tar.gz --no-same-owner && tar xzf vasm.tar.gz --no-same-owner && tar xzf vlink.tar.gz --no-same-owner && tar xzf vbcc_unix_config.tar.gz --no-same-owner -C vbcc && 7z x -y vbcc_target_m68k-amigaos.lha vbcc_target_m68k-amigaos/targets >/dev/null && cp -a vbcc_target_m68k-amigaos/targets vbcc/ \
    && cd /opt/vbcc-sources/vbcc && mkdir -p bin && yes '' | make TARGET=m68k -j1 \
    && cd /opt/vbcc-sources/vasm && make CPU=m68k SYNTAX=mot -j4 \
    && cd /opt/vbcc-sources/vlink && make -j4 \
    && cp -a /opt/vbcc-sources/vbcc/bin /opt/vbcc-sources/vbcc/config /opt/vbcc-sources/vbcc/targets /opt/vbcc/ && cp /opt/vbcc-sources/vasm/vasmm68k_mot /opt/vbcc-sources/vlink/vlink /opt/vbcc/bin/ \
    && rm /tmp/vbcc.tar.gz \
    && test -x /opt/vbcc/bin/vc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
