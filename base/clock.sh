#!/bin/sh
# Native tools see SOURCE_DATE_EPOCH; monotonic time and file mtimes stay real.
set -eu
if [ "${SOURCE_DATE_EPOCH+x}" = x ]; then
    case "$SOURCE_DATE_EPOCH" in
        '' | *[!0-9]*) echo 'rebrew: SOURCE_DATE_EPOCH must be decimal seconds' >&2; exit 1 ;;
        *) ;;
    esac
    if [ "${#SOURCE_DATE_EPOCH}" -gt 10 ] || [ "$SOURCE_DATE_EPOCH" -gt 2147483647 ]; then
        echo 'rebrew: Wine build clock supports SOURCE_DATE_EPOCH in 0..2147483647' >&2
        exit 1
    fi
    for arch in i386-linux-gnu x86_64-linux-gnu; do
        if [ ! -r "/usr/lib/$arch/faketime/libfaketime.so.1" ]; then
            echo 'rebrew: missing native build clock; rebuild the base and toolchain images' >&2
            exit 1
        fi
    done
    export TZ=UTC FAKETIME_FMT=%s FAKETIME="$SOURCE_DATE_EPOCH"
    export FAKETIME_DONT_FAKE_MONOTONIC=1 NO_FAKE_STAT=1
    # $LIB is expanded by the ELF loader for each process's own architecture.
    # shellcheck disable=SC2016
    export LD_PRELOAD='/usr/$LIB/faketime/libfaketime.so.1'
fi
exec "$@"
