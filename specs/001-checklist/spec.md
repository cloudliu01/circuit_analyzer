# Spec: Circuit Ontology Schema and Pattern-Matching Engine

*Aligned Constitution: v1.1.0*

## 1. Purpose
Define the ontology-based data model and reasoning mechanism for hierarchical circuit analysis.
This specification describes how hierarchical SPICE/Verilog netlists are represented as RDF/OWL graphs and how pattern-based graph search and constrained reachability are achieved.
All definitions and behaviors comply with the Constitution principles.

## Clarifications

### Session 2025-11-08

- Q: What performance budget should cap each per-TopPin SPARQL pattern plus constrained reachability evaluation? → A: Allow up to 30 seconds per TopPin to accommodate very large graphs without optimization pressure.
- Q: How should rule evaluation behave when required metadata (voltage class, alias definitions, model tags) is missing for any device involved? → A: Abort the evaluation run and emit no assessment until metadata gaps are resolved.
- Q: Which authentication mechanism should guard the `/ingest` API until centralized IAM is ready? → A: Require per-user API keys supplied via `X-Api-Key` header and tracked in Secrets Manager.

## Scaffold Settings

The current repository layout already contains the directories the ontology, pattern engine, and validation stack rely on. New work must keep the following scaffold to stay aligned with the docker-compose wiring and test fixtures:

```text
.
├── src/
│   ├── cli/
│   ├── common/
│   ├── esd/
│   ├── parser/
│   ├── patterns/
│   ├── query/
│   ├── services/
│   └── validation/
├── api/
│   └── app/
│       ├── main.py
│       └── routers/
│           ├── ingest.py
│           ├── patterns.py
│           ├── query.py
│           └── assessments.py
├── data/
│   └── seed.ttl
├── patterns/
│   ├── README.md
│   └── inv.subckt
├── specs/
│   └── 001-checklist/
│       └── spec.md   # this document
├── tests/
│   ├── test_esd_rules.py
│   └── fixtures/
│       ├── esd_no_clamp.cdl
│       ├── esd_single_diode.cdl
│       └── lv_mos_direct_pad.cdl
├── scripts/
│   └── run_quickstart.sh (placeholder for automation)
└── docker-compose.yml
```

- `src/` contains shared libraries used by both CLI and API workflows:
  - `src/parser` for CDL parsing + RDF emission and TTL writers
  - `src/query` for constrained reachability builders
  - `src/esd` for rule logic + persistence helpers
  - `src/patterns` for pattern metadata + registries
  - `src/services` for GraphDB + ingestion orchestration + instrumentation
  - `src/common` for config, logging, secrets, and API-key providers
  - `src/validation` for SHACL runners
  - `src/cli` for Typer-based commands (e.g., `ingest-cdl`)
- `api/app/main.py` hosts the FastAPI service surface, and `api/app/routers/` always contains `ingest.py`, `patterns.py`, `query.py`, and `assessments.py` so the documented contracts remain routable.
- `patterns/` stores reusable `.subckt` templates that the API container mounts at `/workspace/patterns` (see `docker-compose.yml`) for live pattern extraction.
- `data/` contains canonical RDF exports (e.g., `seed.ttl`) and is volume-mounted into both GraphDB (`/opt/graphdb/home`) and the API container for deterministic fixtures.
- `tests/` houses regression suites: fixture CDL netlists under `tests/fixtures/`, parser ingestion tests under `tests/parser/`, pattern + reachability tests in `tests/patterns/`, and ESD rule regression tests in `tests/esd/`.
- `specs/` holds feature documentation, clarifications, and downstream plans; every scaffold change must document its intent in the corresponding spec directory.
- `scripts/run_quickstart.sh` validates the Quickstart checklist (ingestion + reachability smoke tests) prior to release.
- `docker-compose.yml` orchestrates GraphDB + API services and binds the `patterns/` and `data/` volumes; keep new services consistent with this composition to avoid drift between local dev and CI.

---

## User Stories & Testing

- **User Story 1 – Netlist Ingestion Pipeline (Priority P1)**  
  - *Goal*: CAD engineer ingests a full CDL design via CLI or `/ingest`, producing deterministic RDF split into `design/`, `library/`, and `metadata/` TTL artifacts, guarded by SHACL validation and audit-ready provenance.  
  - *Acceptance / Independent Test*: Run `poetry run ingest-cdl --input tests/fixtures/esd_single_diode.cdl --design test`; confirm the command emits the three TTL artifacts, SHACL report, per-stage duration logs, and uploads a named graph discoverable via `GET /repositories/{id}/contexts`. Repeat via `POST /ingest` to ensure dataset digest + graph URIs match.

