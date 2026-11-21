#!/usr/bin/env python3
"""check_images.py — verify built images against the catalogue's pins.

`make test` proves every Dockerfile verifies its manifest pin; nothing proves
that an image already built and published under a tag came from the recipe the
catalogue now names.  A tag outlives a re-pin: `rebrew/msvc:7.0-win32` was
built while `msvc-7.0` still pinned the 7.1 tree, and the registry kept serving
the 7.1 compiler under the 7.0 tag after the manifest moved to `msvc700`.

Two checks, both read-only:

1. Recipe pins.  Every image's build history must contain its catalogue
   entry's `source.sha256` in the `echo "<sha256>  <file>" | sha256sum -c`
   line the generated recipe runs.  `MISMATCH` means the history checks other
   sums (another source under this tag); `NO-SUMS` means it checks none (a
   recipe from before every image downloaded a pinned source), so nothing ties
   its compiler to the pin.  Both fail.  Read from the local engine, or with
   `--registry URL` from a registry's manifest and config (no layers).
2. Distinct compilers (local engine only: it reads the files).  The directory
   holding each image's compiler binary is hashed file by file; two entries
   whose directories are byte-identical while their family or version differ
   fail as `SAME-COMPILER`.  Byte-identical entries of one family and version
   print as `alias` and pass: a service pack that left the compiler binaries
   unchanged (`msvc-6.0`, `-sp1`, `-sp2`) or a second id for one tree.

Images the engine or registry does not hold print as `absent` and pass: which
images a host carries is that host's choice.  Images keep `rebrew/` as their
namespace; `PREFIX` re-points it as in build.sh.  The local engine is the
Docker Engine API on the unix socket `DOCKER_HOST` names, else
/var/run/docker.sock.  No container is started: the binaries are read from a
created container's filesystem, which is then removed.

Deliberately not part of `make test`: it needs built images or a registry.
Run it by hand (`make images`) before publishing an image, and against the
registry a service pulls from.

Usage:  python3 tests/check_images.py [--registry URL] [profile ...]
Exit:   0 every present image passes, 1 a check failed, 2 a bad selection.
"""

from __future__ import annotations

import contextlib
import hashlib
import http.client
import json
import os
import re
import socket
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import IO

REPO = Path(__file__).resolve().parents[1]
#: A layer pull is not needed: the manifest and its config are small JSON.
REGISTRY_TIMEOUT_SECONDS = 30
#: Generous: reading a large compiler directory streams it through the socket.
ENGINE_TIMEOUT_SECONDS = 300
DEFAULT_ENGINE_SOCKET = "/var/run/docker.sock"
#: The platform the images are built for (build.sh builds linux/amd64 only).
PLATFORM = ("linux", "amd64")
_MANIFEST_TYPES = (
    "application/vnd.oci.image.index.v1+json, "
    "application/vnd.docker.distribution.manifest.list.v2+json, "
    "application/vnd.oci.image.manifest.v1+json, "
    "application/vnd.docker.distribution.manifest.v2+json"
)
#: Read size when hashing a file out of an archive stream.
_CHUNK_BYTES = 1 << 20
#: The checksum line generate.py renders (and the hand-written recipes before it
#: used): `echo "<sha256>  <file>" | sha256sum -c -`.
_RECIPE_SUM = re.compile(r'([0-9a-f]{64}) +[^\s"]+"? *\| *sha256sum -c')
_HTTP_NOT_FOUND = 404
_HTTP_OK = 200
_HTTP_CREATED = 201
_HTTP_NO_CONTENT = 204

type Json = dict[str, object]


class CheckError(RuntimeError):
    """An engine or registry answer this check cannot read."""


def recipe_sums(created_by: list[str]) -> set[str]:
    """The sha256 sums an image's build steps verified, from its history."""
    return {hit for line in created_by for hit in _RECIPE_SUM.findall(line)}


