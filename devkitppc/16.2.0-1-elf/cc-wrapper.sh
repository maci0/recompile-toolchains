#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — devkitppc/16.2.0-1-elf
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/devkitpro/devkitPPC/bin/powerpc-eabi-gcc "$@"
