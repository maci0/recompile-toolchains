# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600/tar.gz/34d4fc4004e880b8d5c44ae5babd7229eeaad993" \
    && echo "636767208193f896f9d49bd884bbe0d00f184c53b83a985c3bf8828f4ca01faa  /tmp/msvc600.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0 \
    && tar xzf /tmp/msvc600.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc6.0 \
    && rm /tmp/msvc600.tar.gz \
    && ls /opt/msvc6.0/VC98/Bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
