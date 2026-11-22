#!/usr/bin/env python3
"""check_images.py — verify built images against the catalogue's pins.

`make test` proves every Dockerfile verifies its manifest pin; nothing proves
that an image already built and published under a tag came from the recipe the
catalogue now names.  A tag outlives a re-pin: `rebrew/msvc:7.0-win32` was
built while `msvc-7.0` still pinned the 7.1 tree, and the registry kept serving
the 7.1 compiler under the 7.0 tag after the manifest moved to `msvc700`.

Two checks, both read-only:

1. Recipe pins.  Every image's build history must contain the sha256 of
   every download its recipe fetches (the primary source, and any parser,
   helper, SDK, binutils or extra pin) in the `echo "<sha256>  <file>" |
   sha256sum -c` line the generated recipe runs.  `MISMATCH` means the
   history checks other sums (another source under this tag, or a secondary
   download re-pinned since the build); `NO-SUMS` means it checks none (a
   recipe from before every image downloaded a pinned source), so nothing ties
   its compiler to the pin.  Both fail.  An image whose history verifies the
   branch archive that a commit archive replaced (`tools/migrate/
   commit-archives.json`, which records both sums for trees compared member
   by member) holds the same tree and prints `ok (branch)`; no other sum
   gets that allowance.  Read from the local engine, or with `--registry URL`
   from a registry's manifest and config (no layers).
2. Distinct compilers (local engine only: it reads the files).  The directory
   holding each image's compiler binary (the recipe's `binary`, or the
   `C:\\...\\X.EXE` a DOSBox command runs) is hashed file by file; entries
   whose directories are byte-identical fail as `SAME-COMPILER` unless they
   are tied together by `same_compiler_as` (one compiler under two ids: the
   product versions `msvc-1.52` and `msvc-1.5`, or service packs that left the
   compiler unchanged, `msvc-6.0-sp1` and `msvc-6.0`) or `variant_of` (another
   front end from the same archive).  A same-version pair needs the
   declaration too: an SP4 tag holding the SP6 tree claims the same version.
   A `same_compiler_as` whose binaries differ fails as `DIFFERENT`.  Every
   recipe names its compiler (`make test` refuses one that does not); an
   entry without one would print `unchecked`.
   A registry cannot answer this check: it serves layers, not files, and a
   layer digest cannot stand in for the binaries, because each entry installs
   under its own `/opt` root, so one compiler in two images is two layers.

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
#: GitHub archives fetched by commit, and the branch archive each replaced.
COMMIT_ARCHIVES = REPO / "tools" / "migrate" / "commit-archives.json"
#: The compiler a DOSBox command runs: `C:\\BIN\\CL.EXE` gives `BIN`.
_DOS_COMPILER = re.compile(r"C:\\+([A-Za-z0-9_]+(?:\\+[A-Za-z0-9_]+)*)\\+[A-Za-z0-9_]+\.EXE")
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
    #: The sha256 of every download the recipe fetches, by pin name ("primary", ...).
    sums: dict[str, str]
    #: For a pin fetched as a commit archive: the sha256 of the branch archive it replaced.
    replaced: dict[str, str]
    #: The compiler version the entry says it is: family and version.
    claim: tuple[str, str]
    #: The in-image directory holding the compiler binary; "" when the recipe names none.
    compiler_dir: str
    #: The entry whose compiler binaries this one declares it shares; "" when none.
    same_compiler_as: str
    #: The entries this one is declared to share a compiler with: its
    #: `same_compiler_as` and its `variant_of`.
    shares: frozenset[str]


def entries() -> dict[str, Entry]:
    """Every catalogue entry, from the rows toolchains.json publishes."""
    sys.path.insert(0, str(REPO))
    import catalog
    import generate
    import toolchains

    prefix = os.environ.get("PREFIX", "rebrew")
    archives = _json(COMMIT_ARCHIVES.read_bytes(), COMMIT_ARCHIVES.name)
    found: dict[str, Entry] = {}
    for profile, entry in catalog.manifest().items():
        row = toolchains.row(profile, entry)
        image = row["image"]
        if not isinstance(image, dict):
            raise CheckError(f"{profile}: catalogue row has no image")
        pins = generate.pin_urls(entry)
        fetches = generate.recipe(entry).get("fetch")
        if not isinstance(fetches, list):
            raise CheckError(f"{profile}: the recipe fetches nothing")
        fetched = [str(fetch.get("pin", "primary")) for fetch in fetches if isinstance(fetch, dict)]
        same = str(row.get("same_compiler_as", ""))
        found[profile] = Entry(
            tag=f"{prefix}/{str(image['tag']).removeprefix('rebrew/')}",
            sums={name: pins[name][1] for name in fetched},
            replaced={
                name: str(archive["branch_sha256"])
                for name in fetched
                if isinstance(archive := archives.get(pins[name][0]), dict)
                and archive.get("sha256") == pins[name][1]
            },
            claim=(str(row["family"]), str(row["version"])),
            compiler_dir=compiler_dir(entry),
            same_compiler_as=same,
            shares=frozenset(filter(None, (same, str(row.get("variant_of", ""))))),
        )
    return found


def compiler_dir(entry: Json) -> str:
    """The in-image directory of the entry's compiler, or "" when the recipe names none.

    A DOSBox recipe names its compiler as a `C:\\...\\X.EXE` path in its command,
    with C: mounted from the wrapper's `dir`.
    """
    import generate

    recipe = generate.recipe(entry)
    binary = recipe.get("binary")
    if isinstance(binary, str) and binary:
        return str(Path(generate.binary_path(entry)).parent)
    wrapper = recipe.get("wrapper")
    if not isinstance(wrapper, dict) or wrapper.get("shape") != "dosbox_compile":
        return ""
    match = _DOS_COMPILER.search(str(wrapper.get("command", "")))
    if match is None:
        return ""
    return "/".join([str(wrapper.get("dir", "")), *re.split(r"\\+", match.group(1))])


def recipe_pins(
    found: dict[str, Entry], selected: list[str], registry: str
) -> tuple[int, list[str]]:
    """Check 1 for *selected*; (failures, profiles whose image is present)."""
    counts = {"ok": 0, "ok (branch)": 0, "MISMATCH": 0, "NO-SUMS": 0, "absent": 0}
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
        missing = [(name, sha) for name, sha in entry.sums.items() if sha not in sums]
        branch = [name for name, _sha in missing if entry.replaced.get(name) in sums]
        if not missing:
            counts["ok"] += 1
            print(f"ok            {profile:30s} {entry.tag}")
        elif len(branch) == len(missing):
            counts["ok (branch)"] += 1
            print(
                f"ok (branch)   {profile:30s} {entry.tag}: built from the branch archive "
                f"its commit archive replaced ({entry.replaced[branch[0]][:12]})"
            )
        elif sums:
            counts["MISMATCH"] += 1
            checked = ", ".join(sorted(s[:12] for s in sums))
            pinned = ", ".join(
                sha[:12] if name == "primary" else f"{name} {sha[:12]}" for name, sha in missing
            )
            print(
                f"MISMATCH      {profile:30s} {entry.tag}: the recipe checked {checked}; "
                f"the catalogue pins {pinned}"
            )
        else:
            counts["NO-SUMS"] += 1
            print(f"NO-SUMS       {profile:30s} {entry.tag}: the recipe checked no sha256")
    print(
        f"\nrecipe pins, {len(selected)} entries: ok {counts['ok']}, "
        f"ok (branch) {counts['ok (branch)']}, "
        f"MISMATCH {counts['MISMATCH']}, NO-SUMS {counts['NO-SUMS']}, absent {counts['absent']}"
    )
    return counts["MISMATCH"] + counts["NO-SUMS"], present


def distinct_compilers(found: dict[str, Entry], present: list[str]) -> int:
    """Check 2: print byte-identical compiler directories; count the failures."""
    digests: dict[str, str] = {}
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
        digests[profile] = digest
    for profile, digest in sorted(digests.items()):
        same = found[profile].same_compiler_as
        if not same:
            continue
        if same not in digests:
            print(f"unverified    {profile:30s} same_compiler_as {same}, which has no image here")
        elif digests[same] == digest:
            print(f"declared      {profile} {same}: identical binaries ({digest[:12]})")
        else:
            failures += 1
            print(
                f"DIFFERENT     {profile} {same}: same_compiler_as is declared, "
                f"but the binaries differ ({digest[:12]}, {digests[same][:12]})"
            )
    groups: dict[str, list[str]] = {}
    for profile, digest in digests.items():
        groups.setdefault(digest, []).append(profile)
    for digest, members in sorted(groups.items()):
        if len(members) == 1:
            continue
        undeclared = _untied(found, members)
        if len(undeclared) == 1:
            continue
        failures += 1
        names = " ".join(sorted(members))
        said = "; ".join(
            sorted(" ".join(filter(None, found[p].claim)) + f" ({p})" for p in undeclared)
        )
        print(
            f"SAME-COMPILER {names}: identical binaries ({digest[:12]}), "
            f"no same_compiler_as ties {said}"
        )
    print(f"compiler binaries, {len(present)} images: {failures} failing")
    return failures


def _untied(found: dict[str, Entry], members: list[str]) -> list[str]:
    """One member of each set the declarations tie together within *members*."""
    root = {member: member for member in members}

    def find(member: str) -> str:
        while root[member] != member:
            member = root[member]
        return member

    for member in members:
        for other in found[member].shares & set(members):
            root[find(member)] = find(other)
    return sorted({find(member) for member in members})


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
        print("compiler binaries: not compared (a registry serves layers, not files)")
    else:
        failures += distinct_compilers(found, present)
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except CheckError as error:
        print(f"images: {error}", file=sys.stderr)
        raise SystemExit(1) from error
