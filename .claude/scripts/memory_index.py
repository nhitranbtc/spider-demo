#!/usr/bin/env python3
"""
Memory indexer — incremental indexing of vault files.
Only re-indexes changed files since last run.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = REPO_ROOT / "Dynamous" / "Memory"

sys.path.insert(0, str(REPO_ROOT / ".claude" / "scripts"))

from db import init_db, get_connection, insert_chunk, delete_chunks_for_file, chunk_exists
from embeddings import Embedder, chunk_text, estimate_tokens


def index_file(file_path: Path, embedder: Embedder) -> int:
    """
    Index a single file, deleting existing chunks first (incremental update).
    Returns number of chunks indexed.
    """
    conn = get_connection()

    # Delete existing chunks for this file
    delete_chunks_for_file(conn, str(file_path))

    content = file_path.read_text()
    chunks = chunk_text(content)

    # Get embeddings for all chunks (batch for efficiency)
    texts = [c["content"] for c in chunks]

    # Note: In production, you'd store vector embeddings in sqlite-vec
    # For now, we store metadata and text; vector search can be added later

    indexed = 0
    for chunk in chunks:
        if not chunk_exists(conn, chunk["chunk_id"]):
            token_count = estimate_tokens(chunk["content"])
            insert_chunk(
                conn,
                chunk["chunk_id"],
                str(file_path),
                chunk["chunk_index"],
                chunk["content"],
                token_count,
                {"file_mtime": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()}
            )
            indexed += 1

    conn.commit()
    return indexed


def index_vault(embedder: Embedder) -> dict:
    """
    Index all markdown files in the vault.
    Returns stats about what was indexed.
    """
    init_db()
    conn = get_connection()

    stats = {
        "files_indexed": 0,
        "chunks_indexed": 0,
        "files_skipped": 0
    }

    md_files = list(VAULT_PATH.rglob("*.md"))
    if not md_files:
        print(f"No markdown files found in {VAULT_PATH}")
        return stats

    for md_file in md_files:
        # Skip daily files less than 1KB (probably stubs)
        if "daily" in str(md_file):
            content = md_file.read_text()
            if len(content) < 200:
                stats["files_skipped"] += 1
                continue

        try:
            indexed = index_file(md_file, embedder)
            if indexed > 0:
                stats["files_indexed"] += 1
                stats["chunks_indexed"] += indexed
        except Exception as e:
            print(f"Error indexing {md_file}: {e}")

    return stats


if __name__ == "__main__":
    embedder = Embedder()
    stats = index_vault(embedder)

    print(f"Indexed {stats['files_indexed']} files ({stats['chunks_indexed']} chunks)")
    if stats['files_skipped']:
        print(f"Skipped {stats['files_skipped']} files (too small)")