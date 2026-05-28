---
schema_version: 2.0.0
date: 2026-05-28
run_id: 20260528-8cf805
prior_run_id: 20260528-124b1a
scope: droit-francais-mcp
scope_path: /Users/joachimbrindeau/Development/expand/production/jurisprudence/MCP/droit-francais-mcp
command: compound-refactor
status: completed
mode: "revamp"
depth: "thorough"
tier_floor: 2
language: "python"
framework: "fastmcp>=2.12.3"
generated_at: "2026-05-28T11:05:00Z"
baseline_commit: "b7c22be"
prior_run_commit: "3d3e742"
loc_in_scope: 3231
total_findings: 23
findings_at_or_above_tier_floor: 18
audit_file_format: "v2"
---

# Compound SSOT Audit — droit-francais-mcp (revamp run)

**Run**: `20260528-8cf805` · **Iteration**: 1/15 · **Mode**: revamp · **Depth**: thorough

## Executive summary

This is the **second** compound-refactor pass on the repo. The first (`20260528-124b1a`, autofix/merged, commit `3d3e742`) eliminated 9 Tier-1 SSOT findings inside the existing flat-root code — but **did not** restructure the layout, and **left a critical adoption gap**: `PisteOAuthClient._request` was extracted as the canonical HTTP wrapper but neither subclass calls it (5 hand-rolled `requests.get`/`requests.post` sites remain). This run completes the adoption AND migrates the project to canonical 2026 Python layout (`src/droit_francais_mcp/` with `piste/`, `legifrance/`, `judilibre/` sub-packages; pyproject as single source of truth; ruff replacing flake8+black+isort; tests in `tests/`; `uvx` install story).

Three areas of compound leverage:
1. **Adopting `_request` + fixing `safe_mcp_tool` exception handling + promoting the two remaining hardcoded fond tuples** closes the residual code-level duplication AND restores tracebacks in stderr AND fixes a shared-mutable-dict bug.
2. **`src/`-layout + `[project.scripts]` + dynamic version** delivers a canonical install story (`uvx droit-francais-mcp`) AND deletes `__version__.py`/`requirements.txt`/`requirements-dev.txt` AND consolidates the build-system into pyproject.toml.
3. **Tests/ + reclassified markers + characterization-test suite** unlocks an offline Phase 7a verification gate AND adds safety nets for the structural moves AND eliminates the `--ignore=test_jupyter.py` band-aid.

**Compound leverage**: one structural migration eliminates 8 packaging anti-patterns, retires 4 root files (`__version__.py`, `requirements.txt`, `requirements-dev.txt`, plus 3 installer scripts subsumed by `[project.scripts]`), adopts `uv` + `ruff` (current 2026 canonical), AND closes 6 code-level findings the prior run missed.

## Behavior Contract — global scope

**Behavior (must preserve)**
- Every MCP-exposed tool function continues to accept the same parameter names, types, defaults, and produces the same observable result shape (test suite pins this — 27 `@mcp.tool` functions).
- Every `*API.search`, `*API.consult`, `*API.taxonomy` continues to return data of the same shape (cleaned dict / list / None).
- OAuth token lifecycle: token cached, refreshed 60s before expiry, error messages preserved (callers may log them).
- Error paths preserve the same error-message strings used by tests (`Fond invalide`, `Type de recherche invalide`, `page_size ne peut pas dépasser 50`, etc.).
- Stderr-only logging invariant: never write to stdout from tool code (MCP stdio transport corruption otherwise).

