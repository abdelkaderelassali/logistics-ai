"""Analysis agent for the logistics workflow.

This agent turns the request plus RAG context into an operational plan.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from app.services.llm_service import get_llm

SYSTEM_PROMPT = """You are the analysis agent in a simple logistics workflow.
Use the request details and retrieved context to propose a clear transport plan.
Focus on truck choice, route choice, timing, and any constraints.
Keep the answer short, practical, and easy to present."""


def run_analysis_agent(user_request: str, request_details: dict, rag_context: str) -> str:
    """Generate the first logistics plan."""
    llm = get_llm()
    prompt = (
        f"User request: {user_request}\n"
        f"Parsed details: {request_details}\n\n"
        f"RAG context:\n{rag_context}"
    )
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    return response.content
