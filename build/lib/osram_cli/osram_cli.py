#!/usr/bin/env python
import click
import requests
import os
import json
import time
import threading
import sys
import shutil
import glob
import re
import subprocess
import hashlib
import sqlite3
import socket
import platform
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
# Rich imports for UI
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.layout import Layout
from rich.align import Align
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.tree import Tree

# Prompt Toolkit imports for advanced CLI features
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import PathCompleter, WordCompleter
# Import local modules
from .providers import PROVIDERS
from .utils import load_config, save_config, setup_database

# Initialize console
console = Console()

# Logo ASCII for Osram  adaptability
LOGO = """
    ..........................................................................................................
..........................................................................................................
.........................................-+#%%%#=:......:-*%%%#+-.........................................
.......................................-#%%%%%%%%%+:...+%%%%%%%%%#-.......................................
......................................-%%%#-:::+%%%+..+%%%*-::-#%%%-......................................
......................................*%%#:.....+%%#:.#%%+.....:#%%#......................................
......................................*%%%-.....-%%%:.#%%=.....-%%%*......................................
.......................................#%%%%#=..=%%%:.%%%=..=#%%%%#.......................................
........................................=*%%%=..=%%%==%%%+..=%%%*=........................................
.............................................-+#%%%%%%%%%%#*-.............................................
..........................................:#%%%%%%%%%%%%%%%%%%#-..........................................
........................................:*%%%%%*-........:+#%%%%#:........................................
.......................................=%%%%*-....:--=-:....:+%%%%=.......................................
......................................-%%%#-....:*%%%%%%#+....:#%%%=......................................
.....................................:%%%#:....=%%%%*+#%%%*....:#%%%:.....................................
.....................................=%%%=.....#%%#:...+%%%-....=%%%+.....................................
.....................................+%%#=.....+%%%=..:*%%#-....-#%%+.....................................
.....................................=%%%=......+%%%%+#%%%=.....=%%%=.....................................
.....................................:#%%#-......-#%%%%%*:.....:#%%%:.....................................
......................................:%%%%*:...:=#%%%%%#=...:+%%%%:......................................
.......................................:*%%%%%%%%%%%%#%%%%%%%%%%%*:.......................................
.........................................:*#%%%%%#*:...=#%%%%%#*:.........................................
..............................................::...........:..............................................
..................................................-*###*-.................................................
.................................................#%%%%%%%#................................................
................................................+%%*:.:#%%+...............................................
................................................+%%#-:-#%%=...............................................
.................................................*%%%%%%%*................................................
..................................................:+*#*=:.................................................
..........................................................................................................
..........................................................................................................
..........................................................................................................
.................:--:......................................................::::...........................
..............=#%%%%%%*:................................................+#%%%%%#=..*%#......:#%+..........
............:*%#=:..:+%%=...-=+=:..:--.==:.:=++-...:=-.=+=..-++:......-#%#-...-#%+.*%#......:#%+..........
............+%%-......+%%:=#%#*#%*.+%%%%*-#%#*#%%=.+%%%%%%%%%%%%*:....*%%:.........+%#......:#%+..........
............+%%:......+%%-=%%*=-:..+%%:....:---#%*.+%%:.:#%*..-%#-...:*%%..........+%#......:#%+..........
............-#%*.....-#%#..:=+*%%*.+%#...-#%+==#%*.+%%:..#%+..-%#-....=%%+.....=+=.+%#......:*%+..........
.............-%%#*++#%%*:.=##=-*%%:+%#...=%%+-+%%*.+%%:..#%+..-%#-.....=%%#*+*#%#-.+%%+++++-:*%+..........
...............:+#%%*=:....-*%%#=..=#+....-#%#==*+.=**...+*=..:*+:.......-+###+-...=*******-:+*-..........
..........................................................................................................
..........................................................................................................

                       Multi-provider AI Assistant                     ║
   
"""

# Data classes for structured data
@dataclass
class FileOperation:
    operation: str
    path: str
    content: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ProjectAnalysis:
    project_path: str
    files_analyzed: List[str]
    dependencies: Dict[str, List[str]]
    structure: Dict[str, Any]
    quality_metrics: Dict[str, float]
    suggestions: List[str]
    
@dataclass
class UserPreferences:
    theme: str = "dark"
    font_size: int = 14
    auto_save: bool = True
    confirm_destructive: bool = True
    streaming: bool = True
    max_history: int = 1000
    preferred_language: str = "python"
    key_bindings: Dict[str, str] = None

# Enums for better type safety
class OperationType(Enum):
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    RENAME = "rename"
    LIST = "list"
    FIND = "find"
    COMPARE = "compare"

class AnalysisType(Enum):
    STRUCTURE = "structure"
    DEPENDENCIES = "dependencies"
    QUALITY = "quality"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    TESTS = "tests"

