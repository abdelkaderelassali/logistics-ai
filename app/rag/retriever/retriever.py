"""Retriever for the logistics knowledge base.

This file connects the private data files, embeddings, and vector DB.
"""

from functools import lru_cache

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex

from app.rag.embeddings.model import get_embedding_model
from app.rag.vector_db.store import get_storage_context
from app.services.llm_service import get_llm

DATA_DIR = "./data"


@lru_cache(maxsize=1)
def get_query_engine():
    """Build the query engine once and reuse it for every request."""
    Settings.llm = get_llm()
    Settings.embed_model = get_embedding_model()
    documents = SimpleDirectoryReader(DATA_DIR).load_data()
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=get_storage_context(),
    )
    return index.as_query_engine(similarity_top_k=3)


def retrieve_context(user_request: str) -> str:
    """Search the private knowledge base and return the most relevant context."""
    response = get_query_engine().query(user_request)
    return str(response)
