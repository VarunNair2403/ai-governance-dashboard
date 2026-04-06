from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .reporter import generate_report
from .audit import log_governance_event, get_audit_log, get_stats

app = FastAPI(
    title="AI Governance Dashboard",
    description="LLM-powered AI governance and compliance screening mapped to NIST AI RMF",
    version="0.1.0",
)


class ScreenRequest(BaseModel):
    text: str
    context: Optional[str] = "input"


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.post("/screen")
def screen_text(request: ScreenRequest):
    result = generate_report(request.text, request.context)
    log_governance_event(result)
    return {
        "text": request.text,
        "context": request.context,
        "overall_flagged": result["overall_flagged"],
        "overall_severity": result["overall_severity"],
        "overall_risk_score": result["overall_risk_score"],
        "nist_functions_triggered": result["nist_functions_triggered"],
        "findings": result["findings"],
        "report": result["report"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/audit")
def audit_log(limit: Optional[int] = 10):
    return {
        "limit": limit,
        "events": get_audit_log(limit=limit),
    }


@app.get("/stats")
def governance_stats():
    return get_stats()