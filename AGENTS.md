# Repository Guidelines

## Project Structure & Module Organization
Keep all executable code under `src/`, mirroring the flow in `README.md`: `src/parser` ingests SPICE `.SUBCKT` hierarchies, `src/transform` manages hierarchy-flattening strategies, and `src/rdf` owns RDFLib serialization. Store reusable SHACL shapes in `schemas/shacl`, ontology vocab in `schemas/ontologies`, and sample netlists or TTL fixtures in `samples/`. Tests live in `tests/` with mirrors of the runtime packages plus `tests/fixtures` for golden SPICE/RDF pairs. Keep documentation, diagrams, and SPARQL notebooks inside `docs/`.

## Build, Test, and Development Commands
`poetry install` sets up the Python toolchain (3.11+) and locks RDFlib, SHACL, and Fuseki client deps. `poetry run pytest` runs the full suite, while `poetry run pytest tests/parser -k hierarchical` targets a single concern. `poetry run ruff check src tests` enforces lint+imports, and `poetry run ruff format` normalizes spacing before commit.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation, explicit type hints, and `snake_case` for functions/modules. Use `PascalCase` for dataclasses representing RDF resources (`ModuleNode`, `LibraryCell`). Encode hierarchy paths with `/`-delimited identifiers (e.g., `top/u1/u2`) and reserve `c:` for schema IRIs to stay aligned with the diagrams.

## Testing Guidelines
Write Pytest modules that mirror package names (`tests/parser/test_netlist_reader.py`). Fixture files go under `tests/fixtures/{netlists,rdf}` with descriptive names like `nand2_partial_flat.ttl`. Each new parser feature needs a round-trip test: parse → hierarchy strategy → RDF serialization → SHACL validation. Target ≥85 % coverage and gate regressions locally with `poetry run pytest --maxfail=1 --cov=src`.

## Commit & Pull Request Guidelines
Use Conventional Commits (`feat:`, `fix:`, `docs:`) so release tooling can derive changelogs. Keep commits focused: parser changes, SHACL updates, and Fuseki integration should land separately. PRs must include a summary, linked issue (if any), reproduction steps, and screenshots or SHACL reports for validation-driven work. Note any data migrations (new named graphs, version switches) so reviewers can replay them locally. Request review once CI passes and no TODOs remain.

## Configuration & Security Notes
Never commit production SPICE netlists; mask IP by trimming to minimal reproductions in `samples/`. Store Fuseki credentials via environment variables (`FUSEKI_URL`, `FUSEKI_TOKEN`) and document required configs in `.env.example`. When contributing SHACL rules, default to warnings for potentially breaking constraints and explain escalation paths in the PR description.

## Active Technologies
- Python 3.11 (Poetry-managed) + rdflib, pySHACL, FastAPI, Pydantic, requests, SPARQLWrapper, Ontotext GraphDB HTTP APIs (001-checklist)
- GraphDB Free (Docker) with mounted `/opt/graphdb/home` dataset plus on-disk Turtle fixtures under `data/` (001-checklist)
- Python 3.11 (Poetry-managed) + rdflib, pySHACL, FastAPI, Pydantic, requests/SPARQLWrapper, Ontotext GraphDB HTTP APIs, typer/Click for CLI wrappers (001-checklist)
- GraphDB Free (Docker) with `/opt/graphdb/home` volume plus on-disk Turtle artifacts under `data/` (001-checklist)

## Recent Changes
- 001-checklist: Added Python 3.11 (Poetry-managed) + rdflib, pySHACL, FastAPI, Pydantic, requests, SPARQLWrapper, Ontotext GraphDB HTTP APIs
