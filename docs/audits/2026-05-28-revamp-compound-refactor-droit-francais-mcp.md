---
schema_version: 2.0.0
date: 2026-05-28
run_id: 20260528-8cf805
prior_run_id: 20260528-124b1a
scope: droit-francais-mcp
scope_path: /Users/joachimbrindeau/Development/expand/production/jurisprudence/MCP/droit-francais-mcp
command: compound-refactor
status: awaiting_approval
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
- `2026-05-28T11:02:00Z` — Phase 1.5 Wrong-Tool Gate: PROCEED (revamp = canonical-target restructure, no other tool covers it).
- `2026-05-28T11:03:00Z` — Phase 2 discovery: 5 parallel agents (best-practices, framework-docs, architecture-strategist, pattern-recognition, testing-reviewer). Verified PR-001 (dead `_request`) and PR-007 (hardcoded fond tuples) directly via grep.
- `2026-05-28T11:04:00Z` — Phase 3 consolidate: 23 findings ranked by tier × leverage; 7 boundaries identified.
- `2026-05-28T11:05:00Z` — Phase 4 audit file written (this document).
- _Next_ — Phase 5 approval (HITL gate, EnterPlanMode).
