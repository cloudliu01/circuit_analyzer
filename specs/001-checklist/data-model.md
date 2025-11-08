# Data Model: Circuit Ontology Schema and Pattern-Matching Engine

## Core Entities

### ckt:Device
- **Description**: Physical or logical component extracted from `.SUBCKT` definitions (NMOS, PMOS, RES, CAP, INV, NAND2, ggNMOS, SCR, etc.).
- **Key fields**:
  - `ckt:type` (string, required) – canonical cell/family identifier.
  - `ckt:role` (enum: VDD, VSS, IO, INTERNAL) – supply/function classification.
  - `tech:ofModel` (ref `tech:Model`, required).
  - `ckt:connectsTo` (multi ref `ckt:Net`, ≥1).
- **Validation rules**:
  - Devices marked `tech:isESDDevice true` must expose ANODE/CATHODE pins.
  - LV devices connected directly to IO pad nets must also connect to an isolation element (series resistor or ESD component) per rule R4.

### ckt:Pin
- **Fields**: `ckt:belongsTo` (Device), `ckt:net` (Net), `ckt:pinType` (enum D,S,G,B,ANODE,CATHODE), optional `io:direction`.
- **Rules**:
  - Each pin inherits voltage class from owning device’s `tech:Model`.
  - Polarity semantics rely on `pinType`; reachability logic enforces ANODE→CATHODE direction only.

### ckt:Net
- **Fields**: `ckt:hasPin` (Pin collection), `tech:aliasOf` (Net alias closure), `h:within` (Module).
- **Rules**:
  - Global rails are represented as `tech:GlobalRail` instances linked via `tech:aliasOf*` to nets.
  - Nets exposed at module boundaries must map to `io:TopPin` or `io:PadCell` references.

### h:Module / h:Instance
- **Module fields**: `h:hasInstance`, `h:hasNet`, `io:hasTopPin`.
- **Instance fields**: `h:instOf` (Module), `h:within` (Module path), `h:hasPin`.
- **Rules**:
  - Hierarchical paths stored as `/`-delimited identifiers (e.g., `top/u1/u2`).
  - Instances must include provenance to original `.SUBCKT` name for traceability.

### pattern:SubcktPattern
- **Fields**: `pattern:source` (string), `pattern:sparqlTemplate` (literal SPARQL text), `pattern:matchType` (Exact/Structural/Functional/Fuzzy), `pattern:scope` (string), `pattern:constraints` (JSON/YAML literal).
- **Rules**:
  - `pattern:constraints` must encode polarity/voltage/device-family filters; schema enforced via JSON schema before storage.
  - Template hash stored under `query:hash`.

### tech:Model / tech:GlobalRail
- **Model fields**: `tech:voltageClass` (LV/HV/IO), `tech:isESDDevice` (bool), `tech:deviceFamily`.
- **GlobalRail fields**: `tech:aliasOf` (alias tree), optional `tech:voltageClass`.
- **Rules**:
  - Alias closure must produce strongly connected components; GraphDB path queries use `tech:aliasOf*`.

### io:TopPin / io:PadCell
- **TopPin fields**: `io:direction` (IN/OUT/INOUT), `ckt:connectsTo` (Net), `io:belongsToModule`.
- **PadCell fields**: `h:instOf`, `h:within`, `ckt:connectsTo`.
- **Rules**:
  - Each `io:TopPin` participates in ESD_PAD_BASIC evaluations; missing metadata aborts rule evaluation per spec.

### esd:Rule / esd:Assessment
- **Rule fields**: `esd:requires` (rule/pattern list), `esd:scope` (TopPin/PadCell), `esd:severity` (BLOCKER/CRITICAL/WARNING), `esd:params` (JSON).
- **Assessment fields**: `esd:status` (PASS/FAIL/SUSPECT), `query:result` (bindings), `query:evidencePath` (RDF list), `query:missingComponents`, `query:score`.
- **Rules**:
  - Assessment must include SPARQL hash + dataset digest for reproducibility.
  - If required metadata missing, no assessment instance is emitted; log `query:missingComponents` describing the gap.

## Relationships
- Devices ↔ Nets via `ckt:connectsTo`.
- Pins belong to devices and nets (`ckt:belongsTo`, `ckt:net`).
- Instances realize modules (`h:instOf`) and reside within parent module (`h:within`).
- Patterns bind to SPARQL templates and constraints; ESD rules reference patterns via `esd:requires`.
- Assessments link to rules and matched graph elements through `query:result`.

## State & Lifecycle Notes
- **Pattern lifecycle**: Extract `.SUBCKT` → normalize IDs → serialize RDF → register pattern metadata → compile SPARQL template → store hash.
- **Assessment lifecycle**: Trigger rule evaluation per TopPin → run constrained reachability (bounded depth) → record evidence path + status → persist to GraphDB.
- **Versioning**: Each RDF ingest stored as separate named graph with provenance (`prov:wasDerivedFrom`, timestamp, tool version) enabling diff/rollback.

## Validation Rules (SHACL Highlights)
- Every `h:Instance` must have both `h:instOf` and `h:within`.
- `ckt:Pin` requires exactly one `ckt:net`.
- `tech:isESDDevice true` devices must expose ANODE and CATHODE pins.
- `io:TopPin` nodes must connect to nets that eventually alias to a `tech:GlobalRail`.
- `esd:Assessment` must not exist unless at least one evidence path or missing component entry is provided.
