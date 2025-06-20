# Development Guide

## Development Environment Setup

### Prerequisites

- **Python**: 3.8+ with pip
- **Git**: For version control
- **IDE**: VS Code recommended with Python extension
- **Optional**: Docker for containerized development

### Initial Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/bejimenez/tech-writers-toolkit.git
   cd tech-writers-toolkit
   python setup_project.py
   ```

2. **Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Development Configuration**
   ```bash
   cp .env.example .env
   # Set DEBUG=true and appropriate API keys for testing
   ```

4. **Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Project Structure

### Directory Organization

```
tech-writer-assistant/
├── src/                     # Source code
│   ├── ui/                 # User interface components
│   │   ├── views/          # Application views
│   │   └── components/     # Reusable UI components
│   ├── document/           # Document processing
│   ├── ai/                 # AI and agent systems
│   ├── agents/             # Review agents
│   ├── storage/            # Database and storage
│   └── utils/              # Utilities and helpers
├── tests/                  # Test files
├── docs/                   # Documentation
├── data/                   # Application data
└── logs/                   # Application logs
```

### Code Organization Principles

- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Use constructor injection for dependencies
- **Interface Segregation**: Small, focused interfaces
- **Error Handling**: Comprehensive exception handling

## Coding Standards

### Python Style Guide

Follow PEP 8 with these specific guidelines:

1. **Line Length**: 88 characters (Black default)
2. **Imports**: Sorted with isort, grouped by standard/third-party/local
3. **Type Hints**: Required for all public methods
4. **Docstrings**: Google-style for all classes and public methods

### Code Formatting

```bash
# Format code with Black
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/ --ignore-missing-imports

# Linting
flake8 src/ tests/
```

### Example Class Structure

```python
# src/agents/example_agent.py
"""Example agent demonstrating coding standards."""

from typing import List, Optional
from dataclasses import dataclass

from src.agents.base_agent import BaseReviewAgent, ReviewContext
from src.storage.models import AgentFinding
from src.utils.logger import LoggerMixin

@dataclass
class ExampleConfig:
    """Configuration for example agent."""
    threshold: float = 0.7
    max_findings: int = 10

class ExampleAgent(BaseReviewAgent, LoggerMixin):
    """
    Example review agent demonstrating best practices.
    
    This agent serves as a template for implementing new review agents
    with proper error handling, logging, and type safety.
    
    Attributes:
        config: Agent configuration settings
        _cache: Internal cache for optimization
    """
    
    def __init__(self, config: Optional[ExampleConfig] = None):
        super().__init__(
            role="Example Reviewer",
            goal="Demonstrate coding standards and patterns",
            backstory="Template agent for development reference"
        )
        self.config = config or ExampleConfig()
        self._cache: dict = {}
        
    def review(self, context: ReviewContext) -> List[AgentFinding]:
        """
        Perform example review of document content.
        
        Args:
            context: Review context with document and session info
            
        Returns:
            List of findings from this agent
            
        Raises:
            ReviewException: If review process fails
        """
        try:
            findings = self._analyze_content(context.document_text)
            
            self.logger.info(
                "Example review completed",
                session_id=context.session_id,
                findings_count=len(findings)
            )
            
            return findings[:self.config.max_findings]
            
        except Exception as e:
            self.logger.error(
                "Example review failed",
                session_id=context.session_id,
                error=str(e)
            )
            raise ReviewException(f"Example agent failed: {e}")
    
    def _analyze_content(self, text: str) -> List[AgentFinding]:
        """Analyze document content for issues."""
        # Implementation details...
        return []
```

## Testing Framework

### Test Organization

Tests are organized by component and type:

```
tests/
├── unit/                   # Unit tests
│   ├── test_agents/       # Agent tests
│   ├── test_document/     # Document processing tests
│   └── test_utils/        # Utility tests
├── integration/           # Integration tests
├── conftest.py           # Shared fixtures
└── test_*.py             # Component tests
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/test_agents/test_technical_agent.py
"""Tests for technical review agent."""

import pytest
from unittest.mock import Mock, patch

from src.agents.technical_agent import TechnicalAgent
from src.agents.base_agent import ReviewContext

