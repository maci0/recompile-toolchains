# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: saturn-cygnus-2.7-96Q3-native64

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Saturn Cygnus 2.7-96Q3 (native64)" \
      org.opencontainers.image.description="Cygnus SH-2 native Linux x86-64 reproduction"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp binutils-sh-elf \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/cc1.tar.gz \
        "https://github.com/sozud/saturn-compiler-repro/releases/download/v1.0.0/cc1-native64.tar.gz" \
    && echo "67f8072355ea2860decb48df87001badbad180008044be1181c1178b65163320  /tmp/cc1.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/saturn-cygnus-native64 \
    && tar xzf /tmp/cc1.tar.gz --no-same-owner -C /opt/saturn-cygnus-native64 \
    && rm /tmp/cc1.tar.gz \
    && chmod +x /opt/saturn-cygnus-native64/cc1-native64 \
    && test -x /opt/saturn-cygnus-native64/cc1-native64

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
