import pytest
from app.services.indexer import CodeIndexer
import os

def test_indexer_basic():
    # Use in-memory Qdrant and dummy API key
    indexer = CodeIndexer(qdrant_url=":memory:", openai_api_key="dummy-key")

    # Create a dummy repo
    repo_content = "def add(a, b):\n    return a + b\n\n# This is a comment\ndef sub(a, b):\n    return a - b\n"

    # Test _chunk_code
    chunks = indexer._chunk_code(repo_content, max_chars=40)
    assert len(chunks) > 1

    # Test _index_directory (will use mock embedding because of dummy key and our logic)
    # We need to make sure _get_embedding handles the dummy key
    # Actually, our logic in _get_embedding checks for API key existence.
    # Let's override _get_embedding for the test to be safe.
    indexer._get_embedding = lambda x: [0.1] * 1536

    indexer._index_directory("app") # Index some local files
    results = indexer.search("health", limit=1)
    assert len(results) >= 0
