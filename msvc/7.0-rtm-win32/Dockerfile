# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-7.0-rtm

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 7.0-rtm (win32, wine)" \
      org.opencontainers.image.description="MSVC 7.0 RTM (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc700.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc700/tar.gz/97fe4cdeaeb0bb934591d4b05eb52c2e8ab3e34b" \
    && echo "e8de768278175a56ace7ef79648a4ac6136bfb074dd5ba991356b16c5d0bcf46  /tmp/msvc700.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc7.0-rtm \
    && tar xzf /tmp/msvc700.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc7.0-rtm \
    && rm /tmp/msvc700.tar.gz \
    && ls /opt/msvc7.0-rtm/Vc7/bin/cl.exe

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
