# Ontology Checklist: Circuit Ontology Schema and Pattern-Matching Engine

**Purpose**: Ensure ontology, pattern-matching, and ESD rule requirements are complete, clear, and testable before implementation.
**Created**: 2025-11-08
**Feature**: specs/001-checklist/spec.md

**Note**: Generated from /speckit.checklist to serve as requirement-quality unit tests prior to development.

## Requirement Completeness

- [x] CHK001 Are namespace definitions covering every data domain the pipeline emits or consumes (parser outputs, pattern metadata, rule assessments), or are additional vocabularies needed? [Completeness, Spec §2]
- [x] CHK002 Are class requirements ensuring each domain actor (devices, nets, pins, modules, instances, patterns, tech models, IO, ESD artifacts) has its mandatory properties and relationships documented? [Completeness, Spec §3]
- [x] CHK003 Does the spec describe how evidence artifacts (SPARQL hash, dataset digest, timestamps, matched subgraphs) are persisted and linked for every pattern execution? [Completeness, Spec §5.2–5.6]
- [x] CHK004 Are validation expectations enumerated for all rule/pattern categories (structural matching, constrained reachability, composite ESD rulepacks) with both positive and negative fixtures? [Completeness, Spec §6]

## Requirement Clarity

- [x] CHK005 Are property semantics such as `tech:aliasOf`, `pattern:scope`, and `pattern:constraints` defined with explicit cardinality, directionality, and evaluation rules to remove interpretation gaps? [Clarity, Spec §4]
- [x] CHK006 Is polarity handling (diode orientation, MOS body diode direction) described with precise criteria tied to `ckt:pinType` values rather than descriptive prose alone? [Clarity, Spec §5.3]
- [x] CHK007 Are severity levels (`esd:severity`) mapped to explicit decision outcomes or gating actions so their impact is unambiguous? [Clarity, Spec §5.4]
- [x] CHK008 Does the definition of `pattern:matchType` explain how Exact vs. Structural vs. Functional vs. Fuzzy matching alters acceptable SPARQL constructs or tolerance thresholds? [Clarity, Spec §5.2]

## Requirement Consistency

- [x] CHK009 Do `pattern:SubcktPattern` class requirements align with property typing (e.g., structured JSON stored as literals) so ontology and serialization expectations are consistent? [Consistency, Spec §3–§4]
- [x] CHK010 Are ESD rule descriptions (R1–R4) consistent with the Validation & Testing success metrics so PASS/FAIL interpretations match? [Consistency, Spec §5.4 & §6]
- [x] CHK011 Is alias-closure behavior (`tech:aliasOf*`) applied consistently across namespace, reachability, and validation sections without conflicting definitions? [Consistency, Spec §2 & §5.3]

## Acceptance Criteria Quality

- [x] CHK012 Are determinism, precision, and recall requirements tied to concrete numeric thresholds or tolerances to enable objective acceptance? [Acceptance Criteria, Spec §6]
- [x] CHK013 Are SPARQL template validity expectations defined with measurable checks (e.g., SPARQL 1.1 compliance tests, linting) rather than qualitative statements? [Acceptance Criteria, Spec §6]

## Scenario Coverage

- [x] CHK014 Are alternate flows such as fuzzy or partial pattern matches documented, including how ambiguous hits are ranked or filtered? [Scenario Coverage, Spec §5.2]
- [x] CHK015 Does the reachability description include behaviors for cycles, disconnected components, or conflicting polarity constraints to prevent undefined outcomes? [Scenario Coverage, Spec §5.3]
- [x] CHK016 Are outputs specified for rule execution when datasets are incomplete (e.g., missing alias definitions or missing pad nets), or is this left unspecified? [Scenario Coverage, Spec §5.6]

## Edge Case Coverage

- [x] CHK017 Are edge conditions like pads lacking direct VDD/VSS rails, multi-rail domains, or voltage-class mismatches enumerated with required handling? [Edge Case Coverage, Spec §5.3]
- [x] CHK018 Does the spec define how conflicting directives inside `pattern:constraints` (simultaneous include/exclude of the same family) are resolved? [Edge Case Coverage, Gap]

## Non-Functional Requirements

- [x] CHK019 Are performance expectations for SPARQL execution and constrained reachability (depth limits, runtime budgets) documented? [Non-Functional, Gap]
- [x] CHK020 Are storage, audit, or access-control requirements for pattern metadata, hashes, and assessments defined to guard sensitive IP? [Non-Functional, Gap]

## Dependencies & Assumptions

- [x] CHK021 Are upstream assumptions about netlist quality, availability of technology model metadata, and naming conventions explicitly captured? [Dependencies, Gap]
- [x] CHK022 Are required external tools/versions (RDFLib, SPARQL engines, Fuseki) documented so ontology features like property paths are supported consistently? [Dependencies, Gap]

## Ambiguities & Conflicts

- [x] CHK023 Is there guidance for reconciling `esd:severity` (BLOCKER/CRITICAL/WARNING) with `esd:status` (PASS/FAIL/SUSPECT) when they disagree? [Ambiguity, Spec §5.4]
- [x] CHK024 Does the versioning section define backward-compatibility or migration requirements for ontology evolution beyond listing version 0.4.0? [Ambiguity, Spec §7]
