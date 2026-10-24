#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — devkita64/16.1.0-1-elf
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/devkitpro/devkitA64/bin/aarch64-none-elf-gcc "$@"