def history_of(config: Json) -> list[str]:
    """The `created_by` lines of an image config's history."""
    history = config.get("history")
    if not isinstance(history, list):
        return []
    return [
        str(step["created_by"])
        for step in history
        if isinstance(step, dict) and isinstance(step.get("created_by"), str)
    ]


def _json(raw: bytes, what: str) -> Json:
    try:
        value = json.loads(raw)
    except ValueError as error:
        raise CheckError(f"{what}: not JSON ({error})") from error
    if not isinstance(value, dict):
        raise CheckError(f"{what}: not a JSON object")
    return value


def _registry_get(url: str, accept: str) -> bytes | None:
    """The body at *url*, or None on 404."""
    request = urllib.request.Request(url, headers={"Accept": accept})  # noqa: S310
    try:
        # S310: the URL is the --registry base the operator passed plus a
        # repository path from our own catalogue.
        with urllib.request.urlopen(  # noqa: S310
            request, timeout=REGISTRY_TIMEOUT_SECONDS
        ) as response:
            body: bytes = response.read()
            return body
    except urllib.error.HTTPError as error:
        error.close()
        if error.code == _HTTP_NOT_FOUND:
            return None
        raise CheckError(f"{url}: HTTP {error.code} {error.reason}") from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise CheckError(f"{url}: {error}") from error


def registry_history(base: str, tag: str) -> list[str] | None:
    """The build history of *tag* in the registry at *base*, or None if absent."""
    repository, _, reference = tag.rpartition(":")
    root = f"{base.rstrip('/')}/v2/{repository}"
    raw = _registry_get(f"{root}/manifests/{reference}", _MANIFEST_TYPES)
    if raw is None:
        return None
    manifest = _json(raw, f"{tag} manifest")
    children = manifest.get("manifests")
    if isinstance(children, list):
        digest = next(
            (
                child.get("digest")
                for child in children
                if isinstance(child, dict)
                and isinstance(child.get("platform"), dict)
                and (child["platform"].get("os"), child["platform"].get("architecture")) == PLATFORM
            ),
            None,
        )
        if not isinstance(digest, str):
            raise CheckError(f"{tag}: the index has no {'/'.join(PLATFORM)} manifest")
        raw = _registry_get(f"{root}/manifests/{digest}", _MANIFEST_TYPES)
        if raw is None:
            raise CheckError(f"{tag}: the index names {digest}, which the registry lacks")
        manifest = _json(raw, f"{tag} manifest {digest}")
    config = manifest.get("config")
    digest = config.get("digest") if isinstance(config, dict) else None
    if not isinstance(digest, str):
        raise CheckError(f"{tag}: the manifest names no config")
    raw = _registry_get(f"{root}/blobs/{digest}", "application/json")
    if raw is None:
        raise CheckError(f"{tag}: the manifest names config {digest}, which the registry lacks")
    return history_of(_json(raw, f"{tag} config"))


class _UnixConnection(http.client.HTTPConnection):
    """HTTP to the Docker Engine API over its unix socket."""

    def __init__(self, path: str) -> None:
        super().__init__("localhost", timeout=ENGINE_TIMEOUT_SECONDS)
        self._socket_path = path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(ENGINE_TIMEOUT_SECONDS)
        sock.connect(self._socket_path)
        self.sock = sock


def engine_socket() -> str:
    """The engine's unix socket path; any other DOCKER_HOST is refused."""
    host = os.environ.get("DOCKER_HOST", "")
    if not host:
        return DEFAULT_ENGINE_SOCKET
    if not host.startswith("unix://"):
        raise CheckError(f"DOCKER_HOST={host}: only a unix:// engine socket is supported")
    return host.removeprefix("unix://")


@contextlib.contextmanager
def _engine(method: str, path: str, body: Json | None = None) -> Iterator[tuple[int, IO[bytes]]]:
    """One Engine API request: (status, body stream)."""
    connection = _UnixConnection(engine_socket())
    try:
        payload = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"} if payload is not None else {}
        connection.request(method, path, body=payload, headers=headers)
        response = connection.getresponse()
        yield response.status, response
    except OSError as error:
        raise CheckError(f"engine {method} {path}: {error}") from error
    finally:
        connection.close()