- **User Story 2 – Pattern Authoring & Reachability (Priority P2)**  
  - *Goal*: Pattern author registers templates (receiving SPARQL hashes) and runs constrained reachability queries that honor polarity, alias closure, and voltage limits while logging GraphDB query IDs, dataset digests, and enforcing ≤30 s execution budgets.  
  - *Acceptance / Independent Test*: POST `/patterns` with a sample template and expect response fields `patternId`, `sparqlHash`. Invoke `/query/reachability` for `PAD_A1` (depth=3) and verify the response includes `status`, `evidencePath`, `queryHash`, `datasetDigest`, and server logs capture query IDs plus timing.

- **User Story 3 – ESD Rule Assessments (Priority P3)**  
  - *Goal*: Reliability engineer evaluates composite ESD rulepacks (R1–R4) to produce PASS/FAIL/SUSPECT assessments with evidence paths, missing component lists, SPARQL hashes, and dataset digests; LV metadata gaps must block assessments.  
  - *Acceptance / Independent Test*: Ingest `lv_mos_direct_pad.cdl`, call `/assessments?topPin=PAD_A1`, and confirm FAIL status referencing missing isolation, recorded `query:evidencePath`, `query:missingComponents`, `queryHash`, `datasetDigest`, and a SHACL report link when violations occur.

---

## 2. Namespaces
| Prefix | URI | Description |
|---------|-----|-------------|
| `ckt:` | http://example.org/ckt# | Devices, nets, pins |
| `h:`   | http://example.org/h# | Hierarchical structure |
| `pattern:` | http://example.org/pattern# | User-defined subcircuit templates |
| `query:` | http://example.org/query# | SPARQL templates, results, artifacts |
| `tech:` | http://example.org/tech# | Technology, models, voltage classes, rails, aliases |
| `io:` | http://example.org/io# | Top pins, pad cells, IO semantics |
| `esd:` | http://example.org/esd# | Composite ESD rules and assessments |

---

## 3. Core Classes
| Class | Description | Key Properties |
|--------|-------------|----------------|
| `ckt:Device` | Circuit component (NMOS, PMOS, RES, CAP, INV, NAND2, DFF, ESD_DIODE, ggNMOS, SCR, etc.) | `ckt:type`, `ckt:role`, `ckt:connectsTo`, `tech:ofModel` |
| `ckt:Net` | Electrical net connecting pins | `ckt:hasPin`, `tech:aliasOf` |
| `ckt:Pin` | Terminal of a device | `ckt:belongsTo`, `ckt:net`, `ckt:pinType` (e.g., D,S,G,B,ANODE,CATHODE) |
| `h:Module` | Logical module/subcircuit | `h:hasInstance` |
| `h:Instance` | Instance of a module | `h:instOf`, `h:within` |
| `pattern:SubcktPattern` | Pattern derived from a subcircuit library | `pattern:source`, `pattern:sparqlTemplate`, `pattern:matchType`, `pattern:scope`, `pattern:constraints` |
| `tech:Model` | Technology model family | `tech:voltageClass`, `tech:isESDDevice`, `tech:deviceFamily` |
| `tech:GlobalRail` | Canonical global rail (e.g., VDD, VSS) | `tech:aliasOf` |
| `io:TopPin` | Top-level IO pin | `io:belongsToModule`, `io:direction` |
| `io:PadCell` | IO pad cell instance | `h:instOf`, `h:within` |
| `esd:Rule` | Composite protection rule | `esd:requires`, `esd:scope`, `esd:severity`, `esd:params` |
| `esd:Assessment` | Protection assessment result | `esd:status`, `query:result`, `query:evidencePath`, `query:missingComponents`, `query:score` |

---

