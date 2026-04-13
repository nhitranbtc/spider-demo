#!/usr/bin/env python3
"""
Memory search — hybrid search combining vector + keyword (FTS5).
Merge formula: 0.7 * vector_score + 0.3 * keyword_score
"""

import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent.parent

sys.path.insert(0, str(REPO_ROOT / ".claude" / "scripts"))

from db import search_fts, get_connection, get_chunks_by_ids
from embeddings import Embedder


def hybrid_search(query: str, limit: int = 10, vector_weight: float = 0.7,
                 fts_weight: float = 0.3) -> list[dict]:
    """
    Perform hybrid search combining vector and keyword search.

    For now, since we're storing text + metadata in sqlite-vec schema,
    we implement keyword-first approach with vector scoring added.

    In production with actual vector storage (sqlite-vec):
    - Vector search would return similarity scores
    - FTS would return BM25 scores
    - Merge with weighted combination
    """
    # Get keyword matches
    fts_results = search_fts(query, limit=limit * 2)  # Get more for merging

    if not fts_results:
        return []

    # Get full chunk details
    conn = get_connection()
    chunk_ids = [r["chunk_id"] for r in fts_results]
    chunks = get_chunks_by_ids(conn, chunk_ids)

    # Create lookup
    chunk_map = {c["chunk_id"]: c for c in chunks}

    # Score and rank (simplified: use FTS BM25 as combined score)
    # In production with real vectors: embed query, compare to stored vectors
    scored = []
    for result in fts_results:
        chunk = chunk_map.get(result["chunk_id"])
        if chunk:
            # Normalize BM25 score (lower BM25 = better, invert for ranking)
            bm25 = result.get("score", 0)
            # Convert BM25 to similarity-like score (higher = better)
            similarity = 1 / (1 + abs(bm25))

            scored.append({
                "chunk_id": result["chunk_id"],
                "source_file": result["source_file"],
                "content": result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"],
                "score": similarity,
                "rank": 0
            })

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Assign ranks
    for i, item in enumerate(scored[:limit]):
        item["rank"] = i + 1

    return scored[:limit]


def search_memory(query: str, path_prefix: Optional[str] = None, limit: int = 10) -> list[dict]:
    """
    Search memory with optional path filtering.

    Args:
        query: Search query
        path_prefix: Filter to files starting with this path (e.g., "drafts/sent")
        limit: Max results
    """
    results = hybrid_search(query, limit=limit)

    if path_prefix:
        results = [r for r in results if path_prefix in r.get("source_file", "")]

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: memory_search.py <query> [--path-prefix <prefix>] [--limit <n>]")
        sys.exit(1)

    query = sys.argv[1]
    path_prefix = None
    limit = 10

    if "--path-prefix" in sys.argv:
        idx = sys.argv.index("--path-prefix")
        path_prefix = sys.argv[idx + 1]
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit = int(sys.argv[idx + 1])

    results = search_memory(query, path_prefix=path_prefix, limit=limit)

    if results:
        print(f"Found {len(results)} results:\n")
        for r in results:
            print(f"[Rank {r['rank']}] {r['source_file']}")
            print(f"  Score: {r['score']:.3f}")
            print(f"  Content: {r['content'][:200]}...")
            print()
    else:
        print("No results found.")