"""
Google Gemini Client for ONE Astrology Content Engine
Uses the free Google AI Pro student subscription
"""

import google.generativeai as genai
import os
from pathlib import Path

# Load API key from environment or config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def configure_gemini(api_key: str = None):
    """Configure Gemini with API key"""
    key = api_key or GEMINI_API_KEY
    if not key:
        raise ValueError(
            "No Gemini API key found. Set GEMINI_API_KEY environment variable "
            "or get your key from https://aistudio.google.com/apikey"
        )
    genai.configure(api_key=key)
    return True

def generate_content(
    prompt: str,
    model: str = "gemini-2.5-pro",
    system_instruction: str = None,
    temperature: float = 0.7
) -> str:
    """
    Generate content using Gemini
    
    Args:
        prompt: The user prompt
        model: Model to use (gemini-2.5-pro, gemini-2.0-flash, etc.)
        system_instruction: System prompt (your voice model)
        temperature: Creativity (0.0 = deterministic, 1.0 = creative)
    
    Returns:
        Generated text
    """
    configure_gemini()
    
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    
    model_instance = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    
    response = model_instance.generate_content(prompt)
    return response.text

def generate_with_voice(
    topic: str,
    platform: str = "twitter",
    voice_file: str = None
) -> str:
    """
    Generate content in Jose's voice for a specific platform
    
    Args:
        topic: What to write about
        platform: twitter, instagram, youtube, long
        voice_file: Path to voice model file
    
    Returns:
        Platform-formatted content
    """
    # Load voice model
    voice_path = voice_file or Path(__file__).parent.parent / "voice" / "jose_voice.md"
    if voice_path.exists():
        voice_model = voice_path.read_text()
    else:
        voice_model = "Write as a direct, scientific voice. No woo-woo."
    
    # Platform-specific formatting
    platform_specs = {
        "twitter": """
Write for Twitter/X. Options:
- Single tweet (280 chars max)
- Thread (3-5 tweets, number them 1/, 2/, etc.)
Choose based on topic complexity.""",
        
        "instagram": """
Write an Instagram caption.
- Start with a hook
- Include line breaks for readability
- End with relevant hashtags (5-10)
- Include a call to action""",
        
        "youtube": """
Write a YouTube video script outline:
- Hook (first 10 seconds)
- Main content sections
- Key talking points
- Call to action
- Suggested title and description""",
        
        "tiktok": """
Write a TikTok script:
- Hook in first 2 seconds
- Keep under 60 seconds of speaking
- End with engagement prompt""",
        
        "long": """
Write a full article/essay:
- Compelling title
- Introduction with hook
- 3-5 main sections
- Conclusion with call to action"""
    }
    
    prompt = f"""
TOPIC: {topic}

PLATFORM: {platform}
{platform_specs.get(platform, platform_specs['twitter'])}

Remember: Create KNOWING, not just thinking. The truth always resonates.
Every claim should connect back to the chart as proof.
"""
    
    return generate_content(
        prompt=prompt,
        system_instruction=voice_model,
        temperature=0.7
    )


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gemini_client.py <topic> [platform]")
        print("Platforms: twitter, instagram, youtube, tiktok, long")
        sys.exit(1)
    
    topic = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else "twitter"
    
    print(f"\n🔮 Generating {platform} content about: {topic}\n")
    print("-" * 50)
    
    try:
        content = generate_with_voice(topic, platform)
        print(content)
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have set your GEMINI_API_KEY:")
        print("  export GEMINI_API_KEY='your-key-here'")
        print("\nGet your key from: https://aistudio.google.com/apikey")
