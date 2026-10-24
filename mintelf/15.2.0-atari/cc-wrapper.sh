#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — mintelf/15.2.0-atari
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /usr/bin/m68k-atari-mintelf-gcc "$@"
