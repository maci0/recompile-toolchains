"""Contract tests for the toolchain image matrix.

Every toolchain image is built from ``<family>/<version>-<arch>/Dockerfile``
and pinned by a ``sources.json`` entry.  These tests pin the uniformity that
matters: a complete manifest whose pin agrees with the Dockerfile, the OCI
labels every image carries, an absolute entrypoint wrapper, the non-root
runtime user, an install root under ``/opt``, and a wrapper that goes through
the shared ``base/wrapper-common.sh`` helpers instead of calling wine or
DOSBox directly (the drift this guards against: older images ran
``exec wine`` and skipped ``REBREW_RUNNER``).
"""

from __future__ import annotations

import json
import re
import unittest
from collections.abc import Mapping
from pathlib import Path

import catalog  # repo root is on sys.path under `python -m unittest discover`
import generate
import toolchains

_REPO = Path(__file__).resolve().parents[1]

_OCI_LABELS = ("source", "licenses", "title", "description")

#: The shared run helpers a wrapper may dispatch through.  A wine image uses
#: ``rebrew_run``, a DOSBox image ``rebrew_dosbox_compile`` /
#: ``rebrew_dosbox_run``, a DOS-binary image ``rebrew_dosemu_run`` (dosemu2),
#: a native-binary image ``rebrew_exec``.
_RUN_HELPERS = (
    "rebrew_run",
    "rebrew_dosbox_compile",
    "rebrew_dosbox_run",
    "rebrew_dosemu_run",
    "rebrew_exec",
)


#: A release tag that names a moving target (a rolling CI release), not a version.
_MOVING_TAG = re.compile(r"/releases/download/(latest|main|master|main-release)/")
#: A GitHub archive of one commit; the commit must be the entry's `commit`.
_CODELOAD_COMMIT = re.compile(r"https://codeload\.github\.com/[^/]+/[^/]+/tar\.gz/([0-9a-f]{40})$")
#: Pins whose bytes upstream serves only under a moving tag: no versioned
#: release and no commit holds them (checked 2026-11-22).  Each needs a dated
#: mirror release, as base-dosemu's dosemu2 packages have in
#: archaic-toolchains/dosemu2-noble, before it can leave this list.
_AWAITING_MIRROR = frozenset(
    {
        ("gcc-2.7.2-kmc", "primary"),
        ("gcc-2.7.2-kmc", "binutils"),
        ("gcc-2.8.1-pm", "primary"),
        ("gcc-2.8.1-pm", "binutils"),
        ("gcc-4.4.0-mips64-elf", "primary"),
        ("gcc-egcs-1.1.2-4", "primary"),
    }
)


def _toolchain_dirs() -> list[Path]:
    """Every ``<family>/<version>-<arch>`` directory (``base/`` excluded)."""
    return sorted(path.parent for path in _REPO.glob("*/*/Dockerfile"))


def _manifest() -> dict[str, dict[str, str]]:
    text = (_REPO / "sources.json").read_text(encoding="utf-8")
    data: dict[str, dict[str, str]] = json.loads(text)
    return data


def _pins(entry: Mapping[str, object]) -> list[tuple[str, str, str]]:
    """Every pinned download as ``(name, url, sha256)``.

    The primary pin plus each secondary pin (``<name>_url`` /
    ``<name>_sha256``: a parser, a helper, an SDK, binutils) and each
    ``extra_pins`` entry.  Secondary pins once slipped past this file — the
    PSY-Q 4.5 SDK download lived here with no hash at all — so they are swept
    too.
    """
    pins = [("primary", str(entry.get("url", "")), str(entry.get("sha256", "")))]
    for key, value in entry.items():
        if key.endswith("_url"):
            name = key[: -len("_url")]
            pins.append((name, str(value), str(entry.get(f"{name}_sha256", ""))))
    extra = entry.get("extra_pins")
    if isinstance(extra, list):
        for index, pin in enumerate(extra):
            if isinstance(pin, dict):
                pins.append((f"extra{index}", str(pin.get("url", "")), str(pin.get("sha256", ""))))
    return pins


