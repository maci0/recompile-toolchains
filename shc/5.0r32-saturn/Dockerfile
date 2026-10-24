# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: shc-5.0r32-sh2

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew SHC 5.0r32 (Saturn SH-2)" \
      org.opencontainers.image.description="SHC 5.0r32 (SH-2, Sega Saturn, PE compiler and ROF-to-ELF pipeline) toolchain image"

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 dos2unix \
    && rm -rf /var/lib/apt/lists/*

ENV REBREW_RUNNER=wibo

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/shc.tar.gz \
        "https://github.com/decompme/compilers/releases/download/compilers/shc-v5.0r32.tar.gz" \
    && echo "21f26227e48a2c9325f0aaf954e569b29db8db1dd1174aff32623017d713fdf5  /tmp/shc.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/shc-5.0r32-sh2 && curl -fsSL --retry 3 --retry-all-errors -o /opt/shc-5.0r32-sh2/rof2elf.py \
        "https://gist.githubusercontent.com/masonc15/cb2354b439e35f1400c71edfca7171ca/raw/2556b4f781d49b167be0952b4420fadd2b5a313f/rof2elf.py" \
    && echo "807f34336f9f3c803ccc2ab01fbd1630e4c7388c29a357fe2f5ba10d2c7dfdef  /opt/shc-5.0r32-sh2/rof2elf.py" | sha256sum -c -

RUN rm -rf /var/lib/apt/lists/* \
    && tar xzf /tmp/shc.tar.gz -C /opt/shc-5.0r32-sh2 \
    && rm /tmp/shc.tar.gz \
    && chmod +x /opt/shc-5.0r32-sh2/rof2elf.py /opt/shc-5.0r32-sh2/bin/* \
    && ls /opt/shc-5.0r32-sh2/bin/shc.exe

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
