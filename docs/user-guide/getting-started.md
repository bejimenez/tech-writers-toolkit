# Getting Started

This guide will help you set up and run the Technical Writing Assistant on your system.

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: Version 3.8 or higher
- **Memory**: At least 4GB RAM recommended
- **Storage**: 500MB for application and dependencies

### Optional Dependencies

For OCR functionality (processing scanned documents):
- **Tesseract OCR**: 
  - Windows: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `sudo apt install tesseract-ocr`

## Installation

### Method 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd tech-writer-assistant
   ```

2. **Run the setup script**
   ```bash
   python setup_project.py
   ```
   
   This will:
   - Create the complete project structure
   - Install all Python dependencies
   - Set up configuration files
   - Create necessary directories

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file with your settings:
   ```bash
   # Optional: Add API keys for Phase 2
   GROK_API_KEY=your_grok_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Application settings
   LOG_LEVEL=INFO
   DEBUG=true
   ```

### Method 2: Manual Setup

1. **Create project structure**
   ```bash
   mkdir -p src/ui/views src/ui/components src/document src/agents src/ai src/utils
   mkdir -p data/reviews data/templates logs tests docs
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy configuration files**
   ```bash
   cp .env.example .env
   ```

## First Run

1. **Start the application**
   ```bash
   python src/main.py
   ```

2. **Login**
   - Username: any value (e.g., "admin")
   - Password: any value (e.g., "password")
   
   *Note: Phase 1 uses simplified authentication*

3. **Test document processing**
   - Click "Review Document"
   - Upload a PDF, TXT, or DOCX file
   - Review the processing results

## Verification

### Check System Status

In the application:
1. Go to **Home** → **System Status**
2. Verify all services show green checkmarks:
   - Document Processing: Ready
   - AI Services: Connected (may show disconnected in Phase 1)
   - Database: Online

### Test Document Processing

1. Navigate to **Review** tab
2. Upload a sample document
3. Verify successful processing and text extraction

### Check Logs

View application logs:
```bash
tail -f logs/app.log
```

Look for successful startup messages and no error entries.

## Troubleshooting

### Common Issues

**Application won't start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check logs
cat logs/app.log
```

**OCR not working**
```bash
# Test Tesseract installation
tesseract --version

# Install if missing (Ubuntu/Debian)
sudo apt install tesseract-ocr

# Install if missing (macOS)
brew install tesseract
```

**File upload fails**
- Ensure file is under 50MB
- Verify file format (PDF, TXT, DOCX only)
- Check file permissions

### Debug Mode

Enable debug logging in `.env`:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

This provides detailed information about application behavior.

### Getting Help

If you encounter issues:

1. Check the [troubleshooting section](user-guide/troubleshooting.md)
2. Review logs in `logs/app.log`
3. Create an issue on GitHub with:
   - Error message
   - Log entries
   - System information

## Next Steps

- Read the [User Guide](user-guide/first-review.md) for detailed usage instructions
- Explore the [Architecture](architecture/overview.md) to understand the system design
- Learn about [Development](development/contributing.md) if you want to contribute