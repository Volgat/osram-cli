# Osram CLI

[![PyPI version](https://badge.fury.io/py/osram-cli.svg)](https://badge.fury.io/py/osram-cli)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Osram CLI is a multi-provider AI assistant for developers, inspired by the Adinkra symbol of adaptability. It provides a unified interface to interact with multiple AI providers including Zhipu AI, Anthropic Claude, Google Gemini, and OpenAI.

## Features

- **Multi-provider Support**: Seamlessly switch between different AI providers
- **Project Analysis**: Analyze project structure, dependencies, and code quality
- **File Operations**: Perform file system operations with natural language commands
- **Interactive Chat**: Engage in conversations with AI assistants
- **Git Integration**: Execute Git operations directly from the CLI
- **Extensible Architecture**: Easy to add new providers and features

## Installation

### From PyPI (Recommended)

```bash
pip install osram-cli
```

### From Source

```bash
git clone https://github.com/Volgat/osram-cli.git
cd osram-cli
pip install -e .
```

## Quick Start

After installation, you can use the `osram` command from anywhere:

```bash
# Configure your API keys
osram config

# List available providers
osram list

# Start a chat session
osram chat "Hello, how are you?"

# Enter interactive mode
osram chat

# Switch to a different provider
osram switch --provider claude

# Analyze your current project
osram analyze .
```

## Configuration

The configuration file is located at `~/.osram_config.json`. You can edit it directly or use the `osram config` command to open it in your default editor.

### Supported Providers

- **Zhipu AI (zai)**: GLM series models
- **Anthropic Claude (claude)**: Claude 3 Opus, Sonnet, and Haiku
- **Google Gemini (gemini)**: Gemini 1.5 Pro and Flash
- **OpenAI (openai)**: GPT-4 Turbo, GPT-4, and GPT-3.5 Turbo

## Commands

| Command | Description |
|---------|-------------|
| `osram chat` | Start a conversation with AI |
| `osram switch` | Switch AI provider or model |
| `osram list` | List available providers and models |
| `osram config` | Edit configuration file |
| `osram analyze` | Analyze project structure and generate report |
| `osram structure` | Analyze project structure |
| `osram dependencies` | Analyze project dependencies |
| `osram quality` | Analyze code quality metrics |
| `osram report` | Generate comprehensive project analysis report |
| `osram ls` | List directory contents |
| `osram read` | Read file content |
| `osram write` | Write content to file |
| `osram mkdir` | Create a new directory |
| `osram rm` | Delete a file or directory |
| `osram cp` | Copy a file or directory |
| `osram mv` | Move a file or directory |
| `osram rename` | Rename a file or directory |
| `osram find` | Find files matching a pattern |
| `osram diff` | Compare two files |
| `osram cd` | Change current directory |
| `osram pwd` | Show current directory |
| `osram shell` | Execute shell command |
| `osram git` | Execute git operation |
| `osram reset` | Reset configuration to defaults |

## Examples

### Chat with AI

```bash
# Single message
osram chat "Explain quantum computing in simple terms"

# Interactive mode
osram chat
```

### Project Analysis

```bash
# Analyze current directory
osram analyze .

# Analyze specific directory
osram analyze /path/to/project

# Generate detailed report
osram report /path/to/project
```

### File Operations

```bash
# List files
osram ls

# Read a file
osram read README.md

# Create a new file
osram write new-file.py "#!/usr/bin/env python\nprint('Hello, World!')"

# Find Python files
osram find "*.py"
```

### Provider Management

```bash
# List all providers
osram list

# Switch to Claude
osram switch --provider claude

# Switch to a specific model
osram switch --model gpt-4-turbo
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Lead Developer**: Mike Amega
- **GitHub**: https://github.com/Volgat
- **LinkedIn**: https://linkedin.com/in/mike-amega-486329184

## Acknowledgments
- The open-source community for their valuable contributions
