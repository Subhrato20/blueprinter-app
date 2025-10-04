"""Utility functions for the Blueprinter CLI."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def get_config_path() -> Path:
    """Get the path to the CLI configuration file."""
    return Path.home() / ".blueprinter" / "config.json"


def load_config() -> Dict[str, Any]:
    """Load CLI configuration from file."""
    config_path = get_config_path()
    
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        console.print("[yellow]Warning: Invalid configuration file, using defaults[/yellow]")
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save CLI configuration to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def interactive_setup() -> Dict[str, Any]:
    """Interactive setup for CLI configuration."""
    console.print("[bold blue]Blueprinter CLI Setup[/bold blue]")
    console.print("Let's configure your CLI settings.\n")
    
    config = load_config()
    
    # API URL
    current_url = config.get("base_url", "http://localhost:8000")
    api_url = Prompt.ask(
        "API Base URL",
        default=current_url,
        show_default=True
    )
    config["base_url"] = api_url
    
    # API Key (optional)
    current_key = config.get("api_key", "")
    if current_key:
        api_key = Prompt.ask(
            "API Key",
            default="***",
            show_default=True
        )
        if api_key != "***":
            config["api_key"] = api_key
    else:
        api_key = Prompt.ask(
            "API Key (optional)",
            default="",
            show_default=False
        )
        if api_key:
            config["api_key"] = api_key
    
    # Default Project ID
    current_project = config.get("default_project_id", "default-project")
    project_id = Prompt.ask(
        "Default Project ID",
        default=current_project,
        show_default=True
    )
    config["default_project_id"] = project_id
    
    save_config(config)
    console.print("\n[green]✅ Configuration saved successfully![/green]")
    
    return config


def format_plan_output(plan_data: Dict[str, Any], format_type: str = "table") -> str:
    """Format plan data for display."""
    if format_type == "json":
        return json.dumps(plan_data, indent=2)
    
    # Default table format
    output = []
    output.append(f"Title: {plan_data.get('title', 'N/A')}")
    output.append(f"Steps: {len(plan_data.get('steps', []))}")
    output.append(f"Files: {len(plan_data.get('files', []))}")
    output.append(f"Risks: {len(plan_data.get('risks', []))}")
    output.append(f"Tests: {len(plan_data.get('tests', []))}")
    
    return "\n".join(output)


def validate_plan_id(plan_id: str) -> bool:
    """Validate if a plan ID looks valid."""
    # Basic validation - should be a UUID-like string
    return len(plan_id) > 10 and "-" in plan_id


def get_project_id_from_cwd() -> Optional[str]:
    """Try to determine project ID from current working directory."""
    cwd = Path.cwd()
    
    # Look for common project files
    project_files = ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "requirements.txt"]
    
    for file_name in project_files:
        if (cwd / file_name).exists():
            return cwd.name
    
    # Look for git repository
    if (cwd / ".git").exists():
        return cwd.name
    
    return None


def confirm_action(message: str, default: bool = True) -> bool:
    """Ask for user confirmation."""
    return Confirm.ask(message, default=default)


def select_from_list(items: List[str], prompt: str = "Select an item") -> Optional[str]:
    """Let user select from a list of items."""
    if not items:
        return None
    
    if len(items) == 1:
        return items[0]
    
    console.print(f"\n{prompt}:")
    for i, item in enumerate(items, 1):
        console.print(f"  {i}. {item}")
    
    while True:
        try:
            choice = Prompt.ask("Enter your choice (number)", default="1")
            index = int(choice) - 1
            if 0 <= index < len(items):
                return items[index]
            else:
                console.print("[red]Invalid choice. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")


def display_error(error: Exception, context: str = "") -> None:
    """Display an error message with context."""
    if context:
        console.print(f"[red]Error in {context}: {error}[/red]")
    else:
        console.print(f"[red]Error: {error}[/red]")


def display_success(message: str) -> None:
    """Display a success message."""
    console.print(f"[green]✅ {message}[/green]")


def display_warning(message: str) -> None:
    """Display a warning message."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def display_info(message: str) -> None:
    """Display an info message."""
    console.print(f"[blue]ℹ️  {message}[/blue]")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_json_file(file_path: str) -> Dict[str, Any]:
    """Parse a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in {file_path}: {e}")


def write_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """Write data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        raise click.ClickException(f"Failed to write to {file_path}: {e}")


def get_environment_variables() -> Dict[str, str]:
    """Get relevant environment variables for the CLI."""
    env_vars = {}
    
    # Blueprinter specific
    for key in ["BLUEPRINTER_API_URL", "BLUEPRINTER_API_KEY", "BLUEPRINTER_PROJECT_ID"]:
        value = os.getenv(key)
        if value:
            env_vars[key] = value
    
    # Development environment
    for key in ["DEBUG", "LOG_LEVEL", "PYTHONPATH"]:
        value = os.getenv(key)
        if value:
            env_vars[key] = value
    
    return env_vars


def check_dependencies() -> List[str]:
    """Check if required dependencies are available."""
    missing = []
    
    try:
        import httpx
    except ImportError:
        missing.append("httpx")
    
    try:
        import click
    except ImportError:
        missing.append("click")
    
    try:
        import rich
    except ImportError:
        missing.append("rich")
    
    return missing


def get_version() -> str:
    """Get the CLI version."""
    try:
        import pkg_resources
        return pkg_resources.get_distribution("blueprinter-backend").version
    except Exception:
        return "unknown"
