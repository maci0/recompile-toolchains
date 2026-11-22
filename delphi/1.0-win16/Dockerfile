# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: delphi-1.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Delphi 1.0 (win16, DOSBox)" \
      org.opencontainers.image.description="Delphi 1.0 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/delphi10.tar.gz \
        "https://codeload.github.com/archaic-toolchains/delphi10/tar.gz/fd12406eeaa6b44099013c5a56d083919676967c" \
    && echo "5f47a18c64cc00e9b8d184fb7f9f223047f1e3dd00f346548be095e6f289f3db  /tmp/delphi10.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/delphi10/DELPHI \
    && tar xzf /tmp/delphi10.tar.gz --no-same-owner --strip-components=1 -C /opt/delphi10 \
    && rm /tmp/delphi10.tar.gz \
    && mv /opt/delphi10/delphi-lib /opt/delphi10/DELPHI/LIB \
    && ls /opt/delphi10/DCC.EXE

COPY dcc-wrapper.sh /usr/local/bin/dcc
RUN chmod +x /usr/local/bin/dcc

ENTRYPOINT ["/usr/local/bin/dcc"]

USER rebrew
