# Bookshelf Vector Indexing (Qdrant + MCP)

This creates a local vector index for all BOOKSHELF files and makes it searchable
through the existing `mcp-ragdocs` server (collection name: `documentation`).

## Why this works
- `mcp-ragdocs` searches the Qdrant `documentation` collection.
- This indexer writes local file chunks into the same collection.
- Result: MCP semantic search over your full local filebase.

## Requirements
- Qdrant running (local or cloud)
- OpenAI API key for embeddings (1536 dims, `text-embedding-ada-002`)

## Install deps
```bash
pip install openai qdrant-client
```

## Run indexing
```bash
python /home/nachochi/ORACLE/ENGINE/core/indexing/bookshelf_vector_indexer.py \
  --root /home/nachochi/LUMINISCRIPT_V2/BOOKSHELF \
  --file-list /home/nachochi/ORACLE/BOOKSHELF_TEXT_FILES.txt
```

### Optional flags
- `--chunk-size 1200` (default)
- `--chunk-overlap 150`
- `--batch-size 64`
- `--max-files 500` (for quick smoke tests)
- `--dry-run` (writes manifest only)

## MCP config
Use your existing `mcp-ragdocs` MCP server. Ensure these env vars are set:
- `QDRANT_URL` (e.g. `http://localhost:6333`)
- `QDRANT_API_KEY` (set to `local-dev-key` for local Qdrant)
- `OPENAI_API_KEY`

## Output
- Manifest: `/home/nachochi/ORACLE/BOOKSHELF_VECTOR_INDEX/manifest.jsonl`
- Qdrant collection: `documentation`
