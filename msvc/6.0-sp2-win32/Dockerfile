# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp2

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp2 (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp2 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp2.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc600_sp2/tar.gz/79157a87dec5e5ff014178f817f27a70098fd862" \
    && echo "8687378f815a857eeb84dd80db655aa1feac3e01c2774d97055ed92564d210eb  /tmp/msvc600_sp2.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp2 \
    && tar xzf /tmp/msvc600_sp2.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc6.0-sp2 \
    && rm /tmp/msvc600_sp2.tar.gz \
    && ls /opt/msvc6.0-sp2/VC98/bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
