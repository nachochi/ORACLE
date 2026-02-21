# ORACLE — Master Save File
> **The canonical source of truth. Clone this repo on any machine and you are fully operational.**

```
Last Updated : 2026-02-20
GitHub       : https://github.com/nachochi/ORACLE
Owner        : nachochi
Sessions     : [Session 1](031f1a62-571d-4f05-a22b-08f2063bb01e)
```

---

## What ORACLE Is

ORACLE is not a trading bot. It is a **universal pattern recognition and self-evolving AI framework** — the same architecture of consciousness and code applied fractally across any signal domain: crypto trading, astrology computation, heartbeat analysis, market microstructure, anything.

The first deployed module is **MASTER_TRADER** — a live AI crypto trading system. Every other domain (astrology engine, general intelligence layer, etc.) plugs into the same substrate.

**Core Insight**: Shapes encode time/data. Every signal stream, regardless of domain, can be encoded as a geometric attractor shape, matched against a library of cached templates in O(1) time — like DNA sequencing or a toddler's shape sorter. This is the geometric substrate.

---

## Machine Setup

### Hardware (current dev machine)
```
CPU   : Intel i7-8850H @ 2.60GHz (6 cores)
RAM   : 15GB
GPU   : NVIDIA Quadro P1000 Mobile (4GB VRAM) — NOT YET ACTIVE on Linux
        Intel UHD 630 (integrated, active)
OS    : Arch Linux, kernel 6.14.4-zen1-1-zen
Disk  : 477GB NVMe SSD (~37GB free after models)
```

> GPU NOTE: The NVIDIA P1000 won't activate on Linux due to Optimus hybrid graphics.
> On Windows it works natively with Ollama — plan to migrate to Windows.
> With 4GB VRAM, 7B models run entirely on GPU (~10x faster than CPU).

### OS Migration Plan
- Current: Arch Linux (Zen kernel)
- Target: Windows 11 (for Optimus GPU support)
- On Windows: reinstall Ollama, reinstall oracle-gateway as Task Scheduler/NSSM service
- Everything else (code, API keys, GitHub) carries over unchanged

---

## Full Project Map

```
/home/nachochi/
├── ORACLE/                              ← This repo (GitHub: nachochi/ORACLE)
│   ├── ORACLE_MASTER.md                 ← YOU ARE HERE — master save file
│   ├── ENGINE/
│   │   └── ollama_gateway/
│   │       ├── gateway.py               ← Authenticated AI API proxy (aiohttp)
│   │       ├── gateway.env              ← API keys + config (NOT committed to git)
│   │       ├── oracle-gateway.service   ← systemd unit (auto-starts on boot)
│   │       └── SETUP.sh                 ← One-shot installer
│   ├── ANGEL/                           ← (empty, reserved)
│   ├── VAULT/                           ← (reserved)
│   ├── MEMORY_BANK/                     ← Persistent memory storage
│   └── RESEARCH_OS/                     ← Research and OS notes
│
└── 00_ACTIVE_WORKSPACE/LUMINISCRIPT/
    └── MASTER_TRADER/                   ← The trading bot (GitHub: nachochi/MASTER_TRADER)
        ├── AGENT_SAVE.md                ← Bot-specific save file
        ├── CONSECRATION.md              ← Project soul document
        ├── config.yaml                  ← Hot-reloading live config
        ├── requirements.txt
        ├── src/
        │   ├── main.py                  ← Entry point + command bus consumer
        │   └── market_analyzer.py       ← OBI, phase, sentiment, topology, geometry
        ├── agents/
        │   └── agent_spawner.py         ← Kelly-criterion position sizing
        ├── configs/
        │   ├── exchange_config.py       ← Binance credentials
        │   └── live_config.py           ← LiveConfig: hot-reload watcher
        ├── dashboard/
        │   └── server.py                ← RPG HUD (aiohttp WS + radial menus)
        ├── neural/
        │   ├── signal_fusion.py         ← Hierarchical MoE neural override
        │   ├── tcn.py                   ← Temporal Convolutional Network
        │   └── geometric_encoding.py    ← Phasor/wavelet feature extraction
        ├── memory/
        │   └── trade_memory.py          ← Shared collective agent memory
        ├── oracle_mind/                 ← Self-building AI layer
        │   ├── model_router.py          ← Routes tasks to best free LLM
        │   ├── sentiment_mind.py        ← INCOMPLETE — Grok crypto sentiment
        │   ├── geometric_substrate.py   ← COMPLETE — Universal shape encoder
        │   └── __init__.py
        ├── docs/
        │   └── PROJECT_VISION.md
        └── timing_substrate/            ← JJ (Jujutsu) repo — version control bus
            └── .git/
```

