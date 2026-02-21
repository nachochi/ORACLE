#!/usr/bin/env python3
"""Index local documents into Qdrant for MCP semantic search.

This script creates Qdrant points compatible with mcp-ragdocs by using
OpenAI's text-embedding-ada-002 (1536 dims) and the same collection name.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest
except ImportError:  # pragma: no cover
    QdrantClient = None
    rest = None

COLLECTION_NAME = "documentation"
EMBED_MODEL = "text-embedding-ada-002"  # 1536 dims (mcp-ragdocs compatible)

ALLOWED_EXTS = {
    ".md",
    ".txt",
    ".vtt",
    ".py",
    ".rs",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".sh",
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
}


@dataclass
class Chunk:
    text: str
    file_path: str
    chunk_index: int
    byte_start: int
    byte_end: int


def iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix.lower() not in ALLOWED_EXTS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(errors="ignore")


def chunk_text(text: str, max_chars: int, overlap: int) -> List[tuple[str, int, int]]:
    if max_chars <= 0:
        return [(text, 0, len(text))]

    chunks: List[tuple[str, int, int]] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + max_chars, text_len)
        chunk = text[start:end]
        chunks.append((chunk, start, end))

        if end == text_len:
            break
        start = max(0, end - overlap)

    return chunks


def deterministic_id(file_path: str, chunk_index: int, text: str) -> str:
    h = hashlib.sha1()
    h.update(file_path.encode("utf-8", errors="ignore"))
    h.update(b"::")
    h.update(str(chunk_index).encode("utf-8"))
    h.update(b"::")
    h.update(text.encode("utf-8", errors="ignore"))
    return h.hexdigest()


def ensure_qdrant_collection(client: QdrantClient) -> None:
    collections = client.get_collections().collections
    if any(c.name == COLLECTION_NAME for c in collections):
        return
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=rest.VectorParams(size=1536, distance=rest.Distance.COSINE),
    )


def embed_text(client: OpenAI, text: str) -> List[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def load_file_list(list_path: Optional[Path], root: Path, max_files: Optional[int]) -> List[Path]:
    if list_path:
        files = [Path(line.strip()) for line in list_path.read_text().splitlines() if line.strip()]
    else:
        files = list(iter_files(root))

    if max_files is not None:
        return files[:max_files]
    return files


def write_manifest_line(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index local docs into Qdrant.")
    parser.add_argument("--root", required=True, help="Root directory to index")
    parser.add_argument("--file-list", help="Optional file list (one path per line)")
    parser.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL", "http://localhost:6333"))
    parser.add_argument("--qdrant-api-key", default=os.getenv("QDRANT_API_KEY", "local-dev-key"))
    parser.add_argument("--openai-api-key", default=os.getenv("OPENAI_API_KEY"))
    parser.add_argument("--chunk-size", type=int, default=1200)
    parser.add_argument("--chunk-overlap", type=int, default=150)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-files", type=int, default=None)
    parser.add_argument("--manifest", default="/home/nachochi/ORACLE/BOOKSHELF_VECTOR_INDEX/manifest.jsonl")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if OpenAI is None or QdrantClient is None:
        print("Missing dependencies. Install with: pip install openai qdrant-client", file=sys.stderr)
        return 1

    if not args.openai_api_key and not args.dry_run:
        print("OPENAI_API_KEY is required for embeddings.", file=sys.stderr)
        return 1

    root = Path(args.root)
    if not root.exists():
        print(f"Root not found: {root}", file=sys.stderr)
        return 1

    file_list = Path(args.file_list) if args.file_list else None
    files = load_file_list(file_list, root, args.max_files)

    openai_client = OpenAI(api_key=args.openai_api_key) if not args.dry_run else None
    qdrant_client = None if args.dry_run else QdrantClient(url=args.qdrant_url, api_key=args.qdrant_api_key)

    if qdrant_client:
        ensure_qdrant_collection(qdrant_client)

    manifest_path = Path(args.manifest)

    batch_points = []
    for file_path in files:
        text = read_text(file_path)
        for chunk_index, (chunk, byte_start, byte_end) in enumerate(
            chunk_text(text, args.chunk_size, args.chunk_overlap)
        ):
            if not chunk.strip():
                continue

            point_id = deterministic_id(str(file_path), chunk_index, chunk)
            payload = {
                "text": chunk,
                "url": f"file://{file_path}",
                "title": file_path.name,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "local-file",
                "file_path": str(file_path),
                "chunk_index": chunk_index,
                "byte_start": byte_start,
                "byte_end": byte_end,
            }

            write_manifest_line(manifest_path, payload)

            if args.dry_run:
                continue

            embedding = embed_text(openai_client, chunk)
            batch_points.append(
                rest.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

            if len(batch_points) >= args.batch_size:
                qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch_points)
                batch_points = []

        # gentle pacing to avoid rate limits when indexing large files
        if not args.dry_run:
            time.sleep(0.1)

    if batch_points and not args.dry_run:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch_points)

    print(f"Indexed {len(files)} files. Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
