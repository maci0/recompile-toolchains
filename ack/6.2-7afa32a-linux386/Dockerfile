# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ack-6.2-7afa32a-linux386

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew ack-6.2-7afa32a-linux386" \
      org.opencontainers.image.description="ack-6.2-7afa32a-linux386 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential flex bison lua5.3 lua-posix python3 ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.gz \
        "https://codeload.github.com/davidgiven/ack/tar.gz/7afa32a0a0f13e865fa2e8104e442689005cd627" \
    && echo "142ad8834ed5409dda0fed8e3ddb1e50f72c772858ef1e2cc9570f13e9cc6ad3  /tmp/toolchain.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ack \
    && tar xzf /tmp/toolchain.tar.gz --no-same-owner --strip-components=1 -C /opt/ack \
    && cd /opt/ack && sed -i 's/^PLATS = all$/PLATS = linux386/' Makefile && make -j8 PREFIX=/opt/ack && make PREFIX=/opt/ack install \
    && rm /tmp/toolchain.tar.gz \
    && test -x /opt/ack/bin/ack

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
