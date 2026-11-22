# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp5-pp

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0 SP5 + Processor Pack (win32, wine)" \
      org.opencontainers.image.description="MSVC 6.0-sp5 + VC6 Processor Pack (win32, wine) toolchain image"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp5_vcpp.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600_sp5_vcpp/tar.gz/762e9382c751613c341daa766f0e22cdeb07152c" \
    && echo "f07b22eef2382fbb901fbef72540c76c163ffc65cdcd9656bc073eacd02d54c5  /tmp/msvc600_sp5_vcpp.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp5-pp \
    && tar xzf /tmp/msvc600_sp5_vcpp.tar.gz --no-same-owner --strip-components=1 -C /opt/msvc6.0-sp5-pp \
    && rm /tmp/msvc600_sp5_vcpp.tar.gz \
    && cp /opt/msvc6.0-sp5-pp/Common/MSDev98/Bin/MSPDB60.DLL /opt/msvc6.0-sp5-pp/VC98/Bin/ \
    && ls /opt/msvc6.0-sp5-pp/VC98/Bin/CL.EXE /opt/msvc6.0-sp5-pp/VC98/Bin/ml.exe /opt/msvc6.0-sp5-pp/VC98/Include/xmmintrin.h /opt/msvc6.0-sp5-pp/VC98/Include/emmintrin.h /opt/msvc6.0-sp5-pp/VC98/PPreadme.htm

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
