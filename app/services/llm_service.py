"""Shared LLM service used by all agents.

This file keeps the model setup in one place so the workflow stays easy to follow.
"""

from os import getenv

from langchain_groq import ChatGroq

MODEL_NAME = "llama-3.1-8b-instant"


def get_llm() -> ChatGroq:
    """Return the shared Groq model for the logistics agents."""
    api_key = getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Please set it in .env")

    return ChatGroq(model=MODEL_NAME, api_key=api_key, temperature=0.1)