def _quoted(name: str) -> str:
    return urllib.parse.quote(name, safe="/:@")


def engine_history(tag: str) -> list[str] | None:
    """The build history of the local image *tag*, or None if absent."""
    with _engine("GET", f"/images/{_quoted(tag)}/history") as (status, stream):
        raw = stream.read()
    if status == _HTTP_NOT_FOUND:
        return None
    if status != _HTTP_OK:
        raise CheckError(f"{tag}: engine history answered {status}")
    try:
        steps = json.loads(raw)
    except ValueError as error:
        raise CheckError(f"{tag}: engine history is not JSON") from error
    if not isinstance(steps, list):
        raise CheckError(f"{tag}: engine history is not a list")
    return [
        str(step["CreatedBy"])
        for step in steps
        if isinstance(step, dict) and isinstance(step.get("CreatedBy"), str)
    ]


def tree_digest(stream: IO[bytes]) -> str:
    """sha256 over a tar stream's regular files and links, by relative path.

    The archive's top directory is dropped, so the same tree read from two
    install roots hashes the same.  Ownership and timestamps are ignored.
    """
    rows: list[str] = []
    with tarfile.open(fileobj=stream, mode="r|") as archive:
        for member in archive:
            relative = member.name.partition("/")[2]
            if member.isfile():
                handle = archive.extractfile(member)
                if handle is None:
                    raise CheckError(f"{member.name}: unreadable in the archive")
                digest = hashlib.sha256()
                while chunk := handle.read(_CHUNK_BYTES):
                    digest.update(chunk)
                rows.append(f"file {relative} {digest.hexdigest()}")
            elif member.issym() or member.islnk():
                rows.append(f"link {relative} {member.linkname}")
    if not rows:
        raise CheckError("the compiler directory holds no files")
    return hashlib.sha256("\n".join(sorted(rows)).encode()).hexdigest()


def engine_tree_digest(tag: str, directory: str) -> str | None:
    """tree_digest of *directory* in *tag*, or None when the image has no such directory.

    The files are read from a created container that is never started.
    """
    with _engine("POST", "/containers/create", {"Image": tag, "NetworkDisabled": True}) as (
        status,
        stream,
    ):
        raw = stream.read()
    if status != _HTTP_CREATED:
        raise CheckError(f"{tag}: engine create answered {status}")
    container = _json(raw, f"{tag} create").get("Id")
    if not isinstance(container, str):
        raise CheckError(f"{tag}: engine create returned no container id")
    try:
        query = urllib.parse.urlencode({"path": directory})
        with _engine("GET", f"/containers/{container}/archive?{query}") as (status, stream):
            if status == _HTTP_NOT_FOUND:
                return None
            if status != _HTTP_OK:
                raise CheckError(f"{tag}: {directory} could not be read ({status})")
            return tree_digest(stream)
    finally:
        with _engine("DELETE", f"/containers/{container}?force=true") as (status, stream):
            stream.read()
        if status not in (_HTTP_NO_CONTENT, _HTTP_NOT_FOUND):
            print(f"warning: container {container} was not removed ({status})", file=sys.stderr)


@dataclass(frozen=True)
class Entry:
    """What the catalogue says one profile's image is."""

    tag: str
    sha256: str
    #: The compiler version the entry says it is: family and version.
    claim: tuple[str, str]
    #: The in-image directory holding the compiler binary; "" when the recipe names none.
    compiler_dir: str


