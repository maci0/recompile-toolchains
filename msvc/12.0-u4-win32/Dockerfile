# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-12.0-u4

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew msvc-12.0-u4" \
      org.opencontainers.image.description="msvc-12.0-u4 pinned compiler toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends unzip \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/toolchain.zip \
        "https://github.com/heinermann/compilers/releases/download/msvc12/msvc12.zip" \
    && echo "2adc1d97b342b6d14113b43321cc965c2afec5b9ff575c04a70c6d5c6e119f43  /tmp/toolchain.zip" | sha256sum -c -

RUN mkdir -p /opt/msvc12.0-u4 \
    && unzip -q /tmp/toolchain.zip -d /opt/msvc12.0-u4 \
    && cp -a /opt/msvc12.0-u4/msvc12/redist/x86/Microsoft.VC120.CRT/msvcr120.dll /opt/msvc12.0-u4/msvc12/redist/x86/Microsoft.VC120.CRT/msvcp120.dll /opt/msvc12.0-u4/msvc12/bin/ \
    && chmod +x /opt/msvc12.0-u4/msvc12/bin/*.exe \
    && rm /tmp/toolchain.zip \
    && test -x /opt/msvc12.0-u4/msvc12/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
