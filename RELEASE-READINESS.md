# Release readiness: 1.15.0 — 2026-11-13

Inspected fetched origin branches/tags, local branches, stashes and worktrees. Only main and its one worktree remain; no unique branches or stashes required deletion. No dependency pins changed. Existing tags remain intact.

Verification passed: `uv run --no-sync make lint` (lock consistency, ShellCheck, Ruff checks/format, mypy) and `uv run --no-sync make test verify` (wrapper regressions, 63 Python tests, migration comparison against 07a7268: 272 compared, 63 new, 26 acknowledged, zero differences). Docker runtime smoke gate passed all 20 cases, including both KVM dosemu2 cases, Delphi module-name checks and MASPSX assembler checks. No cases were skipped and no gates were relaxed. Scheduled download-pin drift checks are separate from the per-push gate.

Deployment: no configured production destination or production rollout runbook is present. This source release does not change a running service. Container recipes and illustrative deployments do not select production infrastructure.

Cleanup: removed disposable caches: .ruff_cache, .mypy_cache, __pycache__, tests/__pycache__, tools/migrate/__pycache__, .scratch (empty). Preserved the installed environment, compiler materials, toolchain images and shared Docker caches used by live processes. Smoke scratch output was removed by its cleanup trap.
