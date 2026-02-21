"""
ORACLE Ollama Gateway
=====================
A hardened, authenticated reverse proxy that sits in front of Ollama,
exposing it as a private OpenAI-compatible API callable from any device.

Features:
  - API key authentication (Bearer token)
  - Per-key rate limiting (requests + tokens per minute)
  - Request logging with timestamps
  - Full OpenAI-compatible pass-through
  - Zero dependencies beyond aiohttp (already in MASTER_TRADER)

Bind:    0.0.0.0:11435
Ollama:  127.0.0.1:11434
Config:  ./gateway.env  (auto-loaded)
"""

import asyncio
import json
import logging
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Optional

import aiohttp
from aiohttp import web

# ── Config ────────────────────────────────────────────────────────────────────

def _load_env(path: str = "gateway.env") -> None:
    env_path = Path(__file__).parent / path
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

_load_env()

OLLAMA_BASE        = os.environ.get("OLLAMA_BASE", "http://127.0.0.1:11434")
GATEWAY_PORT       = int(os.environ.get("GATEWAY_PORT", "11435"))
GATEWAY_HOST       = os.environ.get("GATEWAY_HOST", "0.0.0.0")
LOG_LEVEL          = os.environ.get("LOG_LEVEL", "INFO")

# Comma-separated list of valid API keys
_RAW_KEYS = os.environ.get("ORACLE_API_KEYS", "")
VALID_KEYS: set[str] = {k.strip() for k in _RAW_KEYS.split(",") if k.strip()}

# Rate limits (per key, rolling 60-second window)
MAX_REQUESTS_PER_MIN = int(os.environ.get("MAX_REQUESTS_PER_MIN", "60"))
MAX_TOKENS_PER_MIN   = int(os.environ.get("MAX_TOKENS_PER_MIN", "100000"))

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [GATEWAY] %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("oracle.gateway")

# ── Rate Limiter ──────────────────────────────────────────────────────────────

class RateLimiter:
    """Rolling 60-second window per API key."""

    def __init__(self) -> None:
        # key → list of (timestamp, tokens_used)
        self._log: dict[str, list[tuple[float, int]]] = defaultdict(list)

    def _prune(self, key: str) -> None:
        cutoff = time.monotonic() - 60.0
        self._log[key] = [(t, tok) for t, tok in self._log[key] if t > cutoff]

    def check(self, key: str, est_tokens: int = 0) -> tuple[bool, str]:
        self._prune(key)
        entries = self._log[key]
        req_count = len(entries)
        tok_count = sum(tok for _, tok in entries)

        if req_count >= MAX_REQUESTS_PER_MIN:
            return False, f"Rate limit: {req_count} req/min (max {MAX_REQUESTS_PER_MIN})"
        if tok_count + est_tokens > MAX_TOKENS_PER_MIN:
            return False, f"Rate limit: {tok_count} tokens/min (max {MAX_TOKENS_PER_MIN})"
        return True, "ok"

    def record(self, key: str, tokens_used: int = 0) -> None:
        self._log[key].append((time.monotonic(), tokens_used))


_limiter = RateLimiter()

# ── Auth ──────────────────────────────────────────────────────────────────────

