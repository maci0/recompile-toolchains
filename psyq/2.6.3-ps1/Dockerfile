# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: psyq-2.6.3-221

ARG BASE_IMAGE=rebrew/base-dosemu:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew PSY-Q 2.6.3 (PlayStation 1, dosemu2)" \
      org.opencontainers.image.description="PSY-Q 2.6.3 (MIPS R3000, PS1, DOS binaries under dosemu2) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/psyq.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/psyq_263_221.tar.gz" \
    && echo "082a57e28efe06dc75f1c8be4f2b73ffa65ad5b995c6c345cf67b8dcd19192c5  /tmp/psyq.tar.gz" | sha256sum -c -

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
