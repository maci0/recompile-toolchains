# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: borland-5.5

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Borland C++ 5.5 (win32, wine)" \
      org.opencontainers.image.description="Borland C++ 5.5 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/bcc55.tar.gz \
        "https://codeload.github.com/archaic-toolchains/borlandc55/tar.gz/fcdcaf5bc41fc166ef632329c72baf6d487b50d2" \
    && echo "647c93fb2513255d7447e7d8c8ba1ac1eddc821de2777a58fa145b71ec5891d6  /tmp/bcc55.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/bcc55 \
    && tar xzf /tmp/bcc55.tar.gz --no-same-owner --strip-components=1 -C /opt/bcc55 \
    && rm /tmp/bcc55.tar.gz \
    && ls /opt/bcc55/Bin/bcc32.exe

COPY bcc-wrapper.sh /usr/local/bin/bcc
RUN chmod +x /usr/local/bin/bcc

ENTRYPOINT ["/usr/local/bin/bcc"]

USER rebrew
