# Changelog

## [Unreleased]

## [1.4.0] - 2026-10-14

### Added

- The Delphi 1.0 wrapper accepts complete programs and compiler switches and
  removes stale map files before compiling. Its smoke fixtures cover both
  complete programs and generated function units.

### Changed

- The build source is named `recompile-toolchains` throughout the repository.
  Image names and compiler versions are unchanged.

This release distributes build definitions and wrappers. Proprietary compiler
archives remain external inputs with their existing provenance and hashes.
