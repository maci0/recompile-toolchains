# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: djgpp-12.2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew djgpp-12.2.0" \
      org.opencontainers.image.description="djgpp-12.2.0 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends bzip2 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.bz2 \
        "https://github.com/andrewwutw/build-djgpp/releases/download/v3.4/djgpp-linux64-gcc1220.tar.bz2" \
    && echo "8464f17017d6ab1b2bb2df4ed82357b5bf692e6e2b7fee37e315638f3d505f00  /tmp/toolchain.tar.bz2" | sha256sum -c -

RUN mkdir -p /opt/djgpp-12.2.0 \
    && tar xjf /tmp/toolchain.tar.bz2 --no-same-owner --strip-components=1 -C /opt/djgpp-12.2.0 \
    && rm /tmp/toolchain.tar.bz2 \
    && test -x /opt/djgpp-12.2.0/bin/i586-pc-msdosdjgpp-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
