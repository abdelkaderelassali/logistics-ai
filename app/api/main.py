"""Minimal FastAPI app for the logistics AI workflow.

This is the only API layer the student needs to explain during presentation.
"""

import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.workflow.orchestrator import run_logistics_workflow

app = FastAPI(title="AI Logistics Workflow", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WorkflowRequest(BaseModel):
    request: str = Field(..., min_length=10, max_length=500)


@app.get("/")
def home():
    return FileResponse("frontend/index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "api_key_configured": bool(os.getenv("GROQ_API_KEY")),
        "time": datetime.now().isoformat(),
    }


@app.post("/api/process")
def process_request(payload: WorkflowRequest):
    try:
        return run_logistics_workflow(payload.request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


app.mount("/static", StaticFiles(directory="frontend"), name="static")
