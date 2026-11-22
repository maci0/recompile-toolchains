# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-5.0-sp1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 5.0-sp1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 5.0-sp1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc500sp1.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc500sp1/tar.gz/401174749393c9991a6b91425a795e04e8bdeedb" \
    && echo "3bffbbb3b4569b7f5ca5072651caf97f2d89e837684931522e9d224125b104f3  /tmp/msvc500sp1.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc5.0-sp1 \
    && tar xzf /tmp/msvc500sp1.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc5.0-sp1 \
    && rm /tmp/msvc500sp1.tar.gz \
    && ls /opt/msvc5.0-sp1/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