## 4. Object Properties
| Property | Domain → Range | Description |
|-----------|----------------|-------------|
| `ckt:connectsTo` | Device → Net | Defines electrical connection |
| `ckt:role` | Device → Literal | {VDD, VSS, IO, INTERNAL} |
| `ckt:pinType` | Pin → Literal | {D,S,G,B,ANODE,CATHODE} |
| `h:instOf` | Instance → Module | Maps instance to its module |
| `h:within` | Instance → Module | Indicates hierarchical containment |
| `tech:ofModel` | Device → Model | Device’s technology model |
| `tech:voltageClass` | Model → Literal | {LV, HV, IO} |
| `tech:isESDDevice` | Model → xsd:boolean | Mark device class as ESD |
| `tech:aliasOf` | Net/Rail → Net/Rail | Alias closure for global rails and nets |
| `pattern:source` | SubcktPattern → Literal | Source subckt name or identifier |
| `pattern:sparqlTemplate` | SubcktPattern → Literal | SPARQL query text or generator template |
| `pattern:matchType` | SubcktPattern → Literal | {Exact, Structural, Functional, Fuzzy} |
| `pattern:scope` | SubcktPattern → Literal | Neighborhood scope (e.g., PadNeighborhood(2)) |
| `pattern:constraints` | SubcktPattern → Literal | Direction/voltage/family constraints in JSON/YAML |
| `esd:requires` | Rule → (Pattern/Rule) | Composite rule dependencies |
| `esd:scope` | Rule → Literal | Scope (e.g., per TopPin, per PadCell) |
| `esd:severity` | Rule → Literal | {BLOCKER, CRITICAL, WARNING} |
| `esd:params` | Rule → Literal | Tunables (e.g., minRes, neighborhoodDepth) |
| `esd:status` | Assessment → Literal | {PASS, FAIL, SUSPECT} |
| `query:result` | (Pattern/Rule) → (Device/Net/Module) | Links to matched graph elements |
| `query:evidencePath` | Assessment → Literal/List | Path(s) Pad→…→Rail with polarity |
| `query:missingComponents` | Assessment → Literal/List | Missing diodes/clamps/isolations |
| `query:score` | Assessment → xsd:decimal | Similarity/adequacy score |

---

## 5. Pattern-Based Graph-Matching & Constrained Reachability

### 5.1 Concept
Users or internal processes define **patterns** based on subcircuits (`.SUBCKT`) from a library.
Each pattern is converted into a **SPARQL query template** for structural subgraph matching.
ESD verification additionally requires **reachability with constraints** (direction, polarity, voltage class, device family).

### 5.2 Pattern Definition Workflow
1. **Pattern Extraction:** Parse the target `.SUBCKT`, emit RDF using the ontology (devices, nets, pins, hierarchy), normalize identifiers to variables.
2. **SPARQL Translation:** Generate templates that capture device roles, connectivity, and optional constraints from `pattern:constraints`.
3. **Registration:** Store under `/patterns/` with metadata and version.
4. **Execution:** Run against the RDF dataset; collect `query:result` bindings.
5. **Traceability:** Persist SPARQL hash, dataset digest, timestamps, and matched subgraphs.

#### Match Type Semantics
- **Exact**: all devices/nets specified in the source `.SUBCKT` must be present with identical topology; SPARQL templates use strict `BIND` equality filters. Results are PASS/FAIL with no scoring.
- **Structural**: allows device renaming but requires topological equivalence. Templates constrain degree/roles rather than literal names.
- **Functional**: focuses on intent (e.g., logical NAND behaviour) and allows alternative device families; templates use `VALUES` lists and optional blocks. Responses include qualitative notes but still require deterministic `queryHash`.
- **Fuzzy**: permits partial matches. The engine emits `query:score` (0–1) derived from matched components / expected components. Fuzzy matches are sorted by score and truncated to the top 10 results per request.

Conflicting directives inside `pattern:constraints` are resolved deterministically: `exclude` rules take precedence over `include`, voltage-class filters override device-family filters, and the constraint processor logs a warning plus a `query:missingComponents` note when users request mutually exclusive predicates.

### 5.3 Reachability with Constraints
ESD analysis needs directed/path-constrained search from `io:TopPin` to `tech:GlobalRail` (VDD, VSS) with alias closure (`tech:aliasOf*`). Constraints include:
- **Polarity:** respect diode anode→cathode and MOS body diode direction via `ckt:pinType` and model metadata.
- **Voltage Class:** prevent LV device exposure at the pad without protection (`tech:voltageClass`).
- **Device Family:** prefer paths through `tech:isESDDevice=true` components for protection assertions.
- **Neighborhood Scope:** limit search depth using `pattern:scope` or rule parameters.

Additional reachability safeguards:
- **Cycle protection:** property-path queries include `DISTINCT` and explicit hop counters (default max depth = 4) to avoid infinite loops; repeated nets/devices terminate the traversal with a SUSPECT note.
- **Disconnected components:** when no alias path reaches VDD/VSS, the engine records `query:missingComponents` with the blocking net/device and returns a FAIL for severity BLOCKER/CRITICAL rules, SUSPECT otherwise.
- **Multi-rail domains:** pads referencing multiple rails must declare the intended source/sink; the reachability engine evaluates each rail separately and merges evidence paths to prevent false positives.
- **Polarity conflicts:** if diode orientation conflicts with requested direction, the hop is skipped and a warning is logged; repeated polarity violations elevate the assessment to SUSPECT.

