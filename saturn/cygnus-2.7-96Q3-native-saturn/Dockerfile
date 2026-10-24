# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: saturn-cygnus-2.7-96Q3-native

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Saturn Cygnus 2.7-96Q3 (native)" \
      org.opencontainers.image.description="Cygnus 2.7-96Q3 (SH-2, Sega Saturn, native Linux i386 reproduction) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp binutils-sh-elf \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/cc1.tar.gz \
        "https://github.com/sozud/saturn-compiler-repro/releases/download/v1.0.0/cc1-native.tar.gz" \
    && echo "3f215db5c6c6040461b82b85f4d7564da59da3064d7c13b872c16ad9f5731497  /tmp/cc1.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/saturn-cygnus-native \
    && tar xzf /tmp/cc1.tar.gz -C /opt/saturn-cygnus-native \
    && rm /tmp/cc1.tar.gz \
    && chmod +x /opt/saturn-cygnus-native/cc1-native \
    && test -x /opt/saturn-cygnus-native/cc1-native

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