# List of available models per provider
AVAILABLE_MODELS = {
    "zai": [
        "GLM-4.5",
        "GLM-4-Plus",
        "GLM-4.5-X",
        "GLM-4.5-Air",
        "GLM-4.5-AirX",
        "GLM-4.5-Flash",
        "GLM-4-32B-0414-128K",
        "ViduQ1-text",
        "viduq1-image",
        "viduq1-start-end",
        "vidu2-image",
        "vidu2-start-end",
        "vidu2-reference",
        "CogVideoX-3",
        "GLM-4.5V",
        "Vidu 2"
    ],
    "claude": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-sonnet-4-20250514",
        "claude-opus-4-1-20250805",
        "claude-opus-4-20250214",
        "claude-3-7-sonnet-20250219",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022"
    ],
    "gemini": [
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash-latest",
        "gemini-1.0-pro-latest",
        "gemini-2.5-flash",
        "gemini-2.5-pro"
    ],
    "openai": [
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-o3-2025-04-16",
        "gpt-5-2025-08-07"
    ],
    "qwen": [
        "Qwen3-Coder",
        "Qwen3-235B-A22B",
        "Qwen3-30B-A3B",
        "Qwen2.5-Max",
        "Qwen3-Coder-Flash",
        "Qwen2.5-Plus",
        "Qwen2.5-Turbo",
        "QVQ-Max",
        "Qwen2.5-Omni-7B",
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "qwen-max-longcontext"
    ]
}

# Global variables
current_directory = os.getcwd()
file_operation_results = {}
analysis_state = {
    "current_task": None,
    "subtasks": [],
    "completed_files": [],
    "errors": [],
    "project_analysis": None
}
user_session = {
    "session_id": str(uuid.uuid4()),
    "start_time": datetime.now(),
    "operations_count": 0,
    "errors_count": 0
}

# Initialize database on import
setup_database()

# Style for prompt_toolkit
style = Style.from_dict({
    'prompt': 'green',
    'bottom-toolbar': 'reverse',
})

# Configuration management functions
def get_current_provider():
    """Get current provider configuration"""
    config = load_config()
    provider_name = config.get("current_provider", "zai")
    return provider_name, config["providers"].get(provider_name, {})

def switch_provider(provider_name=None, model_name=None):
    """Switch to a different provider or model"""
    config = load_config()
    
    if provider_name:
        if provider_name not in config["providers"]:
            console.print(f"[red]Provider '{provider_name}' not configured[/red]")
            return False
        
        config["current_provider"] = provider_name
        console.print(f"[green]Switched to provider: {provider_name}[/green]")
    
    if model_name:
        current_provider = config.get("current_provider", "zai")
        if current_provider not in config["providers"]:
            console.print(f"[red]Current provider '{current_provider}' not configured[/red]")
            return False
        
        # Validate model exists for this provider
        if current_provider in AVAILABLE_MODELS and model_name not in AVAILABLE_MODELS[current_provider]:
            console.print(f"[red]Model '{model_name}' not available for provider '{current_provider}'[/red]")
            console.print(f"[yellow]Available models for {current_provider}: {', '.join(AVAILABLE_MODELS[current_provider])}[/yellow]")
            return False
        
        config["providers"][current_provider]["model"] = model_name
        console.print(f"[green]Switched to model: {model_name}[/green]")
    
    return save_config(config)

def list_providers():
    """List all configured providers"""
    config = load_config()
    current_provider = config.get("current_provider", "zai")
    
    table = Table(title="AI Providers")
    table.add_column("Provider", style="cyan", no_wrap=True)
    table.add_column("Model", style="magenta")
    table.add_column("Status", style="green")
    
    for name, provider in config["providers"].items():
        status = "Current" if name == current_provider else "Available"
        api_key_status = "✓ Configured" if provider.get("api_key") else "✗ Missing API key"
        table.add_row(name, provider.get("model", "Not set"), f"{status} - {api_key_status}")
    
    console.print(table)

# API call function with provider support
def call_api(messages, provider_name=None, model_name=None, temperature=None, max_tokens=None):
    """Call AI API with the specified provider"""
    config = load_config()
    
    # Use specified provider or current provider
    provider_name = provider_name or config.get("current_provider", "zai")
    
    if provider_name not in config["providers"]:
        console.print(f"[red]Provider '{provider_name}' not configured[/red]")
        return None
    
    provider_config = config["providers"][provider_name].copy()
    
    # Override model if specified
    if model_name:
        provider_config["model"] = model_name
    
    # Get provider class
    provider_class = PROVIDERS.get(provider_name)
    if not provider_class:
        console.print(f"[red]Provider '{provider_name}' not implemented[/red]")
        return None
    
    # Create provider instance
    provider = provider_class(provider_config)
    
    # Format endpoint with variables if needed
    endpoint = provider.endpoint.format(
        model=provider.model,
        api_key=provider.api_key
    )
    
    try:
        response = requests.post(
            endpoint,
            headers=provider.prepare_headers(),
            json=provider.prepare_body(messages),
            stream=True
        )
        response.raise_for_status()
        
        # Return the streaming response
        return provider.parse_stream(response)
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]API Error: {str(e)}[/red]")
        return None

# File operation functions with enhanced error handling
def list_directory_contents(path="."):
    """List contents of a directory with details"""
    global file_operation_results
    
    try:
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        if not os.path.isdir(path):
            return f"Error: '{path}' is not a directory."
        
        items = os.listdir(path)
        result = [f"Contents of directory: {path}\n"]
        
        for item in items:
            item_path = os.path.join(path, item)
            try:
                stat = os.stat(item_path)
                if os.path.isdir(item_path):
                    result.append(f"📁 {item}/ (directory)")
                else:
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    result.append(f"📄 {item} ({size} bytes, modified: {modified})")
            except Exception as e:
                result.append(f"❌ {item} (error: {str(e)})")
        
        file_operation_results["list_directory"] = "\n".join(result)
        return file_operation_results["list_directory"]
    except Exception as e:
        error_msg = f"Error listing directory: {str(e)}"
        file_operation_results["list_directory"] = error_msg
        return error_msg