class TestTechnicalAgent:
    """Test cases for TechnicalAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create technical agent for testing."""
        return TechnicalAgent()
    
    @pytest.fixture
    def sample_context(self):
        """Create sample review context."""
        return ReviewContext(
            document_text="Sample installation instructions with electrical work.",
            document_info={"filename": "test.pdf", "page_count": 1},
            session_id=1
        )
    
    def test_initialization(self, agent):
        """Test agent initialization."""
        assert agent.role == "Technical Accuracy Reviewer"
        assert agent.confidence_threshold == 0.6
        assert agent.llm_manager is not None or agent.llm_manager is None
    
    def test_review_with_safety_issues(self, agent, sample_context):
        """Test review identifies safety issues."""
        findings = agent.review(sample_context)
        
        # Should find at least one safety-related finding
        safety_findings = [f for f in findings if f.category == "safety"]
        assert len(safety_findings) > 0
        assert any("safety" in f.description.lower() for f in safety_findings)
    
    @patch('src.ai.llm_provider.LLMManager')
    def test_ai_review_fallback(self, mock_llm, agent, sample_context):
        """Test AI review with fallback to rule-based."""
        # Mock AI failure
        mock_llm.return_value.generate_response.side_effect = Exception("API Error")
        
        findings = agent.review(sample_context)
        
        # Should still return findings from rule-based review
        assert isinstance(findings, list)
        # AI failure shouldn't crash the agent
```

#### Integration Test Example

```python
# tests/integration/test_document_to_review.py
"""Integration tests for complete document processing flow."""

import tempfile
from pathlib import Path

import pytest

from src.document.processor import DocumentProcessor
from src.ai.agent_manager import AgentManager

class TestDocumentToReview:
    """Test complete flow from document to review results."""
    
    @pytest.fixture
    def sample_document(self):
        """Create sample document for testing."""
        content = """
        # Installation Instructions
        
        1. Mount the panel using 4 screws
        2. Connect power cable to main source
        3. Wire door contacts to terminals
        """
        
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False
        )
        temp_file.write(content)
        temp_file.close()
        
        yield Path(temp_file.name)
        Path(temp_file.name).unlink()
    
    def test_complete_processing_flow(self, sample_document):
        """Test complete flow from upload to review."""
        # Process document
        processor = DocumentProcessor()
        processed_doc = processor.process_document(
            sample_document, 
            user_id="test_user"
        )
        
        assert processed_doc.session_id is not None
        assert len(processed_doc.text) > 0
        
        # Run agent review
        agent_manager = AgentManager()
        review_result = agent_manager.start_review(processed_doc)
        
        assert review_result.status in ["completed", "partial"]
        assert isinstance(review_result.findings, list)
        assert review_result.session_id == processed_doc.session_id
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_document_processor.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run integration tests only
pytest tests/integration/ -v

# Run with markers
pytest -m "not slow" tests/  # Skip slow tests
```

### Test Configuration

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Development Workflow

### Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-agent-type
   ```

2. **Implement Feature**
   - Write failing tests first (TDD)
   - Implement minimum viable code
   - Refactor and optimize
   - Add comprehensive documentation

3. **Code Quality Checks**
   ```bash
   # Format and check code
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   
   # Run tests
   pytest tests/ --cov=src
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: Add new agent type for X analysis"
   git push origin feature/new-agent-type
   ```

### Adding New Components

#### Adding a New Review Agent

1. **Create Agent Class**
   ```python
   # src/agents/new_agent.py
   from src.agents.base_agent import BaseReviewAgent
   
   class NewAgent(BaseReviewAgent):
       def __init__(self):
           super().__init__(
               role="New Agent Role",
               goal="Agent's specific goal",
               backstory="Agent's expertise context"
           )
       
       def review(self, context: ReviewContext) -> List[AgentFinding]:
           # Implementation
           pass
   ```

2. **Add Agent to Manager**
   ```python
   # src/ai/agent_manager.py
   def _initialize_agents(self):
       # Existing agents...
       self.agents["new"] = NewAgent()
   ```

3. **Create Tests**
   ```python
   # tests/unit/test_agents/test_new_agent.py
   class TestNewAgent:
       def test_agent_initialization(self):
           # Test implementation
           pass
   ```

4. **Add Prompt Template**
   ```python
   # src/ai/prompts.py
   NEW_AGENT_PROMPT = """
   You are a specialized reviewer focusing on...
   """
   ```

#### Adding a New Document Format

1. **Extend Content Extractor**
   ```python
   # src/document/extractor.py
   def _extract_new_format_content(self, file_path: Path, doc_info):
       # Implementation for new format
       pass
   ```

2. **Update Processor**
   ```python
   # src/document/processor.py
   def _determine_processing_method(self, file_path: Path, doc_info, force_ocr):
       if file_path.suffix.lower() == '.new':
           return "new_format_extraction"
   ```

3. **Add Format Tests**
   ```python
   # tests/test_new_format.py
   def test_new_format_processing():
       # Test implementation
       pass
   ```

