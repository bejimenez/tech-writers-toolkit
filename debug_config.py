#!/usr/bin/env python3
"""
Simple test to check if environment variables are loading correctly
"""

import os
import sys
from pathlib import Path

def test_env_loading():
    """Test environment variable loading"""
    
    print("Environment Variable Test")
    print("=" * 30)
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[0]}")
    
    # Check if .env file exists
    env_file = Path(".env")
    print(f".env file exists: {env_file.exists()}")
    
    if env_file.exists():
        print(f".env file path: {env_file.absolute()}")
        # Read .env file directly
        with open(env_file, 'r') as f:
            lines = f.readlines()
        print(f"Lines in .env file: {len(lines)}")
        
        # Check for API key lines
        groq_line = None
        gemini_line = None
        for line in lines:
            if line.startswith('GROQ_API_KEY='):
                groq_line = line.strip()
            elif line.startswith('GEMINI_API_KEY='):
                gemini_line = line.strip()
        
        print(f"Found GROQ line: {groq_line is not None}")
        print(f"Found GEMINI line: {gemini_line is not None}")
        
        if groq_line:
            print(f"GROQ line length: {len(groq_line)}")
        if gemini_line:
            print(f"GEMINI line length: {len(gemini_line)}")
    
    # Test with manual dotenv loading
    try:
        from dotenv import load_dotenv
        
        # Load from current directory
        result = load_dotenv()
        print(f"dotenv load result: {result}")
        
        # Test direct environment access
        groq_from_env = os.getenv("GROQ_API_KEY")
        gemini_from_env = os.getenv("GEMINI_API_KEY")
        
        print(f"GROQ from os.getenv: {groq_from_env is not None}")
        print(f"GEMINI from os.getenv: {gemini_from_env is not None}")
        
        if groq_from_env:
            print(f"GROQ key length: {len(groq_from_env)}")
            print(f"GROQ starts with: {groq_from_env[:10]}")
        
        if gemini_from_env:
            print(f"GEMINI key length: {len(gemini_from_env)}")
            print(f"GEMINI starts with: {gemini_from_env[:10]}")
            
    except ImportError as e:
        print(f"Could not import dotenv: {e}")
    
    # Test direct config import
    print("\n" + "=" * 30)
    print("Testing Config Import")
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        else:
            # Try current working directory
            src_path = Path.cwd() / "src"
            if src_path.exists():
                sys.path.insert(0, str(src_path))
            else:
                print("Could not find 'src' directory for config import.")
        
        from utils.config import Config
        
        print(f"Config.GROQ_API_KEY set: {Config.GROQ_API_KEY is not None}")
        print(f"Config.GEMINI_API_KEY set: {Config.GEMINI_API_KEY is not None}")
        
        if Config.GROQ_API_KEY:
            print(f"Config GROQ length: {len(Config.GROQ_API_KEY)}")
        if Config.GEMINI_API_KEY:
            print(f"Config GEMINI length: {len(Config.GEMINI_API_KEY)}")
            
        # Test AI status
        ai_status = Config.get_ai_status()
        print(f"AI Status: {ai_status}")
        
    except Exception as e:
        print(f"Config import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_env_loading()