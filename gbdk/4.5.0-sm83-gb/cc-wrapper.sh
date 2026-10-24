#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — gbdk/4.5.0-sm83-gb
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

rebrew_exec /opt/gbdk/bin/lcc "$@"
