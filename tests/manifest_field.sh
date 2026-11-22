#!/bin/sh
# manifest_field.sh <profile> <key> — one field of a sources.json entry, for
# tests/smoke.sh: a top-level string field (`host_dir`, `arg_style`, ...), or
# `runner`, the runner its image uses (the recipe's `runner`, unless the
# recipe's `env` sets REBREW_RUNNER, which rebrew_run obeys).  Prints nothing
# for a profile or field the manifest lacks.  sources.json keeps one field per
# line at fixed indents (build.sh reads it the same way); test_smoke_fields.py
# checks every profile against a JSON parse.
set -eu

[ "$#" -eq 2 ] || { echo "usage: manifest_field.sh <profile> <key>" >&2; exit 2; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
awk -v want="  \"$1\": {" -v key="$2" '
    $0 == want { inside = 1; next }
    inside && /^  "/ { exit }
    inside && index($0, "    \"" key "\": \"") == 1 { split($0, field, "\""); top = field[4] }
    inside && /^      "runner": "/ { split($0, field, "\""); runner = field[4] }
    inside && /^        "REBREW_RUNNER": "/ { split($0, field, "\""); env = field[4] }
    END {
        if (key == "runner") print (env != "" ? env : runner)
        else print top
    }
' "$ROOT/sources.json"
