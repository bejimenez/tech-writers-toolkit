# Admin Guide - Configuration and Management

## Installation and Setup

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space for application and data
- **Network**: Internet connection required for AI features

### Initial Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/bejimenez/tech-writers-toolkit.git
   cd tech-writers-toolkit
   ```

2. **Run Setup Script**
   ```bash
   python setup_project.py
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env file with appropriate values
   ```

## Configuration Management

### Environment Variables

The application uses environment variables for configuration. All settings are defined in the `.env` file.

#### Core Application Settings

```bash
# Application Identity
APP_NAME=Technical Writing Assistant
APP_VERSION=1.0.0
DEBUG=true

# Feature Toggles
ENABLE_AI_AGENTS=true
```

#### AI API Configuration

```bash
# Groq API (Primary LLM Provider)
GROQ_API_KEY=your_groq_api_key_here

# Gemini API (Fallback LLM Provider)
GEMINI_API_KEY=your_gemini_api_key_here

# Mistral API (OCR Processing)
MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_BASE_URL=https://api.mistral.ai/v1
MISTRAL_MODEL=pixtral-12b-2409

# Provider Selection
DEFAULT_PROVIDER=groq
FALLBACK_PROVIDER=gemini
```

#### Processing Configuration

```bash
# OCR Settings
OCR_MAX_IMAGE_SIZE=2048  # Max width/height in pixels
OCR_DPI=300              # DPI for PDF to image conversion
OCR_TIMEOUT=30           # Request timeout in seconds

# AI Model Settings
MAX_TOKENS_PER_REQUEST=2000
ENABLE_RESPONSE_CACHE=true
CACHE_TTL_HOURS=24
```

#### Security Configuration

```bash
# Authentication
JWT_SECRET_KEY=generate_a_secure_random_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=8
SESSION_TIMEOUT_MINUTES=30
MAX_LOGIN_ATTEMPTS=3
PASSWORD_MIN_LENGTH=8

# Encryption
ENCRYPTION_KEY=generate_another_secure_key_here
```

#### Logging Configuration

```bash
# Logging Level and Format
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=console       # console or json
LOG_RETENTION_DAYS=30

# External Monitoring
ENABLE_SENTRY=false
SENTRY_DSN=your_sentry_dsn_here
```

### Configuration Validation

The application validates configuration on startup:

```bash
python -c "from src.utils.config import Config; print(Config.validate_config())"
```

Common validation errors:
- Missing required API keys when AI features enabled
- Invalid provider names
- Out-of-range numeric values

## Database Management

### SQLite Database

The application uses SQLite for local data storage:

- **Location**: `data/reviews.db`
- **Tables**: `review_sessions`, `agent_findings`
- **Backup**: Automatically backed up before schema changes

#### Manual Database Operations

```bash
# View database schema
sqlite3 data/reviews.db ".schema"

# Query recent sessions
sqlite3 data/reviews.db "SELECT * FROM review_sessions ORDER BY created_at DESC LIMIT 5;"

# Count findings by severity
sqlite3 data/reviews.db "SELECT severity, COUNT(*) FROM agent_findings GROUP BY severity;"
```

#### Database Backup

```bash
# Create backup
cp data/reviews.db data/reviews_backup_$(date +%Y%m%d).db

# Restore from backup
cp data/reviews_backup_20241220.db data/reviews.db
```

### Data Retention

Configure automatic cleanup of old data:

```bash
# Current retention: LOG_RETENTION_DAYS=30
# Sessions and findings older than 30 days are archived
```

## Logging and Monitoring

### Log Files

Application logs are stored in the `logs/` directory:

- **`app.log`**: Main application log
- **`archive/`**: Rotated log files
- **Console output**: Real-time development logs

### Log Levels

| Level   | Purpose                          | Example                    |
|---------|----------------------------------|----------------------------|
| DEBUG   | Detailed debugging information   | Function entry/exit        |
| INFO    | General application events       | Document processed         |
| WARNING | Potential issues                 | API rate limit approaching |
| ERROR   | Error conditions                 | Processing failed          |

### Monitoring Setup

#### Sentry Integration (Optional)

```bash
# Enable Sentry for error tracking
ENABLE_SENTRY=true
SENTRY_DSN=https://your-dsn@sentry.io/project-id

# Configure environment
SENTRY_ENVIRONMENT=production  # or development
```

#### Log Analysis

```bash
# View recent errors
grep "ERROR" logs/app.log | tail -10

# Monitor API calls
grep "API call" logs/app.log | grep "groq"

# Check processing performance
grep "processing_time" logs/app.log | tail -5
```

## User Management

### Current Authentication

The application currently uses simplified authentication:
- Any username/password combination accepted
- Session management implemented
- JWT tokens generated for future enhancement

### 🚧 Enhanced Authentication (Planned)

Future releases will include:
- User registration and management
- Role-based access control
- Password strength requirements
- Account lockout policies

## Performance Tuning

### Processing Optimization

#### Document Processing

```bash
# Adjust OCR settings for performance vs quality
OCR_DPI=150              # Faster processing, lower quality
OCR_DPI=300              # Balanced (default)
OCR_DPI=600              # Higher quality, slower processing