class TestManifest(unittest.TestCase):
    def test_every_entry_is_complete(self) -> None:
        for profile, entry in _manifest().items():
            for key in ("family", "host_dir", "url", "sha256", "commit"):
                self.assertIn(key, entry, f"{profile}: missing {key}")
            self.assertTrue(entry["family"], profile)
            self.assertTrue(entry["host_dir"], profile)
            self.assertTrue(entry["url"].startswith("https://"), profile)
            self.assertEqual(len(entry["sha256"]), 64, f"{profile}: bad sha256")
            for name, url, sha in _pins(entry):
                self.assertTrue(url.startswith("https://"), f"{profile}: {name} url")
                self.assertEqual(len(sha), 64, f"{profile}: {name} has no sha256")

    def test_every_pin_names_an_immutable_reference(self) -> None:
        """A tagged release must stay buildable after its upstreams move on.

        The sha256 holds the bytes, so a moved reference never installs
        something else; it makes the recipe unbuildable instead.  A GitHub
        archive is fetched by the commit `commit` records, never a branch, and
        no pin names a rolling release tag except the ones awaiting a mirror.
        """
        for profile, entry in _manifest().items():
            for name, url, _sha in _pins(entry):
                self.assertNotIn("refs/heads/", url, f"{profile}: {name} fetches a branch head")
                if _MOVING_TAG.search(url):
                    self.assertIn(
                        (profile, name), _AWAITING_MIRROR, f"{profile}: {name} names a moving tag"
                    )
            archive = _CODELOAD_COMMIT.match(entry["url"])
            if archive:
                self.assertEqual(archive.group(1), entry["commit"], f"{profile}: commit")
        for profile, name in _AWAITING_MIRROR:
            urls = {pin: url for pin, url, _sha in _pins(_manifest()[profile])}
            self.assertRegex(urls[name], _MOVING_TAG, f"{profile}: {name} is mirrored: unlist it")

    def test_tool_root_is_inside_the_install_root(self) -> None:
        """Consumers derive the compiler's INCLUDE and LIB from `tool_root`.

        `msvc-7.0-rtm` declared `/opt/msvc7.0-rtm/Vc7/bin` while its recipe
        installed into `/opt/msvc7.0`, so headers and libraries resolved to a
        directory a rebuilt image would not have.
        """
        for profile, entry in catalog.manifest().items():
            tool_root = entry.get("tool_root")
            if not isinstance(tool_root, str) or not tool_root:
                continue
            root = f"/opt/{generate.install_root(entry)}"
            self.assertTrue(
                tool_root == root or tool_root.startswith(f"{root}/"),
                f"{profile}: tool_root {tool_root} is outside the install root {root}",
            )

    def test_every_pin_appears_in_its_dockerfile(self) -> None:
        for profile, entry in _manifest().items():
            text = (_REPO / entry["host_dir"] / "Dockerfile").read_text(encoding="utf-8")
            for name, url, sha in _pins(entry):
                self.assertIn(url, text, f"{profile}: {name} url not in its Dockerfile")
                self.assertIn(sha, text, f"{profile}: {name} sha256 not in its Dockerfile")

    def test_declared_runner_is_the_one_the_wrapper_uses(self) -> None:
        """The manifest says how each image runs its compiler; the wrapper is
        what actually does it.  They disagreed for 151 profiles — every image
        whose wrapper calls `rebrew_run` was recorded as `wibo` (the opt-in
        runner, not the default) and the DOSBox ones as `exec` — because the
        catalog sniffed the artifact instead of reading the manifest.
        """
        for profile, entry in _manifest().items():
            directory = _REPO / str(entry["host_dir"])
            dockerfile = (directory / "Dockerfile").read_text(encoding="utf-8")
            # code, not comments: a wrapper's prose mentions the helpers it
            # does *not* call ("the shared rebrew_run/rebrew_exec dispatcher")
            wrappers = "\n".join(
                line
                for path in sorted(directory.glob("*.sh"))
                for line in path.read_text(encoding="utf-8").splitlines()
                if not line.strip().startswith("#")
            )
            if "/usr/local/bin/daze" in wrappers:
                observed = "daze"
            elif "rebrew_dosemu_run" in wrappers:
                observed = "dosemu2"
            elif "rebrew_dosbox_run" in wrappers or "rebrew_dosbox_compile" in wrappers:
                observed = "dosbox"
            elif "rebrew_run" in wrappers:
                # wine is the default; `REBREW_RUNNER=wibo` opts into the
                # minimal loader some decomp.me-packaged tools need
                observed = "wibo" if "ENV REBREW_RUNNER=wibo" in dockerfile else "wine"
            elif "rebrew_exec" in wrappers:
                observed = "exec"
            else:
                self.fail(f"{profile}: wrapper calls no known runner helper")
            recipe = entry.get("recipe")
            declared = recipe.get("runner") if isinstance(recipe, dict) else None
            self.assertEqual(declared, observed, f"{profile}: declared runner")

    def test_variants_name_a_base_they_share_a_build_with(self) -> None:
        """`variant_of` is a claim about the data, so it is checked against it.

        A variant compiles with the same archive as the profile it names —
        that is what makes it a front end rather than a different compiler —
        and it has to differ somewhere, or it is a duplicate profile.
        """
        manifest = _manifest()
        for profile, entry in manifest.items():
            base = entry.get("variant_of")
            if not base:
                continue
            self.assertIn(base, manifest, f"{profile}: variant_of names nothing")
            other = manifest[str(base)]
            self.assertEqual(other["url"], entry["url"], f"{profile}: different archive")
            self.assertEqual(other["sha256"], entry["sha256"], f"{profile}: different build")
            self.assertNotIn("variant_of", other, f"{profile}: {base} is itself a variant")
            # and it has to differ somewhere, or it is the same image twice.
            # The pipeline wrappers are hand-written, so their difference lives
            # in the wrapper's reason rather than in a `binary` field: compare
            # the recipes as a whole.
            self.assertNotEqual(entry["recipe"], other["recipe"], f"{profile}: same as {base}")

    def test_same_compiler_names_another_entry_of_the_family(self) -> None:
        """`same_compiler_as` declares one compiler under two ids.

        Two product versions (`msvc-1.52`, `msvc-1.5`) or service packs that
        left the compiler unchanged (`msvc-6.0-sp1`, `msvc-6.0`).  `make images`
        verifies the binaries; this pins the declaration itself: it names a
        real, undeclared entry of the same family.
        """
        rows = {
            profile: toolchains.row(profile, entry) for profile, entry in catalog.manifest().items()
        }
        for profile, row in rows.items():
            other = row.get("same_compiler_as")
            if not isinstance(other, str):
                continue
            self.assertIn(other, rows, f"{profile}: same_compiler_as names nothing")
            self.assertNotIn("same_compiler_as", rows[other], f"{profile}: {other} declares too")
            self.assertEqual(rows[other]["family"], row["family"], f"{profile}: another family")

    def test_every_dockerfile_has_a_manifest_entry(self) -> None:
        """Reverse sweep: a Dockerfile whose download pins nothing is a gap."""
        dirs = {str(d.relative_to(_REPO)) for d in _toolchain_dirs()}
        self.assertEqual(dirs, {e["host_dir"] for e in _manifest().values()})


