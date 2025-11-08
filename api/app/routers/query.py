import os, requests
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

FUSEKI_QUERY_ENDPOINT = os.getenv("FUSEKI_QUERY_ENDPOINT", "http://fuseki:3030/dataset/query")

class QueryIn(BaseModel):
    sparql: str

@router.post("/run")
def run_query(q: QueryIn):
    headers = {"Accept": "application/sparql-results+json"}
    data = {"query": q.sparql}
    r = requests.post(FUSEKI_QUERY_ENDPOINT, data=data, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()
