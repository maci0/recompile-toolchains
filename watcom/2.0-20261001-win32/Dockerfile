# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: watcom-2.0-20261001-win32

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Open Watcom 2.0 (win32, native) 2026-10-01" \
      org.opencontainers.image.description="Open Watcom 2.0 (win32, native) toolchain image 2026-10-01"

ENV WATCOM=/opt/watcom \
    INCLUDE=/opt/watcom/h \
    PATH=/opt/watcom/binl:$PATH

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ow.tar.xz \
        "https://github.com/open-watcom/open-watcom-v2/releases/download/2026-10-01-Build/ow-snapshot.tar.xz" \
    && echo "e6aa1b1e40ac8bbf97658d2c70fff8a4242d6ca4a1c60806f2baa5317083d4fe  /tmp/ow.tar.xz" | sha256sum -c -

RUN mkdir -p /opt/watcom \
    && tar xJf /tmp/ow.tar.xz --no-same-owner --strip-components=1 -C /opt/watcom \
    && rm /tmp/ow.tar.xz \
    && ls /opt/watcom/binl/wcc386

COPY wcc386-wrapper.sh /usr/local/bin/wcc386
RUN chmod +x /usr/local/bin/wcc386

ENTRYPOINT ["/usr/local/bin/wcc386"]

USER rebrew
