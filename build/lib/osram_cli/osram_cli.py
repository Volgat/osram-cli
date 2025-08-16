#!/usr/bin/env python
import os
import json
import re
import hashlib
import subprocess
import shutil
import glob
import uuid
import sqlite3
import platform
import socket
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Generator
from dataclasses import dataclass
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
from .providers import PROVIDERS, call_api, AVAILABLE_MODELS
from .utils import load_config, save_config, setup_database

# Initialize console
console = Console()

# Logo ASCII for Osram
LOGO = """
..........................................................................................................
..........................................................................................................
.........................................-+#%%%#=:......:-*%%%#+-.........................................
.......................................-#%%%%%%%%%+:...+%%%%%%%%%#-.......................................
......................................-%%%#-:::+%%%+..+%%%*-::-#%%%-......................................
......................................*%%#:.....+%%#:.#%%+.....:#%%#......................................
......................................*%%%-.....-%%%:.%%%=.....-%%%*......................................
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
    "errors_count": 0,
    "total_tokens_used": 0,
    "actions_performed": [],
    "trusted_directories": set()
}
token_usage = {
    "total_tokens": 0,
    "operations": []
}
navigation_history = []
history_index = -1

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

# Initialize database on import
setup_database()

# Style for prompt_toolkit
style = Style.from_dict({
    'prompt': 'green',
    'bottom-toolbar': 'reverse',
})

def main():
    """Main function to start the Osram CLI assistant"""
    # Display welcome screen
    display_welcome_screen()
    
    # Start chat session
    start_chat_session()

def display_welcome_screen():
    """Display welcome screen with directory information"""
    console.print(LOGO)
    
    # Get current directory
    current_dir = os.getcwd()
    home_dir = str(Path.home())
    
    # Shorten home directory path for display
    if current_dir.startswith(home_dir):
        display_dir = "~" + current_dir[len(home_dir):]
    else:
        display_dir = current_dir
    
    # Create welcome panel
    welcome_text = f"""
[bold green]Welcome to Osram CLI![/bold green]

Current directory: [bold blue]{display_dir}[/bold blue]

Type your requests in natural language. For example:
- "List the files in this directory"
- "Read the README.md file"
- "Create a new Python file"
- "Analyze this project"

Type [bold]/help[/bold] for help or [bold]/exit[/bold] to quit.
"""
    
    console.print(Panel(welcome_text, title="Osram CLI", border_style="green"))

def start_chat_session():
    """Start the chat session with the AI assistant"""
    # Load configuration
    config = load_config()
    current_provider = config.get("current_provider", "zai")
    
    # Check if API key is configured
    if not config["providers"][current_provider].get("api_key"):
        console.print(f"[yellow]No API key configured for provider '{current_provider}'.[/yellow]")
        if Confirm.ask("[yellow]Would you like to configure it now?[/yellow]"):
            configure_provider()
            config = load_config()
            current_provider = config.get("current_provider", "zai")
        else:
            console.print("[red]Please configure an API key to use the AI assistant.[/red]")
            return
    
    # Initialize chat history
    history_file = Path.home() / ".osram_chat_history"
    history = FileHistory(str(history_file))
    
    # Key bindings
    bindings = KeyBindings()
    
    @bindings.add('c-q')
    def _(event):
        event.app.exit()
    
    # System prompt
    system_prompt = """You are Osram CLI, an AI assistant that helps developers with their tasks. 
    You can perform file operations, run commands, analyze projects, and more.
    When the user asks you to do something, you should:
    
    1. Determine what action needs to be taken
    2. Execute that action using the available tools
    3. Provide a helpful response based on the results
    
    Available tools:
    - List files in a directory
    - Read file contents
    - Write to files
    - Create directories
    - Delete files or directories
    - Copy or move files
    - Find files matching patterns
    - Compare files
    - Change directory
    - Execute system commands
    - Run git operations
    - Analyze projects
    - Execute code
    
    Always show the user what you're doing and provide clear results.
    If you need to execute code, do it safely and show the results.
    
    If the user types "/help", provide information about available commands.
    If the user types "/exit", end the session.
    If the user types "/settings", show current settings.
    If the user types "/tokens", show token usage.
    If the user types "/configure", allow changing provider settings.
    """
    
    # Initialize conversation with system prompt
    messages = [{"role": "system", "content": system_prompt}]
    
    while True:
        try:
            # Get user input with current directory display
            user_input = prompt(
                get_prompt_with_directory(current_provider),
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
                style=style,
                key_bindings=bindings
            )
            
            # Check for special commands
            if user_input.lower() == "/exit":
                console.print("[bold green]Session ended. Goodbye![/bold green]")
                break
            elif user_input.lower() == "/help":
                show_help()
                continue
            elif user_input.lower() == "/settings":
                show_settings()
                continue
            elif user_input.lower() == "/tokens":
                display_token_usage()
                continue
            elif user_input.lower() == "/configure":
                configure_provider()
                continue
            
            # Add user message to conversation
            messages.append({"role": "user", "content": user_input})
            
            # Process user input and get response
            response = process_user_input_with_ai(user_input, messages, current_provider)
            
            # Add AI response to conversation
            messages.append({"role": "assistant", "content": response})
            
            # Display response
            console.print(f"[bold green]AI ({current_provider}):[/bold green]")
            console.print(response)
            
            # Track token usage
            track_tokens("chat", estimate_tokens(user_input + response))
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Use /exit to quit.[/bold yellow]")
        except EOFError:
            console.print("\n[bold green]Session ended. Goodbye![/bold green]")
            break

def show_help():
    """Show help information"""
    help_text = """