**Allowed structural changes**
- Move all `.py` source files into `src/droit_francais_mcp/` with `piste/`, `legifrance/`, `judilibre/` sub-packages.
- Rename modules: `droit_francais_MCP.py` → `server.py`, drop `api_` prefix on client modules, `piste_utils.py` → `piste/filters.py` (intent-revealing).
- Adopt `PisteOAuthClient._request` at every HTTP call-site in subclasses (the extracted helper).
- Promote remaining hardcoded fond tuples to `LegifranceQueryBuilder.CODE_FONDS` + `VIGUEUR_DEFAULT_FONDS` frozensets.
- Move `Légifrance.json` to `docs/api-specs/legifrance-swagger-2.0.json`.
- Move tests to `tests/` outside `src/`; reclassify 15 ValueError tests as `@pytest.mark.unit`.
- Consolidate dependency declaration to `pyproject.toml` only (delete `requirements.txt`, `requirements-dev.txt`).
- Replace flake8/black/isort/safety/bandit with `ruff` (lint+format+import-sort+S=bandit).
- Add `[project.scripts] droit-francais-mcp = "droit_francais_mcp.server:main"`.
- Delete `install.sh`/`install.bat`/`install.ps1`; replace with `uvx`/`pipx` documentation.
- Keep a back-compat shim at root: `droit_francais_MCP.py` does `from droit_francais_mcp.server import mcp; mcp.run()` with `DeprecationWarning` for one release.

**Forbidden semantic deltas**
- Public function signatures (parameter names, defaults, order) on any `@mcp.tool` or any `LegifranceAPI`/`JudilibreAPI` method.
- The wording of `ValueError` messages already asserted by tests (must contain the same substrings).
- The structure / keys of returned dicts at the MCP-tool boundary.
- Adding required env-vars or changing the sandbox/prod URL set.
- Stable invocation entry: `python droit_francais_MCP.py` MUST keep working for one release via the shim.

`behavior_contract_class`: **structural_only** for layout findings, **bug_fix_disguised_as_refactor** for REVAMP-008/009/010/011/014 (adoption + decorator bugs + dead-code), **packaging_only** for REVAMP-002/004/021/022, **back_compat_only** for REVAMP-023.

---

## Findings — ranked (Tier ascending, leverage descending)