def entries() -> dict[str, Entry]:
    """Every catalogue entry, from the rows toolchains.json publishes."""
    sys.path.insert(0, str(REPO))
    import catalog
    import generate
    import toolchains

    prefix = os.environ.get("PREFIX", "rebrew")
    found: dict[str, Entry] = {}
    for profile, entry in catalog.manifest().items():
        row = toolchains.row(profile, entry)
        image, source = row["image"], row["source"]
        if not isinstance(image, dict) or not isinstance(source, dict):
            raise CheckError(f"{profile}: catalogue row has no image or source")
        binary = generate.recipe(entry).get("binary")
        found[profile] = Entry(
            tag=f"{prefix}/{str(image['tag']).removeprefix('rebrew/')}",
            sha256=str(source["sha256"]),
            claim=(str(row["family"]), str(row["version"])),
            compiler_dir=(
                str(Path(generate.binary_path(entry)).parent)
                if isinstance(binary, str) and binary
                else ""
            ),
        )
    return found


def recipe_pins(
    found: dict[str, Entry], selected: list[str], registry: str
) -> tuple[int, list[str]]:
    """Check 1 for *selected*; (failures, profiles whose image is present)."""
    counts = {"ok": 0, "MISMATCH": 0, "NO-SUMS": 0, "absent": 0}
    present: list[str] = []
    for profile in selected:
        entry = found[profile]
        history = registry_history(registry, entry.tag) if registry else engine_history(entry.tag)
        if history is None:
            counts["absent"] += 1
            print(f"absent        {profile:30s} {entry.tag}")
            continue
        present.append(profile)
        sums = recipe_sums(history)
        if entry.sha256 in sums:
            counts["ok"] += 1
            print(f"ok            {profile:30s} {entry.tag}")
        elif sums:
            counts["MISMATCH"] += 1
            checked = ", ".join(sorted(s[:12] for s in sums))
            print(
                f"MISMATCH      {profile:30s} {entry.tag}: the recipe checked {checked}; "
                f"the catalogue pins {entry.sha256[:12]}"
            )
        else:
            counts["NO-SUMS"] += 1
            print(f"NO-SUMS       {profile:30s} {entry.tag}: the recipe checked no sha256")
    print(
        f"\nrecipe pins, {len(selected)} entries: ok {counts['ok']}, "
        f"MISMATCH {counts['MISMATCH']}, NO-SUMS {counts['NO-SUMS']}, absent {counts['absent']}"
    )
    return counts["MISMATCH"] + counts["NO-SUMS"], present


def distinct_compilers(found: dict[str, Entry], present: list[str]) -> int:
    """Check 2: print byte-identical compiler directories; count the failures."""
    groups: dict[str, list[str]] = {}
    failures = 0
    for profile in present:
        entry = found[profile]
        if not entry.compiler_dir:
            print(f"unchecked     {profile:30s} the recipe names no compiler binary")
            continue
        digest = engine_tree_digest(entry.tag, entry.compiler_dir)
        if digest is None:
            failures += 1
            print(f"NO-COMPILER   {profile:30s} {entry.tag}: no {entry.compiler_dir} in the image")
            continue
        groups.setdefault(digest, []).append(profile)
    for digest, members in sorted(groups.items()):
        if len(members) == 1:
            continue
        claims = sorted({found[profile].claim for profile in members})
        names = " ".join(members)
        if len(claims) == 1:
            print(f"alias         {names}: identical binaries ({digest[:12]}), one claimed version")
            continue
        failures += 1
        said = "; ".join(" ".join(filter(None, claim)) for claim in claims)
        print(f"SAME-COMPILER {names}: identical binaries ({digest[:12]}) claim {said}")
    print(f"compiler binaries, {len(present)} images: {failures} failing")
    return failures


def main(argv: list[str]) -> int:
    registry = ""
    if argv[:1] == ["--registry"]:
        if len(argv) == 1:
            print("usage: check_images.py [--registry URL] [profile ...]", file=sys.stderr)
            return 2
        registry, argv = argv[1], argv[2:]
    found = entries()
    unknown = set(argv) - set(found)
    if unknown:
        print(f"images: no such profile: {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2
    failures, present = recipe_pins(found, sorted(argv) if argv else sorted(found), registry)
    if registry:
        print("compiler binaries: not compared (they need the local engine)")
    else:
        failures += distinct_compilers(found, present)
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except CheckError as error:
        print(f"images: {error}", file=sys.stderr)
        raise SystemExit(1) from error
