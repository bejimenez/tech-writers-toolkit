# API Reference

## Core Classes and Interfaces

### Document Processing

#### DocumentProcessor

Main coordinator for document processing operations.

```python
class DocumentProcessor:
    def process_document(
        self, 
        file_path: Path, 
        user_id: str = "default",
        force_ocr: bool = False
    ) -> ProcessedContent
```

**Parameters:**
- `file_path`: Path to the document file
- `user_id`: User identifier for session tracking
- `force_ocr`: Force OCR processing even if text is available

**Returns:** `ProcessedContent` object with extracted information and session ID

**Raises:**
- `ValueError`: If file format is not supported
- `FileNotFoundError`: If file doesn't exist

#### ProcessedContent

Container for processed document content.

```python
@dataclass
class ProcessedContent:
    text: str                    # Full extracted text
    pages: List[str]            # Text content per page
    images: List[bytes]         # Extracted images
    tables: List[str]           # Extracted table data
    document_info: DocumentInfo # Document metadata
    processing_time: float      # Processing duration
    session_id: Optional[int]   # Database session ID
```

#### DocumentInfo

Information about a processed document.

```python
@dataclass
class DocumentInfo:
    filename: str
    page_count: int
    file_size: int
    has_text: bool
    has_images: bool
    processing_method: str      # "text_extraction" or "mistral_ocr"
    metadata: Dict
```

### AI System

#### LLMManager

Manages LLM providers with fallback logic.

```python
class LLMManager:
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        provider: Optional[str] = None
    ) -> str
```

**Parameters:**
- `prompt`: The prompt to send
- `max_tokens`: Maximum tokens to generate
- `temperature`: Generation temperature (0.0-1.0)
- `provider`: Specific provider to use (optional)

**Returns:** Generated response text

```python
def test_connection(self, provider: Optional[str] = None) -> Dict[str, Any]
```

**Parameters:**
- `provider`: Specific provider to test, or None for all

**Returns:** Dictionary with test results including availability and response times

#### AgentManager

Coordinates AI agents for document reviews.

```python
class AgentManager:
    def start_review(
        self, 
        processed_content: ProcessedContent,
        agents_to_use: Optional[List[str]] = None
    ) -> ReviewResult
```

**Parameters:**
- `processed_content`: The processed document content
- `agents_to_use`: List of agent names to use (default: all available)

**Returns:** `ReviewResult` with findings from all agents

#### ReviewResult

Result of a complete review process.

```python
@dataclass
class ReviewResult:
    session_id: int
    findings: List[AgentFinding]
    agent_results: Dict[str, List[AgentFinding]]
    total_processing_time: float
    status: str  # "completed", "partial", "failed"
    summary: Optional[str] = None
```

### Review Agents

#### BaseReviewAgent

Base class for all review agents.

```python
class BaseReviewAgent(ABC):
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        confidence_threshold: float = 0.7,
    )
    
    @abstractmethod
    def review(self, context: ReviewContext) -> List[AgentFinding]
```

#### ReviewContext

Context information for agent review.

```python
@dataclass
class ReviewContext:
    document_text: str
    document_info: Dict[str, Any]
    session_id: int
    user_preferences: Optional[Dict[str, Any]] = None
    previous_findings: Optional[List[AgentFinding]] = None
```

#### AgentFinding

A single finding from an agent.

```python
@dataclass
class AgentFinding:
    id: Optional[int] = None
    session_id: int = 0
    agent_name: str = ""
    severity: str = ""  # error, warning, info
    category: str = ""  # formatting, technical, brand, etc.
    description: str = ""
    location: str = ""  # Page X, Section Y, etc.
    suggestion: Optional[str] = None
    confidence: float = 0.0
    created_at: Optional[datetime] = None
```

### Database Models

#### DatabaseManager

Manages SQLite database operations.

```python
class DatabaseManager:
    def create_review_session(self, session: ReviewSession) -> int
    def add_agent_finding(self, finding: AgentFinding) -> int
    def get_session_findings(self, session_id: int) -> List[AgentFinding]
    def update_session_status(self, session_id: int, status: str, processing_time: float = 0.0)
    def get_recent_sessions(self, user_id: str, limit: int = 10) -> List[ReviewSession]
```

#### ReviewSession

A complete review session.