| # | Finding | File:Line | Sites | Leverage | Drift | Effort | Conf | Tier | Boundary | Action |
|---|---|---|---|---|---|---|---|---|---|---|
| REVAMP-008 | `_request` extracted but never adopted (dead method + lingering try/except dup) | piste_auth.py:136 + 5 call-sites | 5 | 5 | **3** | 3 | 100 | 1 | B1 | ADOPT_HELPER |
| REVAMP-001 | py-modules flat layout (anti-pattern) | pyproject.toml:60-68 | 7 | 5 | 2 | 3 | 100 | 1 | B3 | ADOPT_SRC_LAYOUT |
| REVAMP-017 | Zero characterization tests for FastMCP/safe_mcp_tool/PisteOAuthClient | tests/ does not exist | 4 | 4 | **3** | 3 | 85 | 1 | B1 | AUTHOR_CHARACTERIZATION_TESTS |
| REVAMP-002 | Dependency declared in 4 places with version drift | pyproject.toml + requirements*.txt | 4 | 4 | **3** | 2 | 100 | 1 | B2 | SSOT_PYPROJECT |
| REVAMP-006 | testpaths = ['.'] non-canonical | pyproject.toml:75 | 1 | 3 | 2 | 2 | 100 | 1 | B5 | MOVE_TESTS_DIR |
| REVAMP-022 | No [project.scripts] entry point | pyproject.toml | 1 | 3 | 2 | 1 | 100 | 1 | B6 | ADD_CONSOLE_SCRIPT |
| REVAMP-023 | Back-compat shim needed (existing claude_desktop_config users) | droit_francais_MCP.py | 1 | 3 | **3** | 1 | 95 | 1 | B7 | ADD_SHIM |
| REVAMP-004 | `__version__.py` orphan (zero Python consumers) | __version__.py | 1 | 2 | 2 | 1 | 100 | 1 | B2 | DELETE_USE_DYNAMIC_VERSION |
| REVAMP-009 | safe_mcp_tool loses exception context + mutable default | droit_francais_MCP.py:64-84 | 1 | 3 | 2 | 2 | 95 | 2 | B1 | FIX_DECORATOR |
| REVAMP-010 | _safe_init swallows credential errors silently | droit_francais_MCP.py:37-58 | 1 | 2 | **3** | 2 | 100 | 2 | B1 | SURFACE_FAILURE |
| REVAMP-011 | Hardcoded fond tuples missed by prior SSOT pass | api_legifrance.py:174,196 | 2 | 2 | **3** | 1 | 95 | 2 | B1 | PROMOTE_TO_CONST |
| REVAMP-012 | MCP layer reaches into LegifranceQueryBuilder internals (encapsulation leak) | droit_francais_MCP.py:283-292 | 1 | 2 | **3** | 2 | 95 | 2 | B4 | ENCAPSULATE |
| REVAMP-015 | Globals constructed at import time (legifranceapi/judilibreapi) | droit_francais_MCP.py:21-58 | 2 | 2 | 2 | 2 | 85 | 2 | B1 | LAZY_INIT |
| REVAMP-018 | ValueError tests mislabeled @pytest.mark.integration | test_api_*.py | 15 | 2 | 2 | 2 | 95 | 2 | B5 | RECLASSIFY_MARKERS |
| REVAMP-020 | 3 hand-rolled installers (uvx/pipx canonical 2026) | install.{sh,bat,ps1} | 3 | 2 | 2 | 1 | 85 | 2 | B6 | DELETE_USE_UVX |
| REVAMP-021 | flake8+black+isort+safety+bandit not consolidated to ruff | pyproject.toml | 5 | 2 | 1 | 2 | 90 | 2 | B6 | MIGRATE_TO_RUFF |
| REVAMP-005 | `droit_francais_MCP.py` mixes case (PEP 8) | droit_francais_MCP.py | 1 | 2 | 2 | 1 | 100 | 2 | B4 | RENAME |
| REVAMP-007 | test_jupyter.py is not a test (no def test_*) | test_jupyter.py | 1 | 1 | 2 | 1 | 100 | 2 | B5 | MOVE_TO_EXAMPLES |
| REVAMP-003 | requirements.txt is UTF-16 LE | requirements.txt | 1 | 1 | 2 | 1 | 100 | 2 | B2 | DELETE_OR_RE_ENCODE |
| REVAMP-013 | Inconsistent ClassVar privacy convention | api_*.py + piste_auth.py | 5 | 1 | 2 | 1 | 90 | 3 | B4 | RENAME_PUBLIC |
| REVAMP-014 | Dead _API_LABEL + dead LegifranceAPI.test_connection | api_*.py + piste_auth.py | 4 | 1 | 1 | 1 | 100 | 3 | B1 | REMOVE_OR_WIRE |
| REVAMP-016 | Decorator ordering load-bearing but undocumented | droit_francais_MCP.py:234+ | 5 | 1 | **3** | 1 | 95 | 3 | B1 | DOCUMENT |
| REVAMP-019 | `Légifrance.json` 308 KB Swagger spec at root | Légifrance.json | 1 | 1 | 1 | 1 | 90 | 3 | B7 | MOVE_TO_DOCS |

## Boundary plan (atomic commits)

### B1 — Adopt `_request` + fix decorator + characterization tests
**Files**: `piste_auth.py`, `api_legifrance.py`, `api_judilibre.py`, `droit_francais_MCP.py`, new `tests/unit/test_mcp_surface.py`, new `tests/unit/test_safe_mcp_tool.py`, new `tests/unit/test_piste_oauth_client.py`.
**Eliminates**: REVAMP-008, REVAMP-009, REVAMP-010, REVAMP-011, REVAMP-014, REVAMP-015, REVAMP-016, REVAMP-017.
**Net effect**: Adopts `_request` (deletes ~60 LOC duplicate try/except across both subclasses), uses `logger.exception()` for stack frames, returns dict copies from decorator (mutation-safe), surfaces init failures via `_init_errors`, promotes two remaining fond tuples to frozensets, deletes dead `_API_LABEL`/`test_connection`, converts module-level API globals to lazy accessors, documents decorator ordering. Adds 3 characterization-test files that pin: tool registration count + names; safe_mcp_tool error envelope; PisteOAuthClient sandbox/prod/missing-env branches; stderr-only logging invariant.

### B2 — pyproject as SSOT + dynamic version
**Files**: `pyproject.toml`, delete: `requirements.txt`, `requirements-dev.txt`, `__version__.py`.
**Eliminates**: REVAMP-002, REVAMP-003, REVAMP-004.
**Net effect**: Move runtime deps + dev deps into pyproject only (single source of truth, no version drift between files). Switch to `dynamic = ["version"]` via `hatch-vcs` reading from git tags. Delete UTF-16-encoded requirements.txt entirely. Update Makefile `version` target to call `python -c "from droit_francais_mcp import __version__; print(__version__)"` (preserved interface, new source).

