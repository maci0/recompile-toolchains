# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: sdcc-4.6.0-sm83

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew sdcc-4.6.0-sm83" \
      org.opencontainers.image.description="sdcc-4.6.0-sm83 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends bzip2 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.bz2 \
        "https://downloads.sourceforge.net/project/sdcc/sdcc-linux-amd64/4.6.0/sdcc-4.6.0-amd64-unknown-linux2.5.tar.bz2" \
    && echo "f6b929c62ed3082a26087885e0f1f9bf41878602ef1f57e40b11b4a01bf4f366  /tmp/toolchain.tar.bz2" | sha256sum -c -

RUN mkdir -p /opt/sdcc-4.6.0 \
    && tar xjf /tmp/toolchain.tar.bz2 --no-same-owner --strip-components=1 -C /opt/sdcc-4.6.0 \
    && rm /tmp/toolchain.tar.bz2 \
    && test -x /opt/sdcc-4.6.0/bin/sdcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
