# Spec: Circuit Ontology Schema and Pattern-Matching Engine

*Aligned Constitution: v1.1.0*

## 1. Purpose
Define the ontology-based data model and reasoning mechanism for hierarchical circuit analysis.
This specification describes how hierarchical SPICE/Verilog netlists are represented as RDF/OWL graphs and how pattern-based graph search and constrained reachability are achieved.
All definitions and behaviors comply with the Constitution principles.

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

### 5.3 Reachability with Constraints
ESD analysis needs directed/path-constrained search from `io:TopPin` to `tech:GlobalRail` (VDD, VSS) with alias closure (`tech:aliasOf*`). Constraints include:
- **Polarity:** respect diode anode→cathode and MOS body diode direction via `ckt:pinType` and model metadata.
- **Voltage Class:** prevent LV device exposure at the pad without protection (`tech:voltageClass`).
- **Device Family:** prefer paths through `tech:isESDDevice=true` components for protection assertions.
- **Neighborhood Scope:** limit search depth using `pattern:scope` or rule parameters.

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

### 5.5 Pattern Registration Enhancements
- `pattern:constraints` supports JSON/YAML describing direction, voltage class filters, device family inclusion/exclusion, neighborhood depth.
- Composite rules may reference sub-patterns for reuse.

### 5.6 Outputs
- Matched subgraphs and rule outcomes serialized to RDF/JSON-LD.
- Evidence paths are stored as RDF lists (or JSON-LD arrays) for audit.
- All outputs include SPARQL query hash and dataset digest.

---

## 6. Validation and Testing
- **Pattern Validity:** all generated templates must be valid SPARQL 1.1.
- **Fixture Library:** include positive/negative ESD cases: `no_clamp`, `single_diode_only`, `reverse_diode`, `lv_mos_direct_pad`, `rc_trigger_blocked`, etc.
- **Determinism:** same inputs produce the same matches and assessments.
- **Metrics:** maintain precision/recall over the fixture suite; regress on any rulepack change.
- **Integration:** tests cover alias closure, polarity handling, voltage class filtering, and hierarchical boundary expansion.

---

## 7. Versioning
- Spec version: **0.4.0**
- Aligned Constitution version: **1.1.0**

---

**References:** Constitution §§II–VI; Development Workflow & Quality Gates.
