"""Dashboard backend — FastAPI app serving /api/results + static index.html.

Usage:
  python -m dashboard.serve
  → http://127.0.0.1:8766

Endpoints:
  GET /                — static index.html
  GET /api/results     — list result JSON files in results/
  GET /api/results/{f} — fetch a specific result file
  GET /api/scenarios   — list all scenarios metadata
"""
from __future__ import annotations

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn


ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
SCENARIOS_DIR = ROOT / "scenarios"
DASHBOARD_DIR = Path(__file__).resolve().parent


app = FastAPI(title="TRUSTFALL Dashboard")


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html_path = DASHBOARD_DIR / "index.html"
    return HTMLResponse(html_path.read_text())


@app.get("/api/results")
def list_results() -> dict:
    if not RESULTS_DIR.exists():
        return {"files": []}
    files = sorted([p.name for p in RESULTS_DIR.glob("*.json")])
    return {"files": files}


@app.get("/api/results/{filename}")
def get_result(filename: str) -> JSONResponse:
    # Basic path-traversal guard
    if "/" in filename or ".." in filename:
        raise HTTPException(400, "invalid filename")
    path = RESULTS_DIR / filename
    if not path.exists():
        raise HTTPException(404, "not found")
    return JSONResponse(json.loads(path.read_text()))


@app.get("/api/scenarios")
def list_scenarios() -> dict:
    from corpsim.common.scenarios import load_all_scenarios
    scens = load_all_scenarios(SCENARIOS_DIR)
    return {
        "scenarios": [
            {
                "id": s.id,
                "threat_class": s.threat_class,
                "title": s.title,
                "description": s.description[:500],
                "severity_weight": s.ground_truth.severity_weight,
                "economic_severity_usd": s.ground_truth.economic_severity_usd,
            }
            for s in scens
        ]
    }


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=8766, log_level="info")


if __name__ == "__main__":
    main()
