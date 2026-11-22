# Changelog

## [Unreleased]

### Changed

- `make images` checks what it was assumed to check. It verifies the sha256 of every download a recipe fetches (parser, helper, SDK, binutils, the Daze notices), not the primary source alone, so a re-pinned secondary download fails an image built before it. It compares every entry's compiler: 30 recipes named no `binary` (7 handwritten: `delphi-1.0`, the two SNEW, `icc-5.0.1-010525z`, `ido-4.1`, both Saturn Cygnus; 23 pipelines: 12 PSY-Q, 7 SN64, 4 Apple GCC) and were printed `unchecked`; each now names its compiler or compiler stage (`DCC.EXE`, `CC1PSX.EXE`, `cc1n64.exe`, `cc1`, `CC1.EXE`, `Bin/icl.exe`, `usr/bin/cc`), checked present in the 11 of them built locally, and `make test` refuses a recipe without one. Byte-identical compilers under two entries pass only when `same_compiler_as` or `variant_of` ties them, whatever version they claim: they used to pass silently when both claimed one version, which an SP4 tag holding the SP6 tree would. `same_compiler_as` may therefore name an entry of the same version.
- `same_compiler_as` declarations: `msvc-6.0-sp1` and `msvc-6.0-sp2` name `msvc-6.0` (their `VC98/Bin` is the RTM tree file for file, as their READMEs say: VC 6.0 SP1 and SP2 shipped no compiler; the trees differ in MFC and CRT sources, libraries and redistributables), `msvc-7.0-rtm` names `msvc-7.0` (one archive; `msvc-6.0-sp5-crt` shares `msvc-6.0-sp5`'s archive but adds a `msvcrt.dll` to `VC98/Bin`, so its compiler directory differs and it declares nothing), and `msvc-5.0-sp2` names `msvc-5.0-sp1`: its archive holds `msvc-5.0-sp1`'s tree file for file except `README.md`, which names `msvc500`, and its entry now says so in `notes`.
- `msvc-9.0-sp1`'s entry says that its compiler targets Itanium: the `VC/bin/cl.exe` the wrapper runs prints "Microsoft (R) C/C++ Optimizing Compiler Version 15.00.30729.01 for Itanium" and writes Intel Itanium COFF objects, on the published image (`f67a1c0dcabd`) and on a rebuild alike. The archive (`archaic-toolchains/msvc900_sp1`) carries that compiler as the x86 SP1 build; the entry stays until it is replaced.
- `make images REGISTRY=<url>` says why it compares no binaries: a registry serves layers, and each entry installs under its own `/opt` root, so one compiler in two images is two layers.

### Fixed

- Two `commit` fields named no commit: `agbccpp` recorded `ac51b05a...`, the object of the annotated tag `cp` in `notyourav/agbcc`, and now records the commit that tag points to (`02616ee0...`); `borland-5.6` recorded the abbreviation `09bcecc81184` and now the full `09bcecc8...0e686f9530`. `make test` refuses a `commit` that is not empty or a full 40-character id. `toolchains.json` publishes the field as `source.commit`; the README and `docs/ADDING-TOOLCHAIN.md` now say what it holds: the commit a GitHub archive URL names, the decompme/compilers commit whose `values.yaml` lists a decompme-catalogued asset (`0884197d`, 162 entries, among them release assets of other repositories such as `gcc-4.4.0-mips64-elf`), or a commit of the asset's upstream repository. It is provenance, not a download reference.
- `docs/TOOLCHAINS.md` says what each entry's recipe is checked for: `make test` renders every recipe with its pins, `make pins` resolves every URL and `make verify` compares migrated recipes, but only `make smoke` builds images, and the release notes name the images rebuilt for a release.
- Every GitHub archive is fetched by the commit `sources.json` records instead of a branch head. 36 entries (Borland 2.0, 3.1 and 5.5, Delphi 1.0 and every MSVC from 1.0 to 11.0 with its service packs) fetched `codeload.github.com/.../tar.gz/refs/heads/{main,master}`: the sha256 held the bytes, but any push to one of those branches would have made the tagged recipe unbuildable. Each branch head was still the recorded commit and still served the pinned bytes on 2026-11-22; the archive of that commit holds the same tree member for member (path, mode, content), and its sha256 differs only because its top directory is named after the commit, so each entry carries the commit archive's sha256 now. The two SNEW recipes fetch `modern-asn64.py` from the upstream commit that holds the pinned bytes instead of the rolling `main-release` asset. Six pins remain on rolling release tags, because no versioned release or commit serves their bytes: `gcc-2.7.2-kmc` and `gcc-2.8.1-pm` (compiler and binutils), `gcc-4.4.0-mips64-elf` and `gcc-egcs-1.1.2-4`; they await a dated mirror. `make test` refuses a branch head and a rolling tag outside that list. An image built before this change verified the branch archive's sha256, so `make images` reports it as `MISMATCH` until it is rebuilt; the compiler it installs is the same.

- The three base images are pinned by bytes. `base-noble` was `FROM ubuntu:noble` by tag; it is now `ubuntu:noble@sha256:882e1e56...` (`noble-20261110.1`, the image `rebrew/base-noble:1.0` was last built on), beside `base`'s existing `debian:bookworm-slim` digest. Every distribution package the bases install (Wine, DOSBox, dosemu2's runtime libraries, the libfaketime build tools) comes at an exact version from snapshot.debian.org (`DEBIAN_SNAPSHOT=20261112T180000Z`) or snapshot.ubuntu.com (`UBUNTU_SNAPSHOT=20261121T180000Z`), archive states at which a rebuilt `base`, `base-noble` and `base-dosemu` list the same installed package versions as `rebrew/base:1.0`, `rebrew/base-noble:1.0` and `rebrew/base-dosemu:1.0` (`dpkg-query`, 304, 109 and 227 packages). The images keep the snapshot sources and `Acquire::Check-Valid-Until` off, so a toolchain recipe's own `apt` packages read the same archive state instead of the live mirror. `base` refuses a snapshot older than the one its Debian image names. The dosemu2 and dj64 packages stay pinned by URL and sha256 from `archaic-toolchains/dosemu2-noble`. `make test` checks that every base `FROM` names a digest and every package an exact version.

