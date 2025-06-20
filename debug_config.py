#!/usr/bin/env python3
"""
Debug script to check API key configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def debug_config():
    """Debug configuration setup"""
    
    print("API Configuration Debug")
    print("=" * 30)
    
    # Check .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and add your API keys")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print(f"\nAPI Keys Status:")
    print(f"GROQ_API_KEY: {'✅ Set' if groq_key and groq_key != 'your_groq_api_key_here' else '❌ Not set or placeholder'}")
    if groq_key:
        print(f"   Value starts with: {groq_key[:10]}...")
    
    print(f"GEMINI_API_KEY: {'✅ Set' if gemini_key and gemini_key != 'your_gemini_api_key_here' else '❌ Not set or placeholder'}")
    if gemini_key:
        print(f"   Value starts with: {gemini_key[:10]}...")
    
    # Check for placeholder values and key validity
    groq_valid = groq_key and groq_key != "your_groq_api_key_here" and len(groq_key) > 30
    gemini_valid = gemini_key and gemini_key != "your_gemini_api_key_here" and len(gemini_key) > 30
    
    if groq_key == "your_groq_api_key_here":
        print("⚠️  GROQ_API_KEY still has placeholder value")
    elif groq_key and len(groq_key) < 40:
        print(f"⚠️  GROQ_API_KEY seems too short ({len(groq_key)} chars) - may be truncated")
    
    if gemini_key == "your_gemini_api_key_here":
        print("⚠️  GEMINI_API_KEY still has placeholder value")
    elif gemini_key and len(gemini_key) < 30:
        print(f"⚠️  GEMINI_API_KEY seems too short ({len(gemini_key)} chars)")
    
    if not groq_key and not gemini_key:
        print("❌ No API keys found!")
        return False
    
    if not groq_valid and not gemini_valid:
        print("❌ No valid API keys found!")
        return False
    
    print(f"\nValidation Summary:")
    print(f"Groq key valid: {'✅' if groq_valid else '❌'}")
    print(f"Gemini key valid: {'✅' if gemini_valid else '❌'}")
    
    return True

if __name__ == "__main__":
    debug_config()