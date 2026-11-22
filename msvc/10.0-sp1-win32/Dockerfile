# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-10.0-sp1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 10.0-sp1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 10.0-sp1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc1000_sp1.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc1000_sp1/tar.gz/09a53c11f781ec9ab5e66772ba720b9d85e4c2a4" \
    && echo "4d256b37c4fea1327c554e19f9fda3078155a404699a5fb3f33a8a4804258bfb  /tmp/msvc1000_sp1.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc10.0-sp1 \
    && tar xzf /tmp/msvc1000_sp1.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc10.0-sp1 \
    && rm /tmp/msvc1000_sp1.tar.gz \
    && ls /opt/msvc10.0-sp1/VC/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
