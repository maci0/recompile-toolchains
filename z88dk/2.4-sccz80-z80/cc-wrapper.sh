#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — z88dk/2.4-sccz80-z80
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/z88dk/bin/zcc +embedded -compiler=sccz80 "$@"
