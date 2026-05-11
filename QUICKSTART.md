#!/usr/bin/env python3
# QUICK START GUIDE - Intelligent Logistics & Routing Assistant

"""
QUICK START: 30 SECONDS ⚡

1. Install dependencies:
   pip install -r requirements.txt

2. Configure your API key:
   - Copy .env.example to .env
   - Add your Groq API key to .env

3. Test connection (optional):
   python test_connection.py

4. Run the system:
   python main.py

That's it! 🚀
"""

# ============================================================================
# ARCHITECTURE OVERVIEW
# ============================================================================

ARCHITECTURE_DOCS = """
🏗️ SYSTEM ARCHITECTURE

┌─────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │  LangGraph Orchestrator (main.py)  │
         │  - Manages agent workflow         │
         │  - Maintains state across agents   │
         │  - Handles error recovery          │
         └─────────────────┬──────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         ┌────▼────────┐         ┌─────▼────────┐
         │ RAG Pipeline │         │ Groq LLM API │
         │(LlamaIndex)  │         │ (llama-3.1)  │
         └────┬────────┘         └──────────────┘
              │
         ┌────▼────────────┐
         │ ChromaDB        │
         │ (Vector Store)  │
         └─────────────────┘

AGENT PIPELINE (Sequential):
User Request
    ↓
[1] Agent Recherche (Search)
    - Queries RAG to extract context
    - Retrieves fleet, regulations, maintenance data
    ↓
[2] Agent Analyse (Analysis)
    - Uses RAG context to propose solution
    - Selects truck, plans route
    ↓
[3] Agent Validation (Compliance)
    - Validates plan against constraints
    - Detects violations, suggests alternatives
    ↓
[4] Agent Rédaction (Writing)
    - Formats professional response
    - Compiles final recommendation
    ↓
Final Response to User
"""

# ============================================================================
# FILE STRUCTURE
# ============================================================================

FILE_STRUCTURE = """
📂 PROJECT FILES

main.py                    - Entry point, interactive CLI
├─ Prompts user for requests
├─ Initializes orchestrator
└─ Displays results

test_connection.py         - Diagnostic tool
├─ Checks environment variables
├─ Tests Groq API connection
├─ Verifies embeddings
├─ Tests RAG pipeline
└─ Validates orchestrator

demo.py                    - Demo scenarios
├─ Runs 6 predefined scenarios
├─ Shows different capabilities
└─ Useful for validation

rag_test.py                - RAG-only test
├─ Tests vector store
├─ Checks retrieval quality
└─ Useful for debugging

src/agents.py              - Agent definitions
├─ Agent prompts (4 system prompts)
├─ LLM initialization
└─ Logging setup

src/orchestrator.py        - Workflow orchestration
├─ LangGraph state definition
├─ Node implementations (4 agents)
├─ Graph compilation
└─ Error handling

src/rag_pipeline.py        - RAG implementation
├─ ChromaDB initialization
├─ Document loading
├─ Index creation
├─ Query engine
└─ Tool wrapping for LangChain

data/                      - Private knowledge base
├─ fleet_rules.txt         - Truck specs, costs, rules
├─ city_regulations.txt    - City restrictions, tolls, regulations
└─ maintenance_logs.txt    - Truck maintenance status

chroma_db/                 - Vector store (created at runtime)
├─ chroma.sqlite3          - Persistent embeddings
└─ collections/            - Indexed documents

requirements.txt           - Python dependencies
.env.example              - Configuration template
.env                      - Your configuration (not versioned)
README.md                 - Full documentation
"""

# ============================================================================
# KEY CONCEPTS
# ============================================================================

KEY_CONCEPTS = """
🔑 KEY CONCEPTS

1. RAG (Retrieval-Augmented Generation)
   - LLMs have no knowledge of private company data
   - RAG embeds company documents into a vector store
   - When user asks a question, we:
     a) Convert query to embedding vector
     b) Find similar documents in vector store (retrieval)
     c) Inject retrieved context into LLM prompt (augmentation)
     d) LLM generates response based on company-specific context
   
   Benefits:
   ✓ LLM can answer questions about internal procedures
   ✓ Answers are grounded in company data
   ✓ No need for fine-tuning
   ✓ Easy to update (just change data files)

2. Multi-Agent System
   - Single LLM can do multiple tasks but may lack specialized reasoning
   - Multiple agents with different prompts = better results
   - Agents can collaborate by passing state between them
   - Each agent focuses on their specialty:
     * Search Agent: Information retrieval
     * Analysis Agent: Problem solving
     * Validation Agent: Compliance checking
     * Writing Agent: Communication
   
   Benefits:
   ✓ Clear separation of concerns
   ✓ Easy to debug individual agents
   ✓ Can route to specific agents based on need
   ✓ Better reasoning through specialization

3. LangGraph Orchestration
   - Graph-based workflow engine
   - Nodes = agents/functions
   - Edges = data flow between nodes
   - State = shared data passed between nodes
   
   In this project:
   ✓ Sequential flow (one agent → next)
   ✓ Shared state object contains all intermediate results
   ✓ Each agent reads from state, adds their output to state
   ✓ Final state contains complete execution trace

4. Prompting Strategy
   - System Prompt = agent's role and instructions
   - User Prompt = specific task/question
   - Groq model = fast inference (use cases need quick responses)
   - Temperature 0.1 = deterministic (logistics needs reliability)
"""

# ============================================================================
# COMMON WORKFLOWS
# ============================================================================