## [1.17.0] - 2026-11-21

### Added

- `same_compiler_as`, an optional `sources.json` field published in `toolchains.json`: the profile whose compiler binaries this one ships byte for byte, so the two product versions produce identical objects. `msvc-1.52` declares `msvc-1.5` (both C/C++ 8.00c). `make images` passes byte-identical compilers of two versions only under this declaration and fails a declaration whose binaries differ (`DIFFERENT`); `make test` checks that it names another version of the same family. A consumer may ignore the field.

- `make images` (`tests/check_images.py`) checks images already built, in the local engine or, with `REGISTRY=<url>`, in a registry (manifest and config only). It fails when an image's build history does not verify its catalogue entry's `source.sha256` (`MISMATCH`), verifies no sha256 at all (`NO-SUMS`), lacks the compiler directory its recipe names (`NO-COMPILER`), or when two entries that claim different compiler versions (family and version) hold byte-identical compiler directories (`SAME-COMPILER`, local images; ids of one version that share binaries, such as service packs that left the compiler unchanged, print as `alias`). A DOSBox recipe's compiler directory is the one its command runs (`C:\BIN\CL.EXE`); on the rebuilt 16-bit images the check reports `msvc-1.5` and `msvc-1.52` as one compiler (C/C++ 8.00c, byte-identical `BIN`). A re-pin does not rebuild the images built before it: the LAN registry's `rebrew/msvc:7.0-win32`, built on 2026-09-12 while `msvc-7.0` still pinned `archaic-msvc/msvc710`, served the 7.1 compiler under the 7.0 tag after the pin moved to `msvc700` on 2026-09-13. The check reports it as `MISMATCH` and, beside `msvc-7.1`, as `SAME-COMPILER`.

