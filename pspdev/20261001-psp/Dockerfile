# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: pspdev-20261001

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew pspdev-20261001" \
      org.opencontainers.image.description="pspdev-20261001 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmpc3 libmpfr6 libgmp10 zlib1g libzstd1 \
    && rm -rf /var/lib/apt/lists/*

ENV PSPDEV=/opt/pspdev

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.gz \
        "https://github.com/pspdev/pspdev/releases/download/v20261001/pspdev-debian-latest.tar.gz" \
    && echo "39b20efc7c8492cdbd9929178f45afc801dabb0967b7c882573520f22536920c  /tmp/toolchain.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/pspdev \
    && tar xzf /tmp/toolchain.tar.gz --no-same-owner --strip-components=1 -C /opt/pspdev \
    && rm /tmp/toolchain.tar.gz \
    && test -x /opt/pspdev/bin/psp-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
