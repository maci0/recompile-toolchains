#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — djgpp/12.2.0-msdos
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/djgpp-12.2.0/bin/i586-pc-msdosdjgpp-gcc "$@"
