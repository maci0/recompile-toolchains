# Changelog

## [Unreleased]

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
