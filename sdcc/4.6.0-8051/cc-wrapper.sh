#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — sdcc/4.6.0-8051
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/sdcc-4.6.0/bin/sdcc -mmcs51 "$@"
