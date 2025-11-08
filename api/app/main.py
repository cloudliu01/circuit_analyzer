from fastapi import FastAPI
from .routers import patterns, query

app = FastAPI(title="Circuit Analyzer API", version="0.1.0")
app.include_router(patterns.router, prefix="/patterns", tags=["patterns"])
app.include_router(query.router, prefix="/query", tags=["query"])

@app.get("/health")
def health():
    return {"status": "ok"}
