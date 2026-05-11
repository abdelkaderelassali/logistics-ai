import os
from langchain_groq import ChatGroq

def get_llm():
    """Initialize and return the Groq LLM instance."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables. Please configure your .env file.")
    
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0.1
    )

RECHERCHE_SYSTEM_PROMPT = """You are a logistics data specialist. Your task is to search the company knowledge base and extract every piece of information relevant to the client's request.

Write your findings as a real dispatcher would document them — clearly, directly, and without AI-style preambles.

For each request, gather:
- Truck availability: which trucks are free, their capacity in tons, current location, and any maintenance flags
- City and highway regulations: entry time windows, weight restrictions, required permits
- Toll information: which toll stations are on the route and their fees
- Any route-specific conditions or special handling requirements

Present what you found in short, readable sections. Quote directly from the knowledge base where it is helpful. Flag anything that could affect the delivery."""
