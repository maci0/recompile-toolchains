#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — llvm-mos/23.3.0-c64-mos
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/llvm-mos/bin/mos-c64-clang -fno-lto "$@"