### Changed

- The README and `docs/TOOLCHAINS.md` say what an entry is: a recipe and the tag `./build.sh` gives its image, not a published image. A deployment runs the ids whose images its runtime holds; `make images` lists them.

### Fixed

- `msvc-7.0-rtm` installs into `/opt/msvc7.0-rtm`, the directory its `tool_root` names and the published `rebrew/msvc:7.0-rtm-win32` image uses. The generated recipe installed into `/opt/msvc7.0`, so a rebuilt image's compiler worked while consumers that derive `INCLUDE` and `LIB` from `tool_root` pointed at a directory the image lacked. `make test` now fails when a `tool_root` lies outside its recipe's install root.
- `tests/smoke.sh <profile>` invokes a selected profile that has no case of its own in its argument dialect: `/c t.c` for `msvc`, `-c t.c` for `borland`, `t.c` for `dos`. It passed `-c t.c -o t.o` to every such profile, so `cl` wrote `t.obj` and every selected MSVC image failed with "no object produced".
- `tests/smoke.sh` keeps its scratch directory under the repository's ignored `.scratch/` instead of `${TMPDIR:-/tmp}`.

## [1.16.0] - 2026-11-18

### Added

- `toolchains.json.sha256`, the sha256 of `toolchains.json` in `sha256sum -c` form, generated by `make docs` and checked by `make test`. Each release tag publishes both files at `https://raw.githubusercontent.com/maci0/recompile-toolchains/<tag>/`, so a consumer fetches and verifies the manifest and its digest instead of copying either by hand (README, Vendoring toolchains.json). `.gitattributes` keeps both files LF so a checkout's bytes match the digest.

## [1.15.0] - 2026-11-13

- Consolidate main and record release qualification and cleanup.

## [1.14.0] - 2026-11-12

### Changed

- Align the contributor checksum instructions and PSY-Q SDK source notes with the verified downloads the generator requires.

### Fixed

- Verify installation commands following an inline wrapper's printf during migration checks.

- Compare the complete Docker entrypoint path and arguments during migration verification.

- Verify ordinary printf installation steps instead of treating every printf as an entrypoint wrapper.

- Compare complete base-image references and Docker build stages in migration verification.

- Compare complete quoted, escaped and legacy Dockerfile environment values during migration verification.

- Read tab-separated Dockerfile instruction keywords without altering quoted argument spaces.

- Preserve quoted Dockerfile argument spacing when verifying install steps and inline wrappers.

- Preserve quoted argument spacing when comparing migrated compiler wrappers.

- Verify mixed-case Dockerfile instructions instead of silently skipping added build steps.

- Verify the copied entrypoint wrapper instead of the first sibling shell file in migration checks.
- Refuse directory output targets in generated ELF adapters instead of moving an object inside them.
- Build explicitly selected base images once, with their dependency chain and canonical tags.

- Reject all-zero image build concurrency and timeout settings before running Docker.
- Reject all-zero watchdog timeout values such as 00 instead of disabling the deadline.
- Reject unknown generator options before a misspelled check can rewrite generated files.

- Detect USER and WORKDIR changes in the migration verifier.
- Detect changed or removed download checksum checks in migration verification.
- Match catalog provenance to the download host and path instead of URL substrings.
- Reject unknown profile or base selections in the download pin checker.

### Changed

