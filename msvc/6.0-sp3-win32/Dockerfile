# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp3

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp3 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp3 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc6.0-sp3.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc600_sp3/tar.gz/ff28b93857087f787492eef603e243fcccb0b368" \
    && echo "d59b3460cc3ec125ce4096a8823927f6de68c9078033d26c33f57235d3bf85d1  /tmp/msvc6.0-sp3.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp3 \
    && tar xzf /tmp/msvc6.0-sp3.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc6.0-sp3 \
    && rm /tmp/msvc6.0-sp3.tar.gz \
    && ls /opt/msvc6.0-sp3/VC98/Bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
