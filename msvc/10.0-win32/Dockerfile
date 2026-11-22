# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-10.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 10.0 (win32, wine)" \
      org.opencontainers.image.description="MSVC 10.0 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc1000.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc1000/tar.gz/f8977e2cacbe6cab4f9e73eb2c05695a88519bfe" \
    && echo "923684491a7e3fbdc326a0681c7d8d4ecfb9a9d217638038ac2859c702c45b01  /tmp/msvc1000.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc10.0 \
    && tar xzf /tmp/msvc1000.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc10.0 \
    && rm /tmp/msvc1000.tar.gz \
    && ls /opt/msvc10.0/VC/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
