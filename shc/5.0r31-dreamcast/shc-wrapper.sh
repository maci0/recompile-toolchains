#!/bin/bash
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — shc/5.0r31-dreamcast
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh
compile=no
for arg in "$@"; do
    [ "$arg" != -c ] || compile=yes
done
if [ "$compile" = no ]; then
    SHC_LIB=/opt/shc-5.0r31/bin
    SHC_TMP=${TMPDIR:-/tmp}
    export SHC_LIB SHC_TMP
    rebrew_run /opt/shc-5.0r31/bin/shc.exe "$@"
fi
set -euo pipefail
out=""
args=()
cpp_flags=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] && [ -n "$2" ] || rebrew_die "-o requires an output file"
            out="$2"; shift 2 ;;
        -c) shift ;;
        -I|-D|-U|-include|-isystem)
            [ "$#" -ge 2 ] || rebrew_die "$1 requires an argument"
            cpp_flags+=("$1" "$2"); shift 2 ;;
        -I*|-D*|-U*) cpp_flags+=("$1"); shift ;;
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
[ "$src" != "$out" ] || rebrew_die "source and output must be different files"
work=$(mktemp -d) || rebrew_die "cannot create a temporary directory"
target=""
trap 'rm -rf -- "$work"; [ -z "$target" ] || rm -f -- "$target"' EXIT
( rebrew_exec /usr/bin/cpp -P "${cpp_flags[@]}" "$src" -o "$work/input.i" )
cd "$work"
cp -a /opt/shc-5.0r31/bin/. .
unix2dos -q -n input.i input.c
export SHC_LIB=. SHC_TMP=.
( rebrew_run /opt/shc-5.0r31/bin/shc.exe input.c -cpu=sh4 -endian=little "${flags[@]}" -object=raw.obj )
( rebrew_exec python3 /opt/shc-5.0r31/rof2elf.py raw.obj output.o )
[ -s output.o ] || rebrew_die "compiler pipeline produced no ELF object"
target=$(mktemp "${out}.tmp.XXXXXX")
cp --preserve=mode -- output.o "$target"
mv -f -- "$target" "$out"
