# Implementation Plan: Circuit Ontology Schema and Pattern-Matching Engine

**Branch**: `001-checklist` | **Date**: 2025-11-08 | **Spec**: specs/001-checklist/spec.md
**Input**: Feature specification from `/specs/001-checklist/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an ontology-first pipeline that ingests hierarchical SPICE/Verilog netlists, emits RDF/OWL using the `ckt:/h:/pattern:/tech:/io:/esd:` vocabularies, and persists results inside GraphDB. Provide pattern-registration plus constrained reachability to evaluate ESD rulepacks (pad-to-rail coverage, rail clamps, LV isolation) with deterministic evidence artifacts (SPARQL hash, dataset digest, evidence paths). All work must honor the Constitution’s ontology, determinism, and validation-first requirements while staying inside the documented repository scaffold (FastAPI service, tests, fixtures, data volumes).

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (Poetry-managed)  
**Primary Dependencies**: rdflib, pySHACL, FastAPI, Pydantic, requests, SPARQLWrapper, Ontotext GraphDB HTTP APIs  
**Storage**: GraphDB Free (Docker) with mounted `/opt/graphdb/home` dataset plus on-disk Turtle fixtures under `data/`  
**Testing**: pytest (+ pySHACL validation harness), ruff for lint/import order, optional mypy for types  
**Target Platform**: Dockerized Linux services (api + GraphDB) deployable on developer laptops and CI runners  
**Project Type**: Backend CLI + FastAPI microservice with supporting ETL scripts and SHACL assets  
**Performance Goals**: ≤30 s per TopPin evaluation (pattern + constrained reachability); pipeline processes ≥100k devices / 1M connections ≤60 s (Constitution §V)  
**Constraints**: Ontology-first modeling, deterministic transformations, offline-first operation, no proprietary netlists, GraphDB default triplestore, evidence traceability (hash/digest)  
**Scale/Scope**: Initial scope covers pad-level ESD analysis for ~10–100k device designs with reusable pattern library and regression fixtures

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Ontology-First (Principle I)** – Spec enumerates vocabularies + RDF classes; plan keeps all state in GraphDB with RDF serialization. ✅  
- **Deterministic Transform Pipeline (Principle II)** – Pipeline order (parse → RDF → SHACL → SPARQL → reports) preserved with evidence hashes/digests. ✅  
- **Test-First & Validation-Driven (Principle III)** – Existing fixtures + pySHACL tests remain mandatory; plan adds regression coverage for each pattern/rule change. ✅  
- **Semantic Interoperability (Principle IV)** – Namespaces fixed per spec; FastAPI endpoints expose SPARQL / RDF artifacts only. ✅  
- **Performance & Simplicity (Principle V)** – Targets restated (≤30 s per TopPin, ≤60 s per 100k devices); scoped to simple, inspectable RDF + SPARQL. ✅  
- **Technology & Domain Semantics (Principle VI)** – Voltage classes, device families, alias closure modeled via `tech:` namespace; reachability honors polarity + LV/HV gating. ✅

**Post-Design Re-check (Phase 1)**: Data model, contracts, and quickstart all encode RDF-first flows, GraphDB default, deterministic evidence hashing, and SHACL validation hooks. No constitution violations introduced; Complexity Tracking remains empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-checklist/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
api/
├── Dockerfile
└── app/
    ├── main.py
    └── routers/
        ├── patterns.py
        └── query.py
patterns/
├── README.md
└── inv.subckt
data/
└── seed.ttl
tests/
├── fixtures/
│   ├── esd_no_clamp.cdl
│   ├── esd_single_diode.cdl
│   └── lv_mos_direct_pad.cdl
└── test_esd_rules.py
specs/
└── 001-checklist/
    └── …
docker-compose.yml
```

**Structure Decision**: Monorepo centers on `api/` FastAPI service plus shared RDF assets (`patterns/`, `data/`) and pytest fixtures (`tests/fixtures`). Specs for each feature live under `specs/<feature>/`. Docker compose ties GraphDB + API using the documented volumes; no additional sub-projects required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