# Image size limits
OCR_MAX_IMAGE_SIZE=1024  # Faster processing
OCR_MAX_IMAGE_SIZE=2048  # Balanced (default)
OCR_MAX_IMAGE_SIZE=4096  # Higher quality
```

#### AI Processing

```bash
# Token limits for faster responses
MAX_TOKENS_PER_REQUEST=1000  # Faster, shorter responses
MAX_TOKENS_PER_REQUEST=2000  # Balanced (default)
MAX_TOKENS_PER_REQUEST=4000  # Longer, more detailed responses

# Response caching
ENABLE_RESPONSE_CACHE=true   # Recommended
CACHE_TTL_HOURS=24          # Balance freshness vs performance
```

### Memory Management

Monitor application memory usage:
- Typical usage: 200-500MB
- Peak usage during OCR: 800MB-1.2GB
- Large documents: May require 2GB+

## Security Administration

### API Key Management

1. **Generate Strong Keys**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Rotate Keys Regularly**
   - Update `.env` file
   - Restart application
   - Verify connectivity

3. **Monitor Usage**
   - Track API call volumes
   - Monitor cost implications
   - Set up usage alerts

### Data Security

1. **File Permissions**
   ```bash
   chmod 600 .env           # Environment variables
   chmod 700 data/          # Database directory
   chmod 644 logs/app.log   # Log files
   ```

2. **Database Security**
   - SQLite file encrypted at rest (planned)
   - Regular backups
   - Access logging

### Network Security

1. **HTTPS Enforcement**
   - All API calls use HTTPS
   - Certificate validation enabled
   - No insecure connections

2. **Rate Limiting**
   - Built into AI providers
   - Application-level throttling
   - Error handling for limits

## Troubleshooting

### Common Issues

#### Configuration Problems

```bash
# Validate configuration
python -c "from src.utils.config import Config; errors = Config.validate_config(); print('Errors:' if errors else 'Valid:', errors)"

# Test AI connectivity
python tests/test_llm_connection.py

# Test OCR functionality
python tests/test_mistral_ocr.py
```

#### Performance Issues

```bash
# Check log file sizes
du -h logs/

# Monitor memory usage
ps aux | grep python

# Database size
du -h data/reviews.db
```

#### Processing Failures

1. **Check API Keys**
   ```bash
   grep -E "(GROQ|GEMINI|MISTRAL)_API_KEY" .env
   ```

2. **Verify Network Connectivity**
   ```bash
   curl -s https://api.groq.com/openai/v1/models
   ```

3. **Review Logs**
   ```bash
   tail -f logs/app.log | grep ERROR
   ```

### Diagnostic Commands

```bash
# Application health check
python src/main.py --health-check

# Configuration dump (sensitive data masked)
python -c "from src.utils.config import Config; print(f'Debug: {Config.DEBUG}, AI: {Config.get_ai_status()}')"

# Database integrity check
sqlite3 data/reviews.db "PRAGMA integrity_check;"
```

## Backup and Recovery

### Automated Backup

Set up regular backups:

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$DATE
cp data/reviews.db backups/$DATE/
cp .env backups/$DATE/env_backup
tar -czf backups/backup_$DATE.tar.gz backups/$DATE/
```

### Recovery Procedures

1. **Database Recovery**
   ```bash
   # Stop application
   # Restore database backup
   cp backups/backup_20241220/reviews.db data/reviews.db
   # Restart application
   ```

2. **Configuration Recovery**
   ```bash
   # Restore environment configuration
   cp backups/backup_20241220/env_backup .env
   # Validate configuration
   python -c "from src.utils.config import Config; print(Config.validate_config())"
   ```

3. **Full System Recovery**
   ```bash
   # Extract full backup
   tar -xzf backups/backup_20241220.tar.gz
   # Restore all components
   cp backups/20241220_120000/* ./
   ```

## Maintenance Tasks

### Daily Maintenance

1. **Log Review**
   ```bash
   # Check for errors in last 24 hours
   grep "$(date -d '1 day ago' '+%Y-%m-%d')" logs/app.log | grep ERROR
   ```

2. **Database Health**
   ```bash
   # Check database size growth
   ls -lh data/reviews.db
   
   # Verify recent activity
   sqlite3 data/reviews.db "SELECT COUNT(*) FROM review_sessions WHERE date(created_at) = date('now');"
   ```

### Weekly Maintenance

1. **Performance Review**
   ```bash
   # Analyze processing times
   grep "processing_time" logs/app.log | awk '{print $NF}' | sort -n | tail -10
   
   # Check API usage patterns
   grep "API call completed" logs/app.log | wc -l
   ```