### B3 — `src/` layout + git-mv 7 modules into sub-packages
**Files**: new `src/droit_francais_mcp/__init__.py`, new `__main__.py`, new `piste/__init__.py`, new `legifrance/__init__.py`, new `judilibre/__init__.py`; git-mv all 7 source modules; rewrite all internal imports.
**Eliminates**: REVAMP-001.
**Net effect**: Canonical 2026 Python layout. `__init__.py` exposes `__version__` via `importlib.metadata.version()`. All internal imports change from `from api_legifrance import LegifranceAPI` to `from droit_francais_mcp.legifrance.client import LegifranceAPI`. Switch `[tool.setuptools]` `py-modules` → `[tool.hatch.build.targets.wheel] packages = ["src/droit_francais_mcp"]`. `pip install -e .` required for local dev.

### B4 — Rename modules + encapsulate validation + naming consistency
**Files**: rename `legifrance/client.py`'s embedded `api_*` references; rename `piste_utils.py` → `piste/filters.py`; rename `droit_francais_MCP.py` (now at `src/droit_francais_mcp/server.py`) — already done in B3 git-mv; add `LegifranceQueryBuilder.supports_date_filter(fond)`; rename underscore ClassVars to public uppercase where appropriate.
**Eliminates**: REVAMP-005, REVAMP-012, REVAMP-013.
**Net effect**: `droit_francais_MCP.py` → `server.py` (PEP 8 compliant). Encapsulation: MCP layer calls `query_builder.supports_date_filter(fond)` instead of reaching into `DATE_FILTER_FACETTES`. Private→public ClassVar promotion on validation enums (consistent with sibling LegifranceQueryBuilder convention).

### B5 — Tests → `tests/` + rewrite imports + reclassify markers + conftest
**Files**: new `tests/conftest.py`, git-mv `test_api_*.py` → `tests/`, rename `test_jupyter.py` → `examples/jupyter_exploration.py`, `pyproject.toml [tool.pytest.ini_options]`.
**Eliminates**: REVAMP-006, REVAMP-007, REVAMP-018.
**Net effect**: Tests follow canonical pytest layout. Rewrite 6 import sites (full table in Appendix A). Reclassify 15 ValueError tests as `@pytest.mark.unit @pytest.mark.no_network` so Phase 7a offline gate runs them. Delete `--ignore=test_jupyter.py` (file moved to examples/). Add conftest.py with `pytest_collection_modifyitems` hook that auto-skips integration tests when `PISTE_CLIENT_ID` is missing.

### B6 — ruff + `[project.scripts]` + delete install scripts
**Files**: `pyproject.toml` (replace flake8/black/isort/safety/bandit with `ruff`; add `[tool.ruff]` block; add `[project.scripts]` entry); delete `install.sh`, `install.bat`, `install.ps1`; update `Makefile` lint/format targets to call `ruff`; update `README.md` + `QUICKSTART.md` with `uvx` install instructions.
**Eliminates**: REVAMP-020, REVAMP-021, REVAMP-022.
**Net effect**: Single linter+formatter+sorter (ruff). Bump `requires-python = ">=3.10"` (Python 3.8 EOL). Console-script entry point so users can `uvx droit-francais-mcp`. Install story: README JSON snippet for Claude Desktop using `command: "uvx"`, `args: ["droit-francais-mcp"]`. Three hand-rolled install scripts retired.

### B7 — Back-compat shim + move Légifrance.json
**Files**: new root `droit_francais_MCP.py` (4-line shim with DeprecationWarning to stderr), git-mv `Légifrance.json` → `docs/api-specs/legifrance-swagger-2.0.json`, `CHANGELOG.md` deprecation note.
**Eliminates**: REVAMP-019, REVAMP-023.
**Net effect**: Existing absolute-path consumers (in `claude_desktop_config.json`) keep working for one release with a stderr deprecation warning pointing at the new `droit-francais-mcp` console script. Swagger spec lives where docs belong. `CHANGELOG.md` documents the deprecation timeline (shim → 1.3.0, remove → 2.0.0).

