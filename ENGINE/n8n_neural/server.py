"""
ORACLE n8n Neural MCP Server
=============================
Describe a workflow in plain English → AI designs it → n8n creates it.

Tools exposed to Cursor / any MCP client:
  plan_workflow(description)    → AI designs + creates workflow in n8n
  list_workflows()              → list all your n8n workflows
  activate_workflow(id)         → activate a workflow
  deactivate_workflow(id)       → deactivate a workflow
  delete_workflow(id)           → delete a workflow
  run_workflow(id)              → trigger a workflow manually

Config (env vars or .env file in this directory):
  N8N_URL        default: http://localhost:5678
  N8N_API_KEY    required — generate at n8n Settings → API Keys
  OLLAMA_URL     default: http://localhost:11435/v1
  OLLAMA_KEY     default: v5Jv8iDCBtJoFUqpTdMyOJPE2ZBVJN67Tgbj0Azp27k
  OLLAMA_MODEL   default: qwen2.5-coder:7b-instruct
"""

import json
import os
import urllib.request
import urllib.error
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# ── Config ────────────────────────────────────────────────────────────────────

def _load_env() -> None:
    p = Path(__file__).parent / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

_load_env()

N8N_URL     = os.environ.get("N8N_URL", "http://localhost:5678")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")
OLLAMA_URL  = os.environ.get("OLLAMA_URL", "http://localhost:11435/v1")
OLLAMA_KEY  = os.environ.get("OLLAMA_KEY", "v5Jv8iDCBtJoFUqpTdMyOJPE2ZBVJN67Tgbj0Azp27k")
OLLAMA_MODEL= os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b-instruct")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _n8n(method: str, path: str, body: dict | None = None) -> dict:
    if not N8N_API_KEY:
        raise RuntimeError("N8N_API_KEY not set — generate one at http://localhost:5678/settings/api")
    url = f"{N8N_URL}/api/v1{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode(), "status": e.code}


def _ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert n8n workflow designer. "
                    "When asked to design a workflow, output ONLY a valid n8n workflow JSON object. "
                    "No markdown, no explanation, no code fences — raw JSON only. "
                    "The JSON must have: name (string), nodes (array), connections (object), settings (object). "
                    "Use real n8n node types like: n8n-nodes-base.httpRequest, n8n-nodes-base.telegram, "
                    "n8n-nodes-base.webhook, n8n-nodes-base.schedule, n8n-nodes-base.set, "
                    "n8n-nodes-base.if, n8n-nodes-base.emailSend, n8n-nodes-base.slack. "
                    "Every workflow must start with a trigger node (webhook, schedule, or manual trigger)."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "temperature": 0.2,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/chat/completions", data=data, method="POST",
        headers={
            "Authorization": f"Bearer {OLLAMA_KEY}",
            "Content-Type": "application/json",
        }
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read())
    return result["choices"][0]["message"]["content"].strip()


def _extract_json(text: str) -> dict:
    """Pull JSON out of the AI response even if it wrapped it in markdown."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1:
        raise ValueError("No JSON object found in AI response")
    return json.loads(text[start:end])


# ── MCP Server ────────────────────────────────────────────────────────────────

mcp = FastMCP(
    "n8n-neural",
    instructions=(
        "Use plan_workflow to design and create n8n workflows from plain English. "
        "Use list_workflows to see existing workflows. "
        "Use activate_workflow/deactivate_workflow to control them."
    ),
)


@mcp.tool()
def plan_workflow(description: str) -> str:
    """
    Describe a workflow in plain English and the AI will design it and create it in n8n.
    Example: 'Every hour, fetch BTC price from CoinGecko and post it to Telegram'
    Example: 'When a webhook is hit, send an email to me@example.com with the payload'
    """
    prompt = (
        f"Design a complete n8n workflow that does the following:\n\n{description}\n\n"
        "Output only the raw JSON workflow object."
    )

    try:
        raw = _ollama(prompt)
    except Exception as e:
        return f"AI error: {e}"

    try:
        workflow_json = _extract_json(raw)
    except Exception:
        return f"AI returned invalid JSON. Raw output:\n{raw[:500]}"

    result = _n8n("POST", "/workflows", workflow_json)

    if "error" in result:
        return (
            f"AI designed the workflow but n8n rejected it.\n"
            f"Error: {result['error']}\n\n"
            f"Workflow JSON (you can paste manually into n8n):\n"
            f"{json.dumps(workflow_json, indent=2)}"
        )

    wf_id = result.get("id", "?")
    wf_name = result.get("name", workflow_json.get("name", "Untitled"))
    return (
        f"Workflow created!\n"
        f"  Name : {wf_name}\n"
        f"  ID   : {wf_id}\n"
        f"  URL  : {N8N_URL}/workflow/{wf_id}\n\n"
        f"Run activate_workflow('{wf_id}') to enable it."
    )


@mcp.tool()
def list_workflows() -> str:
    """List all workflows in n8n with their IDs and active status."""
    result = _n8n("GET", "/workflows")
    if "error" in result:
        return f"Error: {result['error']}"
    workflows = result.get("data", [])
    if not workflows:
        return "No workflows found."
    lines = [f"{'ID':<10} {'ACTIVE':<8} NAME"]
    lines.append("-" * 50)
    for w in workflows:
        active = "✓" if w.get("active") else "○"
        lines.append(f"{w['id']:<10} {active:<8} {w['name']}")
    return "\n".join(lines)


@mcp.tool()
def activate_workflow(workflow_id: str) -> str:
    """Activate a workflow by ID so it runs automatically."""
    result = _n8n("PATCH", f"/workflows/{workflow_id}", {"active": True})
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Workflow {workflow_id} is now ACTIVE."


@mcp.tool()
def deactivate_workflow(workflow_id: str) -> str:
    """Deactivate a workflow by ID."""
    result = _n8n("PATCH", f"/workflows/{workflow_id}", {"active": False})
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Workflow {workflow_id} is now INACTIVE."


@mcp.tool()
def delete_workflow(workflow_id: str) -> str:
    """Delete a workflow by ID. This cannot be undone."""
    result = _n8n("DELETE", f"/workflows/{workflow_id}")
    if "error" in result:
        return f"Error: {result['error']}"
    return f"Workflow {workflow_id} deleted."


@mcp.tool()
def get_workflow(workflow_id: str) -> str:
    """Get full details of a workflow by ID."""
    result = _n8n("GET", f"/workflows/{workflow_id}")
    if "error" in result:
        return f"Error: {result['error']}"
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
