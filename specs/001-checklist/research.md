# Research: Circuit Ontology Schema and Pattern-Matching Engine

## Decision 1: GraphDB Free as canonical triplestore
- **Rationale**: Ships SPARQL 1.1, SHACL validation service, and path indexing tuned for constrained reachability; aligns with Constitution update naming GraphDB as default; Docker image already available with persistent volume mapping.
- **Alternatives considered**:
  - *Apache Jena Fuseki*: familiar but removed to avoid dual maintenance and to gain GraphDB’s SHACL/paths tooling.
  - *Blazegraph / RDF4J vanilla*: lighter footprint but missing built-in path evaluation optimizations and SHACL validation UI.

## Decision 2: Repository bootstrap workflow
- **Rationale**: Use REST `POST /rest/repositories` with config template + initial `PUT /repositories/{id}/statements` containing `data/seed.ttl`; ensures reproducible dataset creation and allows CI to reset via HTTP calls.
- **Alternatives considered**:
  - *Manual UI provisioning*: slower, not automatable, diverges between developers.
  - *Mount pre-populated data dir*: possible but harder to version-control repository configs and rulesets.

## Decision 3: RDF export & pattern ingestion strategy
- **Rationale**: rdflib for AST→RDF conversion (supports Turtle + JSON-LD), storing subckt templates under `patterns/` with normalized identifiers, exposing FastAPI endpoints to submit pattern metadata and compile SPARQL templates server-side.
- **Alternatives considered**:
  - *On-client SPARQL generation*: complicates validation and breaks deterministic hashing constraints.
  - *Custom binary format*: violates ontology-first mandate and blocks SHACL validation.

## Decision 4: SHACL + pytest integration
- **Rationale**: Leverage pySHACL inside pytest to enforce structural constraints per fixture; wrap in helper that loads TTL, runs shapes under `schemas/shacl`, and asserts zero violations to preserve Constitution Principle III.
- **Alternatives considered**:
  - *GraphDB’s SHACL service only*: good for runtime but not sufficient for unit-level gating.
  - *Ad-hoc Python validators*: would duplicate SHACL semantics and risk divergence.

## Decision 5: Evidence hashing & determinism
- **Rationale**: After SPARQL execution, compute SHA-256 of query text + dataset digest (GraphDB `GET /repositories/{id}/size` and `HEAD` ETag) to store in RDF as `query:hash` and `query:datasetDigest`, guaranteeing reproducible provenance.
- **Alternatives considered**:
  - *Timestamp-only provenance*: insufficient for regression diffing.
  - *Non-cryptographic hashes*: faster but risk collisions and audit failures.

## Decision 6: Performance safeguards for constrained reachability
- **Rationale**: Enforce query templates that limit path length via `VALUES` depth bounds plus GraphDB path expressions; log GraphDB `X-GraphDB-QueryID` so slow queries can be profiled; ensures <30 s per TopPin target.
- **Alternatives considered**:
  - *Unbounded property paths*: simpler but can explode on large alias graphs.
  - *Manual DFS in Python*: violates ontology-first + reuses less GraphDB optimization.
