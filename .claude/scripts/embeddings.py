#!/usr/bin/env python3
"""
Embeddings module — FastEmbed ONNX batch embedding.
Uses all-MiniLM-L6-v2 (384-dim, ~80MB cache).
"""

import hashlib
import json
from pathlib import Path
from typing import Optional

try:
    from fastembed import TextEmbedding
except ImportError:
    print("Error: fastembed not installed. Run: pip install fastembed")
    exit(1)

# Model configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384

# Cache directory
CACHE_DIR = Path(__file__).parent.parent.parent / ".claude" / "data" / "model_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class Embedder:
    def __init__(self, model_name: str = MODEL_NAME, cache_dir: Path = CACHE_DIR):
        self.model = TextEmbedding(
            model_name=model_name,
            cache_dir=str(cache_dir),
            import_as_tensor=False
        )
        self.embedding_dim = EMBED_DIM

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a batch of texts.
        Returns list of embedding vectors (each 384-dim).
        """
        embeddings = list(self.model.embed(texts))
        return [emb.tolist() for emb in embeddings]

    def embed_single(self, text: str) -> list[float]:
        """Embed a single text."""
        return self.embed([text])[0]


def estimate_tokens(text: str) -> int:
    """Rough token estimation (~4 chars per token for English)."""
    return len(text) // 4


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[dict]:
    """
    Split text into overlapping chunks.
    Returns list of {chunk_id, content, start, end}.
    """
    tokens = text.split()
    chunks = []

    # Simple fixed-token windowing with overlap
    window_tokens = chunk_size
    step_tokens = window_tokens - overlap

    start = 0
    chunk_index = 0

    while start < len(tokens):
        end = min(start + window_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = " ".join(chunk_tokens)

        chunk_id = hashlib.sha256(f"{text[:50]}-{chunk_index}".encode()).hexdigest()[:16]

        chunks.append({
            "chunk_id": chunk_id,
            "content": chunk_text,
            "start_token": start,
            "end_token": end,
            "chunk_index": chunk_index
        })

        start += step_tokens
        chunk_index += 1

    return chunks


if __name__ == "__main__":
    # Test embedding
    embedder = Embedder()
    result = embedder.embed(["Hello, world!", "This is a test."])
    print(f"Embedding dim: {len(result[0])}")
    print(f"Test passed: {len(result) == 2}")