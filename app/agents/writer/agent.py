"""Writer agent for the logistics workflow.

This is the final agent that formats the result for the user.
"""

from langchain_core.messages import HumanMessage, SystemMessage

from app.services.llm_service import get_llm

SYSTEM_PROMPT = """You are the writer agent in a simple logistics workflow.
Write the final answer in a clean, professional style.
Use the validation result to give the final recommendation.
Keep it easy to read for a university presentation."""


def run_writer_agent(user_request: str, analysis_plan: str, validation_report: str) -> str:
    """Create the final user-facing response."""
    llm = get_llm()
    prompt = (
        f"User request: {user_request}\n\n"
        f"Analysis plan:\n{analysis_plan}\n\n"
        f"Validation report:\n{validation_report}"
    )
    response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
    return response.content