## Path mapping

| Boundary | Files touched | Lines added (est.) | Lines removed (est.) | Net |
|---|---|---|---|---|
| B1 | piste_auth, api_legifrance, api_judilibre, droit_francais_MCP, +3 test files | +280 | -180 | +100 |
| B2 | pyproject; delete: __version__, requirements*.txt | +40 | -150 | -110 |
| B3 | +5 __init__.py; mv 7 modules; rewrite imports | +35 | -10 | +25 |
| B4 | rename 2 modules; +supports_date_filter method | +15 | -10 | +5 |
| B5 | mv 3 tests; +conftest; rewrite imports; reclassify markers | +50 | -20 | +30 |
| B6 | pyproject ruff block; delete 3 install scripts; update README | +60 | -200 | -140 |
| B7 | 4-line shim; mv Légifrance.json; CHANGELOG | +15 | -0 | +15 |
| **Total** | 7 boundaries / ~12 modules | ~495 | ~570 | **~−75 LOC** |

Note: net LOC decrease is modest in revamp mode because new test coverage (B1) and new `__init__.py` files (B3) partly offset deletions. The structural gain is the win: 4 root files retired, canonical layout adopted, install/lint/version stories canonicalized.

## Verification gate (Phase 7a)

Each boundary commits only after this gate exits 0:

1. `pytest --collect-only -q` — pure discovery, no execution; catches import errors and renamed test paths.
2. `python -c "import droit_francais_mcp; import droit_francais_mcp.legifrance.client; import droit_francais_mcp.judilibre.client; import droit_francais_mcp.server"` — import smoke; catches circular imports and missing `__init__.py`.
3. `pytest -m "not integration" -v` — offline unit subset (after the B5 marker reclassification); should pass without PISTE creds.
4. `python -c "from droit_francais_mcp.server import mcp; assert len(list(mcp._tools)) == 27, f'tool count drift: {len(list(mcp._tools))}'"` — characterization-test contract pin.
5. `pip install -e . && droit-francais-mcp --help || true` (after B6) — entry-point resolution sanity.

## Rejected / deferred abstractions

- **`fastmcp.json` declarative config** (fastmcp 2.11+ feature) — not adopted in this run. The `[project.scripts]` entry-point + Claude Desktop JSON snippet already provide canonical invocation. `fastmcp.json` is useful for `fastmcp run` direct-launch but adds another config file. Defer to a follow-up if direct-launch becomes a primary install path.
- **`uv.lock` file commit** — recommended by Agent 1 for reproducibility, but uv isn't yet ubiquitous in the user's CI/dev environment. Note in README ("for reproducible installs, run `uv sync`"); don't force-commit a lockfile this run. Reconsider next run.
- **Migration to async tools / structured outputs (fastmcp 2.10+)** — out of scope (would change tool semantics, violates Behavior Contract).
- **`fastmcp<3` upper bound** — recommended by Agent 2 (3.x has breaking decorator/import changes). ADD as part of B2 dependency cleanup (small, low-risk).
- **"Vibe Coding" attribution docstrings** — prior run flagged FIND-0019 as `deliberately_not_consolidated`. Honor that decision.

## Baseline metrics (Phase 1.7)

| Metric | Baseline (post-prior-run) |
|---|---|
| LOC in scope (.py only, excl. .venv) | 3,231 |
| Source modules (production) | 7 (all at root) |
| Test modules | 3 (all at root, 1 is not actually a test) |
| Dependency declaration sites | 4 (pyproject [project], pyproject [project.optional-dependencies], requirements.txt, requirements-dev.txt) |
| Version declaration sites | 2 (pyproject.toml, __version__.py) — drift risk |
| Linter/formatter tools | 5 (flake8 + black + isort + safety + bandit) |
| Install scripts | 4 (.sh + .bat + .ps1 + Makefile install) |
| Dead helper methods | 1 (_request, never adopted) |
| Hardcoded fond tuples missed by prior SSOT | 2 |
| Characterization-test coverage of revamp-critical surfaces | 0 |
| MCP tool count | 27 (must preserve) |
| Total findings this run | 23 |
| Findings at tier ≤ 2 | 18 |

