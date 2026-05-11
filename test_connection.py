#!/usr/bin/env python3
"""
Test connection and initialization of the Logistics Multi-Agent System.
This script verifies that all components (Groq API, LlamaIndex, LangChain) are working correctly.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if .env file exists and GROQ_API_KEY is set."""
    print("[1/5] Testing environment configuration...")
    load_dotenv()
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables.")
        print("   Please create a .env file with your Groq API key.")
        print("   Reference: .env.example")
        return False
    
    if api_key == "your_groq_api_key_here":
        print("❌ GROQ_API_KEY is still set to the placeholder value.")
        print("   Please update your .env file with a real Groq API key from https://console.groq.com")
        return False
    
    print("✅ Environment variables loaded successfully.")
    return True

def test_groq_connection():
    """Test connection to Groq API."""
    print("\n[2/5] Testing Groq API connection...")
    try:
        from langchain_groq import ChatGroq
        
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.environ.get("GROQ_API_KEY"),
            temperature=0.1
        )
        
        # Try a simple query
        response = llm.invoke("Say 'System ready' in one sentence.")
        print(f"✅ Groq API connection successful. Response: {response.content[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

def test_embeddings():
    """Test HuggingFace embeddings."""
    print("\n[3/5] Testing HuggingFace embeddings...")
    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        test_embedding = embed_model.get_text_embedding("Test query")
        print(f"✅ HuggingFace embeddings loaded successfully. Embedding dimension: {len(test_embedding)}")
        return True
    except Exception as e:
        print(f"❌ HuggingFace embeddings failed: {e}")
        return False

def test_rag_pipeline():
    """Test RAG pipeline with sample data."""
    print("\n[4/5] Testing RAG pipeline...")
    try:
        from src.rag_pipeline import setup_rag_pipeline
        
        tool = setup_rag_pipeline()
        print(f"✅ RAG pipeline initialized successfully.")
        print(f"   Tool name: {tool.name}")
        print(f"   Tool description: {tool.description}")
        return True
    except Exception as e:
        print(f"❌ RAG pipeline initialization failed: {e}")
        return False

def test_orchestrator():
    """Test the main orchestrator."""
    print("\n[5/5] Testing orchestrator...")
    try:
        from src.orchestrator import build_orchestrator
        
        app = build_orchestrator()
        print(f"✅ Orchestrator built successfully.")
        return True
    except Exception as e:
        print(f"❌ Orchestrator building failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🚚 Logistics Multi-Agent System - Connection Test")
    print("=" * 60)
    
    tests = [
        test_environment,
        test_groq_connection,
        test_embeddings,
        test_rag_pipeline,
        test_orchestrator,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! You're ready to use the system.")
        print("   Run: python main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())