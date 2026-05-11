import logging
import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph_agents.agent_1_recherche import get_llm, RECHERCHE_SYSTEM_PROMPT
from langgraph_agents.agent_2_analyse import ANALYSE_SYSTEM_PROMPT
from langgraph_agents.agent_3_validation import VALIDATION_SYSTEM_PROMPT
from langgraph_agents.agent_4_redaction import REDACTION_SYSTEM_PROMPT
from langgraph_agents.rag_6_llamaindex import setup_rag_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Define the State
class LogisticsState(TypedDict):
    user_request: str
    rag_context: str
    analysis_plan: str
    validation_report: str
    final_response: str

# Global RAG tool (cached)
_rag_tool = None

def get_rag_tool():
    """Get or initialize the RAG tool (singleton pattern)."""
    global _rag_tool
    if _rag_tool is None:
        _rag_tool = setup_rag_pipeline()
    return _rag_tool

# 2. Define the Nodes with Enhanced Error Handling

def recherche_node(state: LogisticsState):
    """
    Agent Recherche: Search the knowledge base for relevant information.
    Extracts truck specs, regulations, maintenance status, etc.
    """
    print("\n[Agent Recherche] Searching knowledge base...")
    try:
        rag_tool = get_rag_tool()
        
        # Direct RAG query without tool binding to reduce API calls
        print(f"  Querying knowledge base for: '{state['user_request'][:60]}...'")
        time.sleep(1)  # Add rate limit buffer
        context_gathered = rag_tool.invoke(state["user_request"])
        
        print(f"  Search complete. Context retrieved: {len(str(context_gathered))} chars")
        return {"rag_context": str(context_gathered)}
        
    except Exception as e:
        logger.error(f"Error in recherche_node: {e}")
        return {"rag_context": f"[Error retrieving context: {str(e)}]"}

def analyse_node(state: LogisticsState):
    """
    Agent Analyse: Analyze requirements and propose a logistics plan.
    Matches cargo with available trucks and routes.
    """
    print("\n[Agent Analyse] Analyzing request and formulating plan...")
    try:
        llm = get_llm()
        prompt = f"User Request: {state['user_request']}\n\nGathered Facts:\n{state['rag_context']}"
        time.sleep(1)  # Add rate limit buffer
        response = llm.invoke([
            SystemMessage(content=ANALYSE_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        result = response.content
        print(f"  Analysis complete. Plan generated: {len(result)} chars")
        return {"analysis_plan": result}
        
    except Exception as e:
        logger.error(f"Error in analyse_node: {e}")
        return {"analysis_plan": f"[Error analyzing request: {str(e)}]"}

def validation_node(state: LogisticsState):
    """
    Agent Validation: Verify plan compliance with regulations and constraints.
    Identifies violations and suggests alternatives.
    """
    print("\n[Agent Validation] Validating plan against constraints...")
    try:
        llm = get_llm()
        prompt = f"Rules & Constraints:\n{state['rag_context']}\n\nProposed Plan:\n{state['analysis_plan']}"
        time.sleep(1)  # Add rate limit buffer
        response = llm.invoke([
            SystemMessage(content=VALIDATION_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        result = response.content
        print(f"  Validation complete. Report generated: {len(result)} chars")
        return {"validation_report": result}
        
    except Exception as e:
        logger.error(f"Error in validation_node: {e}")
        return {"validation_report": f"[Error validating plan: {str(e)}]"}

def redaction_node(state: LogisticsState):
    """
    Agent Rédaction: Draft final professional response for client.
    Compiles analysis and validation into a structured report.
    """
    print("\n[Agent Redaction] Drafting final response...")
    try:
        llm = get_llm()
        prompt = f"User Request: {state['user_request']}\n\nValidation Report (including the plan):\n{state['validation_report']}"
        time.sleep(1)  # Add rate limit buffer
        response = llm.invoke([
            SystemMessage(content=REDACTION_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        result = response.content
        print(f"  Drafting complete. Response generated: {len(result)} chars")
        return {"final_response": result}
        
    except Exception as e:
        logger.error(f"Error in redaction_node: {e}")
        return {"final_response": f"[Error generating final response: {str(e)}]"}

# 3. Build the Graph
def build_orchestrator():
    """
    Build and compile the LangGraph orchestrator.
    Defines the sequential workflow of the 4 agents.
    """
    logger.info("Building orchestrator graph...")
    workflow = StateGraph(LogisticsState)
    
    # Add nodes
    workflow.add_node("Agent_Recherche", recherche_node)
    workflow.add_node("Agent_Analyse", analyse_node)
    workflow.add_node("Agent_Validation", validation_node)
    workflow.add_node("Agent_Redaction", redaction_node)
    
    # Add edges (Sequential flow: Recherche -> Analyse -> Validation -> Redaction)
    workflow.set_entry_point("Agent_Recherche")
    workflow.add_edge("Agent_Recherche", "Agent_Analyse")
    workflow.add_edge("Agent_Analyse", "Agent_Validation")
    workflow.add_edge("Agent_Validation", "Agent_Redaction")
    workflow.add_edge("Agent_Redaction", END)
    
    # Compile the graph
    app = workflow.compile()
    logger.info("Orchestrator graph compiled successfully")
    return app
