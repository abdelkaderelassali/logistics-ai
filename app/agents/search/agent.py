"""Search agent for the logistics workflow.

It retrieves private knowledge from RAG and prepares the facts for the next agent.
"""

from app.rag.retriever.retriever import retrieve_context
from app.services.request_parser import parse_request


def run_search_agent(user_request: str) -> dict:
    """Return request details and retrieved context."""
    return {
        "request_details": parse_request(user_request),
        "rag_context": retrieve_context(user_request),
    }
