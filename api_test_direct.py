#!/usr/bin/env python3
"""
Direct API test to isolate the issue
"""

import os
import httpx
import json
from dotenv import load_dotenv

def test_groq_direct():
    """Test Groq API directly"""
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print(f"Testing Groq with key: {api_key[:10]}...")
    else:
        print("❌ GROQ_API_KEY not found in environment variables.")
    
    # Test different model names
    models_to_test = [
        "llama-3.1-70b-versatile",  # Current model in code
        "llama3-70b-8192",          # Alternative
        "mixtral-8x7b-32768",       # Alternative
        "llama3-8b-8192"            # Smaller model
    ]
    
    client = httpx.Client(timeout=30)
    
    for model in models_to_test:
        print(f"\nTesting model: {model}")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        try:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success! Response: {result['choices'][0]['message']['content']}")
                return model  # Return working model
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return None

def test_gemini_direct():
    """Test Gemini API directly"""
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"\nTesting Gemini with key: {api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY not found in environment variables.")
    
    client = httpx.Client(timeout=30)
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Hello"}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 10
        }
    }
    
    try:
        response = client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
            json=payload
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"✅ Success! Response: {text}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Main test function"""
    print("Direct API Testing")
    print("=" * 30)
    
    working_groq_model = test_groq_direct()
    gemini_works = test_gemini_direct()
    
    print("\n" + "=" * 30)
    print("Results:")
    
    if working_groq_model:
        print(f"✅ Groq working with model: {working_groq_model}")
    else:
        print("❌ Groq not working with any tested models")
    
    if gemini_works:
        print("✅ Gemini working")
    else:
        print("❌ Gemini not working")
    
    if working_groq_model:
        print(f"\nTo fix your app, update src/ai/llm_provider.py:")
        print(f'Change model to: "{working_groq_model}"')

if __name__ == "__main__":
    main()