WORKFLOWS = """
⚙️ COMMON WORKFLOWS

WORKFLOW 1: User Makes a Request
┌─────────────────────────────────┐
│ 1. User enters request in CLI    │
│ 2. Main creates initial state    │
│ 3. State passed to orchestrator  │
│ 4. Orchestrator runs agents      │
│ 5. Final state returned to main  │
│ 6. Main displays response        │
└─────────────────────────────────┘

WORKFLOW 2: Agent Recherche Executes
┌────────────────────────────────────────┐
│ 1. Receives: user_request from state   │
│ 2. Gets LLM with RAG tool bound        │
│ 3. LLM decides what to query via RAG   │
│ 4. RAG tool converts query to embedding│
│ 5. ChromaDB finds similar chunks       │
│ 6. Chunks returned as text context     │
│ 7. Summarized and stored in state      │
│ 8. Returns: updated state with context │
└────────────────────────────────────────┘

WORKFLOW 3: Adding a New Agent
┌──────────────────────────────────────┐
│ 1. Define prompt: X_SYSTEM_PROMPT    │
│ 2. Create function: x_node()         │
│ 3. Add to orchestrator:              │
│    workflow.add_node("Agent_X", ...) │
│ 4. Connect edges: workflow.add_edge()│
│ 5. Update TypedDict state if needed  │
│ 6. Test with demo.py                │
└──────────────────────────────────────┘

WORKFLOW 4: Updating Knowledge Base
┌──────────────────────────────────┐
│ 1. Edit data/*.txt files          │
│ 2. Delete chroma_db/ (optional)   │
│ 3. Next run auto-re-indexes       │
│ 4. New data immediately available │
└──────────────────────────────────┘
"""

# ============================================================================
# DEBUGGING TIPS
# ============================================================================

DEBUGGING_TIPS = """
🐛 DEBUGGING TIPS

1. Check environment setup:
   python test_connection.py

2. Test RAG in isolation:
   python rag_test.py

3. Run demo scenarios:
   python demo.py

4. Add print statements in agents.py (logging already added)

5. Check ChromaDB:
   - Look in chroma_db/ directory
   - Verify files exist and have size
   - If issues, delete chroma_db/ to rebuild

6. Check RAG retrieval quality:
   - Modify rag_test.py to try different queries
   - Look at what chunks are retrieved
   - Add more specific data if queries don't match

7. Check agent reasoning:
   - Each agent prints progress
   - Review their outputs in the state
   - Adjust prompts if behavior is wrong

8. Common issues:
   
   ❌ "GROQ_API_KEY not found"
   → Create .env file with your key
   
   ❌ "Connection timeout"
   → Check internet connection, Groq service status
   
   ❌ "No relevant documents found"
   → Check data files, add more content, adjust query
   
   ❌ "Agent gives nonsensical answer"
   → Improve system prompt, add more context to RAG data
"""

# ============================================================================
# EXTENSION IDEAS
# ============================================================================

EXTENSIONS = """
💡 WAYS TO EXTEND THE SYSTEM

1. Additional Agents
   - Cost Optimization Agent (finds cheapest routes)
   - Environmental Impact Agent (minimizes emissions)
   - Real-time Traffic Agent (integrates traffic data)
   - Customer Service Agent (handles customer interactions)

2. Parallel Execution
   - Instead of sequential flow
   - Run agents in parallel where possible
   - Merge results intelligently
   - Faster response times

3. External Integrations
   - Real-time traffic API
   - Weather service API
   - GPS tracking
   - Payment processing
   - Customer database

4. User Interface
   - Streamlit web interface
   - REST API with FastAPI
   - Mobile app integration
   - Chat interface (Discord/Slack bot)

5. Feedback Loop
   - User rates responses
   - Feedback used to improve prompts
   - Historical data for learning

6. Additional Data Sources
   - PDF documents
   - CSV files
   - Database queries
   - Web scraping
   - Real-time sensors

7. Advanced Features
   - Multi-turn conversations
   - Conversation history
   - User preferences
   - Custom constraints per user
   - Scenario planning ("what if" analysis)
"""

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  🚚 INTELLIGENT LOGISTICS & ROUTING ASSISTANT                 ║
║     Multi-Agent System with RAG & LLM Orchestration          ║
╚════════════════════════════════════════════════════════════════╝

📖 DOCUMENTATION SECTIONS:

1. QUICK START              - Get running in 30 seconds
2. ARCHITECTURE OVERVIEW    - System design and flow
3. FILE STRUCTURE          - Project organization
4. KEY CONCEPTS            - Understand the technology
5. COMMON WORKFLOWS        - How things work
6. DEBUGGING TIPS          - Troubleshooting guide
7. EXTENSION IDEAS         - Future enhancements

COMMAND:
  python QUICKSTART.md [section_number]

Example:
  python QUICKSTART.md 1     → Shows quick start
  python QUICKSTART.md 4     → Shows key concepts
    """)
    
    print("\n" + "="*70)
    print("QUICK START (30 SECONDS)")
    print("="*70)
    print(__doc__)
    
    print("\n" + "="*70)
    print("ARCHITECTURE OVERVIEW")
    print("="*70)
    print(ARCHITECTURE_DOCS)
    
    print("\n" + "="*70)
    print("FILE STRUCTURE")
    print("="*70)
    print(FILE_STRUCTURE)
    
    print("\n" + "="*70)
    print("KEY CONCEPTS")
    print("="*70)
    print(KEY_CONCEPTS)
    
    print("\n" + "="*70)
    print("COMMON WORKFLOWS")
    print("="*70)
    print(WORKFLOWS)
    
    print("\n" + "="*70)
    print("DEBUGGING TIPS")
    print("="*70)
    print(DEBUGGING_TIPS)
    
    print("\n" + "="*70)
    print("EXTENSION IDEAS")
    print("="*70)
    print(EXTENSIONS)
    
    print("\n" + "="*70)
    print("Ready to start? Run:  python main.py")
    print("="*70)