def read_file_content(file_path):
    """Read content of a file with syntax detection"""
    global file_operation_results
    
    try:
        file_path = os.path.normpath(file_path)
        
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        
        if not os.path.isfile(file_path):
            return f"Error: '{file_path}' is not a file."
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_operation_results["read_file"] = f"Content of file: {file_path}\n\n{content}"
        return file_operation_results["read_file"]
    except Exception as e:
        error_msg = f"Error reading file: {str(e)}"
        file_operation_results["read_file"] = error_msg
        return error_msg

def write_file_content(file_path, content):
    """Write content to a file with backup"""
    global file_operation_results
    
    try:
        file_path = os.path.normpath(file_path)
        
        # Create backup if file exists
        if os.path.exists(file_path):
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = f"Successfully wrote to file: {file_path}"
        if os.path.exists(f"{file_path}.bak"):
            result += f"\nBackup saved as: {file_path}.bak"
        
        file_operation_results["write_file"] = result
        return result
    except Exception as e:
        error_msg = f"Error writing file: {str(e)}"
        file_operation_results["write_file"] = error_msg
        return error_msg

def create_directory(dir_path):
    """Create a new directory"""
    global file_operation_results
    
    try:
        dir_path = os.path.normpath(dir_path)
        
        os.makedirs(dir_path, exist_ok=True)
        result = f"Successfully created directory: {dir_path}"
        file_operation_results["create_directory"] = result
        return result
    except Exception as e:
        error_msg = f"Error creating directory: {str(e)}"
        file_operation_results["create_directory"] = error_msg
        return error_msg

def delete_file_or_path(path):
    """Delete a file or directory with confirmation"""
    global file_operation_results
    
    try:
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        # Move to trash instead of permanent delete
        trash_path = Path.home() / ".osram_cli" / "trash"
        trash_path.mkdir(exist_ok=True)
        
        dest_path = trash_path / os.path.basename(path)
        counter = 1
        while dest_path.exists():
            stem = dest_path.stem
            suffix = dest_path.suffix
            dest_path = trash_path / f"{stem}_{counter}{suffix}"
            counter += 1
        
        shutil.move(path, dest_path)
        
        result = f"Moved to trash: {path} -> {dest_path}"
        file_operation_results["delete_file"] = result
        return result
    except Exception as e:
        error_msg = f"Error deleting path: {str(e)}"
        file_operation_results["delete_file"] = error_msg
        return error_msg

def copy_file(source, destination):
    """Copy a file or directory"""
    global file_operation_results
    
    try:
        source = os.path.normpath(source)
        destination = os.path.normpath(destination)
        
        if not os.path.exists(source):
            return f"Error: Source '{source}' does not exist."
        
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        
        result = f"Successfully copied: {source} -> {destination}"
        file_operation_results["copy_file"] = result
        return result
    except Exception as e:
        error_msg = f"Error copying file: {str(e)}"
        file_operation_results["copy_file"] = error_msg
        return error_msg

def move_file(source, destination):
    """Move a file or directory"""
    global file_operation_results
    
    try:
        source = os.path.normpath(source)
        destination = os.path.normpath(destination)
        
        if not os.path.exists(source):
            return f"Error: Source '{source}' does not exist."
        
        shutil.move(source, destination)
        result = f"Successfully moved: {source} -> {destination}"
        file_operation_results["move_file"] = result
        return result
    except Exception as e:
        error_msg = f"Error moving file: {str(e)}"
        file_operation_results["move_file"] = error_msg
        return error_msg

def rename_file(old_path, new_name):
    """Rename a file or directory"""
    global file_operation_results
    
    try:
        old_path = os.path.normpath(old_path)
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        
        if not os.path.exists(old_path):
            return f"Error: Path '{old_path}' does not exist."
        
        os.rename(old_path, new_path)
        result = f"Successfully renamed: {old_path} -> {new_path}"
        file_operation_results["rename_file"] = result
        return result
    except Exception as e:
        error_msg = f"Error renaming file: {str(e)}"
        file_operation_results["rename_file"] = error_msg
        return error_msg

def find_files(pattern, directory="."):
    """Find files matching a pattern"""
    global file_operation_results
    
    try:
        directory = os.path.normpath(directory)
        
        matches = glob.glob(os.path.join(directory, pattern))
        if not matches:
            result = f"No files found matching pattern: {pattern} in directory: {directory}"
        else:
            result = [f"Files matching pattern '{pattern}' in directory '{directory}':"]
            for match in matches:
                if os.path.isdir(match):
                    result.append(f"📁 {match}/")
                else:
                    size = os.path.getsize(match)
                    result.append(f"📄 {match} ({size} bytes)")
        
        file_operation_results["find_files"] = "\n".join(result)
        return file_operation_results["find_files"]
    except Exception as e:
        error_msg = f"Error finding files: {str(e)}"
        file_operation_results["find_files"] = error_msg
        return error_msg