_Simplified SPARQL sketch_ (illustrative):
```sparql
PREFIX ckt: <http://example.org/ckt#>
PREFIX tech: <http://example.org/tech#>
PREFIX io: <http://example.org/io#>

# From pad to VSS through a forward-biased ESD diode (directional)
SELECT DISTINCT ?pad ?padNet ?vss ?d ?nPad ?nVss
WHERE {
  ?pad a io:TopPin ; ckt:connectsTo ?padNet .
  ?vss a tech:GlobalRail .
  ?vss (tech:aliasOf)* ?vssAlias .

  ?d a ckt:Device ; tech:isESDDevice true ; tech:ofModel ?m ;
     ckt:connectsTo ?nPad, ?nVss .
  ?m tech:deviceFamily "DIODE" .

  # Directionality encoded at export time (e.g., pinType ANODE/CATHODE)
  ?an a ckt:Pin ; ckt:belongsTo ?d ; ckt:pinType "ANODE" ; ckt:net ?nPad .
  ?ca a ckt:Pin ; ckt:belongsTo ?d ; ckt:pinType "CATHODE" ; ckt:net ?nVss .

  FILTER (?nPad = ?padNet && ?nVss = ?vssAlias)
}
```

### 5.4 Composite ESD Rules
Define rulepacks using `esd:Rule` with orchestrated sub-conditions:

**ESD_PAD_BASIC (per TopPin):**
- **R1:** Pad → VDD has a forward path via ESD device(s) (diode/ESD-FET/SCR).
- **R2:** Pad → VSS has a forward path via ESD device(s).
- **R3:** VDD ↔ VSS has a rail clamp (ggNMOS/LVTSCR/RC clamp).
- **R4:** Any LV MOS connected to the pad must be isolated/protected (e.g., series R above threshold or behind ESD device).

The engine evaluates R1–R4 and emits an `esd:Assessment` with:
`esd:status` (PASS/FAIL/SUSPECT), `query:evidencePath`, `query:missingComponents`, optional `query:score`.

#### Severity/Status Reconciliation

| `esd:severity` | Default `esd:status` on violation | Required Action |
|----------------|-----------------------------------|-----------------|
| BLOCKER        | FAIL                              | Stop ingestion/reporting; issue must be fixed before tape-out. |
| CRITICAL       | FAIL (unless explicit waiver)     | Open remediation ticket; assessments remain FAIL until waiver recorded. |
| WARNING        | SUSPECT                           | Continue processing but highlight in assessment summary/logs. |

When a rule’s computed status disagrees with its severity (e.g., fuzzy match returns PASS for a CRITICAL rule), the severity wins: the assessment is downgraded to SUSPECT and annotated with `query:missingComponents` referencing the conflicting evidence. Reviewers can override by attaching a signed waiver reference stored alongside the assessment metadata.

### 5.5 Pattern Registration Enhancements
- `pattern:constraints` supports JSON/YAML describing direction, voltage class filters, device family inclusion/exclusion, neighborhood depth.
- Composite rules may reference sub-patterns for reuse.

### 5.6 Outputs
- Matched subgraphs and rule outcomes serialized to RDF/JSON-LD.
- Evidence paths are stored as RDF lists (or JSON-LD arrays) for audit.
- All outputs include SPARQL query hash and dataset digest.
- If any device or net lacks mandatory metadata (voltage class, alias mapping, model flags), abort the evaluation and emit no assessments; instead log the missing facts and block downstream consumption until metadata is complete.

---

## 6. Netlist Ingestion Pipeline

### 6.1 CDL Parser Requirements
- Accept complete hierarchical CDL (`.cdl`) netlists containing `.SUBCKT` definitions, `.INCLUDE` directives, and `.GLOBAL` statements; resolve includes relative to invocation directory and record provenance.
- Preserve hierarchy paths using `/`-delimited identifiers (e.g., `top/u1/u2`) and emit `h:Module`, `h:Instance`, `ckt:Net`, and `ckt:Device` triples that align with the ontology in §2–§4.
- Normalize device types and pin ordering using technology library metadata so that downstream pattern matching can rely on consistent `ckt:type` + `ckt:pinType` assignments.
- Produce deterministic Turtle output split into:
  - `design/<design-name>.ttl` for topology and hierarchy
  - `library/<lib-name>.ttl` for reusable cell definitions
  - `metadata/<design-name>.ttl` capturing ingestion run info (CLI version, timestamp, SHA-256 of source CDL)
