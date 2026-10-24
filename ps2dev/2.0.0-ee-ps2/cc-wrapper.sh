#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — ps2dev/2.0.0-ee-ps2
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/ps2dev/ee/bin/mips64r5900el-ps2-elf-gcc "$@"
