"""Embedding model configuration for the RAG pipeline.

This file is separate so students can explain embeddings on their own.
"""

from functools import lru_cache

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbedding:
    """Return the shared embedding model used to vectorize private documents."""
    return HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)
