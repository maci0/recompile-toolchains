# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-5.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 5.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 5.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc500.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc500/tar.gz/8abf95ce980161ad87b0b02402269cce76988953" \
    && echo "4f3f44520c8fa53014200eb678beddd52ab2745de8365c92bd3cb16c677809a1  /tmp/msvc500.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc5.0 \
    && tar xzf /tmp/msvc500.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc5.0 \
    && rm /tmp/msvc500.tar.gz \
    && ls /opt/msvc5.0/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
