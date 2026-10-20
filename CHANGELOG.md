# Changelog

## [Unreleased]

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
