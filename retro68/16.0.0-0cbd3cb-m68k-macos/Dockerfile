# Generated from sources.json by generate.py — do not edit; run `make generate`.
# profile: retro68-16.0.0-0cbd3cb-m68k

ARG BASE_IMAGE=rebrew/base:1.0

FROM ${BASE_IMAGE}

USER root

LABEL org.opencontainers.image.source="https://github.com/maci0/rebrew" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.title="rebrew Retro68 m68k GCC 16.0.0" \
      org.opencontainers.image.description="Commit-pinned classic Macintosh m68k cross compiler with open Multiversal Interfaces"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake libgmp-dev libmpfr-dev libmpc-dev libboost-all-dev bison flex texinfo ruby zlib1g-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/retro68.tar.gz \
        "https://codeload.github.com/autc04/Retro68/tar.gz/0cbd3cb918a127a0d30a675b337f8f8e15062786" \
    && echo "c4775801b3d3825d6b4f5209751c6898277e199ccb7844ff02eae77b95a0f4b2  /tmp/retro68.tar.gz" | sha256sum -c -

RUN curl -fsSL --retry 3 --retry-all-errors -o /tmp/multiversal.tar.gz \
        "https://codeload.github.com/autc04/multiversal/tar.gz/580f3309649ad4c788c048be3dff2416d7ba49f3" \
    && echo "2534535e1eaca0a0bb360998528f0c8ba4c2e57189cf7bc56cd9e88c721aa507  /tmp/multiversal.tar.gz" | sha256sum -c -

RUN mkdir -p /opt/retro68-notices /tmp/retro68-src /tmp/retro68-build \
    && tar xzf /tmp/retro68.tar.gz --no-same-owner --strip-components=1 -C /tmp/retro68-src \
    && tar xzf /tmp/multiversal.tar.gz --no-same-owner --strip-components=1 -C /tmp/retro68-src/multiversal \
    && sed -i 's/^BUILD_JOBS=.*/BUILD_JOBS=8/' /tmp/retro68-src/build-toolchain.bash \
    && cd /tmp/retro68-build && /tmp/retro68-src/build-toolchain.bash --prefix=/opt/retro68 --no-ppc --multiversal --clean-after-build \
    && cd /tmp/retro68-src && find . -type f \( -name 'COPYING*' -o -name 'LICENSE*' \) -exec cp --parents '{}' /opt/retro68-notices/ \; \
    && rm -rf /tmp/retro68-src /tmp/retro68-build /tmp/retro68.tar.gz /tmp/multiversal.tar.gz \
    && test -x /opt/retro68/bin/m68k-apple-macos-gcc

COPY cc-wrapper.sh /usr/local/bin/cc
RUN chmod +x /usr/local/bin/cc

ENTRYPOINT ["/usr/local/bin/cc"]

USER rebrew