---

## Layer 1: ORACLE Ollama Gateway

**What it is**: A hardened reverse proxy that wraps your local Ollama install and exposes it as a private, authenticated OpenAI-compatible API. Call it from any program, any device.

**Files**: `/home/nachochi/ORACLE/ENGINE/ollama_gateway/`

### Endpoints
```
GET  /health   → status, loaded models, rate limits (no auth required)
*    /*         → full OpenAI-compatible pass-through (auth required)
```

### Authentication
All requests require: `Authorization: Bearer <your-key>`

### Your API Key
```
v5Jv8iDCBtJoFUqpTdMyOJPE2ZBVJN67Tgbj0Azp27k
```
> This key is stored in `gateway.env` on disk. Do not commit that file.

### Addresses
```
Local   : http://localhost:11435
LAN     : http://192.168.0.24:11435
Off-device : install Tailscale → use Tailscale IP
```

### Loaded Models (as of 2026-02-20)
| Model | Size | Best For |
|-------|------|---------|
| `qwen2.5-coder:7b-instruct` | 4.7GB | Code generation — use for self-builder |
| `llama3.2:3b` | 2.0GB | Ultra-fast utility |
| `deepseek-r1:7b` | 4.7GB | Reasoning (downloading) |
| `gemma3:4b` | 3.3GB | Fast + smart general (downloading) |

### Usage from Any Python Program
```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="v5Jv8iDCBtJoFUqpTdMyOJPE2ZBVJN67Tgbj0Azp27k"
)
response = client.chat.completions.create(
    model="qwen2.5-coder:7b-instruct",
    messages=[{"role": "user", "content": "Your prompt"}]
)
print(response.choices[0].message.content)
```

### Service Management
```bash
# Check status
systemctl status ollama oracle-gateway

# Restart
sudo systemctl restart oracle-gateway

# Logs
journalctl -u oracle-gateway -f

# Gateway runs as: nachochi (user), port 11435
# Ollama runs as:  ollama (system user), port 11434
# Raw port 11434 is firewalled — only 11435 with auth is exposed
```

### Fresh Install on Any New Machine
```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Clone this repo
git clone https://github.com/nachochi/ORACLE
cd ORACLE/ENGINE/ollama_gateway

# 3. Restore gateway.env (copy from password manager or old machine)
#    Set: ORACLE_API_KEYS=<your-key>

# 4. Run setup
sudo bash SETUP.sh

# 5. Pull models
ollama pull qwen2.5-coder:7b-instruct
ollama pull deepseek-r1:7b
ollama pull gemma3:4b
ollama pull llama3.2:3b
```

### Off-Device Access (Tailscale)
```bash
# Install
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Get your permanent IP
tailscale ip -4

# Use that IP from phone, other machine, anywhere on Earth
# Same port, same key, WireGuard encrypted, free
```

---

## Layer 2: MASTER_TRADER (AI Crypto Bot)

**Location**: `/home/nachochi/00_ACTIVE_WORKSPACE/LUMINISCRIPT/MASTER_TRADER/`
**Dashboard**: `http://localhost:8765`

### Signal Stack (10-second cycle)
```
[Binance WebSocket] → live price + order book
        ↓
[market_analyzer.py] → builds context dict:
  • OBI       — Order Book Imbalance (microstructure pressure)
  • Phase     — Takens delay embedding + Lyapunov exponent (chaos detection)
  • Sentiment — Fear & Greed Index + CryptoPanic news (cached)
  • Topology  — Persistent homology alarm (TDA — detects regime change)
  • Geometry  — Wavelet / phasor / attractor Fourier descriptors
  • Neural    — Hierarchical MoE override (online-trained from closed trades)
        ↓
[agent_spawner.py] → Kelly-criterion position sizing
  → confidence >= min_confidence → spawn trade agent
        ↓
[executor] → paper/live entry/exit, P&L tracking
        ↓
[dashboard] → WebSocket broadcast to browser HUD
        ↓
[oracle_mind/] → (planned) watches performance, generates code improvements
```

### Run the Bot
```bash
cd /home/nachochi/00_ACTIVE_WORKSPACE/LUMINISCRIPT/MASTER_TRADER

# Kill stale
fuser -k 8765/tcp 2>/dev/null; pkill -f "src/main.py" 2>/dev/null

# Start (persistent, detached)
nohup python3 -m src.main > /tmp/mt_run.log 2>&1 & disown $!

# Watch
tail -f /tmp/mt_run.log

# Dashboard
# http://localhost:8765
```

