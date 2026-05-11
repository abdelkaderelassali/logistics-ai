"""Simple sequential orchestrator for the AI logistics project.

This file shows the full teaching workflow:
User Request -> Search Agent -> Analysis Agent -> Validation Agent -> Writer Agent
"""

from datetime import datetime

from app.agents.analysis.agent import run_analysis_agent
from app.agents.search.agent import run_search_agent
from app.agents.validation.agent import run_validation_agent
from app.agents.writer.agent import run_writer_agent


def _step(name: str, status: str) -> dict:
    return {"name": name, "status": status, "timestamp": datetime.now().isoformat()}


def run_logistics_workflow(user_request: str) -> dict:
    """Run the complete AI workflow and return all intermediate outputs."""
    workflow = []

    workflow.append(_step("Search", "running"))
    search_result = run_search_agent(user_request)
    workflow[-1]["status"] = "completed"

    workflow.append(_step("Analysis", "running"))
    analysis_plan = run_analysis_agent(
        user_request,
        search_result["request_details"],
        search_result["rag_context"],
    )
    workflow[-1]["status"] = "completed"

    workflow.append(_step("Validation", "running"))
    validation_report = run_validation_agent(
        user_request,
        search_result["rag_context"],
        analysis_plan,
    )
    workflow[-1]["status"] = "completed"

    workflow.append(_step("Writer", "running"))
    final_response = run_writer_agent(user_request, analysis_plan, validation_report)
    workflow[-1]["status"] = "completed"

    return {
        "user_request": user_request,
        "request_details": search_result["request_details"],
        "rag_context": search_result["rag_context"],
        "analysis_plan": analysis_plan,
        "validation_report": validation_report,
        "final_response": final_response,
        "workflow": workflow,
    }