- The third-party proprietary toolchain media now download from our copies in the `archaic-toolchains` org (release `2026-11-10` of `watcom1x`, `msvc600-win9x`, `msvc1200_u4`, `irix-ido`, `borland-cpp-ide`, `msvc800-portable`, `saturn-cygnus`, `psyq`, `sn64`, `icc501`, `vc6redist`, `decompdev-compilers` and `decompme-compilers`), byte for byte the files their upstreams served, so every sha256 is unchanged: 215 pins in `sources.json`. Personal repositories, rotating bundle hosts and vendor download pages had already lost the QuickC media and the dosemu builds. Open-source upstreams keep their own URLs. Each mirror's README names the upstream URL of every file, and `tools/migrate/mirrors.json` records each mirror URL's upstream, which `make verify` compares against the migration baseline in its place.
- `base-dosemu` downloads its ten dosemu2, fdpp, dj64 and comcom `.deb` files from our copies in `archaic-toolchains/dosemu2-noble` (release `2026-11-10`), not from the Launchpad PPAs, which delete superseded builds: four of the pinned ones were gone, so `base-dosemu` and every 16-bit DOS image on it could not be built. Six keep their sha256; `comcom32`, `comcom64`, `libdjstub64-0` and `libdjdev64-0` move to the PPAs' 2026-10-16 rebuilds of the same upstream versions.
- `quickc-2.50` downloads its floppy media from our preservation repo `archaic-toolchains/quickc250` (release `2.50`), byte for byte the WinWorld archive it pinned before, so the sha256 is unchanged. WinWorld's mirror answers a direct request with 404 until the client has visited its download page, which failed `make pins`.

## [1.13.0] - 2026-11-09

### Added

- `toolchains.json`, the generated machine-readable catalogue of every profile (pin, image tag, target, runtime class, entrypoint, aliases and the consumer fields `flags_style`, `arg_style`, `obj_ext`, `bits`, `tool_root`), rendered from `sources.json` by `make docs` and checked by `make test`.

## [1.12.0] - 2026-11-04

### Changed

- Roll up the removed DOS runtime download pin fixes and development tool updates as a minor release.

## [1.11.1] - 2026-11-02

### Changed

- Refresh removed DOSEMU2 and djstub downloads to verified upstream artifacts.

- Update Ruff to 0.17.3, mypy to 2.4.1, Python to 3.15.2 and pinned CI actions.

## [1.11.0] - 2026-11-01

### Changed

- Maintenance release: catalog reload and provenance sync.

## [1.10.0] - 2026-10-27

### Changed

- Load `json` with a `lazy import` in `catalog.py`.
- Cancel superseded CI runs per workflow and ref, and cache uv downloads in
  the lint, pins and smoke workflows.

## [1.9.0] - 2026-10-25

### Changed

- Require Python 3.15 and pin contributor and CI interpreters to 3.15.1.

## [1.8.0] - 2026-10-25

### Changed

- Require Python 3.14, pin contributor and CI interpreters to 3.14.9, and
  refresh Ruff and all locked dependencies to their latest stable releases.

## [1.7.0] - 2026-10-25

### Added

- Add 27 pinned compiler profiles: MSVC 12.0 Update 4, DJGPP, PSPDEV,
  PS2DEV EE/IOP, Bootlin m68k, MiNT ELF, LLVM-MOS C64/NES, GBDK,
  SDCC SM83/Z80/STM8/8051, cc65, z88dk, ACK, IA-16, Retro68,
  devkitARM/devkitA64/devkitPPC, QuickC, VBCC, native64 Saturn and
  the dated October Watcom snapshot. The catalog now contains 335 profiles
  across 46 families; preserve existing compiler versions and variants.
- Record repeatable smoke qualification for every canonical profile, source
  pins, image identities, parity checks and remaining matching/runtime limits.

### Fixed

- Build only the selected images' required base chain; replace deleted FDPP
  runtime package pins and retain rootless archive ownership safeguards.
- Support POSIX object compilation for AGBCC, SHC and PSY-Q 4.6 pipelines
  while preserving raw invocations, relative include paths and existing
  outputs on failure. Preserve complete nested SHC support files.
