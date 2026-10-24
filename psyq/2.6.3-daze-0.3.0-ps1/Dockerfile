# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: psyq-2.6.3-221-daze-0.3.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 2.6.3 (PlayStation 1, Daze 0.3.0)" \
      org.opencontainers.image.description="PSY-Q 2.6.3 (MIPS R3000, PS1, DOS binaries under Daze 0.3.0 (Unicorn)) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends cpp dos2unix g++ zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq_263_221.tar.gz" \
    && echo "082a57e28efe06dc75f1c8be4f2b73ffa65ad5b995c6c345cf67b8dcd19192c5  /tmp/psyq.tar.gz" | sha256sum -c -

RUN mkdir -p /usr/local/bin && curl -fsSL --retry 3 --retry-all-errors -o /usr/local/bin/daze \
        "https://github.com/mkst/daze/releases/download/0.3.0/daze" \
    && echo "4b6f55e5813a0752eedd1462ef4e3877a7ab0d0a244d806f3fab495bcee2894c  /usr/local/bin/daze" | sha256sum -c -

RUN mkdir -p /opt/daze-notices && curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/BUILD-INFO.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/BUILD-INFO.txt" \
    && echo "34147e157731b3ba91ba492641dabe538567978349adfe4f1ce194355e62936e  /opt/daze-notices/BUILD-INFO.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/gcc-copyright \
        "https://github.com/mkst/daze/releases/download/0.3.0/gcc-copyright" \
    && echo "08c6f3dee4c19aa1e57eb7d4ad45829b2e99656313bd07fa0922e2553f500be5  /opt/daze-notices/gcc-copyright" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/glibc-copyright \
        "https://github.com/mkst/daze/releases/download/0.3.0/glibc-copyright" \
    && echo "d3c95b56fa33e28b57860580f0baf4e4f4de2a268a2b80f1d031a5191bade265  /opt/daze-notices/glibc-copyright" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/GPL-2.0.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/GPL-2.0.txt" \
    && echo "6f04ae8364d0079a192b14635f4b1da294ce18724c034c39a6a41d1b09df6100  /opt/daze-notices/GPL-2.0.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/GPL-3.0.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/GPL-3.0.txt" \
    && echo "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986  /opt/daze-notices/GPL-3.0.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/LGPL-2.1.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/LGPL-2.1.txt" \
    && echo "dc626520dcd53a22f727af3ee42c770e56c97a64fe3adb063799d8ab032fe551  /opt/daze-notices/LGPL-2.1.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/LICENSE.md \
        "https://github.com/mkst/daze/releases/download/0.3.0/LICENSE.md" \
    && echo "62ff9cf06bc8ce267b99735069eb307bc72879af5dbddda5c826344696c54171  /opt/daze-notices/LICENSE.md" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/THIRD_PARTY_NOTICES.md \
        "https://github.com/mkst/daze/releases/download/0.3.0/THIRD_PARTY_NOTICES.md" \
    && echo "bbe2d9f9528a2a6f3659921717104bbda950b5afa24272339adc3537b858be30  /opt/daze-notices/THIRD_PARTY_NOTICES.md" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/unicorn-glib.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/unicorn-glib.txt" \
    && echo "d245807f90032872d1438d741ed21e2490e1175dc8aa3afa5ddb6c8e529b58e5  /opt/daze-notices/unicorn-glib.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/unicorn-LGPL-2.0.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/unicorn-LGPL-2.0.txt" \
    && echo "b7993225104d90ddd8024fd838faf300bea5e83d91203eab98e29512acebd69c  /opt/daze-notices/unicorn-LGPL-2.0.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /opt/daze-notices/unicorn-qemu.txt \
        "https://github.com/mkst/daze/releases/download/0.3.0/unicorn-qemu.txt" \
    && echo "139c64b7a9ae62858ff969aae622ecfcf4f1519655bd92d2e70a1a2fb615690e  /opt/daze-notices/unicorn-qemu.txt" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/pcsx-source.tar.gz \
        "https://codeload.github.com/grumpycoders/pcsx-redux/tar.gz/c2edcc4c0d3d1ac573c95b8be5349dd8fbdbf0c2" \
    && echo "90df8b6eecaae5d499601be31f59b36f21066080f9b0d67a2ba93b81fcc29f53  /tmp/pcsx-source.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/pcsx-ELFIO.tar.gz \
        "https://codeload.github.com/serge1/ELFIO/tar.gz/8ae6cec5d60495822ecd57d736f66149da9b1830" \
    && echo "71c1a72e3fac6c9db3d4126c8f9b84bbda902e8dfb563f6dfcbed454636fa1c5  /tmp/pcsx-ELFIO.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/pcsx-fmt.tar.gz \
        "https://codeload.github.com/fmtlib/fmt/tar.gz/407c905e45ad75fc29bf0f9bb7c5c2fd3475976f" \
    && echo "2bc1fe4a5b6d5d6a614239b4ca1d520e66e152a02d3d262684d26dfd6ab3438a  /tmp/pcsx-fmt.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/pcsx-magic_enum.tar.gz \
        "https://codeload.github.com/Neargye/magic_enum/tar.gz/e55b9b54d5cf61f8e117cafb17846d7d742dd3b4" \
    && echo "bdb15ee58b44988a493b514194ca7e770b7c69d8af0c93d4447bcfa5fc044e3a  /tmp/pcsx-magic_enum.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/pcsx-args.tar.gz \
        "https://codeload.github.com/Taywee/args/tar.gz/794f2dc7caa306984cf385cbb8e7176146514959" \
    && echo "009aad8e019da87322cea8feaee68f8b2d1d5434511b23743292bdf474cdd983  /tmp/pcsx-args.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/psyq-2.6.3 \
    && tar xzf /tmp/psyq.tar.gz --no-same-owner -C /opt/psyq-2.6.3 \
    && rm /tmp/psyq.tar.gz \
    && chmod +x /opt/psyq-2.6.3/*.EXE \
    && chmod +x /usr/local/bin/daze \
    && mkdir -p /opt/psyq-parser-source \
    && tar xzf /tmp/pcsx-source.tar.gz --no-same-owner --strip-components=1 -C /opt/psyq-parser-source \
    && tar xzf /tmp/pcsx-ELFIO.tar.gz --no-same-owner --strip-components=1 -C /opt/psyq-parser-source/third_party/ELFIO \
    && tar xzf /tmp/pcsx-fmt.tar.gz --no-same-owner --strip-components=1 -C /opt/psyq-parser-source/third_party/fmt \
    && tar xzf /tmp/pcsx-magic_enum.tar.gz --no-same-owner --strip-components=1 -C /opt/psyq-parser-source/third_party/magic_enum \
    && tar xzf /tmp/pcsx-args.tar.gz --no-same-owner --strip-components=1 -C /opt/psyq-parser-source/third_party/args \
    && cd /opt/psyq-parser-source && g++ -std=c++23 -O2 -DFMT_HEADER_ONLY -Isrc -Ithird_party -Ithird_party/ELFIO -Ithird_party/fmt/include -Ithird_party/magic_enum/include tools/psyq-obj-parser/psyq-obj-parser.cc src/supportpsx/psyq-obj.cc src/support/file.cc -lz -o /opt/psyq-2.6.3/psyq-obj-parser \
    && rm /tmp/pcsx-*.tar.gz \
    && test -x /opt/psyq-2.6.3/psyq-obj-parser

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
