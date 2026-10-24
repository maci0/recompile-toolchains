# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mwcc-4.1-51213p1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MWCC 4.1-51213p1 (GameCube)" \
      org.opencontainers.image.description="MWCC 4.1-51213p1 (CodeWarrior GameCube, PE/x86_32) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/compilers.zip \
        "https://files.decomp.dev/compilers_20251118.zip" \
    && echo "69b0d4980a2eccea4ae6e70b486714b5190cb6c75e3bc7b8fb5878a8854d0d1c  /tmp/compilers.zip" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/mwcc-4.1-51213p1 \
    && unzip -q /tmp/compilers.zip 'GC/3.0a3p1/*' -d /tmp/x \
    && cp -a /tmp/x/GC/3.0a3p1/. /opt/mwcc-4.1-51213p1/ \
    && rm -rf /tmp/x /tmp/compilers.zip \
    && ls /opt/mwcc-4.1-51213p1/mwcceppc.exe

COPY mwcceppc-wrapper.sh /usr/local/bin/mwcceppc
RUN chmod +x /usr/local/bin/mwcceppc

ENTRYPOINT ["/usr/local/bin/mwcceppc"]

USER rebrew
