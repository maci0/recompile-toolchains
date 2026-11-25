#!/bin/bash
# Generated from sources.json by generate.py — do not edit; run `make generate`.
# Entrypoint — psyq/2.6.3-ps1
# cc wrapper — PSY-Q 2.6.3 pipeline (host cpp -> CC1PSX -> ASPSX -> obj parser).
#
# These are 1994 DOS binaries, so each stage runs in its own dosemu2 session
# (see rebrew_dosemu_run; DOSBox cannot load their DJGPP stub).  decomp.me's
# recipe, with the host cpp doing the preprocessing and the image's
# psyq-obj-parser converting the Sony object to an ELF relocatable.
#
# cc -c f.c -o f.o
#
# -o names the output (default <stem>.o); every other argument goes to CC1PSX.
#
# shellcheck source=base/wrapper-common.sh
. /usr/local/lib/rebrew/wrapper-common.sh
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
case "$SRC" in /*) SRC_ABS="$SRC" ;; *) SRC_ABS="$(pwd)/$SRC" ;; esac
case "$OUT" in /*) OUT_ABS="$OUT" ;; *) OUT_ABS="$(pwd)/$OUT" ;; esac

_work="$(mktemp -d)" || rebrew_die "cannot create a temporary directory"
# shellcheck disable=SC2064  # expand $_work now: the trap runs after it may be unset
trap "rm -rf '$_work'" EXIT
/usr/bin/cpp -E "${cpp_flags[@]}" "$SRC_ABS" > "$_work/input.i" \
    || rebrew_die "preprocessing $SRC failed"
cd "$_work" || rebrew_die "cannot enter temporary directory"

# CC1PSX wants preprocessed input with DOS line endings; the DOS side sees this
# directory as drive D: (dosemu2's `+0 <dir> +1` image, set by the helper).
unix2dos < input.i > dos_src.c || rebrew_die "line conversion for $SRC failed"
{
    printf '@echo off\r\n'
    printf 'CC1PSX.EXE -quiet %s D:\\dos_src.c -o D:\\output.s\r\n' "${CC_FLAGS[*]}"
    printf 'EXIT /B\r\n'
} > COMPILE.BAT

rebrew_dosemu_run "$_work" /opt/psyq-2.6.3 "D:\\COMPILE.BAT"
if [ ! -s "$_work/output.s" ]; then
    # Assign first: SC2312 — a command substitution inside the message would
    # mask rebrew_dosemu_failure_note's own exit status.
    _note=$(set -e; rebrew_dosemu_failure_note)
    printf 'cc1psx produced no assembly for %s%s\n' "$SRC" "$_note" >&2
    sed -n '$p' "$_work/dosemu.log" >&2 2>/dev/null
    exit 1
fi

rebrew_dosemu_run "$_work" /opt/psyq-2.6.3 "ASPSX.EXE -quiet D:\\output.s -o D:\\output.obj"
if [ ! -s "$_work/output.obj" ]; then
    _note=$(set -e; rebrew_dosemu_failure_note)
    rebrew_die "aspsx produced no object for $SRC$_note"
fi

/opt/psyq-2.6.3/psyq-obj-parser "$_work/output.obj" -o "$OUT_ABS"
