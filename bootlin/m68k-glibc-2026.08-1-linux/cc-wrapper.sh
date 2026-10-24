#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — bootlin/m68k-glibc-2026.08-1-linux
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/bootlin-m68k/bin/m68k-buildroot-linux-gnu-gcc "$@"