def compare_files(file1, file2):
    """Compare two files"""
    global file_operation_results
    
    try:
        file1 = os.path.normpath(file1)
        file2 = os.path.normpath(file2)
        
        if not os.path.exists(file1):
            return f"Error: File '{file1}' does not exist."
        
        if not os.path.exists(file2):
            return f"Error: File '{file2}' does not exist."
        
        with open(file1, 'r', encoding='utf-8') as f1:
            content1 = f1.readlines()
        
        with open(file2, 'r', encoding='utf-8') as f2:
            content2 = f2.readlines()
        
        diff = []
        for i, (line1, line2) in enumerate(zip(content1, content2)):
            if line1 != line2:
                diff.append(f"Line {i+1}:\n  File1: {line1.strip()}\n  File2: {line2.strip()}")
        
        # Handle different file lengths
        if len(content1) > len(content2):
            for i in range(len(content2), len(content1)):
                diff.append(f"Line {i+1} (only in File1): {content1[i].strip()}")
        elif len(content2) > len(content1):
            for i in range(len(content1), len(content2)):
                diff.append(f"Line {i+1} (only in File2): {content2[i].strip()}")
        
        if not diff:
            result = "Files are identical"
        else:
            result = f"Differences between {file1} and {file2}:\n" + "\n".join(diff)
        
        file_operation_results["compare_files"] = result
        return result
    except Exception as e:
        error_msg = f"Error comparing files: {str(e)}"
        file_operation_results["compare_files"] = error_msg
        return error_msg

def change_directory(path):
    """Change current directory"""
    global current_directory, file_operation_results
    
    try:
        path = os.path.normpath(path)
        
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        if not os.path.isdir(path):
            return f"Error: '{path}' is not a directory."
        
        os.chdir(path)
        current_directory = os.getcwd()
        result = f"Changed directory to: {current_directory}"
        file_operation_results["change_directory"] = result
        return result
    except Exception as e:
        error_msg = f"Error changing directory: {str(e)}"
        file_operation_results["change_directory"] = error_msg
        return error_msg

def get_current_directory():
    """Get current directory"""
    global current_directory, file_operation_results
    
    current_directory = os.getcwd()
    result = f"Current directory: {current_directory}"
    file_operation_results["get_current_directory"] = result
    return result

def execute_shell_command(command):
    """Execute shell command and return output"""
    global file_operation_results
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = f"Command: {command}\n"
        output += f"Return code: {result.returncode}\n"
        
        if result.stdout:
            output += f"Stdout:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"Stderr:\n{result.stderr}\n"
        
        file_operation_results["shell_command"] = output
        return output
    except subprocess.TimeoutExpired:
        error_msg = "Command timed out after 30 seconds"
        file_operation_results["shell_command"] = error_msg
        return error_msg
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        file_operation_results["shell_command"] = error_msg
        return error_msg

def git_operation(operation, *args):
    """Execute git operations"""
    global file_operation_results
    
    try:
        cmd = ["git", operation] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = f"Git operation: git {operation} {' '.join(args)}\n"
        output += f"Return code: {result.returncode}\n"
        
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"Error:\n{result.stderr}\n"
        
        file_operation_results["git_operation"] = output
        return output
    except subprocess.TimeoutExpired:
        error_msg = "Git operation timed out after 60 seconds"
        file_operation_results["git_operation"] = error_msg
        return error_msg
    except Exception as e:
        error_msg = f"Error executing git operation: {str(e)}"
        file_operation_results["git_operation"] = error_msg
        return error_msg

