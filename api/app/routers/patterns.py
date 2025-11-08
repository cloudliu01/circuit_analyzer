from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SubcktIn(BaseModel):
    name: str
    text: str

@router.post("/translate")
def translate(subckt: SubcktIn):
    # Minimal placeholder: return a sketch SPARQL for an inverter-like subckt
    # In production, parse the .SUBCKT and build a topology-aware template.
    sparql = f"""PREFIX ckt: <http://example.org/ckt#>
SELECT DISTINCT ?dev ?in ?out WHERE {{
  ?pm a ckt:Device ; ckt:type "PMOS" ; ckt:connectsTo ?in, ?out .
  ?nm a ckt:Device ; ckt:type "NMOS" ; ckt:connectsTo ?in, ?out .
  FILTER(?pm != ?nm)
}}"""
    return {"pattern": subckt.name, "sparql": sparql}