[bold]Available Commands:[/bold]

- [bold]/help[/bold] - Show this help message
- [bold]/exit[/bold] - Exit the session
- [bold]/settings[/bold] - Show current settings
- [bold]/tokens[/bold] - Display token usage
- [bold]/configure[/bold] - Configure provider settings

[bold]Examples of what you can ask:[/bold]

- "List the files in this directory"
- "Read the README.md file"
- "Create a new Python file called app.py"
- "Analyze this project"
- "Run the command 'python app.py'"
- "Find all Python files in this directory"
- "Show me the directory structure"
"""
    console.print(Panel(help_text, title="Help", border_style="blue"))

def show_settings():
    """Show current settings"""
    config = load_config()
    current_provider = config.get("current_provider", "zai")
    
    table = Table(title="Current Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Current Provider", current_provider)
    table.add_row("Current Model", config["providers"][current_provider].get("model", "Not set"))
    table.add_row("API Key Configured", "Yes" if config["providers"][current_provider].get("api_key") else "No")
    table.add_row("Theme", config["user_preferences"].get("theme", "dark"))
    table.add_row("Font Size", str(config["user_preferences"].get("font_size", 14)))
    table.add_row("Auto Save", str(config["user_preferences"].get("auto_save", True)))
    table.add_row("Confirm Destructive", str(config["user_preferences"].get("confirm_destructive", True)))
    table.add_row("Streaming", str(config["user_preferences"].get("streaming", True)))
    table.add_row("Max History", str(config["user_preferences"].get("max_history", 1000)))
    
    console.print(table)

def configure_provider():
    """Configure provider settings with connection test"""
    console.print("[bold]Configure Provider Settings[/bold]")
    
    config = load_config()
    
    # List available providers
    console.print("\n[bold]Available providers:[/bold]")
    for i, provider in enumerate(config["providers"].keys(), 1):
        current_marker = " (current)" if provider == config.get("current_provider") else ""
        console.print(f"{i}. {provider}{current_marker}")
    
    # Get provider choice
    provider_choice = Prompt.ask("Select a provider", choices=list(config["providers"].keys()))
    
    # Get API key
    api_key = Prompt.ask(f"Enter API key for {provider_choice}", password=True)
    
    # Update config
    config["providers"][provider_choice]["api_key"] = api_key
    config["current_provider"] = provider_choice
    
    # List available models for the provider
    if provider_choice in AVAILABLE_MODELS:
        console.print(f"\n[bold]Available models for {provider_choice}:[/bold]")
        for model in AVAILABLE_MODELS[provider_choice]:
            console.print(f"- {model}")
        
        model_choice = Prompt.ask("Select a model", choices=AVAILABLE_MODELS[provider_choice])
        config["providers"][provider_choice]["model"] = model_choice
    
    # Save config
    if save_config(config):
        console.print(f"[green]Configuration updated successfully![/green]")
        
        # Test the connection
        console.print("[yellow]Testing connection...[/yellow]")
        test_messages = [{"role": "user", "content": "Hello, this is a test message."}]
        response_stream = call_api(test_messages, provider_name=provider_choice)
        
        if response_stream:
            console.print("[green]Connection test successful![/green]")
        else:
            console.print("[red]Connection test failed. Please check your API key.[/red]")
    else:
        console.print("[red]Failed to update configuration.[/red]")

def get_prompt_with_directory(provider):
    """Get prompt with current directory displayed"""
    current_dir = get_current_directory()
    # Shorten home directory path
    home = str(Path.home())
    if current_dir.startswith(home):
        display_dir = "~" + current_dir[len(home):]
    else:
        display_dir = current_dir
    
    return HTML(f"<ansiblue>You</ansiblue> ({provider}) <ansigreen>{display_dir}</ansigreen>: ")

def process_user_input_with_ai(user_input: str, messages: List[Dict[str, str]], current_provider: str) -> str:
    """Process user input with AI assistance and robust error handling"""
    # First, let the AI analyze the user's request
    analysis_prompt = f"""
    Analyze the user's request and determine what action needs to be taken:
    
    User request: {user_input}
    
    Respond with a JSON object containing:
    {{
        "action_type": "list_files|read_file|write_file|create_directory|delete_file|copy_file|move_file|find_files|compare_files|change_directory|run_command|git_operation|analyze_project|execute_code|none",
        "parameters": {{
            // Parameters specific to the action type
        }},
        "requires_ai_response": true/false,
        "is_destructive": true/false
    }}
    """
    
    # Add analysis prompt to messages
    analysis_messages = messages + [{"role": "system", "content": analysis_prompt}]
    
    # Get AI analysis
    try:
        response_stream = call_api(analysis_messages, provider_name=current_provider)
        
        if response_stream is None:
            return "I'm sorry, I'm having trouble connecting to the AI service. Please check your API key and try again."
        
        analysis_response = ""
        for chunk in response_stream:
            analysis_response += chunk
        
        # If we didn't get a proper response, return an error message
        if not analysis_response.strip():
            return "I'm sorry, I received an empty response from the AI service. Please try again."
        
        # Parse JSON response
        try:
            action_data = json.loads(analysis_response)
            action_type = action_data.get("action_type")
            parameters = action_data.get("parameters", {})
            requires_ai_response = action_data.get("requires_ai_response", True)
            is_destructive = action_data.get("is_destructive", False)
            
            # Ask for confirmation if the action is destructive
            if is_destructive:
                config = load_config()
                if config["user_preferences"].get("confirm_destructive", True):
                    if not Confirm.ask(f"[red]This action may modify or delete files. Are you sure you want to continue?[/red]"):
                        return "Action cancelled by user."
            
            # Execute the action
            result = execute_action(action_type, parameters)
            
            # If AI response is required, get it
            if requires_ai_response:
                response_prompt = f"""
                Based on the user's request and the action result, provide a helpful response:
                
                User request: {user_input}
                Action result: {result}
                """
                
                try:
                    response_messages = messages + [{"role": "system", "content": response_prompt}]
                    response_stream = call_api(response_messages, provider_name=current_provider)
                    
                    if response_stream is None:
                        return f"Action completed: {result}\n\nHowever, I'm having trouble generating a detailed response."
                    
                    ai_response = ""
                    for chunk in response_stream:
                        ai_response += chunk
                    
                    return ai_response
                except Exception as e:
                    return f"Action completed: {result}\n\nHowever, I encountered an error while generating a detailed response: {str(e)}"
            else:
                return f"Action completed: {result}"
                
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to get a regular response
            try:
                response_stream = call_api(messages, provider_name=current_provider)
                
                if response_stream is None:
                    return "I'm sorry, I'm having trouble connecting to the AI service. Please check your API key and try again."
                
                response = ""
                for chunk in response_stream:
                    response += chunk
                
                return response
            except Exception as e:
                return f"I'm sorry, I encountered an error while processing your request: {str(e)}"
                
    except Exception as e:
        return f"I'm sorry, I encountered an error while processing your request: {str(e)}"

def execute_action(action_type: str, parameters: Dict[str, Any]) -> str:
    """Execute the specified action with given parameters"""
    if action_type == "list_files":
        path = parameters.get("path", ".")
        return list_directory_contents_real(path)
    
    elif action_type == "read_file":
        file_path = parameters.get("file_path")
        if file_path:
            return read_file_content_real(file_path)
        else:
            return "Error: No file path specified."
    
    elif action_type == "write_file":
        file_path = parameters.get("file_path")
        content = parameters.get("content", "")
        if file_path:
            return write_file_content(file_path, content)
        else:
            return "Error: No file path specified."
    
    elif action_type == "create_directory":
        dir_path = parameters.get("dir_path")
        if dir_path:
            return create_directory(dir_path)
        else:
            return "Error: No directory path specified."
    
    elif action_type == "delete_file":
        path = parameters.get("path")
        if path:
            return delete_file_or_path(path)
        else:
            return "Error: No path specified."
    
    elif action_type == "copy_file":
        source = parameters.get("source")
        destination = parameters.get("destination")
        if source and destination:
            return copy_file(source, destination)
        else:
            return "Error: Both source and destination paths are required."
    
    elif action_type == "move_file":
        source = parameters.get("source")
        destination = parameters.get("destination")
        if source and destination:
            return move_file(source, destination)
        else:
            return "Error: Both source and destination paths are required."
    
    elif action_type == "find_files":
        pattern = parameters.get("pattern")
        directory = parameters.get("directory", ".")
        if pattern:
            return find_files(pattern, directory)
        else:
            return "Error: No search pattern specified."
    
    elif action_type == "compare_files":
        file1 = parameters.get("file1")
        file2 = parameters.get("file2")
        if file1 and file2:
            return compare_files(file1, file2)
        else:
            return "Error: Both file paths are required."
    
    elif action_type == "change_directory":
        path = parameters.get("path")
        if path:
            return advanced_change_directory(path)
        else:
            return "Error: No directory path specified."
    
    elif action_type == "run_command":
        command = parameters.get("command")
        if command:
            return execute_system_command(command)
        else:
            return "Error: No command specified."
    
    elif action_type == "git_operation":
        operation = parameters.get("operation")
        args = parameters.get("args", [])
        if operation:
            return git_operation(operation, *args)
        else:
            return "Error: No git operation specified."
    
    elif action_type == "analyze_project":
        return analyze_project_real()
    
    elif action_type == "execute_code":
        code = parameters.get("code")
        if code:
            return execute_code(code)
        else:
            return "Error: No code specified."
    
    else:
        return "Error: Unknown action type."

# File Operations Functions
def list_directory_contents_real(path="."):
    """List real directory contents"""
    try:
        path = os.path.abspath(path)
        
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
                    result.append(f"📁 {item}/")
                else:
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    result.append(f"📄 {item} ({size} bytes, modified: {modified})")
            except Exception as e:
                result.append(f"❌ {item} (error: {str(e)})")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def read_file_content_real(file_path):
    """Read file content"""
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        
        if not os.path.isfile(file_path):
            return f"Error: '{file_path}' is not a file."
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"Content of file: {file_path}\n\n{content}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file_content(file_path, content, auto_confirm=False):
    """Write content to a file"""
    try:
        file_path = os.path.abspath(file_path)
        
        # Ask for confirmation if not auto-confirm
        if not auto_confirm and not Confirm.ask(f"[yellow]Are you sure you want to write to {file_path}?[/yellow]"):
            return "Operation cancelled by user."
        
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
        
        return result
    except Exception as e:
        return f"Error writing file: {str(e)}"

def create_directory(dir_path, auto_confirm=False):
    """Create a new directory"""
    try:
        dir_path = os.path.abspath(dir_path)
        
        # Ask for confirmation if not auto-confirm
        if not auto_confirm and not Confirm.ask(f"[yellow]Are you sure you want to create directory {dir_path}?[/yellow]"):
            return "Operation cancelled by user."
        
        os.makedirs(dir_path, exist_ok=True)
        return f"Successfully created directory: {dir_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

def delete_file_or_path(path, auto_confirm=False):
    """Delete a file or directory"""
    try:
        path = os.path.abspath(path)
        
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        # Ask for confirmation if not auto-confirm
        if not auto_confirm and not Confirm.ask(f"[red]Are you sure you want to delete {path}? This action cannot be undone.[/red]"):
            return "Operation cancelled by user."
        
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
        
        return f"Moved to trash: {path} -> {dest_path}"
    except Exception as e:
        return f"Error deleting path: {str(e)}"

def copy_file(source, destination, auto_confirm=False):
    """Copy a file or directory"""
    try:
        source = os.path.abspath(source)
        destination = os.path.abspath(destination)
        
        if not os.path.exists(source):
            return f"Error: Source '{source}' does not exist."
        
        # Ask for confirmation if not auto-confirm
        if not auto_confirm and not Confirm.ask(f"[yellow]Are you sure you want to copy {source} to {destination}?[/yellow]"):
            return "Operation cancelled by user."
        
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        
        return f"Successfully copied: {source} -> {destination}"
    except Exception as e:
        return f"Error copying file: {str(e)}"

def move_file(source, destination, auto_confirm=False):
    """Move a file or directory"""
    try:
        source = os.path.abspath(source)
        destination = os.path.abspath(destination)
        
        if not os.path.exists(source):
            return f"Error: Source '{source}' does not exist."
        
        # Ask for confirmation if not auto-confirm
        if not auto_confirm and not Confirm.ask(f"[yellow]Are you sure you want to move {source} to {destination}?[/yellow]"):
            return "Operation cancelled by user."
        
        shutil.move(source, destination)
        return f"Successfully moved: {source} -> {destination}"
    except Exception as e:
        return f"Error moving file: {str(e)}"

def find_files(pattern, directory="."):
    """Find files matching a pattern"""
    try:
        directory = os.path.abspath(directory)
        
        matches = glob.glob(os.path.join(directory, pattern))
        if not matches:
            return f"No files found matching pattern: {pattern} in directory: {directory}"
        
        result = [f"Files matching pattern '{pattern}' in directory '{directory}':"]
        for match in matches:
            if os.path.isdir(match):
                result.append(f"📁 {match}/")
            else:
                size = os.path.getsize(match)
                result.append(f"📄 {match} ({size} bytes)")
        
        return "\n".join(result)
    except Exception as e:
        return f"Error finding files: {str(e)}"

def compare_files(file1, file2):
    """Compare two files"""
    try:
        file1 = os.path.abspath(file1)
        file2 = os.path.abspath(file2)
        
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
            return "Files are identical"
        
        return f"Differences between {file1} and {file2}:\n" + "\n".join(diff)
    except Exception as e:
        return f"Error comparing files: {str(e)}"

def advanced_change_directory(path):
    """Advanced directory change with history"""
    global current_directory, navigation_history, history_index
    
    path = os.path.abspath(path)
    
    if not os.path.exists(path):
        return f"Error: Path '{path}' does not exist."
    
    if not os.path.isdir(path):
        return f"Error: '{path}' is not a directory."
    
    # Update history
    if history_index < len(navigation_history) - 1:
        navigation_history = navigation_history[:history_index + 1]
    
    navigation_history.append(current_directory)
    history_index = len(navigation_history)
    
    os.chdir(path)
    current_directory = os.getcwd()
    
    return f"Changed directory to: {current_directory}"

def change_directory(path):
    """Change current directory"""
    global current_directory
    
    try:
        path = os.path.abspath(path)
        
        if not os.path.exists(path):
            return f"Error: Path '{path}' does not exist."
        
        if not os.path.isdir(path):
            return f"Error: '{path}' is not a directory."
        
        os.chdir(path)
        current_directory = os.getcwd()
        return f"Changed directory to: {current_directory}"
    except Exception as e:
        return f"Error changing directory: {str(e)}"

def get_current_directory():
    """Get current directory"""
    global current_directory
    current_directory = os.getcwd()
    return f"Current directory: {current_directory}"

# System Operations Functions
def execute_system_command(command, timeout=30):
    """Execute system command and return output"""
    try:
        # Log the command
        console.print(f"[dim]Executing: {command}[/dim]")
        
        # Execute the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Prepare the output
        output = f"Command: {command}\n"
        output += f"Return code: {result.returncode}\n"
        
        if result.stdout:
            output += f"Stdout:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"Stderr:\n{result.stderr}\n"
        
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def git_operation(operation, *args):
    """Execute git operations"""
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
        
        return output
    except subprocess.TimeoutExpired:
        return "Git operation timed out after 60 seconds"
    except Exception as e:
        return f"Error executing git operation: {str(e)}"

# Project Analysis Functions
def analyze_project_real():
    """Analyze the current directory project with real file access"""
    current_dir = os.getcwd()
    
    # Step 1: List directory contents
    dir_contents = list_directory_contents_real(current_dir)
    
    # Step 2: Identify project type and key files
    project_files = ['package.json', 'requirements.txt', 'setup.py', 'pom.xml', 'Cargo.toml', 'go.mod', '.git']
    found_files = []
    
    for file in project_files:
        if os.path.exists(os.path.join(current_dir, file)):
            found_files.append(file)
    
    # Step 3: Read key files if they exist
    file_contents = {}
    for file in found_files:
        file_path = os.path.join(current_dir, file)
        file_contents[file] = read_file_content_real(file_path)
    
    # Step 4: Analyze source code files
    source_files = []
    for root, dirs, files in os.walk(current_dir):
        # Skip hidden directories and common build directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git', 'build', 'dist']]
        
        for file in files:
            file_path = os.path.join(root, file)
            # Check for common source file extensions
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', 'rs', '.rb', '.php', '.swift', '.kt', '.scala', '.html', '.css', '.json', '.xml', '.yaml', '.yml')):
                source_files.append(file_path)
    
    # Step 5: Read a sample of source files for analysis
    sample_files = source_files[:5]  # Limit to first 5 files for brevity
    sample_contents = {}
    for file_path in sample_files:
        sample_contents[file_path] = read_file_content_real(file_path)
    
    # Update analysis state
    analysis_state["current_task"] = "Project analysis completed"
    analysis_state["completed_files"] = found_files + sample_files
    
    return f"Project analysis completed. Found {len(found_files)} project files and {len(source_files)} source files."

def execute_code(code):
    """Execute code and return the result"""
    try:
        # For now, we'll just return a placeholder
        # In a real implementation, this would execute the code in a safe environment
        return f"Code execution result for:\n```\n{code}\n```\n\nThis is a placeholder. Code execution would be implemented in a secure environment."
    except Exception as e:
        return f"Error executing code: {str(e)}"

# Token Tracking Functions
def track_tokens(operation_name: str, tokens_used: int):
    """Track token usage for each operation"""
    global token_usage
    
    token_usage["total_tokens"] += tokens_used
    token_usage["operations"].append({
        "operation": operation_name,
        "tokens": tokens_used,
        "timestamp": datetime.now().isoformat()
    })
    
    # Display token usage dynamically
    console.print(f"[dim]Tokens used - {operation_name}: {tokens_used} (Total: {token_usage['total_tokens']})[/dim]")

def display_token_usage():
    """Display a detailed token usage report"""
    table = Table(title="Token Usage")
    table.add_column("Operation", style="cyan")
    table.add_column("Tokens", style="magenta")
    table.add_column("Timestamp", style="green")
    
    for op in token_usage["operations"]:
        table.add_row(op["operation"], str(op["tokens"]), op["timestamp"])
    
    table.add_row("TOTAL", str(token_usage["total_tokens"]), "")
    console.print(table)

def estimate_tokens(text):
    """Estimate the number of tokens in a text"""
    return len(text) // 4 + (1 if len(text) % 4 > 0 else 0)