# agentic-law — Requirements

**Date:** 2026-05-29
**Status:** Ready for planning
**Scope tier:** Deep — product
**Supersedes:** the Python `droit-francais-mcp` (hard cut, no migration)

---

## Summary

`agentic-law` is a fresh TypeScript MCP server, positioned as an **expandable
agentic legal-tech foundation** rather than a one-off port. v0.1.0 ships PISTE
(Légifrance + JudiLibre) as the first data source, but the architecture treats
"a French legal API" as one adapter among future others (EUR-Lex, OpenJustice,
etc.).

It exposes the legal corpus through **two layers of progressive disclosure**:

- **Layer 1 — curated**: ~6 English, workflow-shaped MCP tools that cover the
  80% case with zero learning curve.
- **Layer 2 — generated depth**: the full set of API operations, code-generated
  from the public OpenAPI specs, surfaced through an MCP **resource catalog**
  plus a single raw-caller tool. The agent reads the catalog ("the map") and
  invokes any operation it needs.

The build leans hard on libraries so custom code stays minimal: HTTP
retry/backoff/timeout, rate limiting, response caching, structured logging,
OpenTelemetry tracing, multi-account auth, and pagination streaming are all
delegated to mature dependencies.

This is a clean break from the Python implementation. No shim, no migration
path, no shared repo.

---

## Problem & Motivation

The Python `droit-francais-mcp` reached a polished, well-tested, agent-native
state (91% coverage, strict typing, CI), but four structural limits motivate a
rebuild rather than continued iteration:

1. **Ecosystem fit.** The official MCP SDK and the overwhelming majority of
   community MCP servers ship in TypeScript. A TS implementation aligns with
   the dominant toolchain, improves discoverability and contribution flow, and
   gives a single-language dev loop with Claude Desktop tooling.

2. **Distribution.** Node is preinstalled on more developer machines than
   uv/uvx; `npx` is the default `command:` target in most
   `claude_desktop_config.json` examples. TS reaches more users.

3. **Custom-code carrying cost.** The Python version hand-rolled a ~750-LOC
   query builder, an OAuth client, a recursive response filter, and a retry-less
   HTTP path. Each is a maintenance liability that a well-chosen library or
   codegen step would eliminate.

4. **Coverage ceiling.** The Python tools wrapped only `search` + `consult` per
   API. The public OpenAPI specs describe many more operations. A hand-mapped
   tool-per-endpoint approach doesn't scale; codegen + progressive disclosure
   does.

The naming choice (`agentic-law`, not `droit-francais-mcp-ts`) reflects intent:
this is the seed of a broader agentic legal platform, with PISTE as proof of the
pattern.

---

## Users & Value

**Primary actor:** an AI agent (Claude in Desktop/Cursor/CLI) acting on behalf
of a legal-research user — a lawyer, paralegal, law student, journalist, or
developer building legal tooling.

**What changes for them:**

- The agent can answer the easy 80% (find an article, look up a recent arrêt,
  consult a decision) through curated tools with no ceremony.
- The agent can reach the long tail (any operation the APIs expose) by reading
  the operation catalog and invoking it — no waiting for a maintainer to
  hand-wrap a new endpoint.
- Robustness the Python version lacked: transient PISTE failures retry
  automatically; rate limits are respected; repeated lookups are cached.

**Secondary actor:** a contributor extending the platform. The value: adding a
new operation is regenerating from the spec, not writing a tool by hand; adding
a new data source later is a new adapter directory, not a rewrite.

---

## Product Thesis & Durability

**Thesis:** legal research is a domain where (a) the authoritative data already
lives behind well-specified public APIs, and (b) agents are better at composing
multi-step research workflows than humans are at clicking through portal UIs.
An MCP server that gives an agent both a curated on-ramp and full-depth access
captures that leverage.

**Durability under near-term shifts:**

- *If PISTE adds/changes endpoints* → codegen re-runs against the updated spec;
  Layer 2 picks up changes with a regen, Layer 1 is unaffected unless a curated
  workflow's underlying operation changes.
- *If the MCP spec evolves* → using the official TS SDK means we inherit spec
  updates rather than tracking them by hand (a risk the Python `fastmcp`
  dependency also carried, but the official SDK is the most durable bet).
- *If a competitor ships a French-law MCP* → the `agentic-law` framing (multi-
  source foundation + progressive disclosure depth) is a wider moat than a
  single-API wrapper. The curated/generated split is the differentiator.

**Recorded uncertainty:** demand for Layer 2 depth is assumed, not yet observed.
The Python version only ever exposed Layer 1-equivalent tools and no user asked
for more — but no user *could*. v0.1.0 ships Layer 2 partly to learn whether the
long tail gets used. (Assumption, not validated.)

---

