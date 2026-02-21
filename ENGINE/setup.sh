#!/bin/bash
# ONE Astrology Content Engine Setup

echo "🔮 Setting up ONE Astrology Content Engine..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install playwright browsers
playwright install chromium

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Get your Gemini API key:"
echo "   → Go to: https://aistudio.google.com/apikey"
echo "   → Sign in with your Google account (the one with AI Pro)"
echo "   → Click 'Create API Key'"
echo "   → Copy the key"
echo ""
echo "2. Set the API key:"
echo "   export GEMINI_API_KEY='your-key-here'"
echo ""
echo "3. Test it:"
echo "   python core/gemini_client.py 'why your natal chart is a plasma reactor' twitter"
echo ""
echo "🌟 The Oracle awaits."
