#!/bin/bash
# SHC needs local support files; its Saturn ROF sections use 0xff padding.
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh
set -euo pipefail

out=""
args=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] && [ -n "$2" ] || rebrew_die "-o requires an output file"
            out="$2"
            shift 2
            ;;
        -c) shift ;;
        *) args+=("$1"); shift ;;
    esac
done
rebrew_pick_source "${args[@]}"
[ -n "$out" ] || out="$STEM.o"
flags=()
for arg in "${args[@]}"; do
    [ "$arg" = "$SRC" ] || flags+=("$arg")
done
src=$(realpath -- "$SRC")
out=$(realpath -m -- "$out")
work=$(mktemp -d) || rebrew_die "cannot create a temporary directory"
trap 'rm -rf "$work"' EXIT
cd "$work"
cp /opt/shc-5.0r32-sh2/bin/* .
unix2dos -q -n "$src" src.c
export SHC_LIB=. SHC_TMP=.
( rebrew_run /opt/shc-5.0r32-sh2/bin/shc.exe src.c -comment=nonest \
    -cpu=sh2 -endian=big -sjis -string=const "${flags[@]}" -object=src.obj )
[ -s src.obj ] || rebrew_die "shc produced no ROF object"
( rebrew_exec python3 /opt/shc-5.0r32-sh2/rof2elf.py src.obj output.o \
    --isa=sh2 --padding 0xff )
[ -s output.o ] || rebrew_die "ROF converter produced no ELF object"
cp -- output.o "$out"
