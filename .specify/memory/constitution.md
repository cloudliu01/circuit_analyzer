# Circuit Analysis Ontology Constitution

## Core Principles

### I. Ontology-First (NON-NEGOTIABLE)
All circuit information must be expressed in explicit RDF triples conforming to an ontology.
No implicit logic or hidden state outside the knowledge graph is allowed.
Ontology design governs data modeling, validation, reasoning, and query structure.
Every new capability starts by extending the ontology (RDF/OWL + SHACL).

### II. Deterministic Transform Pipeline
All analysis follows a reproducible, deterministic pipeline:
Hierarchical SPICE/Verilog netlists → RDF/OWL graph → SHACL validation → SPARQL queries → traceable reports.
Intermediate results must be regenerable from the same source and configuration without randomness.

### III. Test-First & Validation-Driven
Every schema, transformation, and query must have:
1. Unit tests (pytest)
2. SHACL conformance checks
3. Expected output examples
No code or ontology change is merged unless its corresponding test initially fails and later passes (Red-Green-Refactor).

### IV. Semantic Interoperability
All components must share consistent namespace and term usage:
- `ckt:` for devices/nets/pins
- `h:` for hierarchy
- `pattern:` for reusable circuit motifs
- `query:` for SPARQL templates
Any integration between modules (analysis, visualization, reporting) must rely on SPARQL or RDF serialization—never ad-hoc JSON or proprietary APIs.

### V. Performance, Scalability & Simplicity
- Target baseline: 100k devices / 1M connections processed ≤60 s on 16 GB RAM.
- Hierarchical flattening must be on-demand and cache-aware.
- Avoid premature complexity: prefer minimal, declarative graph patterns.
- Follow YAGNI and composability principles—simple, inspectable text I/O for all interfaces.

### VI. Technology & Domain Semantics (NON-NEGOTIABLE)
Voltage domains, device families (ESD vs core), model names, rail aliases, and polarity must be first-class data in the ontology.
No protection assessment is valid without domain annotations and alias resolution.

---

## Technical & Security Constraints

- **Language / Runtime:** Python 3.11+, rdflib, pySHACL; GraphDB Free is the default triplestore for development (Fuseki only allowed for legacy replay runs).
- **Interface:** CLI + FastAPI microservice; optional React/TypeScript frontend.
- **Data Formats:** Turtle (.ttl), JSON-LD; all inputs/outputs valid RDF.
- **Offline-First:** Platform must function entirely without Internet access.
- **Compliance:** No proprietary netlists or third-party models uploaded externally.
- **Licensing:** Every dependency reviewed for permissive or compatible license.
- **Performance Standards:** All SPARQL queries must provide complexity notes; prohibit unbounded Cartesian joins.
- **Technology Semantics:** introduce `tech:` namespace capturing model families, voltage classes (`LV/HV/IO`),
  ESD classification, polarity/meta (e.g., `Vmax`) and `tech:GlobalRail`/`tech:aliasOf` mappings to close rail aliases.
- **I/O Semantics:** introduce `io:` namespace for `io:TopPin`, `io:Pad`, `io:PadCell` and standardized IO directions.

---

## Development Workflow & Quality Gates

- **Code Quality:** PEP 8, lint with ruff, static type checks (mypy).
- **Testing:** Coverage ≥ 85 %; integration tests include DFF/INV/NAND2 and ESD rulepacks.
- **Review Process:** Two-maintainer approval for ontology/spec changes; automated CI must verify SHACL conformance.
- **Traceability:** Every analysis output includes SHACL report, SPARQL hash, dataset digest, and tool versions.
- **Versioning:** Semantic Versioning—breaking ontology changes → MAJOR bump; new motifs, rules, or queries → MINOR.
- **Rulepacks:** ESD rulepacks are versioned. Any change must pass ground-truth regression (≥10 pos/≥10 neg), with precision/recall baselines documented.
- **Evidence:** Each ESD assessment must include evidence paths (Pad→…→Rail) and missing components list.

---

## Governance

This Constitution supersedes all other practices and specifications.
All `/plan`, `/specify`, and `/spec` outputs must conform to it.
Amendments require documented rationale, majority maintainer approval, and a migration plan.
Non-compliant components must be rolled back or regenerated.
The Constitution defines **non-negotiable** boundaries for architecture, semantics, security, and quality.

**Version:** 1.1.0  |  **Ratified:** 2025-11-08  |  **Last Amended:** 2025-11-08
