# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-5.0-sp3

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 5.0-sp3 (win32, wine)" \
      org.opencontainers.image.description="MSVC 5.0-sp3 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc500sp3.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc500sp3/tar.gz/259a03f0bc863de5baf657ec064cb60cb20a2cdc" \
    && echo "6f4427b5c46b0ce648242e7b18f4d8b96c5500bae6b27cc68cb5d6a7c8a89347  /tmp/msvc500sp3.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc5.0-sp3 \
    && tar xzf /tmp/msvc500sp3.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc5.0-sp3 \
    && rm /tmp/msvc500sp3.tar.gz \
    && ls /opt/msvc5.0-sp3/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