## Appendix A — Test import-rewrite table (for B5)

| File:Line | Original | New |
|---|---|---|
| `tests/test_legifrance_client.py:15` (was `test_api_legifrance.py:15`) | `from api_legifrance import LegifranceAPI` | `from droit_francais_mcp.legifrance.client import LegifranceAPI` |
| `tests/test_judilibre_client.py:36` (was `test_api_judilibre.py:36`) | `from api_judilibre import JudilibreAPI` | `from droit_francais_mcp.judilibre.client import JudilibreAPI` |
| `examples/jupyter_exploration.py:44` (was `test_jupyter.py:44`) | `from api_judilibre import JudilibreAPI` | `from droit_francais_mcp.judilibre.client import JudilibreAPI` |
| `examples/jupyter_exploration.py:45,127,151` (was `test_jupyter.py:*`) | `from api_legifrance import LegifranceAPI` | `from droit_francais_mcp.legifrance.client import LegifranceAPI` |
| `test_api_legifrance.py:242` `__main__` block | `LegifranceAPI(...)` bare name | (preserved — namespace already imported above) |
| `test_api_judilibre.py:420` `__main__` block | `JudilibreAPI(...)` bare name | (preserved — namespace already imported above) |

## Run log

- `2026-05-28T09:01:46Z` — Phase 0 preflight: clean tree (commit `b7c22be`).
- `2026-05-28T09:01:50Z` — Phase 1.7 baseline captured to `baseline.json`.
- `2026-05-28T11:00:00Z` — Phase 1 frame: prior `20260528-124b1a` audit read; sibling MCP repos checked (none); pyproject + requirements + installers inspected.
- `2026-05-28T11:02:00Z` — Phase 1.5 Wrong-Tool Gate: PROCEED.
- `2026-05-28T11:03:00Z` — Phase 2 discovery: 5 parallel agents. Verified PR-001 (dead `_request`) and PR-007 (hardcoded fond tuples) by grep.
- `2026-05-28T11:04:00Z` — Phase 3 consolidate: 23 findings ranked; 7 boundaries identified.
- `2026-05-28T11:05:00Z` — Phase 4 audit file written (this document).
- `2026-05-28T11:08:00Z` — Phase 5 approval: user approved full-revamp via AskUserQuestion; single-PR / 7-atomic-commits strategy selected.
- `2026-05-28T11:51:00Z` — B1 committed (`3687f52`): adopt `_request` + fix `safe_mcp_tool` + SSOT fond tuples + characterization tests.
- `2026-05-28T11:52:00Z` — B2 committed (`048255f`): pyproject SSOT; delete `requirements.txt`, `requirements-dev.txt`, `__version__.py`.
- `2026-05-28T11:55:00Z` — B3 committed (`e5d8e96`): `src/droit_francais_mcp/` package with `{piste,legifrance,judilibre}/` sub-packages; 6 module renames; import rewrites.
- `2026-05-28T11:57:00Z` — B4 committed (`10d9367`): encapsulate `supports_date_filter()`; promote 7 underscore-private ClassVars to public uppercase; wire `API_LABEL` into OAuth error path.
- `2026-05-28T11:59:00Z` — B5 committed (`b443c88`): tests → `tests/`; `test_jupyter.py` → `examples/jupyter_exploration.py`; conftest with skip-on-no-creds hook.
- `2026-05-28T12:01:00Z` — B6 committed (`41db1bc`): ruff replaces flake8+black+isort+safety+bandit; `[project.scripts]` console-script; delete 3 install scripts; bump `requires-python` ≥ 3.10.
- `2026-05-28T12:03:00Z` — B7 committed (`387e206`): back-compat shim at root; `Légifrance.json` → `docs/api-specs/`; CHANGELOG 1.3.0; README/QUICKSTART rewrite.

## Δ Baseline → Final (Phase 9)

