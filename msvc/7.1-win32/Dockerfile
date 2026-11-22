# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-7.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 7.1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 7.1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc710.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc710/tar.gz/2932d76fe417b0bc49010b26d4be2e5b743cc4be" \
    && echo "487051441db67665baede52f82b06205e927d3530ca0e0a9401bd57802e21adf  /tmp/msvc710.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc7.1 \
    && tar xzf /tmp/msvc710.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc7.1 \
    && rm /tmp/msvc710.tar.gz \
    && ls /opt/msvc7.1/Vc7/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
