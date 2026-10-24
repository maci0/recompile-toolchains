# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: llvm-mos-23.3.0-c64

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew llvm-mos-23.3.0-c64" \
      org.opencontainers.image.description="llvm-mos-23.3.0-c64 pinned compiler toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.xz \
        "https://github.com/llvm-mos/llvm-mos-sdk/releases/download/v23.3.0/llvm-mos-linux.tar.xz" \
    && echo "9f694497bc93a7c876d8c62325c7d74e7860346d80fbcd0555e19ba6856658c8  /tmp/toolchain.tar.xz" | sha256sum -c -

RUN mkdir -p /opt/llvm-mos \
    && tar xJf /tmp/toolchain.tar.xz --no-same-owner --strip-components=1 -C /opt/llvm-mos \
    && rm /tmp/toolchain.tar.xz \
    && test -x /opt/llvm-mos/bin/mos-c64-clang

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
