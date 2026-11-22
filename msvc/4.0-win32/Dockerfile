# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-4.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 4.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 4.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc400.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc400/tar.gz/17122292d394baa5a08fea6c899cdf48b67efb15" \
    && echo "158af9a3303f90ab565009a81629dffe0bfddd1da3d23b617bc2ae5f6e13d2e1  /tmp/msvc400.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc4.0 \
    && tar xzf /tmp/msvc400.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc4.0 \
    && rm /tmp/msvc400.tar.gz \
    && ls /opt/msvc4.0/BIN/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
