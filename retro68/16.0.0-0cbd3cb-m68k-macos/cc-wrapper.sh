#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — retro68/16.0.0-0cbd3cb-m68k-macos
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/retro68/bin/m68k-apple-macos-gcc "$@"
