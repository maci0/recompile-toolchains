# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: ia16-gcc-6.3.0-20260612

ARG BASE_IMAGE=rebrew/base-noble:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew IA-16 GCC 6.3.0 (20260612)" \
      org.opencontainers.image.description="Pinned IA-16 GCC, binutils, newlib and libi86 for segmented 16-bit DOS code"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgmp10 libmpc3 libmpfr6 libstdc++6 zlib1g \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ia16-gcc.deb \
        "https://ppa.launchpadcontent.net/tkchia/build-ia16/ubuntu/pool/main/g/gcc-ia16-elf/gcc-ia16-elf_6.3.0-20260612.00-ppa260612104~noble_amd64.deb" \
    && echo "4a23a16d38366398b9c540745ccc46537d152517f96a324cf69c3d71db67e62d  /tmp/ia16-gcc.deb" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ia16-0.deb \
        "https://ppa.launchpadcontent.net/tkchia/build-ia16/ubuntu/pool/main/b/binutils-ia16-elf/binutils-ia16-elf_2.39-20260423.22-ppa260423231~noble_amd64.deb" \
    && echo "01112d3b45ac9ab04a750488caadb8c4855d99d95c7713c807dc34649c8c7c88  /tmp/ia16-0.deb" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ia16-1.deb \
        "https://ppa.launchpadcontent.net/tkchia/build-ia16/ubuntu/pool/main/libi/libi86-ia16-elf/libi86-ia16-elf_20260727-stage1gcc6.3.0-20260612.00-binutils2.39-20260423.22-ppa260727151~noble_amd64.deb" \
    && echo "233605e2175b8a30446f9acc6cef5b610d3c65b8ce091e7495269aa142b0d14c  /tmp/ia16-1.deb" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/ia16-2.deb \
        "https://ppa.launchpadcontent.net/tkchia/build-ia16/ubuntu/pool/main/libn/libnewlib-ia16-elf/libnewlib-ia16-elf_2.4.0-20260316.15-stage1gcc6.3.0-20260612.00-binutils2.39-20260423.22-ppa260612104~noble_amd64.deb" \
    && echo "b6e88fbd5cd6cb40cebba748e6c39efb41f13b466ba71ebef77412bd2b81b0ba  /tmp/ia16-2.deb" | sha256sum -c -

RUN mkdir -p /opt/ia16-6.3.0 \
    && apt-get update && apt-get install -y --no-install-recommends /tmp/ia16-gcc.deb /tmp/ia16-0.deb /tmp/ia16-1.deb /tmp/ia16-2.deb && rm -rf /var/lib/apt/lists/* \
    && rm /tmp/ia16-gcc.deb /tmp/ia16-0.deb /tmp/ia16-1.deb /tmp/ia16-2.deb \
    && test -x /usr/bin/ia16-elf-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
