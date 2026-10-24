# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: mintelf-gcc-15.2.0

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew MiNT ELF GCC 15.2.0" \
      org.opencontainers.image.description="Atari MiNT ELF cross compiler with pinned binutils and mintlib"

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmpc3 libmpfr6 libgmp10 zlib1g libzstd1 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/part0.tar.xz \
        "https://tho-otto.de/download/mint/gcc-15.2.0-mintelf-20250810-bin-linux64.tar.xz" \
    && echo "1f86cc5caa9a5b2429b253bd2218bdf82973ef772260b1e692e19010b1ea6c34  /tmp/part0.tar.xz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/part1.tar.xz \
        "https://tho-otto.de/download/mint/binutils-2.45-mintelf-20250812-bin-linux64.tar.xz" \
    && echo "e37c22f84baaf8ffc890a11265d4369498f9bc4e68aaac21dcef887d3655f025  /tmp/part1.tar.xz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/part2.tar.xz \
        "https://tho-otto.de/download/mint/mintlib-0.60.1-mintelf-20240718-dev.tar.xz" \
    && echo "0a9f4f61c976af26b3b4c2fdfbfcaaa19c671174a6a1c874496375f775ff33ec  /tmp/part2.tar.xz" | sha256sum -c -

RUN mkdir -p /opt/mintelf-15.2.0 \
    && tar xJf /tmp/part0.tar.xz --no-same-owner -C / \
    && tar xJf /tmp/part1.tar.xz --no-same-owner -C / \
    && tar xJf /tmp/part2.tar.xz --no-same-owner -C / \
    && rm /tmp/part*.tar.xz \
    && test -x /usr/bin/m68k-atari-mintelf-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