```python
@dataclass
class ReviewSession:
    id: Optional[int] = None
    document_filename: str = ""
    document_path: str = ""
    user_id: str = ""
    created_at: Optional[datetime] = None
    processing_method: str = ""
    total_processing_time: float = 0.0
    status: str = "pending"  # pending, processing, completed, failed
```

### Configuration

#### Config

Application configuration management.

```python
class Config:
    # App Configuration
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    
    # API Configuration
    MISTRAL_API_KEY: Optional[str]
    GROQ_API_KEY: Optional[str]
    GEMINI_API_KEY: Optional[str]
    DEFAULT_PROVIDER: str
    
    # Processing Settings
    MAX_TOKENS_PER_REQUEST: int
    OCR_MAX_IMAGE_SIZE: int
    OCR_DPI: int
    
    @classmethod
    def validate_config(cls) -> List[str]
    
    @classmethod
    def get_ai_status(cls) -> Dict[str, Any]
```

### Prompt Templates

#### PromptTemplates

Collection of prompt templates for different agent types.

```python
class PromptTemplates:
    @classmethod
    def get_agent_prompt(cls, agent_type: str, document_text: str) -> str
    
    @classmethod
    def get_summary_prompt(cls, all_findings: str) -> str
```

**Agent Types:**
- `"technical"`: Technical accuracy and safety review
- `"brand"`: Brand consistency and presentation
- `"formatting"`: Formatting and standards compliance
- `"diagram"`: Visual elements and diagrams

### Utilities

#### Logging

```python
def setup_logging() -> None
def get_logger(name: Optional[str] = None) -> structlog.BoundLogger
```

#### Decorators

```python
@log_execution_time
def your_function():
    """Logs function execution time"""
    pass

@log_api_call(provider="groq")
def api_function():
    """Logs API calls with provider information"""
    pass

@handle_exceptions(default_return=None, reraise=True)
def risky_function():
    """Handles exceptions and logs them"""
    pass
```

## Error Handling

### Exception Hierarchy

```python
class ReviewException(Exception):
    """Base exception for review processes"""
    pass
```

### Common Error Patterns

**Configuration Errors:**
- Missing API keys
- Invalid provider configuration
- File permission issues

**Processing Errors:**
- Unsupported file formats
- OCR processing failures
- Network connectivity issues

**AI Errors:**
- API rate limiting
- Invalid responses
- Provider unavailability

## Usage Examples

### Basic Document Processing

```python
from src.document.processor import DocumentProcessor
from pathlib import Path

processor = DocumentProcessor()
result = processor.process_document(
    Path("document.pdf"), 
    user_id="user123"
)

print(f"Extracted {len(result.text)} characters")
print(f"Session ID: {result.session_id}")
```

### AI Review

```python
from src.ai.agent_manager import AgentManager

agent_manager = AgentManager()
review_result = agent_manager.start_review(
    processed_content,
    agents_to_use=["technical"]
)

print(f"Found {len(review_result.findings)} issues")
for finding in review_result.findings:
    print(f"{finding.severity}: {finding.description}")
```

### Configuration Testing

```python
from src.utils.config import Config

# Validate configuration
errors = Config.validate_config()
if errors:
    print("Configuration errors:", errors)

# Check AI status
status = Config.get_ai_status()
print(f"AI enabled: {status['ai_enabled']}")
print(f"Available providers: {status}")
```

## Testing Framework

### Test Structure

Tests are organized by component:
- `tests/test_document_processor.py` - Document processing tests
- `tests/test_llm_connection.py` - AI connectivity tests
- `tests/test_config.py` - Configuration validation tests

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_document_processor.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Test Fixtures

Common fixtures are available in `tests/conftest.py`:
- `temp_directory`: Temporary directory for test files
- `sample_text_file`: Sample text file for testing
- `sample_pdf_content`: Mock PDF content

## Placeholder Sections

### 🚧 To Be Implemented

The following API sections will be added as Phase 2 completion progresses:

#### Multi-Agent System
- `BrandAgent` class documentation
- `FormattingAgent` class documentation  
- `DiagramAgent` class documentation
- `SummaryAgent` class documentation

#### Report Generation
- `ReportGenerator` class documentation
- Export format specifications
- Template system API

#### Advanced Features
- Caching mechanism API
- Performance metrics API
- Configuration validation enhancements