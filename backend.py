"""FastAPI backend for enterprise logistics optimization platform."""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import random
import re
import uuid
import time
import io
import csv

import sys
from pathlib import Path
# Add subfolder to path so we can import agents
root_dir = Path(__file__).parent.absolute()
sub_backend = root_dir / "Smart-Logistics-Route-Optimizer-main" / "python_backend"
if str(sub_backend) not in sys.path:
    sys.path.append(str(sub_backend))

from langgraph_agents.orchestrateur_5_langchain import build_orchestrator

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Dispatch Center API",
    description="Operational logistics platform and automated planning engine",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
orchestrator = None
request_history = []
active_sessions: Dict[str, Dict[str, str]] = {}

users = {
    "admin": {"password": "admin123", "role": "Admin", "name": "Operations Admin"},
    "dispatch": {"password": "dispatch123", "role": "Dispatcher", "name": "Route Dispatcher"},
    "driver": {"password": "driver123", "role": "Driver", "name": "Fleet Driver"},
}

fleet_data = [
    {
        "id": "TRK-ALPHA",
        "name": "Volvo FH16",
        "capacity_tons": 20,
        "status": "available",
        "fuel_efficiency_km_l": 8.0,
        "maintenance_risk": "low",
        "utilization_pct": 62,
        "location": "Rabat",
    },
    {
        "id": "TRK-BETA",
        "name": "Mercedes Actros",
        "capacity_tons": 15,
        "status": "in_delivery",
        "fuel_efficiency_km_l": 7.2,
        "maintenance_risk": "medium",
        "utilization_pct": 79,
        "location": "Casablanca",
    },
    {
        "id": "TRK-GAMMA",
        "name": "MAN TGX",
        "capacity_tons": 28,
        "status": "maintenance",
        "fuel_efficiency_km_l": 6.6,
        "maintenance_risk": "high",
        "utilization_pct": 38,
        "location": "Tangier",
    },
]


# ============================================================================
# DATA MODELS
# ============================================================================

class LogisticsRequest(BaseModel):
    """Client request model"""
    request: str = Field(..., min_length=10, max_length=500, description="Logistics request")
    client_id: Optional[str] = Field(None, description="Optional client identifier")


class AgentResponse(BaseModel):
    """Individual agent response"""
    agent: str
    status: str
    output: str
    timestamp: str


class LogisticsResponse(BaseModel):
    """Complete orchestrator response"""
    request_id: str
    user_request: str
    rag_context: str
    analysis_plan: str
    validation_report: str
    final_response: str
    agents: List[AgentResponse]
    workflow: List[dict]
    truck_recommendation: dict
    operational_summary: dict
    processing_time: float
    status: str


class SystemStatus(BaseModel):
    """System health status"""
    status: str
    api_configured: bool
    orchestrator_ready: bool
    history_count: int
    timestamp: str


class LoginRequest(BaseModel):
    username: str
    password: str


class WhatIfRequest(BaseModel):
    scenario: str
    truck_id: Optional[str] = None
    delay_minutes: Optional[int] = 0


def _extract_weight_tons(request_text: str) -> Optional[float]:
    match = re.search(r"(\d+(?:\.\d+)?)\s*tons?", request_text.lower())
    if not match:
        return None
    return float(match.group(1))


def _recommend_truck(request_text: str) -> Dict[str, Any]:
    required = _extract_weight_tons(request_text)
    available = [t for t in fleet_data if t["status"] == "available"]
    if not available:
        return {
            "name": "No available truck",
            "status": "blocked",
            "reason": "All fleet units are currently unavailable.",
        }

    if required is None:
        chosen = sorted(available, key=lambda x: x["capacity_tons"])[0]
        return {
            "name": chosen["name"],
            "truck_id": chosen["id"],
            "capacity_tons": chosen["capacity_tons"],
            "status": "recommended",
            "reason": "No cargo weight detected. Assigned smallest suitable available truck.",
        }

    candidates = [t for t in available if t["capacity_tons"] >= required]
    if not candidates:
        return {
            "name": "No available truck",
            "status": "blocked",
            "reason": f"Required {required}t but no available truck matches this capacity.",
        }

    chosen = sorted(candidates, key=lambda x: x["capacity_tons"])[0]
    return {
        "name": chosen["name"],
        "truck_id": chosen["id"],
        "capacity_tons": chosen["capacity_tons"],
        "status": "recommended",
        "reason": f"Selected for {required}t cargo with best-fit capacity.",
    }


