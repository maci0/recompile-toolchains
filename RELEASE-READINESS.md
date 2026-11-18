# Release readiness: 1.16.0, 2026-11-18

Adds `toolchains.json.sha256`, the published digest of `toolchains.json` (CHANGELOG). `toolchains.json` is byte-identical to 1.15.0 (sha256 `f850d0755b68d489fc501575a199e4ad94d6e6098bee1fb838cd24d85c84970a`), and no Dockerfile, wrapper or `sources.json` entry changed since 1.15.0. No dependency pins changed.

Verification passed on the release commit's tree, with uv 0.13.6: `uv sync --group lint --locked`, `uv run --no-sync make lint` (lock consistency, ShellCheck, Ruff checks/format, mypy), `uv run --no-sync make test` (wrapper regressions, 66 Python tests), `uv run --no-sync make verify` (272 compared, 63 new, 26 acknowledged, 0 differ against 07a7268) and `sha256sum -c toolchains.json.sha256` (`toolchains.json: OK`). The Docker smoke gate (`make smoke`) passed all 20 cases with none skipped. The pin check (`make pins`) checked 507 pinned URLs with 0 failing. No gates were relaxed.

Deployment: no configured production destination. This source release changes no running service; consumers fetch the manifest and its checksum file from the tag.
