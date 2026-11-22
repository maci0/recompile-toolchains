"""Render ``toolchains.json``, the machine-readable toolchain catalogue.

The catalogue is derived from the same two inputs as ``docs/TOOLCHAINS.md``:
``sources.json`` (what is pinned, how each image runs its compiler, and the
consumer fields every image declares) and each ``<family>/<version>-<platform>/
Dockerfile`` (the wrapper the image exposes).  The release artifact is pinned
by its own sha256 in the consumers that vendor it; see
[ADR 0010](../../docs/adr/0010-cross-tool-architecture-decisions.md).  That
sha256 is published beside it as ``toolchains.json.sha256``, in the form
``sha256sum -c`` reads.

Usage:
    python toolchains.py            # rewrite toolchains.json and its .sha256
    python toolchains.py --check     # exit 1 when a committed copy differs
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import catalog

REPO = Path(__file__).resolve().parent
ARTIFACT = REPO / "toolchains.json"
CHECKSUM = REPO / "toolchains.json.sha256"

SCHEMA_VERSION = 1

#: ``<family>/<version>-<platform>`` suffixes, longest first so ``linux-x64``
#: wins over a bare ``linux``.  ``host`` is the fallback for a tree whose
#: target is not encoded in its directory name.
PLATFORMS = (
    "linux-x64",
    "linux-i386",
    "linux386",
    "android-x86",
    "dreamcast",
    "macos",
    "msdos",
    "switch",
    "win16",
    "win32",
    "x360",
    "wiiu",
    "sm83",
    "m68k",
    "atari",
    "amiga",
    "saturn",
    "ps1",
    "ps2",
    "psp",
    "n64",
    "nds",
    "3ds",
    "gba",
    "wii",
    "gc",
    "gb",
    "c64",
    "nes",
    "mos",
    "z80",
    "8051",
    "stm8",
    "elf",
    "linux",
)

#: Platform → detector architecture and code model.  The compiler-detector
#: consumer matches its observations against these; a profile without an
#: entry here simply omits ``arch``/``bits`` rather than guessing.
TARGETS: dict[str, tuple[str, int]] = {
    "linux-x64": ("x86_64", 64),
    "linux-i386": ("x86", 32),
    "linux386": ("x86", 32),
    "android-x86": ("x86", 32),
    "win16": ("x86_16", 16),
    "msdos": ("x86_16", 16),
    "win32": ("x86", 32),
    "x360": ("powerpc", 32),
    "wiiu": ("powerpc", 32),
    "wii": ("powerpc", 32),
    "gc": ("powerpc", 32),
    "switch": ("aarch64", 64),
    "ps1": ("mips", 32),
    "ps2": ("mips", 32),
    "psp": ("mips", 32),
    "n64": ("mips", 32),
    "gba": ("arm", 32),
    "nds": ("arm", 32),
    "3ds": ("arm", 32),
    "saturn": ("sh2", 32),
    "dreamcast": ("sh4", 32),
    "gb": ("sm83", 8),
    "c64": ("mos6502", 8),
    "nes": ("mos6502", 8),
    "mos": ("mos6502", 8),
    "atari": ("m68k", 32),
    "amiga": ("m68k", 32),
    "z80": ("z80", 8),
    "8051": ("mcs51", 8),
    "stm8": ("stm8", 8),
    "sm83": ("sm83", 8),
    "m68k": ("m68k", 32),
}

#: The devkit trees encode their target in the family, not the directory.
DEVKIT_TARGETS: dict[str, tuple[str, int]] = {
    "devkitarm": ("arm", 32),
    "devkitppc": ("powerpc", 32),
    "devkita64": ("aarch64", 64),
}

#: Recipe runner → runtime class consumers can execute.
RUNTIME_CLASS = {
    "exec": "exec",
    "native": "exec",
    "wine": "wine",
    "wibo": "wibo",
    "dosbox": "dosbox",
    "dosemu2": "dosemu2",
    "daze": "daze",
}

#: Consumer fields every image declares in ``sources.json``.  They are not
#: documentation: rebrew and compiler-detector invoke and identify by them.
CONSUMER_FIELDS = ("flags_style", "arg_style", "obj_ext")

_ENTRYPOINT = re.compile(r'^ENTRYPOINT \["/usr/local/bin/([^"]+)"\]$', re.MULTILINE)
_YEAR = re.compile(r"^(19|20)\d{2}\.\d+$")


def _text(entry: dict[str, object], key: str) -> str:
    value = entry.get(key, "")
    return value if isinstance(value, str) else ""


def _platform(entry: dict[str, object]) -> str:
    host_dir = _text(entry, "host_dir")
    suffix = host_dir.split("/", 1)[1] if "/" in host_dir else host_dir
    return next((p for p in PLATFORMS if suffix.endswith(p)), "host")


def _version_arch(entry: dict[str, object]) -> str:
    host_dir = _text(entry, "host_dir")
    return host_dir.split("/", 1)[1] if "/" in host_dir else host_dir


def _version(profile: str, family: str) -> str:
    """The compiler version encoded after the family in a profile id.

    ``gcc-14.2.0`` names 14.2.0, ``ia16-gcc-6.3.0-20260612`` names 6.3.0 and
    ``msvc-6.0-sp5-crt`` names 6.0.  A tree without a version (``agbcc``)
    leaves the field empty rather than inventing one.
    """
    rest = profile.removeprefix(family + "-")
    match = re.search(r"(?<![\d.])(\d+(?:\.\d+)+)", rest)
    if match is None or _YEAR.match(match.group(1)):
        return ""
    return match.group(1)


def _service_pack(profile: str) -> str:
    match = re.search(r"-sp(\d+)(?:-|$)", profile)
    return f"sp{match.group(1)}" if match else ""


def _arch_bits(entry: dict[str, object]) -> tuple[str, int]:
    platform = _platform(entry)
    arch, bits = TARGETS.get(platform, ("", 0))
    if platform == "elf":
        arch, bits = DEVKIT_TARGETS.get(_text(entry, "family"), ("", 0))
    host_dir = _text(entry, "host_dir")
    if platform == "macos":
        if "m68k" in host_dir:
            arch, bits = "m68k", 32
        elif "powerpc" in host_dir:
            arch, bits = "powerpc", 32
    declared = entry.get("bits")
    if isinstance(declared, int):
        bits = declared
        if arch == "x86_64" and bits == 32:
            arch = "x86"
        elif arch == "x86" and bits == 64:
            arch = "x86_64"
        elif arch == "x86_16" and bits == 32:
            # A 32-bit DOS extender compiler (DJGPP) writes i386 code.
            arch = "x86"
    return arch, bits


def _entrypoint(entry: dict[str, object]) -> tuple[str, str]:
    """The wrapper name and its absolute in-image path."""
    recipe = entry.get("recipe")
    name = _text(recipe, "entrypoint") if isinstance(recipe, dict) else ""
    if not name:
        dockerfile = REPO / _text(entry, "host_dir") / "Dockerfile"
        match = _ENTRYPOINT.search(dockerfile.read_text(encoding="utf-8"))
        name = match.group(1) if match else ""
    return name, f"/usr/local/bin/{name}" if name else ""


def _runtime(entry: dict[str, object]) -> str:
    recipe = entry.get("recipe")
    runner = _text(recipe, "runner") if isinstance(recipe, dict) else ""
    return RUNTIME_CLASS.get(runner, runner)


def _aliases(entry: dict[str, object]) -> list[str]:
    value = entry.get("aliases", [])
    return [str(alias) for alias in value] if isinstance(value, list) else []


def _consumer(entry: dict[str, object], profile: str) -> dict[str, object]:
    missing = [field for field in CONSUMER_FIELDS if not _text(entry, field)]
    if missing:
        raise ValueError(f"{profile}: sources.json is missing {', '.join(missing)}")
    tool_root = _text(entry, "tool_root")
    return {
        "flags_style": _text(entry, "flags_style"),
        "arg_style": _text(entry, "arg_style"),
        "obj_ext": _text(entry, "obj_ext"),
        "tool_root": tool_root or None,
    }


def row(profile: str, entry: dict[str, object]) -> dict[str, object]:
    """One catalogue row, the shape consumers read."""
    family = _text(entry, "family")
    arch, bits = _arch_bits(entry)
    entrypoint, image_entrypoint = _entrypoint(entry)
    source = {
        "url": _text(entry, "url"),
        "sha256": _text(entry, "sha256"),
        "commit": _text(entry, "commit") or None,
    }
    out: dict[str, object] = {
        "id": profile,
        "family": family,
        "version": _version(profile, family),
        "platform": _platform(entry),
        "runtime": _runtime(entry),
        "entrypoint": entrypoint,
        "image_entrypoint": image_entrypoint,
        "image": {"tag": f"rebrew/{family}:{_version_arch(entry)}"},
        "aliases": _aliases(entry),
        "source": source,
        "consumer": _consumer(entry, profile),
    }
    if arch and bits:
        out["arch"] = arch
        out["bits"] = bits
    service_pack = _service_pack(profile)
    if service_pack:
        out["service_pack"] = service_pack
    variant = _text(entry, "variant_of")
    if variant:
        out["variant_of"] = variant
    same = _text(entry, "same_compiler_as")
    if same:
        out["same_compiler_as"] = same
    withdrawn = _text(entry, "withdrawn")
    if withdrawn:
        # The id stays so stored records resolve; a consumer must not offer or run it.
        out["withdrawn"] = withdrawn
    return out


def render(entries: dict[str, dict[str, object]]) -> dict[str, object]:
    """The full catalogue for the given manifest, deterministically ordered."""
    return {
        "schema_version": SCHEMA_VERSION,
        "source": "recompile-toolchains sources.json",
        "count": len(entries),
        "toolchains": [row(profile, entries[profile]) for profile in sorted(entries)],
    }


def dump(data: dict[str, object]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def checksum(text: str) -> str:
    """The ``sha256sum`` line for *text* written as ``toolchains.json``."""
    return f"{hashlib.sha256(text.encode('utf-8')).hexdigest()}  {ARTIFACT.name}\n"


def main(argv: list[str]) -> int:
    """Write the artifact and its checksum, or (``--check``) verify both."""
    if set(argv) - {"--check"}:
        print("usage: toolchains.py [--check]", file=sys.stderr)
        return 2
    text = dump(render(catalog.manifest()))
    outputs = ((ARTIFACT, text), (CHECKSUM, checksum(text)))
    if "--check" in argv:
        stale = [
            path.name
            for path, expected in outputs
            if (path.read_text(encoding="utf-8") if path.exists() else "") != expected
        ]
        for name in stale:
            print(f"stale: {name}; run `make docs`", file=sys.stderr)
        if stale:
            return 1
        print("toolchains.json and toolchains.json.sha256 are up to date")
        return 0
    for path, expected in outputs:
        path.write_text(expected, encoding="utf-8")
        print(f"wrote {path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