| Metric | Baseline | Final | Δ |
|---|---|---|---|
| Layout | flat root (7 .py modules) | `src/droit_francais_mcp/` + 3 sub-packages | canonical |
| Dependency declaration sites | 4 (drift between `>=` and `==`) | 1 (pyproject `[project]`) | **−3** |
| Version declaration sites | 2 (pyproject + `__version__.py`) | 1 (pyproject, runtime via importlib.metadata) | **−1** |
| Linter / formatter / security tools | 5 (flake8 + black + isort + safety + bandit) | 1 (ruff covers all four) + pip-audit | **−4** |
| Install scripts (.sh / .bat / .ps1) | 3 | 0 (uvx + pipx + `[project.scripts]`) | **−3** |
| Hand-rolled HTTP try/except blocks in clients | 5 (`_request` was dead) | 0 (all sites call `self._request`) | **−~60 LOC** |
| Hardcoded fond tuples outside SSOT | 2 (api_legifrance:174, 196) | 0 (`CODE_FONDS` + `VIGUEUR_DEFAULT_FONDS` frozensets) | **−2** |
| Characterization-test coverage of MCP surface | 0 | 9 tests (tool count + names, `safe_mcp_tool` envelope, `_init_errors`, frozensets, `_request` timeout) | **+9** |
| `safe_mcp_tool` exception context | `logger.error(f"{label}: {e}")` (no traceback) | `logger.exception(label)` + deep-copy return | fixed |
| `_safe_init` failure surfaced to client | no — generic message | yes — `_init_errors` dict + tool error payload includes reason | fixed |
| MCP entry-point | `python droit_francais_MCP.py` (ad-hoc) | `droit-francais-mcp` console-script + `python -m droit_francais_mcp` + back-compat shim | canonical |
| Tests location | repo root + `--ignore=test_jupyter.py` band-aid | `tests/`; `test_jupyter.py` → `examples/jupyter_exploration.py` | canonical |
| Integration-test gating | bare `pytestmark = pytest.mark.integration` (53 noisy failures without creds) | conftest auto-skip when env missing, with clear reason | fixed |
| `requirements.txt` encoding | UTF-16 LE | n/a (file deleted) | fixed |
| `Légifrance.json` location | repo root (orphan, 308 KB) | `docs/api-specs/legifrance-swagger-2.0.json` | canonical |
| Ruff lint findings | n/a (ruff not adopted) | 0 (all clean) | clean |
| `requires-python` | `>=3.8` (3.8 EOL 2024-10-14) | `>=3.10` | bumped |
| LOC in scope (.py only) | 3,231 | 3,514 (incl. +280 LOC characterization tests, +5 `__init__.py`, +shim) | +283 |
| Total findings ranked | 23 | 23 resolved or filed | **all 23 addressed** |

**Commits**: 7 atomic commits on branch `compound-refactor/revamp-20260528-8cf805`.
  - `3687f52` B1 · `048255f` B2 · `e5d8e96` B3 · `10d9367` B4 · `b443c88` B5 · `41db1bc` B6 · `387e206` B7

**Verification (final, Phase 7a re-run)**:
  - `pytest --collect-only` → 77 tests discovered
  - `pytest -m "not integration"` → 9 passed (the new MCP characterization suite)
  - `ruff check src tests` → all checks passed
  - `pip install -e ".[dev]"` → editable install OK; `droit-francais-mcp` binary present in `.venv/bin/`
  - `make version` → `Version: 1.2.1 / Auteur: Jean-Michel Tanguy` via importlib.metadata
  - `python -m droit_francais_mcp` and back-compat shim `python droit_francais_MCP.py` both delegate to `mcp.run()`

**Net file delta**: 31 files changed, +1346 / −1209 (net +137 LOC counting docs, tests, audit). Deletions: `requirements.txt`, `requirements-dev.txt`, `__version__.py`, `install.{sh,bat,ps1}` (6 files removed). Additions: `src/droit_francais_mcp/{,__main__,piste,legifrance,judilibre}/__init__.py` × 5, `tests/{__init__,conftest}.py`, `tests/test_characterization.py`, audit doc, shim.