def _build_workflow(start_time: float, end_time: float) -> List[dict]:
    labels = [
        "Parsing Request",
        "Searching Regulations",
        "Checking Fleet",
        "Route Optimization",
        "Compliance Validation",
        "Generating Delivery Plan",
    ]
    total_ms = max(1, int((end_time - start_time) * 1000))
    step_ms = max(150, total_ms // len(labels))
    base_ts = datetime.now()
    output = []
    for idx, label in enumerate(labels):
        ts = base_ts.timestamp() + ((idx + 1) * step_ms / 1000)
        output.append(
            {
                "step": idx + 1,
                "label": label,
                "status": "completed",
                "duration_ms": step_ms,
                "timestamp": datetime.fromtimestamp(ts).isoformat(),
            }
        )
    return output


def _get_role_kpis(role: str) -> Dict[str, Any]:
    role_lower = role.lower()
    if role_lower == "admin":
        return {
            "title": "Admin Control Center",
            "highlights": [
                "Global fleet utilization: 59%",
                "Compliance score: 96%",
                "Open incidents: 2",
            ],
        }
    if role_lower == "dispatcher":
        return {
            "title": "Dispatcher Queue",
            "highlights": [
                "Pending manifests: 4",
                "Reroute candidates: 2",
                "Average dispatch latency: 7 min",
            ],
        }
    return {
        "title": "Driver Mission Console",
        "highlights": [
            "Assigned route: Rabat -> Casablanca",
            "Next checkpoint ETA: 42 min",
            "Cargo integrity alerts: 0",
        ],
    }


# ============================================================================
# INITIALIZATION
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global orchestrator
    try:
        logger.info("Initializing Logistics Assistant System...")
        orchestrator = build_orchestrator()
        logger.info("System initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}")
        raise


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Serve frontend"""
    return FileResponse("frontend/index.html")


@app.get("/api/health")
async def health_check() -> SystemStatus:
    """Check system health and readiness"""
    api_key = os.environ.get("GROQ_API_KEY")
    return SystemStatus(
        status="healthy" if orchestrator else "initializing",
        api_configured=bool(api_key and api_key != "your_groq_api_key_here"),
        orchestrator_ready=orchestrator is not None,
        history_count=len(request_history),
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/auth/login")
async def login(req: LoginRequest) -> dict:
    user = users.get(req.username.lower())
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = str(uuid.uuid4())
    active_sessions[token] = {
        "username": req.username,
        "role": user["role"],
        "name": user["name"],
    }
    return {
        "token": token,
        "role": user["role"],
        "name": user["name"],
        "message": f"Authenticated as {user['role']}",
    }


@app.get("/api/auth/profile")
async def profile(token: str) -> dict:
    session = active_sessions.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or invalid token")
    return session


@app.get("/api/role-dashboard/{role}")
async def role_dashboard(role: str) -> dict:
    return _get_role_kpis(role)


@app.post("/api/process")
async def process_request(req: LogisticsRequest) -> LogisticsResponse:
    """
    Process a logistics request through the multi-agent system
    
    Args:
        req: LogisticsRequest with user query
        
    Returns:
        LogisticsResponse with complete agent outputs and final plan
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    if not os.environ.get("GROQ_API_KEY"):
        raise HTTPException(
            status_code=400,
            detail="GROQ_API_KEY not configured. Please set up your environment."
        )
    
    try:
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        # Invoke orchestrator
        state = {
            "user_request": req.request,
            "rag_context": "",
            "analysis_plan": "",
            "validation_report": "",
            "final_response": ""
        }
        
        final_state = orchestrator.invoke(state)
        processing_time = time.time() - start_time
        workflow = _build_workflow(start_time, time.time())
        truck_recommendation = _recommend_truck(req.request)
        
        # Build agent timeline
        agents = [
            AgentResponse(
                agent="Recherche",
                status="completed",
                output=final_state.get("rag_context", ""),
                timestamp=datetime.now().isoformat()
            ),
            AgentResponse(
                agent="Analyse",
                status="completed",
                output=final_state.get("analysis_plan", ""),
                timestamp=datetime.now().isoformat()
            ),
            AgentResponse(
                agent="Validation",
                status="completed",
                output=final_state.get("validation_report", ""),
                timestamp=datetime.now().isoformat()
            ),
            AgentResponse(
                agent="Rédaction",
                status="completed",
                output=final_state.get("final_response", ""),
                timestamp=datetime.now().isoformat()
            ),
        ]
        
        response = LogisticsResponse(
            request_id=request_id,
            user_request=req.request,
            rag_context=final_state.get("rag_context", ""),
            analysis_plan=final_state.get("analysis_plan", ""),
            validation_report=final_state.get("validation_report", ""),
            final_response=final_state.get("final_response", ""),
            agents=agents,
            workflow=workflow,
            truck_recommendation=truck_recommendation,
            operational_summary={
                "fuel_estimate_l": round(random.uniform(65, 120), 1),
                "eta_hours": round(random.uniform(2.5, 7.5), 1),
                "risk_level": random.choice(["low", "medium"]),
            },
            processing_time=processing_time,
            status="completed"
        )
        
        # Store in history
        request_history.append({
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "request": req.request,
            "processing_time": processing_time
        })
        
        logger.info(f"Request {request_id} processed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/api/history")
async def get_history(limit: int = 10) -> List[dict]:
    """Get recent request history"""
    return request_history[-limit:]


@app.get("/api/stats")
async def get_stats() -> dict:
    """Get system statistics"""
    if not request_history:
        return {
            "total_requests": 0,
            "avg_processing_time": 0,
            "min_processing_time": 0,
            "max_processing_time": 0
        }
    
    times = [r["processing_time"] for r in request_history]
    return {
        "total_requests": len(request_history),
        "avg_processing_time": sum(times) / len(times),
        "min_processing_time": min(times),
        "max_processing_time": max(times)
    }


@app.get("/api/fleet-overview")
async def get_fleet_overview() -> dict:
    """Operational fleet counters and chart-ready data."""
    available = sum(1 for t in fleet_data if t["status"] == "available")
    maintenance = sum(1 for t in fleet_data if t["status"] == "maintenance")
    in_delivery = sum(1 for t in fleet_data if t["status"] == "in_delivery")
    active_deliveries = max(1, in_delivery)
    fuel_consumption = round(sum((100 / t["fuel_efficiency_km_l"]) for t in fleet_data), 2)
    completed_missions = 74 + len(request_history)

    return {
        "kpis": {
            "available_trucks": available,
            "in_maintenance": maintenance,
            "active_deliveries": active_deliveries,
            "fuel_consumption_index": fuel_consumption,
            "completed_missions": completed_missions,
        },
        "truck_cards": fleet_data,
        "utilization": [
            {"name": t["name"], "value": t["utilization_pct"]} for t in fleet_data
        ],
        "status_distribution": [
            {"name": "Available", "value": available},
            {"name": "In Delivery", "value": in_delivery},
            {"name": "Maintenance", "value": maintenance},
        ],
    }


@app.get("/api/live-simulation")
async def get_live_simulation() -> dict:
    """Lightweight live simulation data for map and bottom cards."""
    return {
        "truck": {
            "id": "TRK-ALPHA",
            "name": "Volvo FH16",
            "lat": 33.9806 + random.uniform(-0.03, 0.03),
            "lng": -6.8326 + random.uniform(-0.03, 0.03),
            "speed_kmh": random.randint(58, 82),
            "fuel_pct": random.randint(46, 88),
            "eta_minutes": random.randint(90, 245),
        },
        "route": {
            "origin": "Rabat",
            "destination": "Casablanca",
            "distance_km": 87,
            "risk_alerts": random.choice(
                [
                    ["Urban delivery window starts at 14:00"],
                    ["Moderate congestion near Mohammedia"],
                    ["Toll station queue detected on A1"],
                ]
            ),
        },
    }


@app.post("/api/upload-manifest")
async def upload_manifest(file: UploadFile = File(...)) -> dict:
    filename = file.filename or "unknown"
    ext = filename.lower().split(".")[-1] if "." in filename else ""
    content = await file.read()

    if ext == "csv":
        text = content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        preview = rows[:5]
        return {
            "file": filename,
            "type": "csv",
            "rows_detected": len(rows),
            "columns": reader.fieldnames or [],
            "preview": preview,
        }

    if ext == "pdf":
        reader = PdfReader(io.BytesIO(content))
        extracted = []
        for page in reader.pages[:2]:
            extracted.append((page.extract_text() or "").strip())
        joined = "\n".join(extracted).strip()
        return {
            "file": filename,
            "type": "pdf",
            "pages_scanned": min(2, len(reader.pages)),
            "extracted_preview": joined[:1200],
        }

    raise HTTPException(status_code=400, detail="Unsupported file type. Upload CSV or PDF.")


@app.post("/api/what-if")
async def what_if_simulation(req: WhatIfRequest) -> dict:
    scenario = req.scenario.lower()
    base_eta = random.randint(95, 165) + max(0, req.delay_minutes or 0)
    suggested_route = random.choice(["A1 Express", "N1 Toll Saver", "A3 Night Lane"])

    if "breakdown" in scenario:
        alternatives = [t for t in fleet_data if t["status"] == "available" and t["id"] != req.truck_id]
        reassigned = alternatives[0]["name"] if alternatives else "No immediate reassignment"
        return {
            "scenario": req.scenario,
            "impact": "Critical",
            "action": "Reassign truck and reroute mission",
            "reassigned_truck": reassigned,
            "new_eta_minutes": base_eta + 35,
            "route": suggested_route,
            "fuel_delta_l": 12,
        }

    if "traffic" in scenario:
        return {
            "scenario": req.scenario,
            "impact": "Medium",
            "action": "Switch to lower congestion corridor",
            "reassigned_truck": "No reassignment required",
            "new_eta_minutes": base_eta + 22,
            "route": "N1 Alternate",
            "fuel_delta_l": 5,
        }

    return {
        "scenario": req.scenario,
        "impact": "Low",
        "action": "Maintain primary plan with monitoring",
        "reassigned_truck": "Not required",
        "new_eta_minutes": base_eta,
        "route": suggested_route,
        "fuel_delta_l": 2,
    }


@app.post("/api/route-options")
async def get_route_options(payload: Dict[str, str]) -> dict:
    """Return route options using OSRM public API with fallback values."""
    origin = payload.get("origin", "Rabat")
    destination = payload.get("destination", "Casablanca")

    city_coords = {
        "rabat": (-6.83255, 34.02088),
        "casablanca": (-7.58984, 33.57311),
        "tangier": (-5.79975, 35.75947),
        "marrakech": (-8.00889, 31.62947),
    }
    o = city_coords.get(origin.lower())
    d = city_coords.get(destination.lower())

    if not o or not d:
        return {
            "origin": origin,
            "destination": destination,
            "options": [
                {
                    "profile": "Fastest",
                    "distance_km": 120,
                    "duration_min": 130,
                    "toll_mad": 42,
                }
            ],
        }

    try:
        url = (
            "https://router.project-osrm.org/route/v1/driving/"
            f"{o[0]},{o[1]};{d[0]},{d[1]}?overview=false&alternatives=true"
        )
        res = requests.get(url, timeout=6)
        res.raise_for_status()
        body = res.json()
        routes = body.get("routes", [])[:3]
        options = []
        for idx, route in enumerate(routes, start=1):
            options.append(
                {
                    "profile": f"Option {idx}",
                    "distance_km": round(route["distance"] / 1000, 1),
                    "duration_min": int(route["duration"] / 60),
                    "toll_mad": random.randint(25, 70),
                }
            )

        if not options:
            raise ValueError("No routes returned")

        return {"origin": origin, "destination": destination, "options": options}
    except Exception:
        return {
            "origin": origin,
            "destination": destination,
            "options": [
                {
                    "profile": "Fallback Fastest",
                    "distance_km": 87,
                    "duration_min": 95,
                    "toll_mad": 32,
                },
                {
                    "profile": "Fallback Toll Saver",
                    "distance_km": 102,
                    "duration_min": 122,
                    "toll_mad": 12,
                },
            ],
        }


# Mount frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
