# Changelog

## [Unreleased]

### Changed

- Align the contributor checksum instructions and PSY-Q SDK source notes with the verified downloads the generator requires.

### Fixed

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