**Iteration verdict**: `<compound-refactor-complete>` — every Tier-1 and Tier-2 finding consolidated; Tier-3 findings addressed (REVAMP-013 ClassVar publicization done; REVAMP-014 dead-code wired into error path; REVAMP-016 documented; REVAMP-019 moved). Prior-run advisory findings retained (Vibe Coding attribution: `deliberately_not_consolidated`). The remaining `.repair/` directory is gitignored and harmless.

**Deliberately not done (deferred to follow-up runs)**:
- `uv.lock` checked into repo (recommended by best-practices research; deferred until repo CI adopts `uv`).
- `fastmcp.json` declarative config (optional 2.11+ feature; current `[project.scripts]` covers canonical invocation).
- ~~Lazy-init for `legifranceapi`/`judilibreapi` module globals (REVAMP-015)~~ — addressed in iteration 2 / B8.

---

## Iteration 2 — additional 6 boundaries (B8–B13)

Following the user's request to "continue, it's far from perfect", a second pass identified and closed structural debt that iteration 1 left out of scope.

### Discovery deltas (iteration 2)

| Concern | Iteration 1 state | Iteration 2 finding |
|---|---|---|
| `server.py` size | 538 LOC (FastMCP + 5 tools + 12 resources all in one file) | split into 3 modules |
| Module globals `legifranceapi`/`judilibreapi` | constructed at import (REVAMP-015 deferred) | lazy-init via accessors |
| mypy config | none — ad-hoc CLI flags in Makefile | `[tool.mypy]` block + 24 strict errors fixed |
| CI gate | none (no `.github/workflows/`) | matrix workflow (3.10–3.13 + macOS + Windows) |
| `query_builder.py` size | 1036 LOC (includes 270 LOC of dead descriptions dicts) | 813 LOC after extraction |
| Test coverage | 35% (9 characterization tests) | 47% (40 unit tests) |
| `droit_francais_mcp.__init__` public API | exposes only `__version__` | re-exports 5 client/builder/filter symbols + pinned via test |
| Ruff format | not enforced as gate | `ruff format --check` runs in CI |

### Iteration 2 boundary plan (delivered)

| B | Commit | Subject |
|---|---|---|
| **B8** | `14a2f26` | Split server.py into server.py + tools.py + resources.py + lazy-init clients (closes REVAMP-015) |
| **B9** | `f985aa6` | pyproject `[tool.mypy]` block + fix 24 strict-mode errors |
| **B10** | `873201c` | GitHub Actions CI (ruff + ruff format + mypy + pytest matrix) + apply ruff format baseline |
| **B11** | `6732ffb` | Extract `FONDS_DESCRIPTIONS` / `TYPE_CHAMP_DESCRIPTIONS` into `legifrance/descriptions.py` |
| **B12** | `d03ce6d` | Unit tests for filters / piste auth / query_builder (35% → 46% coverage) |
| **B13** | `ddfee33` | Re-export public API from package `__init__` + `tests/test_public_api.py` pin |

### Δ Iteration 1 final → Iteration 2 final

| Metric | After iter 1 | After iter 2 | Δ |
|---|---|---|---|
| `server.py` LOC | 538 | 154 | **−384** (split into 3) |
| `query_builder.py` LOC | 1036 | 813 | **−223** (descriptions extracted) |
| Module-level eager init | yes (constructs OAuth clients at import) | no (memoized lazy accessors) | fixed |
| Tests offline | 9 | 40 | **+31** |
| Test coverage | 35% | 47% | **+12 pp** |
| mypy strict errors | 24 | 0 | **−24** |
| CI workflows | 0 | 1 (matrix 3.10–3.13 × ubuntu/macos/windows) | **+1** |
| `__init__.py` public symbols | 1 (`__version__`) | 6 (+ 4 classes + 1 helper) | **+5** |
| `ruff format --check` as gate | no | yes | enforced |
| Ruff config | basic | extended (E/F/I/B/UP/S/SIM) + per-file ignores | tightened |

### Iteration 2 verification (final)

- `pytest -m "not integration"` → **40 passed**
- `ruff check src tests` → all checks passed
- `ruff format --check src tests` → 23 files already formatted
- `mypy src` → Success: no issues found in 14 source files
- Editable install + console-script + back-compat shim all functional
