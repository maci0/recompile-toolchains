# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: z88dk-2.4-sccz80

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew z88dk-2.4-sccz80" \
      org.opencontainers.image.description="z88dk-2.4-sccz80 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential bison flex libxml2-dev zlib1g-dev m4 libgmp-dev libboost-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV ZCCCFG=/opt/z88dk/lib/config \
    PATH=/opt/z88dk/bin:${PATH}

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.gz \
        "https://github.com/z88dk/z88dk/releases/download/v2.4/z88dk-src-2.4.tgz" \
    && echo "96a57a01d44ff1d65d84e38b04aebb0a4e10eccb4845cb71f5a26f10abe7c5ac  /tmp/toolchain.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/z88dk \
    && tar xzf /tmp/toolchain.tar.gz --no-same-owner --strip-components=1 -C /opt/z88dk \
    && cd /opt/z88dk && ./build.sh -l -z \
    && rm /tmp/toolchain.tar.gz \
    && test -x /opt/z88dk/bin/zcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
