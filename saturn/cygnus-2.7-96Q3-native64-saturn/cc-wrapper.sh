#!/bin/bash
# Native Saturn pipeline, matching decomp.me's cpp -> cc1 -> SH assembler recipe.
# shortcut: GNU as may add trailing NOP padding, use the DOS profile for exact section padding.
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

( rebrew_exec /usr/bin/cpp -E "$src" -o "$work/input.i" )
( rebrew_exec /opt/saturn-cygnus-native64/cc1-native64 -quiet "${flags[@]}" \
    "$work/input.i" -o "$work/output.s" )
( rebrew_exec sh-elf-as "$work/output.s" -o "$work/output.o" )
[ -s "$work/output.o" ] || rebrew_die "assembler produced no object"
cp -- "$work/output.o" "$out"
