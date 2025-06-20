# User Guide - Application Overview

## Introduction

The Technical Writing Assistant is a desktop application designed to help technical writers improve their documentation through AI-powered review processes. The system combines document processing capabilities with specialized AI agents to analyze different aspects of technical documents.

## Current Features (Phase 1 Complete + Phase 2 Steps 1-2)

### Document Processing
- **Multi-format Support**: PDF (text and scanned), TXT, and DOCX files
- **OCR Processing**: Handles scanned documents using Mistral Vision API
- **Intelligent Processing**: Automatically chooses best extraction method
- **Session Tracking**: Database storage of all processing sessions

### AI Review System
- **Technical Agent**: Analyzes technical accuracy, safety issues, and completeness
- **LLM Integration**: Supports Groq and Gemini APIs with fallback
- **Rule-based Fallback**: Works even without AI API keys
- **Structured Findings**: Categorized issues with severity levels and suggestions

### User Interface
- **Modern Desktop App**: Built with Flet framework
- **Navigation**: Home, Review, and Settings views
- **Real-time Progress**: Visual feedback during processing
- **Results Display**: Comprehensive review results with export options

## Quick Start

1. **Login**: Use any username/password combination
2. **Upload Document**: Navigate to Review tab and upload a document
3. **Review Results**: View processing results and document analysis
4. **AI Review**: Click "Start AI Review" to get detailed technical feedback

## Authentication

Currently uses simplified authentication for development:
- Any username/password combination will work
- Session management included for future enhancement
- User context preserved throughout application

## Document Upload

### Supported Formats
- **PDF**: Both text-based and scanned documents
- **TXT**: Plain text files
- **DOCX**: Microsoft Word documents

### Upload Methods
- Drag and drop files onto upload area
- Click "Browse Files" to select documents
- File validation with size limits (50MB max)

### Processing Options
- **Auto-detect**: System chooses best processing method
- **Force OCR**: Override for testing OCR on readable PDFs
- **Session Tracking**: All uploads tracked in database

## Review Results

### Document Information
- Filename and file statistics
- Page count and processing method
- Text extraction quality indicators
- Processing time and session ID

### Text Preview
- First 1000 characters of extracted text
- Full text available for copy/paste
- Character count and extraction statistics

### AI Review Features
- **Technical Analysis**: Safety, accuracy, and completeness checks
- **Severity Levels**: Error, Warning, and Info classifications
- **Location References**: Specific document sections identified
- **Improvement Suggestions**: Actionable recommendations

## Navigation

### Home View
- Quick action buttons for common tasks
- System status indicators
- Recent review access

### Review View
- AI status and connection testing
- Document upload and processing
- Results display and export options
- Session history access

### Settings View
- Application configuration options
- Theme and display preferences
- System information display

## AI Features

### Connection Testing
- Test individual providers (Groq, Gemini)
- Verify API connectivity
- Response time measurement
- Sample response display

### Provider Configuration
- Primary and fallback providers
- Automatic failover between services
- Cost-effective model selection
- Rate limiting and optimization

## Session Management

### Processing Sessions
- Unique session ID for each document
- Processing method tracking
- Time and status recording
- User attribution

### Review History
- Recent processing sessions display
- Status and timing information
- Session retrieval by ID
- Processing method comparison

## Troubleshooting

### Common Issues

**AI Features Disabled**
- Verify API keys in .env file
- Check connection with test buttons
- Review logs for authentication errors

**File Upload Failures**
- Ensure file size under 50MB
- Verify supported format
- Check file permissions

**OCR Processing Issues**
- Confirm Mistral API key configuration
- Test with "Force OCR" option
- Review OCR-specific logs

### Getting Help
- Check application logs in `logs/app.log`
- Use debug mode for detailed information
- Reference error messages for specific issues

## What's Coming Next

### Phase 2 Completion (In Progress)
- **Multi-Agent System**: Brand, formatting, and diagram reviewers
- **Advanced Analysis**: Comprehensive document evaluation
- **Report Generation**: Detailed review reports with recommendations

### Future Features
- **Export Capabilities**: PDF reports and structured data
- **Collaborative Reviews**: Multi-user feedback systems
- **Integration Options**: API access and external tool connections