#!/bin/bash
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — psyq/3.5-daze-0.3.0-ps1
# Original DOS stages with explicit software emulation; every stage has a watchdog.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh
set -euo pipefail
OUT=""
args=()
cpp_flags=()
while [ "$#" -gt 0 ]; do
    case "$1" in
        -o)
            [ "$#" -ge 2 ] && [ -n "$2" ] || rebrew_die "-o requires an output file"
            OUT="$2"
            shift 2
            ;;
        -c) shift ;;
        -I|-D|-U|-include|-imacros|-isystem|-iquote|-idirafter)
            [ "$#" -ge 2 ] && [ -n "$2" ] || rebrew_die "$1 requires an argument"
            cpp_flags+=("$1" "$2")
            shift 2
            ;;
        -I*|-D*|-U*|-nostdinc|-undef)
            cpp_flags+=("$1")
            shift
            ;;
        *) args+=("$1"); shift ;;
    esac
done
rebrew_pick_source "${args[@]}"
[ -n "$OUT" ] || OUT="$STEM.o"
CC_FLAGS=()
for arg in "${args[@]}"; do
    [ "$arg" = "$SRC" ] || CC_FLAGS+=("$arg")
done
src=$(realpath -- "$SRC")
out=$(realpath -m -- "$OUT")
[ "$src" != "$out" ] || rebrew_die "source and output must be different files"
work=$(mktemp -d) || rebrew_die "cannot create a temporary directory"
target=""
trap 'rm -rf -- "$work"; [ -z "$target" ] || rm -f -- "$target"' EXIT
( rebrew_exec /usr/bin/cpp -E  "${cpp_flags[@]}" "$src" -o "$work/preprocessed.c" )
cd "$work"

# Each stage keeps its exit status and watchdog; compiler files are read-only.
run_dos() {
    ( rebrew_exec /usr/local/bin/daze --no-tmp --backend unicorn \
        --mount-ro C:/opt/psyq-3.5 --mount "D:$work" \
        --env TMP=D:/ --env TEMP=D:/ "$@" )
}
unix2dos -q -n preprocessed.c dos_src.c

run_dos C:/CC1PSX.EXE -quiet "${CC_FLAGS[@]}" D:/dos_src.c -o D:/output.s
[ -s output.s ] || rebrew_die "compiler produced no assembly"
run_dos C:/ASPSX.EXE -quiet D:/output.s -o D:/output.obj
[ -s output.obj ] || rebrew_die "assembler produced no object"
( rebrew_exec /opt/psyq-3.5/psyq-obj-parser output.obj -o output.o )
[ -s output.o ] || rebrew_die "converter produced no ELF object"
target=$(mktemp "${out}.tmp.XXXXXX")
cp --preserve=mode -- output.o "$target"
mv -fT -- "$target" "$out"