### Live Config (hot-reload while running)
Edit `config.yaml` — changes take effect within one cycle, no restart needed:
```yaml
mode:
  paper: true
  symbol: BTCUSDT
  analysis_interval_sec: 10
  initial_balance: 10000.0
risk:
  stop_loss_pct: 0.003      # 0.3% scalp stop
  take_profit_pct: 0.006    # 0.6% target (2:1 R:R)
  min_confidence: 0.55
  kelly_max_fraction: 0.25
signals:
  microstructure: true
  phase_space: true
  sentiment: true
  topology: true
  geometry: true
  neural_fusion: true
```

### Dashboard: RPG Command Deck
Inspired by Kingdom Hearts, Skyrim, FFXIV HUD design:

| Panel | Content |
|-------|---------|
| Top-left | Vitals: balance, P&L, win rate, trade count |
| Top-center | Price chart with gradient, S/R lines, phase space minimap |
| Top-right | Signal Tower (FFXIV Job Gauge style per signal layer) |
| Middle | Hexagonal radar chart (market condition fingerprint) |
| Bottom | Agent roster cards |
| Bottom bar | ▲ LONG · ▼ SHORT · ✕ ALL · ◎ MENU buttons |

**Radial Menu** (Space/Tab): 8-sector SVG wheel, Skyrim Nordic puzzle lock style
Sectors: LONG, SHORT, CLOSE, RISK, NEURAL, MARKET, PORTFOLIO, SYSTEM

**Keyboard shortcuts**:
`L` Force long · `S` Force short · `C` Close all · `R` Reset balance
`P` Toggle phase minimap · `F1` Help · `1-8` Select sector · `Esc` Close

### Command Bus
Frontend POSTs to `/cmd` → `asyncio.Queue` → `main.py` consumes each cycle:
```
spawn_long  spawn_short  close_all  paper_reset
conf_down   neural_save  neural_reset  refresh_sent
```

---

## Layer 3: Geometric Substrate (The Heart of ORACLE)

**File**: `MASTER_TRADER/oracle_mind/geometric_substrate.py`
**Status**: COMPLETE, self-tested

### The Concept
Every signal stream → geometric attractor → Fourier shape fingerprint → O(1) match against template library.

Same encoder. Same library. Different domain plugged in.

```
Signal (any domain)
    ↓ normalize to [0, 2π]
    ↓ phasor encode: e^(iθ) on unit circle
    ↓ Takens delay embedding → 2D attractor
    ↓ boundary extraction
    ↓ Fourier descriptors (shape fingerprint)
    ↓
ShapeLibrary.best_match() → O(1) analog recognition
```

### Why This Works
- Rotation / scale / translation invariant
- Domain-agnostic: price data and planetary angles produce the same types of shapes
- Sub-millisecond: 0.775ms match time
- Biologically inspired: same as DNA template fitting, shape sorter, retinal pattern recognition

### Pre-seeded Templates
```
market/  : bullish_spiral, bearish_spiral, chaotic_expansion,
           stable_oscillation, mean_reversion, breakout_impulse
astrology/: conjunction, opposition, trine, square_tension
```

### Self-Test
```bash
cd /home/nachochi/00_ACTIVE_WORKSPACE/LUMINISCRIPT/MASTER_TRADER
python3 oracle_mind/geometric_substrate.py
```
Expected output:
```
Library: astrology:4 | market:6
Encode: 0.96ms  |  Match: 0.775ms  ← O(1) analog computation
✓ FITS  market/bearish_spiral     distance=0.0002
✓ FITS  astrology/conjunction     distance=0.0000
Same encoder. Same library. Different domain plugged in.
```

---

## Layer 4: Self-Building AI (`oracle_mind/`)

### Status
| Component | Status |
|-----------|--------|
| `geometric_substrate.py` | COMPLETE |
| `model_router.py` | COMPLETE (uses OpenRouter) |
| `sentiment_mind.py` | INCOMPLETE (StrReplace aborted) |
| `self_builder.py` | NOT CREATED YET |

