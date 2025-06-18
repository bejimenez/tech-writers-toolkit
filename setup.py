# setup.py
"""Setup script for the Technical Writing Assistant application"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for the long description
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="technical-writing-assistant",
    version="1.0.0",
    description="AI-powered technical documentation review system and assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Brittani Jimenez",
    author_email="brittani.jimenez@assaabloy.com",
    url="github.com/bejimenez/tech-writers-toolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "flet>=0.21.2",
        "python-dotenv>=1.0.0",
        "PyMuPDF>=1.23.0",
        "pdf2image>=3.1.0",
        "pytesseract>=0.3.10",
        "Pillow>=10.0.0",
        "structlog>=23.2.0",
        "rich>=13.7.0",
        "cryptography>=41.0.0",
    ],
        extras_require={
        "ai": [
            "crewai>=0.41.1",
            "langchain>=0.1.0",
            "langchain-openai>=0.1.0",
            "langchain-google-genai>=1.0.0",
            "openai>=1.0.0",
            "google-generativeai>=0.3.0",
            "chromadb>=0.4.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
            "mkdocstrings[python]>=0.24.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "tech-writer=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: General",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="technical writing, documentation, ai, review, flet",
)