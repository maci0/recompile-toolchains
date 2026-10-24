# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ps2dev-2.0.0-ee

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew ps2dev-2.0.0-ee" \
      org.opencontainers.image.description="ps2dev-2.0.0-ee pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmpc3 libmpfr6 libgmp10 zlib1g libzstd1 \
    && rm -rf /var/lib/apt/lists/*

ENV PS2DEV=/opt/ps2dev

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.tar.gz \
        "https://github.com/ps2dev/ps2dev/releases/download/v2.0.0/ps2dev-ubuntu-latest.tar.gz" \
    && echo "c8e5dedccf62084d476894e88cd0451b57f1ed288e741eb3c1263010aaffc028  /tmp/toolchain.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/ps2dev \
    && tar xzf /tmp/toolchain.tar.gz --no-same-owner --strip-components=1 -C /opt/ps2dev \
    && rm /tmp/toolchain.tar.gz \
    && test -x /opt/ps2dev/ee/bin/mips64r5900el-ps2-elf-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