def _extract_key(request: web.Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    # Also accept ?api_key= query param (for quick curl tests)
    return request.rel_url.query.get("api_key")

def _auth(request: web.Request) -> tuple[bool, str]:
    if not VALID_KEYS:
        return False, "No API keys configured — edit gateway.env"
    key = _extract_key(request)
    if not key:
        return False, "Missing Authorization header (Bearer <key>)"
    if key not in VALID_KEYS:
        return False, "Invalid API key"
    return True, key

# ── Proxy Core ────────────────────────────────────────────────────────────────

_session: Optional[aiohttp.ClientSession] = None

async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session is None or _session.closed:
        timeout = aiohttp.ClientTimeout(total=300, connect=5)
        _session = aiohttp.ClientSession(timeout=timeout)
    return _session


async def _proxy(request: web.Request) -> web.StreamResponse:
    # ── Auth check
    ok, key_or_err = _auth(request)
    if not ok:
        log.warning("AUTH FAIL  %s  %s", request.remote, key_or_err)
        return web.json_response({"error": key_or_err}, status=401)

    api_key = key_or_err

    # ── Estimate token usage from request body (rough: 1 token ≈ 4 chars)
    body_bytes = await request.read()
    est_tokens = len(body_bytes) // 4

    # ── Rate limit check
    allowed, msg = _limiter.check(api_key, est_tokens)
    if not allowed:
        log.warning("RATE LIMIT key=…%s  %s", api_key[-6:], msg)
        return web.json_response({"error": msg}, status=429)

    # ── Forward to Ollama
    target_url = OLLAMA_BASE + request.path_qs
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "authorization", "content-length")}

    log.info("%-6s %-40s  key=…%s", request.method, request.path, api_key[-6:])

    try:
        session = await _get_session()
        async with session.request(
            request.method,
            target_url,
            headers=headers,
            data=body_bytes,
            allow_redirects=False,
        ) as upstream:
            # Stream the response back
            response = web.StreamResponse(
                status=upstream.status,
                headers={k: v for k, v in upstream.headers.items()
                         if k.lower() not in ("transfer-encoding", "connection")},
            )
            await response.prepare(request)

            total_bytes = 0
            async for chunk in upstream.content.iter_chunked(4096):
                await response.write(chunk)
                total_bytes += len(chunk)

            await response.write_eof()

        # Record usage (rough token estimate from response size)
        _limiter.record(api_key, total_bytes // 4)
        return response

    except aiohttp.ClientConnectorError:
        log.error("Cannot reach Ollama at %s — is it running?", OLLAMA_BASE)
        return web.json_response(
            {"error": f"Ollama not reachable at {OLLAMA_BASE}. Run: sudo systemctl start ollama"},
            status=503,
        )
    except Exception as exc:
        log.exception("Proxy error: %s", exc)
        return web.json_response({"error": str(exc)}, status=500)


# ── Health endpoint (no auth required) ───────────────────────────────────────

async def _health(request: web.Request) -> web.Response:
    try:
        session = await _get_session()
        async with session.get(f"{OLLAMA_BASE}/api/tags", timeout=aiohttp.ClientTimeout(total=3)) as r:
            data = await r.json()
            models = [m["name"] for m in data.get("models", [])]
    except Exception:
        models = []
        status = "ollama_unreachable"
    else:
        status = "ok"

    return web.json_response({
        "status": status,
        "gateway": "ORACLE Ollama Gateway",
        "ollama_base": OLLAMA_BASE,
        "models_loaded": models,
        "rate_limits": {
            "requests_per_min": MAX_REQUESTS_PER_MIN,
            "tokens_per_min": MAX_TOKENS_PER_MIN,
        },
    })


# ── App setup ─────────────────────────────────────────────────────────────────

async def _on_startup(app: web.Application) -> None:
    log.info("=" * 60)
    log.info("  ORACLE Ollama Gateway starting")
    log.info("  Listening : %s:%d", GATEWAY_HOST, GATEWAY_PORT)
    log.info("  Ollama    : %s", OLLAMA_BASE)
    log.info("  API keys  : %d configured", len(VALID_KEYS))
    log.info("  Rate limit: %d req/min, %d tok/min", MAX_REQUESTS_PER_MIN, MAX_TOKENS_PER_MIN)
    if not VALID_KEYS:
        log.warning("  ⚠  No API keys set! Edit gateway.env before exposing to network.")
    log.info("=" * 60)


async def _on_cleanup(app: web.Application) -> None:
    if _session and not _session.closed:
        await _session.close()


def build_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_on_cleanup)

    # Health check (no auth)
    app.router.add_get("/health", _health)

    # Catch-all proxy (auth required)
    app.router.add_route("*", "/{path_info:.*}", _proxy)

    return app


if __name__ == "__main__":
    web.run_app(build_app(), host=GATEWAY_HOST, port=GATEWAY_PORT, print=None)
