#!/usr/bin/env python3
"""
Setup script for Technical Writing Assistant Phase 1
Creates the complete project structure and installs dependencies
"""

import os
import subprocess
import sys
from pathlib import Path

def create_project_structure():
    """Create the complete project directory structure"""
    
    directories = [
        # Main source directories
        "src",
        "src/ui",
        "src/ui/views",
        "src/ui/components",
        "src/agents",
        "src/document",
        "src/ai",
        "src/security",
        "src/storage",
        "src/utils",
        
        # Data directories
        "data",
        "data/reviews",
        "data/templates",
        "data/knowledge",
        
        # Logs directory
        "logs",
        "logs/archive",
        
        # Documentation
        "docs",
        "docs/user-guide",
        "docs/admin-guide",
        "docs/api",
        "docs/architecture",
        "docs/development",
        
        # Tests
        "tests",
        "tests/unit",
        "tests/integration",
    ]
    
    print("Creating project structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory.startswith("src/"):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✓ Project structure created")

def create_requirements_file():
    """Create requirements.txt with all necessary dependencies"""
    
    requirements = """# Core Framework
flet>=0.21.2
python-dotenv>=1.0.0

# AI and ML
crewai>=0.41.1
langchain>=0.1.0
langchain-openai>=0.1.0
langchain-google-genai>=1.0.0
openai>=1.0.0
google-generativeai>=0.3.0

# Document Processing
PyMuPDF>=1.23.0
pdf2image>=3.1.0
pytesseract>=0.3.10
Pillow>=10.0.0

# Database and Storage
chromadb>=0.4.0
sqlite3-backup>=0.1.0

# Security
cryptography>=41.0.0
PyJWT>=2.8.0
passlib[bcrypt]>=1.7.4
bcrypt>=4.0.0

# Logging and Monitoring
structlog>=23.2.0
sentry-sdk>=1.38.0
rich>=13.7.0
python-json-logger>=2.0.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.4.0
mkdocstrings[python]>=0.24.0
mkdocs-mermaid2-plugin>=1.1.0
mkdocs-video>=1.5.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-mock>=3.12.0

# Development
black>=23.0.0
flake8>=6.1.0
mypy>=1.7.0
pre-commit>=3.5.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("✓ requirements.txt created")

def create_env_example():
    """Create .env.example file with configuration template"""
    
    env_content = """# API Configuration
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Model Selection
DEFAULT_PROVIDER=groq
FALLBACK_PROVIDER=gemini

# Cost Control
MAX_TOKENS_PER_REQUEST=2000
ENABLE_RESPONSE_CACHE=true
CACHE_TTL_HOURS=24

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=console
ENABLE_SENTRY=false
SENTRY_DSN=your_sentry_dsn_here
LOG_RETENTION_DAYS=30

# Security Configuration
JWT_SECRET_KEY=generate_a_secure_random_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
ENCRYPTION_KEY=generate_another_secure_key_here
SESSION_TIMEOUT_MINUTES=30
MAX_LOGIN_ATTEMPTS=3
PASSWORD_MIN_LENGTH=8

# App Configuration
APP_NAME=Technical Writing Assistant
APP_VERSION=1.0.0
DEBUG=true
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("✓ .env.example created")

def create_gitignore():
    """Create .gitignore file"""
    
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
logs/*.log
logs/archive/
data/reviews/
data/temp/
*.db
*.db-journal

# Flet
.flet/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✓ .gitignore created")

def install_dependencies():
    """Install Python dependencies"""
    
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        print("You may need to install them manually with: pip install -r requirements.txt")

def main():
    """Main setup function"""
    
    print("Setting up Technical Writing Assistant - Phase 1")
    print("=" * 50)
    
    create_project_structure()
    create_requirements_file()
    create_env_example()
    create_gitignore()
    
    # Ask user if they want to install dependencies
    install_deps = input("\nWould you like to install dependencies now? (y/n): ").lower().strip()
    if install_deps == 'y':
        install_dependencies()
    else:
        print("Skipping dependency installation. Run 'pip install -r requirements.txt' later.")
    
    print("\n" + "=" * 50)
    print("Phase 1 setup complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and add your API keys")
    print("2. Run the main application: python src/main.py")
    print("3. Check the README.md for detailed instructions")

if __name__ == "__main__":
    main()