# Osram CLI - Technical Information

## System Requirements

- Python 3.7 or higher
- pip package manager
- Internet connection for AI provider APIs
- API keys for the AI providers you want to use

## Installation Methods

### Method 1: From PyPI (Recommended)

```bash
pip install osram-cli
```

### Method 2: From Source

```bash
git clone https://github.com/Volgat/osram-cli.git
cd osram-cli
pip install -e .
```

### Method 3: Development Installation

For contributors and developers:

```bash
git clone https://github.com/Volgat/osram-cli.git
cd osram-cli
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

## Configuration

### Configuration File Location

The configuration file is automatically created at:
- **Linux/macOS**: `~/.osram_config.json`
- **Windows**: `C:\Users\<YourUsername>\.osram_config.json`

### Configuration Structure

```json
{
  "current_provider": "zai",
  "providers": {
    "zai": {
      "api_key": "your_zhipu_api_key",
      "model": "GLM-4-Plus",
      "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    },
    "claude": {
      "api_key": "your_anthropic_api_key",
      "model": "claude-3-opus-20240229",
      "endpoint": "https://api.anthropic.com/v1/messages"
    },
    "gemini": {
      "api_key": "your_google_api_key",
      "model": "gemini-1.5-pro-latest",
      "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}"
    },
    "openai": {
      "api_key": "your_openai_api_key",
      "model": "gpt-4-turbo",
      "endpoint": "https://api.openai.com/v1/chat/completions"
    }
  },
  "temperature": 0.7,
  "max_tokens": 4096,
  "save_history": true,
  "history_file": "osram_history.json",
  "trust_current_directory": false,
  "history_per_directory": true,
  "auto_approve_file_operations": false,
  "persistent_analysis": true,
  "enable_plugins": true,
  "enable_git_integration": true,
  "enable_collaboration": false,
  "enable_streaming": true,
  "cache_responses": true,
  "log_operations": true,
  "user_preferences": {
    "theme": "dark",
    "font_size": 14,
    "auto_save": true,
    "confirm_destructive": true,
    "streaming": true,
    "max_history": 1000,
    "preferred_language": "python",
    "key_bindings": null
  }
}
```

### Environment Variables

You can also configure Osram CLI using environment variables:

```bash
export OSRAM_CURRENT_PROVIDER="zai"
export OSRAM_ZAI_API_KEY="your_zhipu_api_key"
export OSRAM_CLAUDE_API_KEY="your_anthropic_api_key"
export OSRAM_GEMINI_API_KEY="your_google_api_key"
export OSRAM_OPENAI_API_KEY="your_openai_api_key"
```

## File Structure

```
osram-cli/
├── setup.py                 # Package setup configuration
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
├── about.md                # Project background and philosophy
├── info.md                 # Technical information
├── LICENSE                 # MIT License
├── osram_cli/              # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Main CLI implementation
│   ├── providers.py        # AI provider implementations
│   └── utils.py            # Utility functions
└── tests/                  # Test files (not included in initial release)
```

## Database Schema

Osram CLI uses SQLite for caching and maintaining conversation history. The database is located at:

- **Linux/macOS**: `~/.osram_cli/osram_cli.db`
- **Windows**: `C:\Users\<YourUsername>\.osram_cli\osram_cli.db`

### Tables

#### Cache Table
```sql
CREATE TABLE cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    timestamp DATETIME,
    expires_at DATETIME
)
```

#### Operations Log Table
```sql
CREATE TABLE operations_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    operation TEXT,
    path TEXT,
    status TEXT,
    timestamp DATETIME,
    details TEXT
)
```

#### Project Analysis Table
```sql
CREATE TABLE project_analysis (
    project_path TEXT PRIMARY KEY,
    analysis_data TEXT,
    last_updated DATETIME
)
```

## API Endpoints

### Zhipu AI
- **Endpoint**: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- **Authentication**: Bearer token
- **Streaming**: Supported

### Anthropic Claude
- **Endpoint**: `https://api.anthropic.com/v1/messages`
- **Authentication**: x-api-key header
- **Streaming**: Supported

### Google Gemini
- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}`
- **Authentication**: API key as query parameter
- **Streaming**: Supported

### OpenAI
- **Endpoint**: `https://api.openai.com/v1/chat/completions`
- **Authentication**: Bearer token
- **Streaming**: Supported

## Troubleshooting

### Common Issues

#### Installation Issues
```bash
# If you encounter permission errors
pip install --user osram-cli

# If you encounter dependency conflicts
pip install --upgrade pip setuptools wheel
```

#### Configuration Issues
```bash
# Reset configuration to defaults
osram reset

# Open configuration file for manual editing
osram config
```

#### API Connection Issues
```bash
# Check your internet connection
ping google.com

# Test API connectivity
curl -X POST https://api.openai.com/v1/chat/completions -H "Authorization: Bearer YOUR_API_KEY" -H "Content-Type: application/json" -d '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"}]}'
```

#### Performance Issues
```bash
# Clear cache
rm -rf ~/.osram_cli/

# Reduce history size
osram config
# Then set "max_history" to a lower value
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export OSRAM_DEBUG=1
osram --help
```

## Contributing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Volgat/osram-cli.git
cd osram-cli

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=osram_cli

# Run specific test file
pytest tests/test_providers.py
```

### Code Formatting

```bash
# Format code
black osram_cli/

# Check for linting errors
flake8 osram_cli/

# Type checking
mypy osram_cli/
```

## Version History

### 1.0.0 (2023-10-XX)
- Initial release
- Support for Zhipu AI, Anthropic Claude, Google Gemini, and OpenAI
- Project analysis features
- File operations
- Interactive chat mode

## Contact Information

**Lead Developer**: Mike Amega
- **GitHub**: https://github.com/Volgat
- **LinkedIn**: https://linkedin.com/in/mike-amega-486329184

For technical support, please open an issue on GitHub.
