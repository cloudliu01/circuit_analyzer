# Tasks: Circuit Ontology Schema and Pattern-Matching Engine

**Input**: Design documents from `/specs/001-checklist/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included only where the specification mandates SHACL/pytest regression coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment hygiene.

- [ ] T001 Add rdflib, pySHACL, SPARQLWrapper, typer, and ingestion extras to `pyproject.toml`
- [ ] T002 Document required env vars (`GRAPHDB_URL`, `GRAPHDB_REPOSITORY`, `API_INGEST_KEY`) inside `.env.example`
- [ ] T003 Describe end-to-end bootstrap (Docker + Poetry + ingestion CLI) in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities needed by every user story. No story work can start until these complete.

- [ ] T004 Create central settings loader for env + secrets at `src/common/config.py`
- [ ] T005 Implement reusable GraphDB HTTP client with auth + retry logic in `src/services/graphdb_client.py`
- [ ] T006 Add SHACL validation helper that runs pySHACL against generated TTL in `src/validation/shacl_runner.py`
- [ ] T007 Configure structured logging + tracing helpers shared across CLI/API in `src/common/logging.py`
- [ ] T008 Build API-key provider backed by Secrets Manager (file-based mock) with audit logging in `src/common/api_keys.py`

---

## Phase 3: User Story 1 – Netlist Ingestion Pipeline (Priority: P1) 🎯 MVP

**Goal**: As a CAD engineer, I can ingest a full hierarchical CDL netlist (via CLI or `/ingest`) into GraphDB with deterministic RDF, SHACL gating, and API-key enforcement.

**Independent Test**: Run `poetry run ingest-cdl --input tests/fixtures/esd_single_diode.cdl --design test` and confirm the command emits `design/`, `library/`, and `metadata/` TTL artifacts plus a SHACL report, then verify GraphDB shows the new named graph via `GET /repositories/{id}/contexts`; POSTing the same CDL through `/ingest` must return matching graph URI and dataset digest.

- [ ] T009 [P] [US1] Parse CDL `.SUBCKT`, `.INCLUDE`, `.GLOBAL`, and device statements into normalized AST in `src/parser/cdl_reader.py`
- [ ] T010 [P] [US1] Emit RDF triples for modules/instances/devices/nets with `/` hierarchy paths in `src/parser/rdf_emitter.py`
- [ ] T011 [US1] Generate deterministic TTL artifacts (`design/*.ttl`, `library/*.ttl`, `metadata/*.ttl` with CLI version/timestamp/SHA) via `src/parser/ttl_writer.py`
- [ ] T012 [US1] Wire ingestion CLI command with Typer entry point at `src/cli/ingest_cdl.py` (parse → RDF → SHACL → artifact staging)
- [ ] T013 [US1] Implement ingestion orchestration service that uploads TTL artifacts, records dataset digests, and persists provenance in `src/services/ingest_service.py`
- [ ] T014 [US1] Add FastAPI router + schema for `/ingest` with API-key guard, streaming upload, and SHACL error responses in `api/app/routers/ingest.py`
- [ ] T015 [US1] Add ingestion regression test covering CLI + `/ingest` happy paths using fixture netlists in `tests/parser/test_cdl_ingest.py`
- [ ] T016 [US1] Instrument ingestion pipeline with per-stage duration logs, <30 minute safety aborts, and SHACL report storage under `data/reports/` via `src/services/ingest_metrics.py`

---

## Phase 4: User Story 2 – Pattern Authoring & Reachability (Priority: P2)

**Goal**: As a pattern author, I can register subcircuit patterns, store template metadata, and run constrained reachability queries that honor polarity, voltage class, and depth limits.

**Independent Test**: POST a pattern payload to `/patterns`, then run `/query/reachability` for a pad in `data/seed.ttl` and verify the response includes query hash, dataset digest, and bounded evidence path.

- [ ] T017 [P] [US2] Define pattern metadata dataclasses (source, scope, constraints, hashes) in `src/patterns/models.py`
- [ ] T018 [P] [US2] Implement persistent pattern registry (CRUD + hashing + validation) backed by GraphDB in `src/patterns/registry.py`
- [ ] T019 [US2] Extend `api/app/routers/patterns.py` to validate payloads, call registry, and return SPARQL hashes per contract
- [ ] T020 [P] [US2] Build constrained reachability query builder with polarity/alias/voltage gates in `src/query/reachability.py`
- [ ] T021 [US2] Update `api/app/routers/query.py` to execute reachability templates, enforce ≤30 s budgets, log GraphDB query IDs, and include `queryHash` + `datasetDigest` in responses
- [ ] T022 [US2] Add pattern + reachability tests using RDF fixtures in `tests/patterns/test_pattern_workflow.py`
- [ ] T023 [US2] Implement precision/recall regression harness over the positive/negative fixture suite (≥95% precision, ≥90% recall) in `tests/patterns/test_metrics.py`
- [ ] T024 [US2] Integrate SPARQL validation step (GraphDB `/validate` + `sparql --validate`) into `src/patterns/registry.py` pipeline before persisting templates

---

## Phase 5: User Story 3 – ESD Rule Assessments (Priority: P3)

**Goal**: As a reliability engineer, I can evaluate composite ESD rulepacks (R1–R4), view PASS/FAIL/SUSPECT assessments, and obtain evidence paths plus missing components.

**Independent Test**: With existing pad fixtures, run the rule engine via `/assessments?topPin=PAD_A1` and confirm the response includes `esd:status`, `query:evidencePath`, `query:missingComponents`, SPARQL hash, and dataset digest; LV MOS violations should block assessment creation.

- [ ] T025 [P] [US3] Encode rule metadata (scope, severity, parameters) and reusable predicates in `src/esd/rules.py`
- [ ] T026 [US3] Implement rule engine that orchestrates pattern executions, constrained reachability, and LV isolation checks in `src/esd/engine.py`
- [ ] T027 [US3] Persist assessments, evidence paths, SPARQL hashes, and dataset digests back into GraphDB via `src/esd/persistence.py`
- [ ] T028 [US3] Expose `/assessments` router for listing/filtering rule outcomes with evidence URIs in `api/app/routers/assessments.py`
- [ ] T029 [US3] Add regression tests covering PASS/FAIL/SUSPECT scenarios and metadata gating in `tests/esd/test_rule_engine.py`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, documentation, and operational readiness.

- [ ] T030 Add automated quickstart verification script to `scripts/run_quickstart.sh` that executes ingestion + reachability smoke tests
- [ ] T031 Document API-key management and rotation guidance in `docs/security.md`
- [ ] T032 Add structured logging & metrics wiring for ingestion, pattern, and assessment routers inside `api/app/main.py`

---

## Dependencies & Execution Order

1. **Setup → Foundational**: Complete Phase 1 before Phase 2. Foundational utilities (`config`, `graphdb_client`, `shacl_runner`, logging) block every story.
2. **User Story sequencing**:
   - **US1 (P1)** depends on Foundational only. Once finished, CLI + `/ingest` provide datasets consumed by later stories.
   - **US2 (P2)** requires US1 outputs (ingested graphs) but can run in parallel with US3 once ingestion artifacts exist.
   - **US3 (P3)** depends on US1 data and US2 reachability primitives; start after US2’s query builder is stable.
3. **Polish** starts after all targeted user stories reach their independent test criteria.

## Parallel Execution Examples

- **US1**: T009 and T010 can proceed in parallel (parser vs RDF emitter) before converging in T011/T012.
- **US2**: T017/T018 (metadata + registry) can run concurrently with T020 (reachability builder) and T023/T024 (metrics/validation) once foundational services exist.
- **US3**: T025 (rule definitions) and T027 (persistence) can proceed in parallel once US2’s reachability APIs are stable.

## Implementation Strategy

1. **MVP (US1)**: Focus first on CDL ingestion—deliver CLI + `/ingest` so the team can load real designs and validate ontology mappings.
2. **Incremental layers**: Add pattern authoring + reachability (US2) next, then layer ESD rule evaluations (US3) leveraging prior services.
3. **Polish**: After all stories pass independent tests, run the quickstart script, tighten logging/observability, and document API-key rotation.