#### Adding a New UI View

1. **Create View Class**
   ```python
   # src/ui/views/new_view.py
   class NewView:
       def __init__(self, app):
           self.app = app
       
       def build(self) -> ft.Control:
           # UI implementation
           pass
   ```

2. **Add Navigation**
   ```python
   # src/ui/app.py
   def _initialize_views(self):
       self.views["new"] = NewView(self)
   ```

3. **Update Navigation Rail**
   ```python
   # Add destination to navigation rail in relevant views
   ```

## Debugging and Development Tools

### Logging for Development

```python
# Enable debug logging
import logging
from src.utils.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

# Use structured logging
logger.debug("Debug information", key="value", count=42)
logger.info("Process completed", processing_time="1.23s")
logger.error("Operation failed", error=str(e), context="additional_info")
```

### Development Utilities

#### Test Data Generation

```python
# src/utils/test_helpers.py
"""Utilities for generating test data."""

def create_test_document(content_type="technical"):
    """Create sample documents for testing."""
    templates = {
        "technical": "Sample technical installation instructions...",
        "brand": "Marketing-focused document content...",
        "formatting": "Document with various formatting issues..."
    }
    return templates.get(content_type, templates["technical"])

def create_test_session(session_id=1, user_id="test_user"):
    """Create test review session."""
    return ReviewSession(
        id=session_id,
        document_filename="test.pdf",
        user_id=user_id,
        status="completed"
    )
```

#### Development Scripts

```python
# scripts/dev_test_agent.py
"""Quick script to test agent functionality."""

if __name__ == "__main__":
    from src.agents.technical_agent import TechnicalAgent
    from src.agents.base_agent import ReviewContext
    
    agent = TechnicalAgent()
    context = ReviewContext(
        document_text="Test document content",
        document_info={"filename": "test.txt"},
        session_id=0
    )
    
    findings = agent.review(context)
    print(f"Found {len(findings)} issues")
    for finding in findings:
        print(f"- {finding.severity}: {finding.description}")
```

### Performance Profiling

```python
# Performance testing
import cProfile
import pstats
from pathlib import Path

def profile_document_processing():
    """Profile document processing performance."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code to profile
    processor = DocumentProcessor()
    result = processor.process_document(Path("test.pdf"))
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

if __name__ == "__main__":
    profile_document_processing()
```

## Documentation Standards

### Code Documentation

1. **Module Docstrings**
   ```python
   """Brief module description.
   
   Longer description explaining the module's purpose,
   key classes, and usage patterns.
   """
   ```

2. **Class Docstrings**
   ```python
   class ExampleClass:
       """Brief class description.
       
       Longer description explaining the class purpose,
       key methods, and usage examples.
       
       Attributes:
           attribute_name: Description of attribute
           another_attr: Description with type info
       
       Example:
           >>> instance = ExampleClass()
           >>> result = instance.method()
       """
   ```

3. **Method Docstrings**
   ```python
   def example_method(self, param1: str, param2: int = 0) -> bool:
       """Brief method description.
       
       Longer description explaining what the method does,
       its behavior, and any important notes.
       
       Args:
           param1: Description of first parameter
           param2: Description with default value info
           
       Returns:
           Description of return value and its type
           
       Raises:
           ValueError: When parameter validation fails
           CustomException: In specific error conditions
           
       Example:
           >>> result = obj.example_method("test", 42)
           >>> assert result is True
       """
   ```

### API Documentation

API documentation is automatically generated from docstrings using mkdocstrings. Ensure all public interfaces are well documented.

## 🚧 Development Roadmap

### Phase 2 Completion (Current)

**In Progress:**
- Multi-agent system implementation
- Advanced prompt engineering
- Result aggregation and summary generation

**Next Steps:**
1. Implement remaining agents (Brand, Formatting, Diagram)
2. Add agent coordination and result synthesis
3. Implement comprehensive reporting system

### Phase 3 Planning (Future)

**Advanced Features:**
- Custom agent creation framework
- Machine learning model integration
- Real-time collaborative editing
- Advanced caching and optimization

**Enterprise Features:**
- Multi-tenant architecture
- Advanced security and compliance
- Scalability improvements
- Cloud deployment options

### Contributing Guidelines

1. **Code Style**: Follow established patterns and style guide
2. **Testing**: Maintain >80% test coverage for new code
3. **Documentation**: Document all public interfaces
4. **Performance**: Consider performance implications of changes
5. **Backward Compatibility**: Maintain API compatibility when possible

For detailed contributing guidelines, see [CONTRIBUTING.md](contributing.md).