## Architecture Decisions

> These are product/architectural decisions resolved in this brainstorm because
> the brainstorm is itself about a technical rebuild. Implementation specifics
> (file names, class shapes, exact library versions) are deferred to planning.

### AD-1 — Progressive disclosure via resource-as-catalog

Two layers:

- **Layer 1 (curated):** ~6 English workflow tools, hand-written, stable
  contract.
- **Layer 2 (depth):** an MCP **resource** (e.g. `piste://operations`) that the
  agent reads to discover the full generated operation set, plus a single
  raw-caller tool that invokes any operation by id with params.

**Rationale:** the Python version already proved MCP resources work well for
static documentation in this domain (`legifrance://documentation/*`). A
generated operations catalog is the same pattern at scale. The catalog carries
OpenAPI descriptions, examples, and deprecation flags — richness a flat
`tools/list` entry can't hold — so the agent chooses operations well.

**Rejected alternatives:**
- *Meta-tool gateway* (`discover_advanced_operation` + `call_advanced_operation`):
  viable fallback if a client struggles with read-then-call, but adds a second
  always-present tool and a mandatory two-hop for every deep call.
- *Per-API namespace gateways* with operation lists baked into tool
  descriptions: zero-extra-call discovery, but long descriptions get truncated
  by some clients and the contract is harder to evolve.

### AD-2 — Codegen owns Layer 2 contract; English curated names own Layer 1

- **Layer 1 tool names** are hand-authored English verbs (workflow-shaped).
- **Layer 2 operation ids** come straight from each spec's `operationId`. The
  codegen owns that naming; new upstream operations appear automatically on
  regen.

**Both specs are confirmed public and machine-readable:**
- Légifrance: Swagger 2.0 (already on disk at
  `docs/api-specs/legifrance-swagger-2.0.json` in the Python repo; will be
  copied into `agentic-law`).
