# Technical Writing Assistant - Phase 1

A Python-based desktop application for reviewing and analyzing technical documentation using AI-powered agents. This is the Phase 1 implementation focusing on core infrastructure and document processing.

## Features (Phase 1)

- **Document Processing**: Extract text and metadata from PDF, TXT, and DOCX files
- **OCR Support**: Process scanned documents using Tesseract OCR
- **Modern UI**: Clean, responsive interface built with Flet
- **Logging**: Comprehensive structured logging with Rich console output
- **Configuration**: Environment-based configuration management
- **File Upload**: Drag-and-drop file upload with validation
- **Multi-format Support**: PDF (text and scanned), plain text, and Word documents

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Optional (for OCR functionality)
- Tesseract OCR engine
  - Windows: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `sudo apt install tesseract-ocr`

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tech-writer-assistant
   ```

2. **Run the setup script**
   ```bash
   python setup_project.py
   ```
   This will:
   - Create the complete project structure
   - Generate requirements.txt
   - Create configuration templates
   - Optionally install dependencies

3. **Create your environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys (optional for Phase 1):
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Install dependencies (if not done by setup script)**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

## Project Structure

```
tech-writer-assistant/
├── src/                     # Source code
│   ├── main.py             # Application entry point
│   ├── ui/                 # User interface components
│   │   ├── app.py          # Main Flet application
│   │   ├── views/          # Different app views
│   │   └── components/     # Reusable UI components
│   ├── document/           # Document processing
│   │   ├── processor.py    # Main document processor
│   │   ├── extractor.py    # Text extraction
│   │   └── ocr_handler.py  # OCR processing
│   ├── utils/              # Utilities
│   │   ├── config.py       # Configuration management
│   │   ├── logger.py       # Logging setup
│   │   └── decorators.py   # Useful decorators
│   └── agents/             # AI agents (Phase 2)
├── data/                   # Data storage
├── logs/                   # Application logs
├── docs/                   # Documentation
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Usage

### Basic Document Review

1. **Login**: Use any username/password combination (authentication is simplified in Phase 1)

2. **Upload Document**: 
   - Click "Review Document" on the home page
   - Drag and drop a file or click "Browse Files"
   - Supported formats: PDF, TXT, DOCX

3. **View Results**: 
   - See document information and processing details
   - Preview extracted text content
   - Review processing statistics

### Navigation

- **Home**: Overview and quick actions
- **Review**: Document upload and processing
- **Settings**: Application configuration and system info

## Configuration

The application uses environment variables for configuration. Key settings:

```bash
# Application
APP_NAME=Technical Writing Assistant
DEBUG=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=console

# API Keys (for Phase 2)
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

## Logging

The application includes comprehensive logging:

- **Console Output**: Rich-formatted logs during development
- **File Logging**: Persistent logs in `logs/app.log`
- **Structured Logging**: JSON-formatted logs for production
- **Error Tracking**: Optional Sentry integration

View logs in real-time:
```bash
tail -f logs/app.log
```

## Troubleshooting

### Common Issues

1. **OCR not working**
   - Install Tesseract OCR engine
   - Ensure it's in your system PATH

2. **File upload fails**
   - Check file size (max 50MB)
   - Verify file format is supported
   - Check file permissions

3. **Application won't start**
   - Check Python version (3.8+)
   - Verify all dependencies are installed
   - Check `logs/app.log` for error details

### Debug Mode

Enable debug mode in `.env`:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

This provides detailed logging and error information.

## Development

### Adding New Features

1. **Document Processing**: Extend `src/document/` modules
2. **UI Components**: Add to `src/ui/components/` 
3. **Views**: Create new views in `src/ui/views/`
4. **Utilities**: Add helpers to `src/utils/`

### Code Style

- Follow PEP 8 conventions
- Use type hints
- Add docstrings for public methods
- Keep functions under 60 lines
- Use structured logging

### Testing

Run tests (when implemented):
```bash
pytest tests/
```

## Phase 2 Roadmap

The next phase will add:

- **AI Agents**: Multi-agent review system using CrewAI
- **LLM Integration**: Groq and Gemini API integration
- **Advanced Analysis**: Technical accuracy, formatting, and diagram review
- **Export Features**: Generate review reports
- **Database Storage**: Review history and analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Check the troubleshooting section
- Review logs in `logs/app.log`
- Create an issue on GitHub

---

**Phase 1 Status**: ✅ Complete
- Document processing pipeline
- Modern Flet UI
- Comprehensive logging
- Configuration management
- File upload and validation

**Next**: Phase 2 - AI Agent Implementation