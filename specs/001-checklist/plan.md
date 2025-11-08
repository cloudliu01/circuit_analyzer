# Implementation Plan: Circuit Ontology Schema and Pattern-Matching Engine

**Branch**: `001-checklist` | **Date**: 2025-11-08 | **Spec**: specs/001-checklist/spec.md
**Input**: Feature specification from `/specs/001-checklist/spec.md`

## Summary

Deliver an ontology-first toolchain that ingests full CDL netlists, emits RDF/OWL using the `ckt:/h:/tech:/pattern:/io:/esd:` vocabularies, validates with SHACL, and persists graphs in GraphDB. Provide FastAPI endpoints for pattern registration, constrained reachability, ESD rule assessments, and a secure `/ingest` API that wraps the CDL parser + GraphDB imports. Preserve deterministic evidence artifacts (SPARQL hash, dataset digest, evidence paths) and hit the 30-second per TopPin evaluation budget while enforcing metadata completeness gates.

## Technical Context

**Language/Version**: Python 3.11 (Poetry-managed)
**Primary Dependencies**: rdflib, pySHACL, FastAPI, Pydantic, requests/SPARQLWrapper, Ontotext GraphDB HTTP APIs, typer/Click for CLI wrappers
**Storage**: GraphDB Free (Docker) with `/opt/graphdb/home` volume plus on-disk Turtle artifacts under `data/`
**Testing**: pytest (unit + SHACL regression), ruff (lint/imports), optional mypy for static typing
**Target Platform**: Dockerized Linux services (GraphDB + FastAPI) for local dev/CI runners
**Project Type**: Backend CLI + FastAPI microservice with RDF ETL scripts and SHACL schemas
**Performance Goals**: ≤30 s per TopPin evaluation (pattern + reachability); ≤60 s to convert/ingest 100k devices / 1M connections (Constitution §V)
**Constraints**: Ontology-first modeling, deterministic pipeline, offline-first operation, API-key auth on `/ingest`, evidence traceability (hash/digest), metadata completeness gates
**Scale/Scope**: Covers pad-level ESD verification for ~10–100k device designs with reusable pattern/rule libraries and regression fixtures

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Ontology-First (Principle I)** – Parser, CLI, and APIs emit only RDF/OWL aligned with declared namespaces; no ad-hoc JSON persistence. ✅
- **Deterministic Transform Pipeline (Principle II)** – Workflow (CDL → RDF → SHACL → GraphDB → SPARQL) remains deterministic with SHA-256 digests recorded. ✅
- **Test-First & Validation-Driven (Principle III)** – Each parser/pattern change requires SHACL + pytest fixtures before merge. ✅
- **Semantic Interoperability (Principle IV)** – FastAPI contracts expose RDF/SPARQL artifacts and reuse canonical prefixes. ✅
- **Performance & Simplicity (Principle V)** – Targets restated; GraphDB path limits + CLI batching maintain budgets. ✅
- **Technology & Domain Semantics (Principle VI)** – Voltage class, polarity, alias closure, and LV isolation encoded in ontology + enforced during ingestion/reachability. ✅

**Post-Design Re-check (Phase 1)** – Data model, contracts, and quickstart preserve the same guarantees (GraphDB default, deterministic artifacts, required metadata gates). No violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/001-checklist/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.yaml
│   └── graphdb-repo-config.json
└── tasks.md (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── cli/
│   └── ingest_cdl.py
├── common/
│   ├── config.py
│   ├── logging.py
│   └── api_keys.py
├── esd/
│   ├── rules.py
│   ├── engine.py
│   └── persistence.py
├── parser/
│   ├── cdl_reader.py
│   ├── rdf_emitter.py
│   └── ttl_writer.py
├── patterns/
│   └── registry.py
├── query/
│   └── reachability.py
├── services/
│   ├── graphdb_client.py
│   ├── ingest_service.py
│   └── ingest_metrics.py
└── validation/
    └── shacl_runner.py
api/
└── app/
    ├── main.py
    └── routers/
        ├── ingest.py
        ├── patterns.py
        ├── query.py
        └── assessments.py
patterns/
└── inv.subckt
data/
├── seed.ttl
└── uploads/
tests/
├── fixtures/
│   ├── esd_no_clamp.cdl
│   ├── esd_single_diode.cdl
│   └── lv_mos_direct_pad.cdl
├── parser/
└── esd/
scripts/
└── run_quickstart.sh
specs/
└── 001-checklist/
docker-compose.yml
```

**Structure Decision**: Single repo with a shared `src/` library (parser/query/esd/patterns/services/common) consumed by both the CLI and FastAPI service. GraphDB + API remain orchestrated via docker-compose, mounting `data/` and `patterns/` alongside the new `src/` modules, matching the scaffold documented in the spec.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|---------------------------------------|
| _None_ | – | – |
