# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Turbo C 2.0 (win16, DOSBox)" \
      org.opencontainers.image.description="Turbo C 2.0 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/tc20.tar.gz \
        "https://codeload.github.com/archaic-toolchains/tc20/tar.gz/64b5ef09a7c18b65c38902a217bcfec67c4b113b" \
    && echo "1abebda4eab015dba7b2b816d60d4d6d5d74fd9391128bfe627d8d162f166a33  /tmp/tc20.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/tc20 \
    && tar xzf /tmp/tc20.tar.gz --no-same-owner --strip-components=1 -C /opt/tc20 \
    && rm /tmp/tc20.tar.gz \
    && ls /opt/tc20/BIN/TCC.EXE

COPY tc20-run.sh /usr/local/bin/tcc
RUN chmod +x /usr/local/bin/tcc

ENTRYPOINT ["/usr/local/bin/tcc"]

USER rebrew
