"""Validation agent for the logistics workflow.

It checks the analysis against fleet and regulation constraints.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from app.services.llm_service import get_llm

SYSTEM_PROMPT = """You are the validation agent in a simple logistics workflow.
Check whether the proposed plan is valid.
Look for capacity issues, city restrictions, maintenance issues, and timing problems.
Return a short validation report with either approval or clear warnings."""


def run_validation_agent(user_request: str, rag_context: str, analysis_plan: str) -> str:
    """Validate the proposed logistics plan."""
    llm = get_llm()
    prompt = (
        f"User request: {user_request}\n\n"
        f"RAG context:\n{rag_context}\n\n"
        f"Proposed plan:\n{analysis_plan}"
    )
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    return response.content
