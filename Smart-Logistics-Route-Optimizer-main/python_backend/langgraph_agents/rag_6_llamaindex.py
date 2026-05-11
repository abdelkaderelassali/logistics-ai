import os
import chromadb
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from langchain_core.tools import Tool

# Global cache for RAG pipeline
_rag_pipeline_cache = None

def setup_rag_pipeline(data_dir="./data", persist_dir="./chroma_db"):
    """Set up and cache the RAG pipeline (only initializes once)."""
    global _rag_pipeline_cache
    
    # Return cached pipeline if available
    if _rag_pipeline_cache is not None:
        return _rag_pipeline_cache
    
    # Configure Groq LLM and HuggingFace Embeddings
    print("System: Initializing RAG Pipeline (LlamaIndex)...")
    llm = Groq(model="llama-3.1-8b-instant", api_key=os.environ.get("GROQ_API_KEY"))
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    
    # Initialize ChromaDB
    db = chromadb.PersistentClient(path=persist_dir)
    chroma_collection = db.get_or_create_collection("logistics_data")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Check if we already have indexed data to avoid redundant processing
    if chroma_collection.count() > 0:
        print("System: Loading existing knowledge base from ChromaDB...")
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    else:
        print(f"System: Indexing new documents from {data_dir}...")
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    
    # Use a retriever instead of a query engine to save an LLM call
    # This speeds up the process significantly and avoids intermediate synthesis
    retriever = index.as_retriever(similarity_top_k=5)
    
    # Wrap Retriever as a LangChain Tool
    def rag_retrieval(query: str) -> str:
        """Use this tool to search the private logistics knowledge base for rules, truck locations, restrictions, and maintenance logs."""
        nodes = retriever.retrieve(query)
        # Combine retrieved text chunks into a single context string
        context = "\n\n".join([n.get_content() for n in nodes])
        return context

    rag_tool = Tool(
        name="logistics_knowledge_base",
        description="Useful for finding information about truck locations, capacities, tolls, city restrictions, and maintenance logs.",
        func=rag_retrieval
    )
    
    # Cache the tool
    _rag_pipeline_cache = rag_tool
    return rag_tool
