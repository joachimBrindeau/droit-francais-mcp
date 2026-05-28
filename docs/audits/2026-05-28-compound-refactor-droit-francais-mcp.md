---
schema_version: 2.0.0
date: 2026-05-28
run_id: 20260528-124b1a
scope: droit-francais-mcp
scope_path: /Users/joachimbrindeau/Development/expand/production/jurisprudence/MCP/droit-francais-mcp
command: compound-refactor
status: in-progress
mode: "autofix"
depth: "merged"
tier_floor: 3
language: "python"
framework: "fastmcp"
generated_at: "2026-05-28T06:05:00Z"
baseline_commit: "2737b1e"
loc_in_scope: 3611
total_findings: 20
findings_at_or_above_tier_floor: 17
audit_file_format: "v2"
---

# Compound SSOT Audit — droit-francais-mcp

**Run**: `20260528-124b1a` · **Iteration**: 1/10 · **Mode**: autofix · **Depth**: merged

## Executive summary

The codebase is a French-law MCP server bridging two PISTE-hosted government APIs (Légifrance + JudiLibre). Two sibling `*API` client classes (`LegifranceAPI`, `JudilibreAPI`) re-implement the same OAuth 2.0 Client-Credentials lifecycle, the same recursive response-filter (`clean()`), and the same `requests.RequestException`-to-generic-`Exception` re-raise pattern across 8+ HTTP call-sites. The MCP wrapper (`droit_francais_MCP.py`) re-implements identical try/except/log/error-dict shapes across 5 `@mcp.tool` functions and embeds the `FONDS_WITH_DATE_FILTERS` constant inline — drifted relative to the canonical list in `LegifranceQueryBuilder.add_dates`. Three of the 20 findings are latent defects (mutable list default, bare `except:` clauses, OAuth `Host` header mis-placed in form body).

**Compound leverage**: one base class + one helper module + one decorator eliminates ~250 LOC of duplication AND closes 8 production-hang vectors (missing `timeout=`) AND fixes 3 latent defects AND restores docstring/code parity.

## Behavior Contract — global scope

**Behavior (must preserve)**
- Every MCP-exposed tool function continues to accept the same parameter names, types, defaults, and produces the same observable result shape (the test suite pins this).
- Every `*API.search`, `*API.consult`, `*API.taxonomy` continues to return data of the same shape (cleaned dict / list / None).
- OAuth token lifecycle: token cached, refreshed 60s before expiry, error messages preserved (callers may log them).
- Error paths preserve the same error-message strings used by tests (`Fond invalide`, `Type de recherche invalide`, `page_size ne peut pas dépasser 50`, etc.) — test_api_legifrance.py / test_api_judilibre.py grep these strings.

**Allowed structural changes**
- Extract a `PisteOAuthClient` base class for OAuth init + `get_access_token` + `_get_api_headers` + `_post`/`_get` HTTP wrapper.
- Extract a module-level `_recursive_filter(data, allowed_keys, max_depth)` helper.
- Convert self-mapping dicts (`TYPE_CHAMP`, `TYPE_RECHERCHE`, `FONDS`) to `frozenset[str]` class attributes; replace `.values()` membership-check sites accordingly.
- Promote `FONDS_WITH_DATE_FILTERS` to a class attribute on `LegifranceQueryBuilder` (single source-of-truth).
- Add `@safe_mcp_tool` decorator around all `@mcp.tool` functions.
- Add module-level `PISTE_HTTP_TIMEOUT = 30` and apply to every `requests` call.

**Forbidden semantic deltas**
- Public function signatures (parameter names, defaults, order) on any `@mcp.tool` or any `LegifranceAPI`/`JudilibreAPI` method.
- The wording of `ValueError` messages already asserted by tests (must contain the same substrings).
- The structure / keys of returned dicts at the MCP-tool boundary.
- Adding required env-vars or changing the sandbox/prod URL set.

`behavior_contract_class`: **structural_only** for SSOT findings, **bug_fix_disguised_as_refactor** for FIND-0010/12/15 (mutable default, bare except, docstring drift) — those are pure latent-defect repairs.

---

## Findings — ranked (Tier ascending, leverage descending)