2. **Storage Cleanup**
   ```bash
   # Clean old log files (keep last 30 days)
   find logs/archive -name "*.log" -mtime +30 -delete
   
   # Archive old sessions if needed
   # (Custom script based on retention policy)
   ```

### Monthly Maintenance

1. **Security Audit**
   ```bash
   # Review access patterns
   grep "User authenticated" logs/app.log | sort | uniq -c
   
   # Check for failed login attempts
   grep "authentication failed" logs/app.log
   ```

2. **Performance Optimization**
   ```bash
   # Database optimization
   sqlite3 data/reviews.db "VACUUM;"
   sqlite3 data/reviews.db "ANALYZE;"
   ```

## Deployment Considerations

### Development to Production

1. **Environment Preparation**
   ```bash
   # Production environment variables
   DEBUG=false
   LOG_LEVEL=INFO
   LOG_FORMAT=json
   ENABLE_SENTRY=true
   ```

2. **Security Hardening**
   - Use strong, unique API keys
   - Enable HTTPS enforcement
   - Configure proper file permissions
   - Set up monitoring and alerting

3. **Performance Configuration**
   ```bash
   # Optimized for production
   MAX_TOKENS_PER_REQUEST=1500
   ENABLE_RESPONSE_CACHE=true
   CACHE_TTL_HOURS=12
   ```

### Scaling Considerations

For high-volume usage:

1. **Database Migration**
   - Consider PostgreSQL for better concurrency
   - Implement connection pooling
   - Add database replication

2. **Caching Strategy**
   - Implement Redis for response caching
   - Add document processing cache
   - Cache AI model responses

3. **Load Balancing**
   - Multiple AI provider accounts
   - Request queue management
   - Horizontal scaling preparation

## Cost Management

### API Usage Monitoring

Track and optimize API costs:

1. **Groq API Usage**
   ```bash
   # Monitor token usage
   grep "groq.*tokens" logs/app.log | awk '{sum+=$NF} END {print "Total tokens:", sum}'
   
   # Estimate costs (example: $0.0005 per 1K tokens)
   # Cost = (total_tokens / 1000) * 0.0005
   ```

2. **Gemini API Usage**
   ```bash
   # Track Gemini requests
   grep "gemini.*API call completed" logs/app.log | wc -l
   ```

3. **Mistral OCR Usage**
   ```bash
   # Count OCR operations
   grep "Mistral OCR.*completed" logs/app.log | wc -l
   ```

### Cost Optimization

1. **Caching Strategy**
   - Enable response caching
   - Increase cache TTL for stable content
   - Cache document processing results

2. **Model Selection**
   - Use smaller models for simple tasks
   - Reserve advanced models for complex analysis
   - Implement intelligent model routing

3. **Rate Limiting**
   - Implement user-based rate limits
   - Batch similar requests
   - Optimize prompt efficiency

## Integration Management

### External API Dependencies

The application integrates with several external services:

1. **Groq API**
   - Status: https://status.groq.com/
   - Documentation: https://console.groq.com/docs
   - Rate limits: Model-dependent

2. **Gemini API**
   - Status: https://status.cloud.google.com/
   - Documentation: https://ai.google.dev/docs
   - Rate limits: 60 requests/minute (free tier)

3. **Mistral API**
   - Status: https://status.mistral.ai/
   - Documentation: https://docs.mistral.ai/
   - Rate limits: Account-dependent

### Health Monitoring

Implement health checks for external dependencies:

```bash
# API health check script
python tests/test_llm_connection.py > health_report.txt
grep "PASSED\|FAILED" health_report.txt
```

## 🚧 Future Administrative Features

### Planned Enhancements

1. **Advanced User Management**
   - Role-based access control (Admin, Reviewer, Viewer)
   - User activity auditing
   - Password policy enforcement
   - Multi-factor authentication

2. **Enhanced Monitoring**
   - Real-time performance dashboards
   - Automated alerting system
   - Cost tracking and budgeting
   - Usage analytics and reporting

3. **Advanced Security**
   - Document encryption at rest
   - Audit trail compliance
   - LDAP/SSO integration
   - API access controls

4. **Scalability Features**
   - Database clustering support
   - Horizontal scaling capabilities
   - Load balancer integration
   - Cloud deployment options

### Migration Planning

Future database migrations will be handled through:
- Automated schema versioning
- Data migration scripts
- Rollback capabilities
- Zero-downtime upgrades

## Support and Maintenance Contacts

### Technical Support

- **Application Issues**: Check logs and GitHub issues
- **API Problems**: Refer to provider status pages
- **Performance Issues**: Review monitoring data

### Escalation Procedures

1. **Level 1**: Application logs and basic troubleshooting
2. **Level 2**: Configuration and integration issues
3. **Level 3**: Advanced debugging and development support

For urgent issues requiring immediate attention, ensure proper backup procedures are in place before attempting any recovery operations.