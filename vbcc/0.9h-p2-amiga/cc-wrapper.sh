#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — vbcc/0.9h-p2-amiga
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/vbcc/bin/vc +aos68k "$@"
