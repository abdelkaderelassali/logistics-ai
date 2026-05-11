from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import os
import re
from dotenv import load_dotenv

from langgraph_agents.orchestrateur_5_langchain import build_orchestrator
from app.graph_router import get_all_cities, calculate_route

# Load environment variables
load_dotenv()

app = FastAPI(title="Logistics AI Assistant API")

# Allow CORS for React frontend (default runs on 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = None

@app.on_event("startup")
def startup_event():
    global orchestrator
    try:
        orchestrator = build_orchestrator()
        print("System: AI Orchestrator initialized successfully")
    except Exception as e:
        print(f"Error: Failed to initialize AI Orchestrator: {e}")

class AIRequest(BaseModel):
    request: str = Field(..., min_length=10)

@app.get("/api/health")
def health():
    return {
        "status": "healthy" if orchestrator else "initializing",
        "api_key_configured": bool(os.getenv("GROQ_API_KEY"))
    }

@app.get("/api/cities")
def get_cities():
    return {"count": len(get_all_cities()), "cities": get_all_cities()}

@app.get("/api/route/{optimize}")
def get_route(optimize: str, request: Request):
    from_city = request.query_params.get("from", "Casablanca")
    to_city = request.query_params.get("to", "Tanger")
    route = calculate_route(from_city, to_city, optimize)
    if not route:
        raise HTTPException(status_code=404, detail="City not found")
    return route

@app.post("/api/route/multi")
def get_multi_route(payload: dict):
    # For simplicity, just calculate start to end
    stops = payload.get("stops", [])
    if len(stops) < 2:
        raise HTTPException(status_code=400, detail="At least 2 stops required")
    route = calculate_route(stops[0], stops[-1], payload.get("optimize", "distance"))
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    # Tweak the response to match multi
    route["stops"] = len(stops)
    return route

def extract_cities_from_text(text: str):
    cities = [c["name"] for c in get_all_cities()]
    found = []
    for c in cities:
        if c.lower() in text.lower() and c not in found:
            found.append(c)
    return found

@app.post("/api/process")
def process_request(payload: AIRequest):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="AI System not initialized")
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=400, detail="GROQ_API_KEY is not configured in .env")

    try:
        state = {
            "user_request": payload.request,
            "rag_context": "",
            "analysis_plan": "",
            "validation_report": "",
            "final_response": ""
        }
        
        final_state = orchestrator.invoke(state)
        
        # Try to extract a route from the AI response to control the map automatically!
        found_cities = extract_cities_from_text(payload.request)
        ai_route = None
        if len(found_cities) >= 2:
            # Assume first is origin, second is destination
            ai_route = calculate_route(found_cities[0], found_cities[1], "distance")
        
        return {
            "rag_context": final_state.get("rag_context", "No context generated."),
            "analysis_plan": final_state.get("analysis_plan", "No analysis generated."),
            "validation_report": final_state.get("validation_report", "No validation generated."),
            "final_response": final_state.get("final_response", "No response generated."),
            "ai_route": ai_route
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
