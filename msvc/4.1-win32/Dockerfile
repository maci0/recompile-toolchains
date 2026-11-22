# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-4.1

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 4.1 (win32, wine)" \
      org.opencontainers.image.description="MSVC 4.1 (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc410.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc410/tar.gz/373f5e621ac8fb7b219873b37334ef1d0a2149e6" \
    && echo "72904772611a8cb23ea51fc2e670e58cf35d4e5d26c80d7a9c740ac73ef3636a  /tmp/msvc410.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc4.1 \
    && tar xzf /tmp/msvc410.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc4.1 \
    && rm /tmp/msvc410.tar.gz \
    && ls /opt/msvc4.1/bin/CL.EXE

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
