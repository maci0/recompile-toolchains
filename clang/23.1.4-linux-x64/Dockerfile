# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: clang-23.1.4

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Clang 23.1.4 (ELF/x86_64, native)" \
      org.opencontainers.image.description="Clang 23.1.4 (ELF/x86_64, native, LLVM release build) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libc6-dev libstdc++6 libtinfo6 libzstd1 zlib1g libxml2 xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/clang.tar.xz \
        "https://github.com/llvm/llvm-project/releases/download/llvmorg-23.1.4/LLVM-23.1.4-Linux-X64.tar.xz" \
    && echo "25d814fda50d5fb0084b42be09605d8b1595d49d5e2e03a3345d7e112ff6f9f3  /tmp/clang.tar.xz" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/clang-23.1.4 \
    && tar xJf /tmp/clang.tar.xz --no-same-owner --strip-components=1 -C /opt/clang-23.1.4 \
    && rm /tmp/clang.tar.xz \
    && /opt/clang-23.1.4/bin/clang --version

COPY clang-wrapper.sh /usr/local/bin/clang
RUN chmod +x /usr/local/bin/clang

ENTRYPOINT ["/usr/local/bin/clang"]

USER rebrew