class TestImageContract(unittest.TestCase):
    def test_fetch_destinations_exist_before_the_download(self) -> None:
        """Every `curl -o <dest>` is preceded, in an earlier RUN (or its own),
        by a `mkdir -p` of `<dest>`'s parent.  Each RUN is a fresh layer, so
        a destination whose directory nothing has made yet fails the build
        with a bare `curl: (23) Failure writing output to destination` —
        which is how the sn64/egcs/Apple-GCC fetch RUNs broke while every
        gate stayed green: their `RUN curl` wrote into directories the
        generator only `mkdir`d later.
        """
        for d in _toolchain_dirs():
            lines = (d / "Dockerfile").read_text(encoding="utf-8").splitlines()
            made = {"/tmp"}  # noqa: S108 — the shared scratch dir, always present
            for number, line in enumerate(lines, start=1):
                for chunk in line.split("&&"):
                    token = chunk.strip().removeprefix("RUN ").strip()
                    if token.startswith("mkdir -p "):
                        made.update(token[len("mkdir -p ") :].split())
                match = re.search(r"curl [^&]*?-o (\S+)", line)
                if not match:
                    continue
                parent = str(Path(match.group(1).strip('"')).parent)
                self.assertIn(
                    parent,
                    made,
                    f"{d}:{number}: curl writes before mkdir -p {parent}",
                )

    def test_entrypoint_is_chmodded_after_it_is_copied(self) -> None:
        """The wrapper is COPYed in, then made executable.

        A `chmod +x /usr/local/bin/<entrypoint>` in the install steps runs
        before the COPY, when there is no such file — the image fails to
        build.  It is a cheap contract to state and needs no Docker daemon to
        check, which is why it caught nothing until the smoke run did.
        """
        for d in _toolchain_dirs():
            lines = (d / "Dockerfile").read_text(encoding="utf-8").splitlines()
            copied = next(
                (
                    i
                    for i, line in enumerate(lines)
                    if line.startswith("COPY ") and "/usr/local/bin/" in line
                ),
                None,
            )
            if copied is None:
                continue
            entrypoint = lines[copied].split()[-1]
            for index, line in enumerate(lines):
                if f"chmod +x {entrypoint}" in line:
                    self.assertGreater(
                        index, copied, f"{d}: chmod of the entrypoint before its COPY"
                    )

    def test_carries_the_oci_labels(self) -> None:
        for d in _toolchain_dirs():
            text = (d / "Dockerfile").read_text(encoding="utf-8")
            for key in _OCI_LABELS:
                self.assertIn(f"org.opencontainers.image.{key}", text, f"{d}: {key}")

    def test_entrypoint_is_an_absolute_wrapper(self) -> None:
        for d in _toolchain_dirs():
            text = (d / "Dockerfile").read_text(encoding="utf-8")
            self.assertRegex(
                text,
                r'(?m)^ENTRYPOINT \["/usr/local/bin/[^"]+"\]$',
                f"{d}: ENTRYPOINT must be an absolute /usr/local/bin wrapper",
            )

    def test_installs_as_root_and_runs_as_the_unprivileged_user(self) -> None:
        for d in _toolchain_dirs():
            text = (d / "Dockerfile").read_text(encoding="utf-8")
            self.assertRegex(text, r"(?m)^USER root$", f"{d}: install steps need root")
            self.assertRegex(text, r"(?m)^USER rebrew$", f"{d}: must drop the runtime user")

    def test_install_root_is_under_opt(self) -> None:
        for d in _toolchain_dirs():
            self.assertIn("mkdir -p /opt/", (d / "Dockerfile").read_text(encoding="utf-8"), d)

    def test_every_toolchain_directory_is_manifested(self) -> None:
        """Any directory carrying image inputs must be a manifest host_dir.

        The reverse sweep above only looks at directories holding a
        Dockerfile; a directory with just a wrapper file (what a template
        escaping bug leaves behind) would otherwise slip through.
        """
        known = {str(e["host_dir"]) for e in _manifest().values()}
        for path in sorted(_REPO.glob("*/*")):
            if not path.is_dir():
                continue
            has_inputs = (path / "Dockerfile").exists() or next(path.glob("*.sh"), None)
            self.assertTrue(
                has_inputs is None or str(path.relative_to(_REPO)) in known,
                f"{path.relative_to(_REPO)}: image inputs but no manifest entry",
            )

    def test_wrapper_goes_through_the_shared_helpers(self) -> None:
        """Inline wrappers and sibling ``*.sh`` wrappers are both allowed, but
        every one of them must source ``wrapper-common.sh`` and dispatch
        through a shared run helper."""
        for d in _toolchain_dirs():
            parts = [(d / "Dockerfile").read_text(encoding="utf-8")]
            parts += [p.read_text(encoding="utf-8") for p in sorted(d.glob("*.sh"))]
            blob = "\n".join(parts)
            self.assertIn("wrapper-common.sh", blob, f"{d}: wrapper does not source the helpers")
            self.assertTrue(
                any(helper in blob for helper in _RUN_HELPERS),
                f"{d}: wrapper uses none of {_RUN_HELPERS}",
            )