- Build PSY-Q 2.6.3's converter from pinned PCSX-Redux sources, handling
  relocation 30 with code/data/relocation parity under DOSEMU and Daze.
- Validate the PSY-Q ELF adapter in CI smoke tests and recreate host-owned
  failure fixtures safely when the runner and compiler container use different UIDs.
- Keep the papermario compiler's helper path and use pipes to exclude random
  assembly filenames from debug metadata.

## [1.6.0] - 2026-10-24

### Fixed

- Normalize IDO 4.1 and Microsoft C 6.0 archive permissions so the non-root
  compiler user can execute the emulator and stage the compiler payload.

### Added

- Add 22 PS1 GCC variants with maspsx pinned at `4ffa8b5`, plus Daze 0.3.0
  variants for four DOS PSY-Q compilers and Saturn Cygnus 2.7-96Q3. Daze uses
  the Unicorn software backend and includes the release's dependency notices.
  Existing GNU assembler and DOSEMU profiles keep their names and behavior.
- MWCC 4.1 build 51213 patch 1, native Linux Saturn Cygnus 2.7-96Q3,
  Saturn SHC 5.0r32 with SH-2 ELF conversion, GCC 16.2.0 and Clang 23.1.4.
- The verified `msvc8.0sp1` alias for the existing MSVC 8.0 SP1 profile.

### Fixed

- Replace the deleted DOSEMU `libfdldr35` and `libfdpp35` downloads with
  hash-verified versioned packages from the same PPA.

### Changed

- Refresh the dependency lock and current CI interpreter selection; preserve the
  archived compiler versions and source hashes.

### Fixed

- Extract compiler archives without preserving the publisher's numeric owners.
  Rootless engines can unpack LLVM payloads with high upstream UIDs without
  changing host subordinate ID ranges; compiler execution remains non-root.

## [1.5.0] - 2026-10-20

### Changed

- Update Ruff to 0.17.1 and mypy to 2.4.0, with refreshed locked dependencies.
- Pin CI checkout 7.0.1 and setup-uv 10.3.0 by commit.
- Refresh the shared Debian Bookworm base digest to its current security
  snapshot. Compiler archive versions/hashes are unchanged; the accepted
  MSVC payload and fixed-clock compiler output remain byte-identical.

### Fixed

- Clarify the `recompile-toolchains` repository name and retained `rebrew/` image
  tags and `REBREW_*` settings; use the current name in the pin-check user agent.

## [1.4.2] - 2026-10-15

### Added

- The MSVC 6.0 SP5 CRT profile Dockerfile and `cl` wrapper. `sources.json` already named `msvc/6.0-sp5-crt-win32`, and image-contract tests read that Dockerfile.

## [1.4.1] - 2026-10-15

### Added

- MSVC 6.0 SP5 profile that pins the SP5 compiler tree and Microsoft's VC6
  redistributable, and checks the native MSVCRT hash before that DLL is kept.
  Provenance and the toolchain catalog name the source.

### Changed

- CI installs Python through setup-uv.
- The Wine base image keeps the pinned libfaketime source snapshot.
  `SOURCE_DATE_EPOCH` enables the native build clock. The wrapper rejects
  the static wibo runner when that clock is requested, and the wrapper tests
  cover the contract.

## [1.4.0] - 2026-10-14

### Added

- The Delphi 1.0 wrapper accepts complete programs and compiler switches and
  removes stale map files before compiling. Its smoke fixtures cover both
  complete programs and generated function units.

### Changed

- The build source is named `recompile-toolchains` throughout the repository.
  Image names and compiler versions are unchanged.

### Fixed

- Refresh seven dosemu2/dj64 runtime package pins whose superseded Launchpad
  downloads returned 404. Each replacement is pinned to its published file and
  verified SHA-256; the build never selects a package from a moving index.

This release distributes build definitions and wrappers. Proprietary compiler
archives remain external inputs with their existing provenance and hashes.
