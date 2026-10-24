#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — msvc/12.0-u4-win32
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

INCLUDE='Z:\opt\msvc12.0-u4\msvc12\include'
LIB='Z:\opt\msvc12.0-u4\msvc12\lib'
export INCLUDE LIB
rebrew_run /opt/msvc12.0-u4/msvc12/bin/cl.exe "$@"
