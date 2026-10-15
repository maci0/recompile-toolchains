# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: msvc-6.0-sp5-crt

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MSVC 6.0-sp5 with native VC6 CRT (win32, wine)" \
      org.opencontainers.image.description="Stock SP5 tools and archives; pinned Microsoft MSVCRT 6.0.8797 for native import qsort ordering"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cabextract \
    && rm -rf /var/lib/apt/lists/*

ENV WINEDLLOVERRIDES="msvcrt=n,b"

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/msvc600_sp5.tar.gz \
        "https://codeload.github.com/archaic-msvc/msvc600_sp5/tar.gz/refs/heads/master" \
    && echo "a95a9c17cbcbe0d97a3e80ef9596f12404eb28f36bab24e89aabcbe37acbbef6  /tmp/msvc600_sp5.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/vc6-runtime.exe \
        "https://download.microsoft.com/download/vc60pro/Update/2/W9XNT4/EN-US/VC6RedistSetup_deu.exe" \
    && echo "c2eb91d9c4448d50e46a32fecbcc3b418706d002beab9b5f4981de552098cee7  /tmp/vc6-runtime.exe" | sha256sum -c -

RUN mkdir -p /opt/msvc6.0-sp5-crt \
    && tar xzf /tmp/msvc600_sp5.tar.gz --strip-components=1 -C /opt/msvc6.0-sp5-crt \
    && rm /tmp/msvc600_sp5.tar.gz \
    && cp /opt/msvc6.0-sp5-crt/Common/MSDev98/Bin/MSPDB60.DLL /opt/msvc6.0-sp5-crt/VC98/Bin/ \
    && ls /opt/msvc6.0-sp5-crt/VC98/Bin/CL.EXE /opt/msvc6.0-sp5-crt/VC98/Bin/MSPDB60.DLL \
    && mkdir -p /tmp/vc6-runtime \
    && cabextract -q -F vcredist.exe -d /tmp/vc6-runtime /tmp/vc6-runtime.exe \
    && cabextract -q -F msvcrt.dll -d /tmp/vc6-runtime /tmp/vc6-runtime/vcredist.exe \
    && echo '887eb5ce93edb7192ca3e9220f07f9ca0f94db02af5862ebcbdfcb852db99fd1  /tmp/vc6-runtime/msvcrt.dll' | sha256sum -c - \
    && cp -a /tmp/vc6-runtime/msvcrt.dll /opt/msvc6.0-sp5-crt/VC98/Bin/ \
    && rm -rf /tmp/vc6-runtime.exe /tmp/vc6-runtime \
    && ls /opt/msvc6.0-sp5-crt/VC98/Bin/msvcrt.dll

COPY cl-wrapper.sh /usr/local/bin/cl
RUN chmod +x /usr/local/bin/cl

ENTRYPOINT ["/usr/local/bin/cl"]

USER rebrew