#: A base stage's FROM: one of the repository's own bases, or an image by digest ARG.
_BASE_FROM = re.compile(r"FROM (\$\{(?:HELPER|NOBLE)_IMAGE\}|\S+@\$\{(\w+_DIGEST)\})(?: AS \S+)?$")
#: The package list of one `apt-get install`, up to the next `&&`.
_APT_INSTALL = re.compile(r"apt-get (?:-o \S+ )*install -y --no-install-recommends ([^&]+)")


class TestBases(unittest.TestCase):
    """Every toolchain image sits on a base, so the bases are pinned by bytes too.

    A rebuilt base must run the release's OS and Wine/dosemu2 packages: each
    OS image is pinned by digest, each distribution package by exact version
    from a dated snapshot archive the sources are switched to.
    """

    def _dockerfiles(self) -> dict[str, str]:
        found = {
            path.parent.name: re.sub(r"\\\n\s*", " ", path.read_text(encoding="utf-8"))
            for path in sorted(_REPO.glob("base*/Dockerfile"))
        }
        self.assertEqual(set(found), set(generate.BASES))
        return found

    def test_every_base_image_is_pinned_by_digest(self) -> None:
        for name, text in self._dockerfiles().items():
            for line in (ln for ln in text.splitlines() if ln.startswith("FROM ")):
                match = _BASE_FROM.match(line)
                self.assertIsNotNone(match, f"{name}: {line} is not pinned by digest")
                if match and match.group(2):
                    self.assertRegex(text, rf"ARG {match.group(2)}=sha256:[0-9a-f]{{64}}\n", name)

    def test_every_package_comes_at_a_version_from_a_snapshot(self) -> None:
        for name, text in self._dockerfiles().items():
            for match in _APT_INSTALL.finditer(text):
                # A local .deb is the file the same RUN downloaded and checked by sha256.
                for package in match.group(1).split():
                    self.assertTrue(
                        package.endswith(".deb") or re.fullmatch(r"[a-z0-9.+-]+=\S+", package),
                        f"{name}: {package} has no exact version",
                    )
            # A base on an OS image switches its sources; one on a base inherits them.
            if re.search(r"^FROM \S+@\$\{\w+_DIGEST\}", text, re.MULTILINE):
                self.assertRegex(text, r"URIs: https?://snapshot\.(debian\.org|ubuntu\.com)/", name)
                self.assertIn('Acquire::Check-Valid-Until "false";', text, name)


if __name__ == "__main__":
    unittest.main()
