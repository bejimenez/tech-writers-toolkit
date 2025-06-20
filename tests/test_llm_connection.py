#!/usr/bin/env python3
"""
Test script for Phase 2 Step 1: Basic LLM Provider Setup
Use this to test AI connectivity without running the full application
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import Config
from src.utils.logger import setup_logging, get_logger

def test_step1():
    """Test Step 1 implementation"""
    
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)
    
    print("Phase 2 Step 1 Test: Basic LLM Provider Setup")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration...")
    config_errors = Config.validate_config()
    if config_errors:
        print("❌ Configuration errors:")
        for error in config_errors:
            print(f"   - {error}")
        print("\nPlease update your .env file and try again.")
        return False
    print("✅ Configuration validated")
    
    # Test 2: AI Status
    print("\n2. Checking AI Status...")
    ai_status = Config.get_ai_status()
    print(f"   AI Enabled: {ai_status['ai_enabled']}")
    print(f"   Groq Configured: {ai_status['groq_configured']}")
    print(f"   Gemini Configured: {ai_status['gemini_configured']}")
    print(f"   Default Provider: {ai_status['default_provider']}")
    print(f"   Has Any AI Key: {ai_status['has_any_ai_key']}")
    
    if not ai_status['has_any_ai_key']:
        print("⚠️  No AI API keys found. Add GROQ_API_KEY or GEMINI_API_KEY to .env file")
        print("You can still test the UI, but AI features will be disabled.")
        return True
    
    # Test 3: LLM Manager Initialization
    print("\n3. Testing LLM Manager...")
    try:
        from src.ai.llm_provider import LLMManager
        llm_manager = LLMManager()
        print("✅ LLM Manager initialized")
        
        # Test available providers
        available = llm_manager.get_available_providers()
        print(f"   Available providers: {available}")
        
    except Exception as e:
        print(f"❌ LLM Manager initialization failed: {e}")
        return False
    
    # Test 4: Connection Test
    print("\n4. Testing AI Connections...")
    try:
        results = llm_manager.test_connection()
        
        for provider, result in results.items():
            if result["available"]:
                print(f"✅ {provider.title()}: Connected ({result['response_time']})")
                print(f"   Sample response: {result['response'][:100]}...")
            else:
                print(f"❌ {provider.title()}: Failed - {result['error']}")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    # Test 5: Prompt Templates
    print("\n5. Testing Prompt Templates...")
    try:
        from src.ai.prompts import PromptTemplates
        
        # Test getting a prompt
        test_prompt = PromptTemplates.get_agent_prompt("technical", "Sample document text")
        print("✅ Prompt templates working")
        print(f"   Sample prompt length: {len(test_prompt)} characters")
        
    except Exception as e:
        print(f"❌ Prompt templates failed: {e}")
        return False
    
    # Test 6: Simple AI Response
    print("\n6. Testing AI Response Generation...")
    try:
        response = llm_manager.generate_response(
            PromptTemplates.CONNECTION_TEST,
            max_tokens=100,
            temperature=0.3
        )
        
        print("✅ AI response generation working")
        print(f"   Response: {response}")
        
    except Exception as e:
        print(f"❌ AI response generation failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Step 1 Test PASSED!")
    print("\nYou can now:")
    print("1. Run the main application: python src/main.py")
    print("2. Go to Review tab")
    print("3. Test AI connection using the buttons")
    print("4. Upload a document and try 'Start AI Review'")
    print("\nNext: Implement Step 2 (Single Agent Review)")
    
    return True

if __name__ == "__main__":
    success = test_step1()
    sys.exit(0 if success else 1)