# Advanced analysis functions
def analyze_project_structure(project_path):
    """Analyze project structure"""
    global analysis_state
    
    try:
        project_path = os.path.normpath(project_path)
        
        if not os.path.exists(project_path):
            return f"Error: Project path '{project_path}' does not exist."
        
        if not os.path.isdir(project_path):
            return f"Error: '{project_path}' is not a directory."
        
        # Initialize analysis
        structure = {
            "name": os.path.basename(project_path),
            "path": project_path,
            "files": [],
            "directories": [],
            "file_types": {},
            "total_files": 0,
            "total_size": 0
        }
        
        # Walk through project directory
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git', 'build', 'dist']]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip hidden files
                if file.startswith('.'):
                    continue
                
                try:
                    stat = os.stat(file_path)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    # Update file types count
                    if file_ext:
                        structure["file_types"][file_ext] = structure["file_types"].get(file_ext, 0) + 1
                    else:
                        structure["file_types"]["no_extension"] = structure["file_types"].get("no_extension", 0) + 1
                    
                    # Add file to structure
                    rel_path = os.path.relpath(file_path, project_path)
                    structure["files"].append({
                        "path": rel_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    
                    # Update totals
                    structure["total_files"] += 1
                    structure["total_size"] += stat.st_size
                    
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not analyze file {file_path}: {str(e)}[/yellow]")
        
        # Add directories
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git', 'build', 'dist']]
            
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                rel_path = os.path.relpath(dir_path, project_path)
                
                try:
                    stat = os.stat(dir_path)
                    structure["directories"].append({
                        "path": rel_path,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not analyze directory {dir_path}: {str(e)}[/yellow]")
        
        # Update analysis state
        analysis_state["project_analysis"] = ProjectAnalysis(
            project_path=project_path,
            files_analyzed=structure["files"],
            dependencies={},
            structure=structure,
            quality_metrics={},
            suggestions=[]
        )
        
        return f"Analyzed project structure: {structure['total_files']} files, {len(structure['directories'])} directories"
    
    except Exception as e:
        error_msg = f"Error analyzing project structure: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

def analyze_project_dependencies(project_path):
    """Analyze project dependencies"""
    global analysis_state
    
    try:
        project_path = os.path.normpath(project_path)
        
        if not os.path.exists(project_path):
            return f"Error: Project path '{project_path}' does not exist."
        
        if not os.path.isdir(project_path):
            return f"Error: '{project_path}' is not a directory."
        
        dependencies = {}
        
        # Check for package.json (Node.js)
        package_json_path = os.path.join(project_path, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_json = json.load(f)
                
                if "dependencies" in package_json:
                    dependencies["npm"] = list(package_json["dependencies"].keys())
                
                if "devDependencies" in package_json:
                    if "npm" not in dependencies:
                        dependencies["npm"] = []
                    dependencies["npm"].extend(package_json["devDependencies"].keys())
                
                console.print("[green]Found Node.js dependencies[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse package.json: {str(e)}[/yellow]")
        
        # Check for requirements.txt (Python)
        requirements_paths = [
            os.path.join(project_path, "requirements.txt"),
            os.path.join(project_path, "requirements", "base.txt"),
            os.path.join(project_path, "requirements", "local.txt"),
            os.path.join(project_path, "requirements", "production.txt")
        ]
        
        for req_path in requirements_paths:
            if os.path.exists(req_path):
                try:
                    with open(req_path, 'r') as f:
                        requirements = f.read()
                    
                    # Parse requirements
                    reqs = []
                    for line in requirements.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (remove version specifiers)
                            pkg_name = re.split(r'[<>=!]', line)[0].strip()
                            if pkg_name:
                                reqs.append(pkg_name)
                    
                    if reqs:
                        dependencies["pip"] = reqs
                        console.print(f"[green]Found Python dependencies in {os.path.basename(req_path)}[/green]")
                        break
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not parse {req_path}: {str(e)}[/yellow]")
        
        # Check for pom.xml (Maven/Java)
        pom_path = os.path.join(project_path, "pom.xml")
        if os.path.exists(pom_path):
            try:
                # Simple regex-based extraction (for a real implementation, use an XML parser)
                with open(pom_path, 'r') as f:
                    pom_content = f.read()
                
                # Extract dependencies
                deps = re.findall(r'<dependency>.*?<groupId>(.*?)</groupId>.*?<artifactId>(.*?)</artifactId>.*?</dependency>', pom_content, re.DOTALL)
                if deps:
                    dependencies["maven"] = [f"{group_id}:{artifact_id}" for group_id, artifact_id in deps]
                    console.print("[green]Found Maven dependencies[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse pom.xml: {str(e)}[/yellow]")
        
        # Check for build.gradle or build.gradle.kts (Gradle/Java/Kotlin)
        for gradle_file in ["build.gradle", "build.gradle.kts"]:
            gradle_path = os.path.join(project_path, gradle_file)
            if os.path.exists(gradle_path):
                try:
                    with open(gradle_path, 'r') as f:
                        gradle_content = f.read()
                    
                    # Extract dependencies (simplified)
                    deps = re.findall(r'(?:implementation|api|compile|testImplementation)\s+[\"\']([^\"\']+)[\"\']', gradle_content)
                    if deps:
                        dependencies["gradle"] = deps
                        console.print(f"[green]Found Gradle dependencies in {gradle_file}[/green]")
                        break
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not parse {gradle_file}: {str(e)}[/yellow]")
        
        # Check for Cargo.toml (Rust)
        cargo_path = os.path.join(project_path, "Cargo.toml")
        if os.path.exists(cargo_path):
            try:
                with open(cargo_path, 'r') as f:
                    cargo_content = f.read()
                
                # Extract dependencies
                deps = re.findall(r'^(\w+)\s*=\s*[\"\']([^\"\']+)[\"\']', cargo_content, re.MULTILINE)
                if deps:
                    dependencies["cargo"] = [f"{name}={version}" for name, version in deps]
                    console.print("[green]Found Cargo dependencies[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse Cargo.toml: {str(e)}[/yellow]")
        
        # Check for go.mod (Go)
        go_mod_path = os.path.join(project_path, "go.mod")
        if os.path.exists(go_mod_path):
            try:
                with open(go_mod_path, 'r') as f:
                    go_mod_content = f.read()
                
                # Extract dependencies
                deps = re.findall(r'^\s*(\S+)\s+\S+', go_mod_content, re.MULTILINE)
                if deps:
                    dependencies["go"] = deps
                    console.print("[green]Found Go dependencies[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not parse go.mod: {str(e)}[/yellow]")
        
        # Update analysis state
        if analysis_state.get("project_analysis"):
            analysis_state["project_analysis"].dependencies = dependencies
        else:
            analysis_state["project_analysis"] = ProjectAnalysis(
                project_path=project_path,
                files_analyzed=[],
                dependencies=dependencies,
                structure={},
                quality_metrics={},
                suggestions=[]
            )
        
        return f"Analyzed project dependencies: {sum(len(deps) for deps in dependencies.values())} dependencies found"
    
    except Exception as e:
        error_msg = f"Error analyzing project dependencies: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

def analyze_code_quality(project_path):
    """Analyze code quality metrics"""
    global analysis_state
    
    try:
        project_path = os.path.normpath(project_path)
        
        if not os.path.exists(project_path):
            return f"Error: Project path '{project_path}' does not exist."
        
        if not os.path.isdir(project_path):
            return f"Error: '{project_path}' is not a directory."
        
        # Initialize quality metrics
        quality_metrics = {
            "total_lines": 0,
            "comment_lines": 0,
            "complex_files": [],
            "large_files": [],
            "duplicate_files": [],
            "potential_issues": []
        }
        
        # File hashes for detecting duplicates
        file_hashes = {}
        
        # Walk through project directory
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git', 'build', 'dist']]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip binary files and non-code files
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext not in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala']:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Calculate file hash for duplicate detection
                    file_hash = hashlib.md5(content.encode()).hexdigest()
                    if file_hash in file_hashes:
                        # Found a duplicate
                        duplicate_path = file_hashes[file_hash]
                        quality_metrics["duplicate_files"].append((file_path, duplicate_path))
                    else:
                        file_hashes[file_hash] = file_path
                    
                    # Count lines
                    lines = content.split('\n')
                    line_count = len(lines)
                    quality_metrics["total_lines"] += line_count
                    
                    # Count comment lines
                    comment_count = 0
                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('"""'):
                            comment_count += 1
                    
                    quality_metrics["comment_lines"] += comment_count
                    
                    # Check for large files (> 500 lines)
                    if line_count > 500:
                        quality_metrics["large_files"].append((file_path, line_count))
                    
                    # Check for complex files (simplified heuristic)
                    # Count control structures
                    control_structures = re.findall(r'\b(if|else|for|while|switch|case|try|catch|except|finally)\b', content)
                    if len(control_structures) > 20:
                        quality_metrics["complex_files"].append((file_path, len(control_structures)))
                    
                    # Check for potential issues
                    issues = []
                    
                    # Check for TODO comments
                    todos = re.findall(r'TODO|FIXME|XXX|HACK', content, re.IGNORECASE)
                    if todos:
                        issues.append(f"Found {len(todos)} TODO/FIXME comments")
                    
                    # Check for long lines (> 100 characters)
                    long_lines = [line for line in lines if len(line) > 100]
                    if long_lines:
                        issues.append(f"Found {len(long_lines)} lines longer than 100 characters")
                    
                    # Check for potential security issues (simplified)
                    if re.search(r'password\s*=\s*[\"\'][^\"\']+[\"\']', content, re.IGNORECASE):
                        issues.append("Potential hardcoded password found")
                    
                    if issues:
                        quality_metrics["potential_issues"].append((file_path, issues))
                
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not analyze file {file_path}: {str(e)}[/yellow]")
        
        # Calculate comment ratio
        if quality_metrics["total_lines"] > 0:
            comment_ratio = quality_metrics["comment_lines"] / quality_metrics["total_lines"]
            quality_metrics["comment_ratio"] = comment_ratio
        else:
            quality_metrics["comment_ratio"] = 0
        
        # Update analysis state
        if analysis_state.get("project_analysis"):
            analysis_state["project_analysis"].quality_metrics = quality_metrics
        else:
            analysis_state["project_analysis"] = ProjectAnalysis(
                project_path=project_path,
                files_analyzed=[],
                dependencies={},
                structure={},
                quality_metrics=quality_metrics,
                suggestions=[]
            )
        
        return f"Analyzed code quality: {quality_metrics['total_lines']} lines of code, {quality_metrics['comment_ratio']:.2%} comments"
    
    except Exception as e:
        error_msg = f"Error analyzing code quality: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

def generate_project_report(project_path):
    """Generate a comprehensive project analysis report"""
    global analysis_state
    
    try:
        project_path = os.path.normpath(project_path)
        
        # Run all analyses
        analyze_project_structure(project_path)
        analyze_project_dependencies(project_path)
        analyze_code_quality(project_path)
        
        # Get analysis results
        analysis = analysis_state.get("project_analysis")
        if not analysis:
            return "No analysis data available. Please run analysis first."
        
        # Generate report
        report = []
        report.append(f"# Project Analysis Report: {analysis.project_path}")
        report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Structure section
        report.append("## Project Structure")
        report.append(f"- Total files: {analysis.structure.get('total_files', 0)}")
        report.append(f"- Total directories: {len(analysis.structure.get('directories', []))}")
        report.append(f"- Total size: {analysis.structure.get('total_size', 0) / (1024*1024):.2f} MB")
        
        # File types
        file_types = analysis.structure.get('file_types', {})
        if file_types:
            report.append("")
            report.append("### File Types")
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"- {ext or 'no extension'}: {count} files")
        
        # Dependencies section
        dependencies = analysis.dependencies
        if dependencies:
            report.append("")
            report.append("## Dependencies")
            for dep_type, deps in dependencies.items():
                report.append(f"### {dep_type.capitalize()} ({len(deps)} dependencies)")
                for dep in sorted(deps)[:10]:  # Show top 10
                    report.append(f"- {dep}")
                if len(deps) > 10:
                    report.append(f"- ... and {len(deps) - 10} more")
        
        # Quality metrics section
        quality_metrics = analysis.quality_metrics
        if quality_metrics:
            report.append("")
            report.append("## Code Quality")
            report.append(f"- Total lines of code: {quality_metrics.get('total_lines', 0)}")
            report.append(f"- Comment ratio: {quality_metrics.get('comment_ratio', 0):.2%}")
            
            # Large files
            large_files = quality_metrics.get('large_files', [])
            if large_files:
                report.append("")
                report.append("### Large Files (> 500 lines)")
                for file_path, line_count in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
                    rel_path = os.path.relpath(file_path, project_path)
                    report.append(f"- {rel_path}: {line_count} lines")
            
            # Complex files
            complex_files = quality_metrics.get('complex_files', [])
            if complex_files:
                report.append("")
                report.append("### Complex Files (> 20 control structures)")
                for file_path, complexity in sorted(complex_files, key=lambda x: x[1], reverse=True)[:5]:
                    rel_path = os.path.relpath(file_path, project_path)
                    report.append(f"- {rel_path}: {complexity} control structures")
            
            # Duplicate files
            duplicate_files = quality_metrics.get('duplicate_files', [])
            if duplicate_files:
                report.append("")
                report.append("### Duplicate Files")
                for file1, file2 in duplicate_files[:5]:
                    rel_path1 = os.path.relpath(file1, project_path)
                    rel_path2 = os.path.relpath(file2, project_path)
                    report.append(f"- {rel_path1} is identical to {rel_path2}")
            
            # Potential issues
            potential_issues = quality_metrics.get('potential_issues', [])
            if potential_issues:
                report.append("")
                report.append("### Potential Issues")
                for file_path, issues in potential_issues[:5]:
                    rel_path = os.path.relpath(file_path, project_path)
                    report.append(f"- {rel_path}:")
                    for issue in issues:
                        report.append(f"  - {issue}")
        
        # Suggestions section
        suggestions = analysis.suggestions
        if not suggestions:
            # Generate some basic suggestions based on analysis
            suggestions = []
            
            # Suggest adding documentation if comment ratio is low
            comment_ratio = quality_metrics.get('comment_ratio', 0)
            if comment_ratio < 0.1:
                suggestions.append("Consider adding more comments and documentation to improve code maintainability.")
            
            # Suggest refactoring large files
            large_files = quality_metrics.get('large_files', [])
            if large_files:
                suggestions.append(f"Consider refactoring {len(large_files)} large files to improve maintainability.")
            
            # Suggest handling duplicate files
            duplicate_files = quality_metrics.get('duplicate_files', [])
            if duplicate_files:
                suggestions.append(f"Consider removing or refactoring {len(duplicate_files)} duplicate files.")
            
            # Suggest addressing potential issues
            potential_issues = quality_metrics.get('potential_issues', [])
            if potential_issues:
                suggestions.append(f"Review and address {len(potential_issues)} files with potential issues.")
        
        if suggestions:
            report.append("")
            report.append("## Suggestions")
            for suggestion in suggestions:
                report.append(f"- {suggestion}")
        
        # Write report to file
        report_path = os.path.join(project_path, "osram_analysis_report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        
        return f"Generated project analysis report: {report_path}"
    
    except Exception as e:
        error_msg = f"Error generating project report: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return error_msg

# CLI commands
@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Osram CLI - Multi-provider AI assistant for developers"""
    console.print(LOGO)
    console.print("Welcome to Osram CLI - Your AI-powered development assistant")

@cli.command()
@click.argument('message', required=False)
@click.option('--provider', '-p', help='Specify provider (zai, claude, gemini, openai, qwen)')
@click.option('--model', '-m', help='Specify model')
def chat(message, provider, model):
    """Chat with AI assistant"""
    config = load_config()
    
    # Use current provider if not specified
    if not provider:
        provider = config.get("current_provider", "zai")
    
    # Check if provider is configured
    if provider not in config["providers"]:
        console.print(f"[red]Provider '{provider}' not configured[/red]")
        return
    
    provider_config = config["providers"][provider]
    
    # Check if API key is set
    if not provider_config.get("api_key"):
        console.print(f"[red]API key not configured for provider '{provider}'[/red]")
        console.print(f"[yellow]Run 'osram config' to set up your API key[/yellow]")
        return
    
    # Use current model if not specified
    if not model:
        model = provider_config.get("model")
    
    # Start chat
    if message:
        # Single message mode
        messages = [{"role": "user", "content": message}]
        
        console.print(f"[bold green]You:[/bold green] {message}")
        console.print("[bold blue]AI:[/bold blue] ", end="")
        
        response_stream = call_api(messages, provider, model)
        if response_stream:
            response_text = ""
            for chunk in response_stream:
                console.print(chunk, end="")
                response_text += chunk
            console.print()
        else:
            console.print("[red]Failed to get response from AI[/red]")
    else:
        # Interactive mode
        console.print("[bold green]Interactive chat mode (type 'exit' to quit)[/bold green]")
        
        messages = []
        
        while True:
            try:
                user_input = prompt("\n[You] ", history=FileHistory(os.path.expanduser("~/.osram_history.json")))
                
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                if not user_input.strip():
                    continue
                
                messages.append({"role": "user", "content": user_input})
                
                console.print("[bold blue]AI:[/bold blue] ", end="")
                
                response_stream = call_api(messages, provider, model)
                if response_stream:
                    response_text = ""
                    for chunk in response_stream:
                        console.print(chunk, end="")
                        response_text += chunk
                    console.print()
                    
                    # Add assistant response to history
                    messages.append({"role": "assistant", "content": response_text})
                else:
                    console.print("[red]Failed to get response from AI[/red]")
            
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted by user[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")

@cli.command()
@click.option('--provider', '-p', help='Provider to switch to')
@click.option('--model', '-m', help='Model to switch to')
def switch(provider, model):
    """Switch AI provider or model"""
    if not provider and not model:
        console.print("[yellow]Please specify a provider or model to switch to[/yellow]")
        console.print("Example: osram switch --provider claude")
        console.print("Example: osram switch --model gpt-4")
        return
    
    success = switch_provider(provider, model)
    if success:
        console.print("[green]Switch successful[/green]")
    else:
        console.print("[red]Switch failed[/red]")

@cli.command()
def list():
    """List available providers"""
    list_providers()

@cli.command()
@click.argument('path', default='.')
def analyze(path):
    """Analyze project structure, dependencies, and code quality"""
    console.print(f"[bold]Analyzing project: {path}[/bold]")
    
    # Run all analyses
    structure_result = analyze_project_structure(path)
    console.print(f"[green]{structure_result}[/green]")
    
    dependencies_result = analyze_project_dependencies(path)
    console.print(f"[green]{dependencies_result}[/green]")
    
    quality_result = analyze_code_quality(path)
    console.print(f"[green]{quality_result}[/green]")
    
    # Generate report
    report_result = generate_project_report(path)
    console.print(f"[green]{report_result}[/green]")

@cli.command()
def config():
    """Edit configuration"""
    config_path = Path.home() / ".osram_config.json"
    
    if not config_path.exists():
        console.print("[yellow]Configuration file not found. Creating default configuration...[/yellow]")
        load_config()
    
    console.print(f"[bold]Opening configuration file: {config_path}[/bold]")
    
    # Try to open with default editor
    try:
        if platform.system() == "Windows":
            os.startfile(config_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", str(config_path)])
        else:  # Linux
            subprocess.run(["xdg-open", str(config_path)])
    except Exception as e:
        console.print(f"[red]Could not open configuration file: {str(e)}[/red]")
        console.print(f"[yellow]Please manually edit: {config_path}[/yellow]")

@cli.command()
@click.argument('path', default='.')
def report(path):
    """Generate project analysis report"""
    result = generate_project_report(path)
    console.print(result)

@cli.command()
@click.argument('path', default='.')
def ls(path):
    """List directory contents"""
    result = list_directory_contents(path)
    console.print(result)

@cli.command()
@click.argument('file_path')
def read(file_path):
    """Read file content"""
    result = read_file_content(file_path)
    console.print(result)

@cli.command()
@click.argument('file_path')
@click.argument('content')
def write(file_path, content):
    """Write content to file"""
    result = write_file_content(file_path, content)
    console.print(result)

@cli.command()
@click.argument('dir_path')
def mkdir(dir_path):
    """Create directory"""
    result = create_directory(dir_path)
    console.print(result)

@cli.command()
@click.argument('path')
def rm(path):
    """Delete file or directory"""
    result = delete_file_or_path(path)
    console.print(result)

@cli.command()
@click.argument('source')
@click.argument('destination')
def cp(source, destination):
    """Copy file or directory"""
    result = copy_file(source, destination)
    console.print(result)

@cli.command()
@click.argument('source')
@click.argument('destination')
def mv(source, destination):
    """Move file or directory"""
    result = move_file(source, destination)
    console.print(result)

@cli.command()
@click.argument('old_path')
@click.argument('new_name')
def rename(old_path, new_name):
    """Rename file or directory"""
    result = rename_file(old_path, new_name)
    console.print(result)

@cli.command()
@click.argument('pattern')
@click.option('--directory', '-d', default='.', help='Directory to search in')
def find(pattern, directory):
    """Find files matching pattern"""
    result = find_files(pattern, directory)
    console.print(result)

@cli.command()
@click.argument('file1')
@click.argument('file2')
def diff(file1, file2):
    """Compare two files"""
    result = compare_files(file1, file2)
    console.print(result)

@cli.command()
@click.argument('path')
def cd(path):
    """Change directory"""
    result = change_directory(path)
    console.print(result)

@cli.command()
def pwd():
    """Print current directory"""
    result = get_current_directory()
    console.print(result)

@cli.command()
@click.argument('command')
def shell(command):
    """Execute shell command"""
    result = execute_shell_command(command)
    console.print(result)

@cli.command()
@click.argument('operation')
@click.argument('args', nargs=-1)
def git(operation, args):
    """Execute git operation"""
    result = git_operation(operation, *args)
    console.print(result)

if __name__ == "__main__":
    cli()