import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    config_path = Path.home() / ".osram_config.json"
    
    if not config_path.exists():
        # Create default config
        config = {
            "current_provider": "zai",
            "providers": {
                "zai": {
                    "api_key": "",
                    "model": "GLM-4-Plus",
                    "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                },
                "claude": {
                    "api_key": "",
                    "model": "claude-3-opus-20240229",
                    "endpoint": "https://api.anthropic.com/v1/messages"
                },
                "gemini": {
                    "api_key": "",
                    "model": "gemini-1.5-pro-latest",
                    "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}"
                },
                "openai": {
                    "api_key": "",
                    "model": "gpt-4-turbo",
                    "endpoint": "https://api.openai.com/v1/chat/completions"
                },
                "qwen": {
                    "api_key": "",
                    "model": "Qwen3-Coder",
                    "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                }
            },
            "temperature": 0.7,
            "max_tokens": 4096,
            "save_history": True,
            "history_file": "osram_history.json",
            "trust_current_directory": False,
            "history_per_directory": True,
            "auto_approve_file_operations": False,
            "persistent_analysis": True,
            "enable_plugins": True,
            "enable_git_integration": True,
            "enable_collaboration": False,
            "enable_streaming": True,
            "cache_responses": True,
            "log_operations": True,
            "user_preferences": {
                "theme": "dark",
                "font_size": 14,
                "auto_save": True,
                "confirm_destructive": True,
                "streaming": True,
                "max_history": 1000,
                "preferred_language": "python",
                "key_bindings": None
            }
        }
        save_config(config)
        return config
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Ensure backward compatibility
        if "providers" not in config:
            # Convert old format to new format
            old_api_key = config.get("api_key", "")
            old_model = config.get("model", "GLM-4-Plus")
            
            config["providers"] = {
                "zai": {
                    "api_key": old_api_key,
                    "model": old_model,
                    "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions"
                }
            }
            config["current_provider"] = "zai"
            
            # Add other providers with empty keys
            config["providers"]["claude"] = {
                "api_key": "",
                "model": "claude-3-opus-20240229",
                "endpoint": "https://api.anthropic.com/v1/messages"
            }
            config["providers"]["gemini"] = {
                "api_key": "",
                "model": "gemini-1.5-pro-latest",
                "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}"
            }
            config["providers"]["openai"] = {
                "api_key": "",
                "model": "gpt-4-turbo",
                "endpoint": "https://api.openai.com/v1/chat/completions"
            }
            config["providers"]["qwen"] = {
                "api_key": "",
                "model": "Qwen3-Coder",
                "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            }
            
            save_config(config)
        
        return config
    except Exception as e:
        print(f"Error loading configuration: {str(e)}")
        return {}

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file"""
    config_path = Path.home() / ".osram_config.json"
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving configuration: {str(e)}")
        return False

def setup_database():
    """Setup SQLite database for caching and history"""
    db_path = Path.home() / ".osram_cli" / "osram_cli.db"
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        value TEXT,
        timestamp DATETIME,
        expires_at DATETIME
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS operations_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        operation TEXT,
        path TEXT,
        status TEXT,
        timestamp DATETIME,
        details TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS project_analysis (
        project_path TEXT PRIMARY KEY,
        analysis_data TEXT,
        last_updated DATETIME
    )
    ''')
    
    conn.commit()
    conn.close()