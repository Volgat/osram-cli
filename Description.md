# Osram CLI

![Osram CLI Logo](https://raw.githubusercontent.com/Volgat/osram-cli/main/docs/osram-logo.png)

[![PyPI version](https://badge.fury.io/py/osram-cli.svg)](https://badge.fury.io/py/osram-cli)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI/CD](https://github.com/Volgat/osram-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/Volgat/osram-cli/actions/workflows/ci.yml)

A powerful, adaptable command-line interface that brings the capabilities of multiple AI providers directly to your terminal. Osram CLI seamlessly integrates with leading AI services to enhance your development workflow.

## ✨ Features

### 🔄 Multi-Provider Integration
Switch effortlessly between AI providers with a single command:
- **Zhipu AI** (GLM series)
- **Anthropic Claude** (Claude 3 Opus, Sonnet, Haiku)
- **Google Gemini** (Gemini 1.5 Pro, Flash)
- **OpenAI** (GPT-4 Turbo, GPT-4, GPT-3.5 Turbo)

### 📊 Intelligent Project Analysis
Gain deep insights into your codebase:
- **Structure Analysis**: Visualize project architecture
- **Dependency Mapping**: Understand project dependencies across multiple ecosystems
- **Code Quality Metrics**: Identify potential issues and areas for improvement
- **Automated Reporting**: Generate comprehensive analysis reports

### 💬 Natural Language Interface
Interact with your development environment using natural language:
- Execute file operations with intuitive commands
- Generate code and documentation
- Perform Git operations
- Run shell commands

### 🛠️ Extensible Architecture
Built with developers in mind:
- Modular design for easy extension
- Plugin system for custom functionality
- Clean separation of concerns
- Comprehensive API for integration

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install osram-cli

# Or from source
git clone https://github.com/Volgat/osram-cli.git
cd osram-cli
pip install -e .
```

### Basic Usage

```bash
# Configure your API keys
osram config

# Start a conversation
osram chat "Explain quantum computing in simple terms"

# Enter interactive mode
osram chat

# Switch AI providers
osram switch --provider claude

# Analyze your project
osram analyze .
```

## 📚 Documentation

For detailed documentation, visit our [Wiki](https://github.com/Volgat/osram-cli/wiki).

### Key Commands

| Command | Description |
|---------|-------------|
| `osram chat` | Start a conversation with AI |
| `osram switch` | Switch AI provider or model |
| `osram list` | List available providers |
| `osram analyze` | Analyze project structure |
| `osram config` | Edit configuration |
| `osram report` | Generate project report |

## 🏗️ Architecture

Osram CLI is built with a clean, modular architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Provider Layer  │    │  Analysis Layer  │
│                 │    │                 │    │                 │
│ • Command       │───▶│ • Zhipu AI      │───▶│ • Structure      │
│ • Parsing       │    │ • Claude        │    │ • Dependencies   │
│ • Output        │    │ • Gemini        │    │ • Code Quality   │
│ • History       │    │ • OpenAI        │    │ • Reporting      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                │
                    ┌─────────────────┐
                    │   Utils Layer    │
                    │                 │
                    │ • Config        │
                    │ • Database      │
                    │ • File Ops      │
                    │ • Cache         │
                    └─────────────────┘
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Volgat/osram-cli.git
cd osram-cli

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black osram_cli/
```

## 📝 Roadmap

### Version 1.1 (Planned)
- [ ] Web-based interface
- [ ] Advanced project templates
- [ ] Team collaboration features
- [ ] IDE integrations

### Version 1.2 (Planned)
- [ ] Plugin system
- [ ] Additional AI providers
- [ ] Custom command creation
- [ ] Enhanced code generation

### Version 2.0 (Long-term)
- [ ] AI-powered refactoring
- [ ] Natural language to API conversion
- [ ] Multi-language support
- [ ] Mobile companion app

## 🐛 Reporting Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/Volgat/osram-cli/issues) on GitHub.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all AI providers for their amazing platforms
- The open-source community for inspiration and feedback
- Contributors who help make Osram CLI better every day

## 📧 Contact

**Lead Developer**: Mike Amega
- **GitHub**: [Volgat](https://github.com/Volgat)
- **LinkedIn**: [Mike Amega](https://linkedin.com/in/mike-amega-486329184)

---

<p align="center">
  Made with ❤️ by developer, for developers
</p>
