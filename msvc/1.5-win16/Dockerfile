# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-1.5

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 1.5 (win16, DOSBox)" \
      org.opencontainers.image.description="MSVC 1.5 (win16, DOSBox) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc15.tar.gz \
        "https://codeload.github.com/archaic-toolchains/msvc15/tar.gz/3649e12977c169bd60662362400677f28a716ef1" \
    && echo "46db20c355a1b49869de719092d9237cee939fdf0e481e451f4f63835923f7e7  /tmp/msvc15.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc15 \
    && tar xzf /tmp/msvc15.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc15 \
    && rm /tmp/msvc15.tar.gz \
    && ls /opt/msvc15/BIN/CL.EXE

COPY cl15-wrapper.sh /usr/local/bin/cl15
RUN chmod +x /usr/local/bin/cl15

ENTRYPOINT ["/usr/local/bin/cl15"]

USER rebrew
