#!/usr/bin/env python3
"""
DB abstraction layer — SQLite with sqlite-vec (vector search) and FTS5 (full-text search).
Local deployment: no external database needed.
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / ".claude" / "data" / "memory.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Enable FTS5
    cursor.execute("PRAGMA journal_mode=WAL")

    # Create FTS5 virtual table for keyword search
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            chunk_id,
            source_file,
            content,
            tokenize='porter'
        )
    """)

    # Create table for vector embeddings (sqlite-vec)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_vectors (
            chunk_id TEXT PRIMARY KEY,
            source_file TEXT NOT NULL,
            chunk_text TEXT NOT NULL,
            metadata TEXT,
            vec BLOB
        )
    """)

    # Create chunks table for metadata
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            source_file TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            token_count INTEGER,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    return conn


def chunk_exists(conn: sqlite3.Connection, chunk_id: str) -> bool:
    """Check if a chunk already exists."""
    cursor = conn.execute(
        "SELECT 1 FROM chunks WHERE chunk_id = ?",
        (chunk_id,)
    )
    return cursor.fetchone() is not None


def insert_chunk(conn: sqlite3.Connection, chunk_id: str, source_file: str,
                 chunk_index: int, content: str, token_count: int, metadata: dict = None):
    """Insert a chunk into the database."""
    metadata_json = json.dumps(metadata) if metadata else None

    conn.execute("""
        INSERT OR REPLACE INTO chunks (chunk_id, source_file, chunk_index, content, token_count, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (chunk_id, source_file, chunk_index, content, token_count, metadata_json))

    # Also insert into FTS
    conn.execute("""
        INSERT OR REPLACE INTO memory_fts (chunk_id, source_file, content)
        VALUES (?, ?, ?)
    """, (chunk_id, source_file, content))


def delete_chunks_for_file(conn: sqlite3.Connection, source_file: str):
    """Delete all chunks for a given source file (for incremental re-indexing)."""
    # Get chunk IDs for this file
    cursor = conn.execute(
        "SELECT chunk_id FROM chunks WHERE source_file = ?",
        (source_file,)
    )
    chunk_ids = [row[0] for row in cursor.fetchall()]

    if chunk_ids:
        placeholders = ",".join("?" * len(chunk_ids))
        conn.execute(f"DELETE FROM chunks WHERE chunk_id IN ({placeholders})", chunk_ids)
        conn.execute(f"DELETE FROM memory_fts WHERE chunk_id IN ({placeholders})", chunk_ids)
        conn.execute(f"DELETE FROM memory_vectors WHERE chunk_id IN ({placeholders})", chunk_ids)


def search_fts(query: str, limit: int = 10) -> list[dict]:
    """Search using FTS5 keyword matching."""
    conn = get_connection()
    cursor = conn.execute("""
        SELECT chunk_id, source_file, content,
               bm25(memory_fts) as score
        FROM memory_fts
        WHERE memory_fts MATCH ?
        ORDER BY score
        LIMIT ?
    """, (query, limit))

    return [
        {"chunk_id": row[0], "source_file": row[1], "content": row[2], "score": row[3]}
        for row in cursor.fetchall()
    ]


def get_chunks_by_ids(conn: sqlite3.Connection, chunk_ids: list[str]) -> list[dict]:
    """Get chunks by their IDs."""
    if not chunk_ids:
        return []

    placeholders = ",".join("?" * len(chunk_ids))
    cursor = conn.execute(f"""
        SELECT chunk_id, source_file, chunk_index, content, token_count, metadata
        FROM chunks
        WHERE chunk_id IN ({placeholders})
    """, chunk_ids)

    return [
        {
            "chunk_id": row[0],
            "source_file": row[1],
            "chunk_index": row[2],
            "content": row[3],
            "token_count": row[4],
            "metadata": json.loads(row[5]) if row[5] else {}
        }
        for row in cursor.fetchall()
    ]


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")