- Provide a Poetry CLI entry point `poetry run ingest-cdl --input samples/foo.cdl --design foo --out data/foo` that drives parsing, RDF generation, SHACL validation, and optional upload to GraphDB.
- Emit SHACL reports when violations occur and fail the command (non-zero exit) if any constraint is broken.

### 6.2 GraphDB Loading API
- Add FastAPI endpoint `POST /ingest` that accepts a multipart form:
  - `designName` (string)
  - `cdl` (CDL file)
  - optional `config` (JSON, e.g., hierarchy strategy)
- Server-side flow:
  1. Store raw CDL under `data/uploads/<designName>/<timestamp>/`.
  2. Run the same parser pipeline as the CLI to create RDF artifacts.
  3. Use GraphDB HTTP API (`PUT /repositories/{repo}/statements`) to import generated Turtle into a named graph `urn:circuit:{designName}:{timestamp}`.
  4. Record dataset digest, SPARQL hash, and ingestion metadata (`prov:wasDerivedFrom`) inside GraphDB and respond with ingestion ID plus named graph URI.
- API must reject uploads lacking required technology metadata (voltage class, alias definitions) and return `422` with diagnostic JSON listing the missing facts.
- Enforce authentication via per-user API keys stored in Secrets Manager; clients must pass `X-Api-Key` on every call, keys map to ingest identity for auditing, and rotation is handled via environment refresh. Apply rate limiting per key to mitigate accidental overload.

### 6.3 Error Handling & Observability
- Both CLI and API ingestion flows must:
  - Log per-stage durations (parse, RDF emit, SHACL, GraphDB import) and stop if any single stage exceeds 30 minutes for full-design loads.
  - Attach `query:missingComponents` entries describing unresolved references (e.g., unknown `.MODEL`) before aborting.
  - Emit structured JSON or LD responses capturing success/failure, evidence hashes, and pointers to SHACL reports stored under `data/reports/<designName>/`.

---

## 7. Validation and Testing
- **Pattern Validity:** all generated templates must be valid SPARQL 1.1.
- **Fixture Library:** include positive/negative ESD cases: `no_clamp`, `single_diode_only`, `reverse_diode`, `lv_mos_direct_pad`, `rc_trigger_blocked`, etc.
- **Determinism:** same inputs produce the same matches and assessments.
- **Metrics:** maintain ≥95% precision and ≥90% recall over the fixture suite (10 positive / 10 negative minimum). Any regression outside this bound blocks release until addressed.
- **SPARQL Validation:** every generated template must pass GraphDB’s `/repositories/{id}/validate` endpoint and Apache Jena `sparql --query ... --validate` checks before promotion.
- **Integration:** tests cover alias closure, polarity handling, voltage class filtering, and hierarchical boundary expansion.
- **Performance Budget:** each per-TopPin evaluation (pattern execution plus constrained reachability) must complete within 30 seconds on nominal dataset sizes; log any overruns for tuning.

---

## 8. Versioning
- Spec version: **0.4.0**
- Aligned Constitution version: **1.1.0**

---

## 9. Assumptions & Dependencies

- **Netlist inputs**: CDL files must be LVS-clean, include `.MODEL` statements with voltage-class annotations, and follow `/`-delimited hierarchy names (e.g., `top/u1/u2`). Missing metadata is treated as a hard stop (see §6.3).
- **Technology metadata**: Standard cell libraries supply pin order, device families, and alias rails used by the parser to normalize `ckt:type` and `ckt:pinType`.
- **Toolchain versions**:
  - Python **3.11**
  - `rdflib >= 6.3`, `pySHACL >= 0.23`, `SPARQLWrapper >= 2.0`
  - Ontotext GraphDB **10.5.x** (Docker image `ontotext/graphdb:10.5.3`) with `/repositories/{id}/validate` support
  - Apache Jena `arq` CLI for template validation
- **Deployment assumptions**: Docker + docker-compose orchestrate GraphDB and FastAPI services; no external network access is required after container builds.
- **Security dependencies**: API keys are stored via Secrets Manager (or `.env` placeholders for local dev) and rotated through environment refresh; ingestion relies on HTTPS when deployed remotely.

---

**References:** Constitution §§II–VI; Development Workflow & Quality Gates.
