# Quickstart: Circuit Ontology Schema and Pattern-Matching Engine

## Prerequisites
- Python 3.11 with Poetry installed.
- Docker + Docker Compose v2.
- 8 GB RAM free for GraphDB + API containers.

## 1. Install dependencies
```bash
poetry install
poetry run ruff check .
```

## 2. Launch GraphDB + API stack
```bash
docker compose up -d graphdb api
```
- GraphDB UI: http://localhost:7200
- API docs (FastAPI): http://localhost:8000/docs

## 3. Seed repository & fixtures
```bash
curl -X POST http://localhost:7200/rest/repositories \
  -H 'Content-Type: application/json' \
  -d @specs/001-checklist/contracts/graphdb-repo-config.json
curl -X PUT http://localhost:7200/repositories/circuit/statements \
  -H 'Content-Type: text/turtle' \
  --data-binary @data/seed.ttl
```

## 4. Ingest a CDL design
CLI workflow:
```bash
poetry run ingest-cdl --input samples/foo.cdl --design foo --out data/foo
curl -X PUT http://localhost:7200/repositories/circuit/statements \
  -H 'Content-Type: text/turtle' \
  --data-binary @data/foo/design/foo.ttl
```
API workflow:
```bash
curl -X POST http://localhost:8000/ingest \
  -H 'X-Api-Key: $API_KEY' \
  -F designName=foo \
  -F cdl=@samples/foo.cdl
```
- Response returns ingestion ID and named graph URI.

## 5. Run validation & tests
```bash
poetry run pytest --maxfail=1 --cov=api --cov=src
poetry run pytest tests/test_esd_rules.py -k pad
poetry run ruff format api tests
```

## 6. Register a pattern
```bash
curl -X POST http://localhost:8000/patterns \
  -H 'Content-Type: application/json' \
  -d @patterns/example_pattern.json
```
- Response includes `patternId`, SPARQL hash, and persisted metadata.

## 7. Execute constrained reachability
```bash
curl -X POST http://localhost:8000/query/reachability \
  -H 'Content-Type: application/json' \
  -d '{"top_pin":"PAD_A1","direction":"PAD_TO_VSS","depth":3}'
```
- Expect RDF/JSON-LD response with evidence path, status, and missing components.

## 8. Shut down
```bash
docker compose down
```

## Troubleshooting
- **GraphDB not healthy**: `docker compose logs graphdb`, ensure `data/` volume has write permission.
- **SHACL failures**: Run `poetry run pytest tests/test_esd_rules.py -k shacl` to inspect reports under `tests/artifacts`.
- **Slow queries**: Capture `X-GraphDB-QueryID` from API logs and profile via GraphDB Workbench.
