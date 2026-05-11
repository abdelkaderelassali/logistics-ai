"""Vector database setup for private logistics documents.

This file only handles ChromaDB storage so retrieval stays modular.
"""

from functools import lru_cache

import chromadb
from llama_index.core import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

PERSIST_DIR = "./chroma_db"
COLLECTION_NAME = "logistics_data"


@lru_cache(maxsize=1)
def get_vector_store() -> ChromaVectorStore:
    """Return the cached Chroma vector store."""
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    return ChromaVectorStore(chroma_collection=collection)


def get_storage_context() -> StorageContext:
    """Create the storage context used by the retriever."""
    return StorageContext.from_defaults(vector_store=get_vector_store())
