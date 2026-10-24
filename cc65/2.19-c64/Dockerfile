# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: cc65-2.19-c64

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew cc65-2.19-c64" \
      org.opencontainers.image.description="cc65-2.19-c64 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV CC65_HOME=/opt/cc65

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.gz \
        "https://codeload.github.com/cc65/cc65/tar.gz/refs/tags/V2.19" \
    && echo "157b8051aed7f534e5093471e734e7a95e509c577324099c3c81324ed9d0de77  /tmp/toolchain.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/cc65 \
    && tar xzf /tmp/toolchain.tar.gz --no-same-owner --strip-components=1 -C /opt/cc65 \
    && cd /opt/cc65 && make -j8 bin \
    && rm /tmp/toolchain.tar.gz \
    && test -x /opt/cc65/bin/cl65

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
