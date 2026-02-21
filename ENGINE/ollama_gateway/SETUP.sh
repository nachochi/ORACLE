#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════
# ORACLE Ollama Gateway — One-Shot Setup
# Run once as yourself (not root). Will ask for sudo when needed.
# ═══════════════════════════════════════════════════════════════════════
set -e
GATEWAY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ORACLE Ollama Gateway Setup${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"

# ── Step 1: Generate API key if not set ──────────────────────────────
if grep -q "REPLACE_WITH_YOUR_SECRET_KEY" "$GATEWAY_DIR/gateway.env"; then
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s|REPLACE_WITH_YOUR_SECRET_KEY_RUN_THE_GENERATE_COMMAND|$NEW_KEY|" "$GATEWAY_DIR/gateway.env"
    echo -e "${GREEN}✓ Generated API key${NC}"
    echo -e "${YELLOW}  YOUR KEY: $NEW_KEY${NC}"
    echo -e "${YELLOW}  Save this somewhere safe! It's in gateway.env too.${NC}"
else
    echo -e "${GREEN}✓ API key already set${NC}"
fi

# ── Step 2: Ensure aiohttp is installed ─────────────────────────────
python3 -c "import aiohttp" 2>/dev/null || {
    echo "Installing aiohttp..."
    pip3 install --user aiohttp
}
echo -e "${GREEN}✓ aiohttp available${NC}"

# ── Step 3: Enable Ollama systemd service ────────────────────────────
echo "Enabling ollama.service..."
sudo systemctl enable ollama
sudo systemctl start ollama
sleep 2
if systemctl is-active --quiet ollama; then
    echo -e "${GREEN}✓ Ollama service running${NC}"
else
    echo -e "${RED}✗ Ollama failed to start — check: journalctl -u ollama -n 30${NC}"
fi

# ── Step 4: Configure Ollama to bind to all interfaces ───────────────
# Add OLLAMA_HOST env to the service override so LAN/Tailscale can reach it
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/network.conf > /dev/null << 'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
sudo systemctl daemon-reload
sudo systemctl restart ollama
echo -e "${GREEN}✓ Ollama bound to 0.0.0.0:11434${NC}"

# ── Step 5: Install gateway as systemd service ───────────────────────
sudo cp "$GATEWAY_DIR/oracle-gateway.service" /etc/systemd/system/oracle-gateway.service
sudo systemctl daemon-reload
sudo systemctl enable oracle-gateway
sudo systemctl start oracle-gateway
sleep 2
if systemctl is-active --quiet oracle-gateway; then
    echo -e "${GREEN}✓ Gateway service running on port 11435${NC}"
else
    echo -e "${RED}✗ Gateway failed — check: journalctl -u oracle-gateway -n 30${NC}"
fi

# ── Step 6: Firewall (ufw if present) ───────────────────────────────
if command -v ufw &>/dev/null; then
    sudo ufw allow 11435/tcp comment "ORACLE Ollama Gateway"
    # Keep raw 11434 local-only (do NOT expose without auth)
    sudo ufw deny 11434/tcp 2>/dev/null || true
    echo -e "${GREEN}✓ Firewall: port 11435 open, 11434 blocked externally${NC}"
fi

# ── Step 7: Pull a default model if none exist ───────────────────────
MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    print(len(d.get('models',[])))
except:
    print(0)
")
if [ "$MODELS" = "0" ]; then
    echo -e "${YELLOW}No models found. Pulling deepseek-r1:8b (~5GB)...${NC}"
    ollama pull deepseek-r1:8b
    echo -e "${GREEN}✓ Model ready${NC}"
else
    echo -e "${GREEN}✓ $MODELS model(s) already loaded${NC}"
fi

# ── Done ─────────────────────────────────────────────────────────────
LOCAL_IP=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}') || LOCAL_IP=$(ip addr show | grep 'inet ' | grep -v 127 | awk '{print $2}' | cut -d/ -f1 | head -1)
API_KEY=$(grep "ORACLE_API_KEYS=" "$GATEWAY_DIR/gateway.env" | cut -d= -f2)

echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ORACLE Gateway is LIVE${NC}"
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
echo ""
echo "  Local:    http://localhost:11435"
echo "  LAN:      http://$LOCAL_IP:11435"
echo "  Health:   http://localhost:11435/health  (no auth needed)"
echo ""
echo "  Test it:"
echo "  curl http://localhost:11435/health"
echo ""
echo "  curl http://localhost:11435/v1/chat/completions \\"
echo "    -H 'Authorization: Bearer $API_KEY' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"model\":\"deepseek-r1:8b\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello ORACLE\"}]}'"
echo ""
echo -e "${YELLOW}  For OFF-DEVICE access → install Tailscale:${NC}"
echo "  curl -fsSL https://tailscale.com/install.sh | sh"
echo "  sudo tailscale up"
echo "  # Then use your Tailscale IP instead of LAN IP"
echo ""
echo -e "${GREEN}══════════════════════════════════════════════${NC}"
