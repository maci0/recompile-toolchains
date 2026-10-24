# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: gbdk-4.5.0-sm83

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew gbdk-4.5.0-sm83" \
      org.opencontainers.image.description="gbdk-4.5.0-sm83 pinned compiler toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.gz \
        "https://github.com/gbdk-2020/gbdk-2020/releases/download/4.5.0/gbdk-linux64.tar.gz" \
    && echo "d7857a5f6d135ee4c249043ca26aad9f2ec8ab5d4106d97720d404114f42605c  /tmp/toolchain.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/gbdk \
    && tar xzf /tmp/toolchain.tar.gz --no-same-owner --strip-components=1 -C /opt/gbdk \
    && rm /tmp/toolchain.tar.gz \
    && test -x /opt/gbdk/bin/lcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
