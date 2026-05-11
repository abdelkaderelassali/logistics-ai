#!/usr/bin/env python3
"""
Streamlit Web Interface for Intelligent Logistics & Routing Assistant
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.orchestrator import build_orchestrator

# Page configuration
st.set_page_config(
    page_title="Logistics Assistant",
    page_icon="truck",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 1.2em;
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    .info-box {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .plan-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None
    st.session_state.history = []

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="main-header">Intelligent Logistics Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-Agent System with RAG & AI Orchestration</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("System Configuration")
    
    # Check API key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        st.error("GROQ_API_KEY not configured")
        st.info("Please create a `.env` file with your Groq API key from https://console.groq.com")
    else:
        st.success("API Key Configured")
    
    st.divider()
    
    # System info
    st.subheader("System Info")
    st.write("""
    - **Framework**: LangChain + LangGraph
    - **RAG**: LlamaIndex + ChromaDB
    - **LLM**: Groq (llama-3.1-8b-instant)
    - **Embeddings**: HuggingFace (BAAI/bge-small-en-v1.5)
    """)
    
    st.divider()
    
    # Clear history button
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()
    
    # About section
    st.subheader("About This System")
    st.write("""
    This is a Multi-Agent Logistics System that helps plan optimal 
    transport routes considering:
    - Truck availability & capacity
    - City restrictions & tolls
    - Maintenance requirements
    - Time constraints
    """)

# Main content area
st.markdown("---")

# Initialize orchestrator
if st.session_state.orchestrator is None:
    with st.spinner("Initializing system..."):
        try:
            st.session_state.orchestrator = build_orchestrator()
            st.success("System initialized successfully")
        except Exception as e:
            st.error(f"Failed to initialize system: {e}")
            st.stop()

# Request input
st.subheader("Request a Logistics Plan")

col1, col2 = st.columns([4, 1])
with col1:
    user_request = st.text_area(
        "Enter your logistics request:",
        placeholder="e.g., I need to transport 15 tons from Rabat to Casablanca at 14:00",
        height=80
    )

with col2:
    st.write("")
    st.write("")
    submit_button = st.button("Submit Request", use_container_width=True)

# Process request
if submit_button and user_request.strip():
    with st.spinner("Processing your request through the multi-agent system..."):
        try:
            # Create placeholders for progress
            progress_placeholder = st.empty()
            details_placeholder = st.empty()
            result_placeholder = st.empty()
            
            # Initial state
            state = {
                "user_request": user_request,
                "rag_context": "",
                "analysis_plan": "",
                "validation_report": "",
                "final_response": ""
            }
            
            # Run orchestrator
            final_state = st.session_state.orchestrator.invoke(state)
            
            # Add to history
            st.session_state.history.append({
                "request": user_request,
                "response": final_state.get("final_response", "No response")
            })
            
            # Display results
            st.success("Request processed successfully!")
            
            # Show the final logistics plan
            st.markdown("---")
            st.subheader("Final Logistics Plan")
            
            with st.container():
                response_text = final_state.get("final_response", "No response generated")
                st.info(response_text)
            
            # Show agent details in expanders
            with st.expander("Agent Recherche - Knowledge Base Search"):
                st.write(final_state.get("rag_context", "No context retrieved"))
            
            with st.expander("Agent Analyse - Route Analysis"):
                st.write(final_state.get("analysis_plan", "No analysis generated"))
            
            with st.expander("Agent Validation - Compliance Check"):
                st.write(final_state.get("validation_report", "No validation report"))
            
        except Exception as e:
            st.error(f"❌ Error processing request: {e}")
            st.info("Please check your API configuration and try again")

# History section
if st.session_state.history:
    st.markdown("---")
    st.subheader("Request History")
    
    for idx, item in enumerate(reversed(st.session_state.history[-5:]), 1):
        with st.expander(f"Request #{len(st.session_state.history) - idx + 1}: {item['request'][:50]}..."):
            st.write("**Request:**")
            st.write(item['request'])
            st.write("**Response:**")
            st.info(item['response'][:500] + "..." if len(item['response']) > 500 else item['response'])

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; margin-top: 30px;">
    <p>Intelligent Logistics & Routing Assistant | Powered by LangChain, LlamaIndex & Groq</p>
    <p>For issues or feedback, contact your system administrator</p>
</div>
""", unsafe_allow_html=True)