| # | Finding | File:Line | Sites | Leverage | Drift | Effort | Conf | Tier | Boundary | Action |
|---|---|---|---|---|---|---|---|---|---|---|
| FIND-0009 | requests calls missing `timeout=` | api_legifrance.py:93 | 8 | 16 | 2 | 1 | 100 | 1 | B1 | PROMOTE_TO_CONST |
| FIND-0014 | Hardcoded PISTE base URLs duplicated | api_legifrance.py:38 | 4 | 8 | 2 | 1 | 100 | 1 | B1 (dominated by FIND-0001) | PROMOTE_TO_CONST |
| FIND-0008 | FONDS_WITH_DATE_FILTERS knowledge duplicated | droit_francais_MCP.py:260 | 2 | 6 | **3** | 1 | 100 | 1 | B4 | PROMOTE_TO_CONST |
| FIND-0006 | MCP tool try/except boilerplate | droit_francais_MCP.py:248 | 5 | 5 | 2 | 2 | 100 | 1 | B3 | EXTRACT_HELPER |
| FIND-0003 | `_get_api_headers` duplicated | api_legifrance.py:109 | 2 | 4 | 2 | 1 | 100 | 1 | B1 | EXTRACT_HELPER |
| FIND-0005 | `requests.RequestException → raise` boilerplate | api_legifrance.py:106 | 8 | 4 | 1 | 2 | 100 | 1 | B1 | EXTRACT_HELPER |
| FIND-0001 | OAuth client init duplicated | api_legifrance.py:27 | 2 | 3 | **3** | 2 | 100 | 1 | B1 | EXTRACT_HELPER |
| FIND-0002 | `get_access_token` duplicated | api_legifrance.py:66 | 2 | 3 | **3** | 2 | 100 | 1 | B1 | EXTRACT_HELPER |
| FIND-0015 | Wrong docstring defaults (LegifranceAPI.search) | api_legifrance.py:240 | 1 | 3 | **3** | 1 | 100 | 1 | B5 | RENAME_FOR_INTENT |
| FIND-0016 | TYPE_CHAMP/TYPE_RECHERCHE/FONDS self-mapping dicts | api_legifrance_query_builder.py:23 | 3 | 3 | 1 | 1 | 100 | 2 | B6 | INTRODUCE_TYPE |
| FIND-0004 | `clean()` recursive helper duplicated | api_legifrance.py:479 | 2 | 2 | 2 | 2 | 100 | 2 | B2 | EXTRACT_HELPER |
| FIND-0007 | API-client init blocks duplicated in MCP module | droit_francais_MCP.py:44 | 2 | 2 | 1 | 1 | 100 | 2 | B3 | EXTRACT_HELPER |
| FIND-0010 | Mutable list default `jurisdiction=[...]` | api_judilibre.py:110 | 1 | 2 | 2 | 1 | 100 | 2 | B5 | DEFAULT_SSOT |
| FIND-0011 | OAuth `data` dict contains HTTP headers | api_judilibre.py:64 | 1 | 2 | 2 | 1 | 100 | 2 | B1 (dominated by FIND-0002) | EXTRACT_HELPER |
| FIND-0012 | Bare `except:` clauses | api_legifrance.py:179 | 2 | 2 | 2 | 1 | 100 | 2 | B5 | RENAME_FOR_INTENT |
| FIND-0013 | 403-message text duplicated | api_legifrance.py:174 | 2 | 2 | 1 | 1 | 100 | 2 | B1 | PROMOTE_TO_CONST |
| FIND-0020 | Unused `Union` import | droit_francais_MCP.py:16 | 1 | 1 | 1 | 1 | 100 | 3 | B6 | REMOVE_DEAD_CODE |
| FIND-0018 | `Légifrance.json` 308KB orphan at root | Légifrance.json:0 | 1 | 1 | 1 | 1 | 75 | advisory | — | FLAG_ONLY |
| FIND-0019 | "Vibe Coding" attribution in 4 modules | api_legifrance.py:1 | 4 | 0 | 0 | 1 | 75 | advisory | — | FLAG_ONLY (deliberately_not_consolidated) |
| FIND-0017 | `.repair/` working dir present | .repair:0 | 1 | 0 | 0 | 1 | 50 | advisory | — | FLAG_ONLY |

## Boundary plan (atomic commits)

### B1 — `PisteOAuthClient` base class
**Files**: new `piste_auth.py`, refactor `api_legifrance.py`, refactor `api_judilibre.py`.
**Eliminates**: FIND-0001, FIND-0002, FIND-0003, FIND-0005, FIND-0009, FIND-0011, FIND-0013, FIND-0014.
**Net effect**: ~120 LOC duplicated init+token+headers code → single inheritable base; closes 8 missing-`timeout=` vectors; promotes 4 URL string-literals + 1 403-message + 1 HTTP-timeout constant; fixes the OAuth `data`-dict header-misplacement latent bug.

### B2 — `piste_utils._recursive_filter`
**Files**: new `piste_utils.py`, refactor `api_legifrance.clean`, refactor `api_judilibre.clean`.
**Eliminates**: FIND-0004.
**Net effect**: ~85 LOC duplicated recursive filter → 30 LOC helper; each class declares only `ALLOWED_KEYS` + `MAX_DEPTH`.

