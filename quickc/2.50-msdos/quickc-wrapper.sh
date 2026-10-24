#!/bin/sh
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — quickc/2.50-msdos
# Compile one source with Microsoft QuickC 2.50 under DOSBox.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh

set -e
rebrew_pick_source "$@"
rebrew_flags_except_source "$@"

rebrew_dosbox_compile /opt/quickc2.50 quickc \
    "set INCLUDE=C:\\INCLUDE
C:\\QCL.EXE /c $FLAGS SRC.C > C:\\quickcout.txt" \
    quickcout.txt
