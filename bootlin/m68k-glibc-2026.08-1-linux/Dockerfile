# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: bootlin-m68k-glibc-2026.08-1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew bootlin-m68k-glibc-2026.08-1" \
      org.opencontainers.image.description="bootlin-m68k-glibc-2026.08-1 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends file python3 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.xz \
        "https://toolchains.bootlin.com/downloads/releases/toolchains/m68k-68xxx/tarballs/m68k-68xxx--glibc--stable-2026.08-1.tar.xz" \
    && echo "c92f32f48cdbaf5fcc80723ef957cb062fd1dbaa6189cc93834a02d59d7082e9  /tmp/toolchain.tar.xz" | sha256sum -c -

RUN mkdir -p /opt/bootlin-m68k \
    && tar xJf /tmp/toolchain.tar.xz --no-same-owner --strip-components=1 -C /opt/bootlin-m68k \
    && cd /opt/bootlin-m68k && ./relocate-sdk.sh \
    && rm /tmp/toolchain.tar.xz \
    && test -x /opt/bootlin-m68k/bin/m68k-buildroot-linux-gnu-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