- JudiLibre: OpenAPI 3.0.2, maintained at
  [`Cour-de-cassation/judilibre-search`](https://github.com/Cour-de-cassation/judilibre-search/blob/dev/public/JUDILIBRE-public.json).

### AD-3 — Commit generated code

The generated TypeScript (types + client) is committed to the repo, not built
on `postinstall`. Rationale: reviewable diffs when specs change, no
install-time surprises, deterministic builds. Tradeoff: larger repo. Regen via
a documented script (e.g. `pnpm run codegen`).

### AD-4 — Node ≥ 20 LTS primary, Bun opt-in

Node is the default ship target (broadest compatibility, most stable library
ecosystem, `command: "npx"` in MCP config). Bun is documented as a supported
alternative runtime and tested in CI, but is not the primary target. This
keeps the library-heavy mandate low-risk (some deps — e.g. OpenTelemetry
exporters — are most stable on Node).

### AD-5 — Expandable foundation, single package for v0.1.0

`agentic-law` ships as a single package in v0.1.0 with **internal boundaries**
that make later expansion additive, not a refactor:

- a source-agnostic MCP/core layer (server wiring, tool registration, the
  raw-caller, the catalog resource mechanism, auth/HTTP/cache/observability
  cross-cutting concerns), and
- a PISTE-specific adapter layer (the two generated clients, the curated Layer 1
  tools, PISTE auth specifics).

Adding a future non-PISTE source = a new adapter, not a rewrite. **Monorepo /
multi-package split is explicitly deferred** until a second source actually
exists (YAGNI on package boundaries).

### AD-6 — Library-delegated cross-cutting concerns

Custom code is the bare minimum. Delegated to libraries (specific choices
finalized in planning):

- HTTP with retry/backoff/timeout (e.g. `ky` or `got`)
- Rate limiting (e.g. `bottleneck`)
- Response caching (e.g. `keyv`)
- Structured stderr logging (e.g. `pino`) — **stderr only**, stdout is reserved
  for MCP JSON-RPC framing
- Tracing/metrics (OpenTelemetry Node SDK)
- Multi-account auth: multiple PISTE credential sets resolvable simultaneously
  (e.g. sandbox + prod side by side), not one-cred-per-process as in Python
- Pagination as async iterators / streamed tool results for large result sets

---

## Layer 1 Tool Set (v0.1.0, frozen)

| Tool | Purpose | Maps to |
|------|---------|---------|
| `search_legifrance` | Multi-fond legislative/text search | Légifrance `POST /search` |
| `consult_legifrance` | Full text of an article/text by id | Légifrance `POST /consult/*` (routed by id prefix) |
| `ping_legifrance` | OAuth + connectivity diagnostic | Légifrance `GET /search/ping` |
| `search_jurisprudence` | Case-law search | JudiLibre `GET /search` |
| `consult_decision` | Full text of a decision by id | JudiLibre `GET /decision` |
| `list_taxonomy` | Valid filter values (chambers, jurisdictions, …) | JudiLibre `GET /taxonomy` |

Tool *names* are English; tool *arguments* keep domain terms where the API does
(fond codes `JORF`/`CODE_ETAT`, chamber codes `civ1`, etc. — these are the
data's own vocabulary, not translatable labels).

---

## Success Criteria

- [ ] All 6 Layer 1 tools functional against PISTE sandbox, returning the same
      observable shapes a user would get through the portal.
- [ ] Layer 2: the operations catalog resource lists every operation from both
      generated specs; the raw-caller successfully invokes a representative
      operation not covered by Layer 1.
- [ ] Transient failures (5xx, network blips) retry automatically; rate limits
      respected; identical repeat lookups served from cache within TTL.
- [ ] Multiple PISTE accounts usable in one process (sandbox + prod).
- [ ] Large search result sets stream/paginate rather than returning one blob.
- [ ] Structured logs go to stderr only; stdout carries clean JSON-RPC.
- [ ] Test coverage ≥ 85% before first tagged release; offline test suite runs
      with no credentials (integration tests gated behind env presence).
- [ ] CI green on Node ≥ 20 LTS matrix; Bun job passes as opt-in.
- [ ] `npx agentic-law` starts the server; a documented
      `claude_desktop_config.json` snippet registers the tools.
- [ ] Regenerating from an updated spec is a single documented command.

---

## Scope Boundaries

### In scope (v0.1.0)

- Fresh TypeScript repo named `agentic-law`, greenfield, hard cut from Python.
- Official MCP TypeScript SDK as the server framework.
- Codegen pipeline for both PISTE specs; generated code committed.
- Layer 1 (6 curated tools) + Layer 2 (catalog resource + raw caller).
- Library-delegated cross-cutting concerns (AD-6).
- Multi-account auth.
- Pagination/streaming for large results.
- Offline-first test suite + integration tests gated on creds; CI matrix.
- Community/docs baseline (README with the `npx` install + config snippet,
  CONTRIBUTING, SECURITY, capability map equivalent).

### Deferred for later (post-v0.1.0)

- A second, non-PISTE legal data source (EUR-Lex, OpenJustice, …) — the
  foundation is built to accept one, but none ships in v0.1.0.
- Monorepo / multi-package split (only when a second source exists).
- Derived analytics / cross-source synthesis tools.
- Persisted/accumulated cross-session context (the agent's client handles
  session memory; revisit if a concrete need appears).

### Outside this product's identity

- A migration shim or compatibility layer for Python `droit-francais-mcp` users
  (explicit hard cut).
- Coexistence inside the Python repo.
- French Layer 1 tool names (English curated surface is a deliberate
  ecosystem-fit decision).
- A web UI / dashboard (MCP servers are headless).
- Writing to / mutating PISTE data (the public APIs are read-only).

---

## Dependencies & Assumptions

- **Assumption (validated):** both PISTE APIs expose public, machine-readable
  OpenAPI/Swagger specs suitable for codegen. Confirmed for Légifrance (on disk)
  and JudiLibre (Cour-de-cassation GitHub).
- **Assumption (not validated):** there is real demand for Layer 2 depth beyond
  the curated 6. v0.1.0 ships it partly to learn this.
- **Dependency:** the official MCP TypeScript SDK's support for resources and
  streamed tool results at the maturity Layer 2 needs — to be confirmed against
  current SDK docs in planning.
- **Dependency:** valid PISTE credentials (sandbox + optionally prod) for
  integration testing; offline suite must not require them.
- **Assumption:** committing generated code keeps the repo reviewable without
  bloating it past acceptable limits — revisit if generated output is larger
  than expected.

---

## Open Questions for Planning

1. Exact library choices per cross-cutting concern (AD-6 names candidates;
   planning picks and pins).
2. Codegen tool selection (`openapi-typescript` vs alternatives) and how it
   handles Swagger 2.0 (Légifrance) vs OpenAPI 3.0.2 (JudiLibre) in one
   pipeline.
3. Catalog resource shape: one combined `piste://operations` resource vs
   per-API resources; how much per-operation detail to inline vs link.
4. Raw-caller param validation strategy: pass-through (API-as-validator) vs
   generated per-operation schemas.
5. Multi-account auth surface: how an agent selects which account a call uses
   (tool arg? separate tool instances? config-driven default + override?).
6. Package manager + build tooling (pnpm assumed; confirm).

---

## Handoff

Recommended next step: `/ce-plan` against this document to produce the phased
implementation plan (repo scaffold → codegen pipeline → core/MCP layer → PISTE
adapter + Layer 1 → Layer 2 catalog → cross-cutting libraries → tests/CI →
release).
