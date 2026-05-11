import os
import sys
from dotenv import load_dotenv

# Add the backend to path
sys.path.append(os.path.abspath("./Smart-Logistics-Route-Optimizer-main/python_backend"))

load_dotenv("./Smart-Logistics-Route-Optimizer-main/python_backend/.env")

print("Testing imports...")
try:
    from langgraph_agents.orchestrateur_5_langchain import build_orchestrator
    print("OK: orchestrateur_5_langchain imported")
    
    from langgraph_agents.rag_6_llamaindex import setup_rag_pipeline
    print("OK: rag_6_llamaindex imported")
    
    from langgraph_agents.agent_1_recherche import get_llm
    print("OK: agent_1_recherche imported")
    
    print("Building orchestrator...")
    orchestrator = build_orchestrator()
    print("OK: Orchestrator built")
    
    print("All imports and build successful!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