### B4 — `LegifranceQueryBuilder.DATE_FILTER_FACETTES`
**Files**: `api_legifrance_query_builder.py`, `droit_francais_MCP.py`.
**Eliminates**: FIND-0008.
**Net effect**: single `{fond: facette}` dict on the query builder; MCP layer uses `.keys()` for validation; closes a `drift_hazard=3` finding.

### B6 — query-builder cleanup (frozensets + dead imports)
**Files**: `api_legifrance_query_builder.py`, `droit_francais_MCP.py`, `api_legifrance.py` (membership-check sites).
**Eliminates**: FIND-0016, FIND-0020.
**Net effect**: `TYPE_RECHERCHE`/`TYPE_CHAMP`/`FONDS` self-mapping dicts → `frozenset[str]`; remove unused `Union` import.

### B3 — `@safe_mcp_tool` decorator + `_safe_init` helper
**Files**: `droit_francais_MCP.py`.
**Eliminates**: FIND-0006, FIND-0007.
**Net effect**: 5 try/except blocks collapse into one decorator; 2 API-init blocks collapse into one helper.

### B5 — latent defect fixes
**Files**: `api_legifrance.py`, `api_judilibre.py`.
**Eliminates**: FIND-0010 (mutable default), FIND-0012 (bare except), FIND-0015 (docstring drift).
**Net effect**: pure defect repair, `behavior_contract_class=bug_fix_disguised_as_refactor`.

## Path mapping

| Boundary | Files touched | Lines added (est.) | Lines removed (est.) | Net |
|---|---|---|---|---|
| B1 | +piste_auth.py, api_legifrance.py, api_judilibre.py | +110 | -180 | -70 |
| B2 | +piste_utils.py, api_legifrance.py, api_judilibre.py | +35 | -90 | -55 |
| B4 | api_legifrance_query_builder.py, droit_francais_MCP.py | +12 | -20 | -8 |
| B6 | api_legifrance_query_builder.py, droit_francais_MCP.py, api_legifrance.py | +10 | -55 | -45 |
| B3 | droit_francais_MCP.py | +30 | -110 | -80 |
| B5 | api_legifrance.py, api_judilibre.py | +8 | -10 | -2 |
| **Total** | 6 boundaries / 7 modules | ~205 | ~465 | **~−260 LOC** |

## Rejected abstractions

- **Do NOT** merge `FONDS_DESCRIPTIONS` into a single SSOT shared between the MCP resource strings and the query-builder docstring. Two reasons: the MCP `@mcp.resource` returns markdown for LLM consumption, the query-builder dicts are reflection-safe Python; their formats are too different and the maintenance cost of bridging them exceeds the duplication cost. Filed under `deliberately_not_consolidated`.
- **Do NOT** unify the "Vibe Coding" attribution docstrings (FIND-0019) — each module's authorship is meant to be readable in isolation. `deliberately_not_consolidated`.
- **Do NOT** auto-delete `Légifrance.json` (FIND-0018); ask the maintainer whether it's a deliberate reference attachment.

## Baseline metrics (Phase 1.7)

| Metric | Baseline |
|---|---|
| LOC in scope (.py only, excl. .venv) | 3,611 |
| Modules | 5 production + 3 tests |
| Duplicated OAuth init/token/headers | ~120 LOC across 2 files |
| Duplicated `clean()` recursive filter | ~85 LOC across 2 files |
| Duplicated MCP tool try/except boilerplate | ~80 LOC across 5 functions |
| Missing `timeout=` on `requests` calls | 8 |
| Bare `except:` clauses | 2 |
| Mutable default arguments | 1 |
| Docstring/code default drift | 2 |
| Total findings | 20 |
| Findings at confidence ≥ 75 | 19 |
| Tier-1 findings (drift or leverage) | 9 |

## Run log

- `2026-05-28T05:50Z` — Phase 0 preflight: tree clean (commit `2737b1e`).
- `2026-05-28T05:52Z` — Phase 1 frame: scope written, mode=autofix, depth=merged.
- `2026-05-28T05:53Z` — Phase 1.5 Wrong-Tool Gate: PROCEED (multi-file SSOT obvious on first read).
- `2026-05-28T05:55Z` — Phase 1.7 baseline captured to `baseline.json`.
- `2026-05-28T06:00Z` — Phase 2 discovery: orchestrator-direct recording of 20 envelopes (all schema-validated by `runtime-cli validate-envelope`).
- `2026-05-28T06:04Z` — Phase 3 consolidate: `pareto-dedup.ts` ran clean; 2 Pareto-dominations annotated (FIND-0014→FIND-0001, FIND-0011→FIND-0002); no fingerprint collisions.
- `2026-05-28T06:05Z` — Phase 4 audit file written (this document).
- (next: Phase 5/5b/6 — autofix mode auto-approves; behavior contract above; characterization-test gate satisfied by existing pytest integration suite + the structural-only contracts.)