### model_router.py — Updated for Free APIs
The router should be updated to use free endpoints instead of paid OpenRouter:
```python
PROVIDERS = {
    "code":      {"base_url": "http://localhost:11435/v1",  "model": "qwen2.5-coder:7b-instruct"},
    "reasoning": {"base_url": "http://localhost:11435/v1",  "model": "deepseek-r1:7b"},
    "fast":      {"base_url": "http://localhost:11435/v1",  "model": "gemma3:4b"},
    # Cloud bursts (free tiers):
    "cloud_code":{"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                  "model": "gemini-2.5-pro", "api_key_env": "GEMINI_API_KEY"},
    "cloud_fast":{"base_url": "https://api.cerebras.ai/v1/",
                  "model": "llama-3.3-70b", "api_key_env": "CEREBRAS_API_KEY"},
}
```

### Planned self_builder.py Behavior
1. Runs as background asyncio task alongside main.py
2. Monitors: win rate, Sharpe ratio, drawdown, signal accuracy per layer
3. When performance drops below threshold → calls model_router("reasoning") with:
   - Current code of the underperforming module
   - Last N trade outcomes
   - "What specific change would improve this?"
4. Applies the suggested patch
5. Commits to timing_substrate (JJ) with performance metrics as commit message
6. Rolls back automatically if next N trades worsen

---

## Free AI API Stack (No Per-Token Cost)

### Local (Zero Cost Forever)
```
Ollama @ http://localhost:11435/v1
Key: v5Jv8iDCBtJoFUqpTdMyOJPE2ZBVJN67Tgbj0Azp27k
Models: qwen2.5-coder:7b, deepseek-r1:7b, gemma3:4b, llama3.2:3b
```

### Cloud Free Tiers (get API keys, all free)
| Service | URL | Free Limit | Best For |
|---------|-----|-----------|---------|
| Google AI Studio | aistudio.google.com | 1M tokens/day | Code, architecture (Gemini 2.5 Pro) |
| Cerebras | cloud.cerebras.ai | 1M tokens/day | Sentiment, fast inference (2000 t/s) |
| Groq | console.groq.com | 100K tokens/day | Fast Llama 70B |
| DeepSeek | platform.deepseek.com | 5M tokens free | Reasoning (R1) |
| Mistral | console.mistral.ai | 1B tokens/month | Code (Codestral) |

---

## Incomplete / Next Tasks

### High Priority
1. **`oracle_mind/sentiment_mind.py`** — Complete the Grok/local-LLM powered crypto sentiment analyzer. Feed output into signal stack as a live signal layer.
2. **`oracle_mind/self_builder.py`** — The self-evolving agent. See architecture above.
3. **3D/4D Phase Space Renderer** — Three.js WebGL panel in dashboard. Replace the 2D minimap with a full 3D Takens attractor rendered in real-time, colored by Lyapunov value. Geometry is already computed — just needs the renderer.

### Medium Priority
4. **Wire geometric_substrate into live signal stack** — `market_analyzer.py` computes geometry separately. Plug `ShapeLibrary.best_match()` results into the context dict as named signal layer.
5. **Update model_router.py** — Replace OpenRouter (paid) with local Ollama gateway + free cloud tiers as documented above.
6. **Astrology domain module** — Build planetary angle → phasor encoder that feeds same ShapeLibrary. Cross-domain correlation signals.

### Low Priority / Future
7. **Windows migration** — Reinstall Ollama + gateway on Windows for Optimus GPU support. P1000 = 4GB VRAM = 7B models fully on GPU.
8. **Tailscale** — Install for off-device access to the gateway.
9. **Harden the OS** — Pre-Windows migration.
10. **Live trading** — Currently paper mode. Switch `mode.paper: false` in config.yaml + add real exchange keys. Geo-blocked on VPN — needs proxy or direct IP.

---

## Session History

| Session | Link | Key Work Done |
|---------|------|--------------|
| Session 1 | [031f1a62](031f1a62-571d-4f05-a22b-08f2063bb01e) | MASTER_TRADER build: all signal layers, neural fusion, RPG dashboard, radial menus, command bus, geometric substrate, oracle_mind architecture |
| Session 2 | (this session) | Ollama gateway: auth proxy, systemd service, free AI API stack, model curation, this master save file |

---

## Philosophy

> *"This same financial system is going to fractally holographically be the same type of subsystem with the same AI framework of consciousness and code running for this and astrology computation... with minimal compute intensity via direct analogous encoding within the geometric cached objects. Like the shapes through the holes as a toddler. It doesn't get easier than that. Even DNA genomes are sequenced like this."*
> — nachochi

ORACLE is not a product. It is a way of seeing. The geometric substrate is the universal language: shapes encode time, data, domain, meaning. Build it once. Plug in any domain. The consciousness scales.

---

*"Not just a crypto bot — an AI trading ecosystem that reproduces and adapts in real-time."*
*"Same framework of consciousness and code. Different domain plugged in."*
