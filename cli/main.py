#!/usr/bin/env python3
"""Blueprinter CLI - Command-line interface for the Blueprinter development planning tool."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import httpx
import structlog
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)
console = Console()


class BlueprinterClient:
    """Client for interacting with the Blueprinter API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
            timeout=30.0
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy."""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()
    
    async def create_plan(self, idea: str, project_id: str) -> Dict[str, Any]:
        """Create a new development plan."""
        response = await self.client.post(
            "/api/plan",
            json={"idea": idea, "projectId": project_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def get_plan(self, plan_id: str) -> Dict[str, Any]:
        """Get a plan by ID."""
        response = await self.client.get(f"/api/plan/{plan_id}")
        response.raise_for_status()
        return response.json()
    
    async def ask_copilot(self, plan_id: str, node_path: str, selection_text: str, user_question: str) -> Dict[str, Any]:
        """Ask the copilot for suggestions."""
        response = await self.client.post(
            "/api/ask",
            json={
                "planId": plan_id,
                "nodePath": node_path,
                "selectionText": selection_text,
                "userQuestion": user_question
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def create_cursor_link(self, plan_id: str) -> Dict[str, Any]:
        """Create a Cursor deep link for a plan."""
        response = await self.client.post(
            "/api/cursor-link",
            json={"planId": plan_id}
        )
        response.raise_for_status()
        return response.json()
    
    async def apply_patch(self, plan_id: str, patch: List[Dict[str, Any]], message_id: Optional[str] = None) -> Dict[str, Any]:
        """Apply a patch to a plan."""
        response = await self.client.post(
            "/api/plan/patch",
            json={
                "planId": plan_id,
                "patch": patch,
                "messageId": message_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def create_coding_preference(self, category: str, preference_text: str, context: Optional[str] = None, strength: str = "moderate") -> Dict[str, Any]:
        """Create a coding preference."""
        response = await self.client.post(
            "/api/coding-preferences/",
            json={
                "category": category,
                "preference_text": preference_text,
                "context": context,
                "strength": strength
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_coding_preferences(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get coding preferences."""
        params = {}
        if category:
            params["category"] = category
        
        response = await self.client.get("/api/coding-preferences/", params=params)
        response.raise_for_status()
        return response.json()
    
    async def search_similar_preferences(self, query_text: str, similarity_threshold: float = 0.7, max_results: int = 10) -> Dict[str, Any]:
        """Search for similar coding preferences."""
        response = await self.client.post(
            "/api/coding-preferences/search",
            json={
                "query_text": query_text,
                "similarity_threshold": similarity_threshold,
                "max_results": max_results
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_coding_style_summary(self) -> List[Dict[str, Any]]:
        """Get coding style summary."""
        response = await self.client.get("/api/coding-preferences/summary")
        response.raise_for_status()
        return response.json()
    
    async def create_coding_signal(self, signal_type: str, signal_data: Dict[str, Any], confidence_score: float = 1.0) -> Dict[str, Any]:
        """Create a coding signal."""
        response = await self.client.post(
            "/api/coding-preferences/signals",
            json={
                "signal_type": signal_type,
                "signal_data": signal_data,
                "confidence_score": confidence_score
            }
        )
        response.raise_for_status()
        return response.json()


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment."""
    config_file = Path.home() / ".blueprinter" / "config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Default configuration
    return {
        "base_url": os.getenv("BLUEPRINTER_API_URL", "http://localhost:8000"),
        "api_key": os.getenv("BLUEPRINTER_API_KEY"),
        "default_project_id": os.getenv("BLUEPRINTER_PROJECT_ID", "default-project")
    }


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_dir = Path.home() / ".blueprinter"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)


@click.group()
@click.option('--base-url', default=None, help='API base URL')
@click.option('--api-key', default=None, help='API key for authentication')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, base_url, api_key, verbose):
    """Blueprinter CLI - Development planning and coding preferences tool."""
    ctx.ensure_object(dict)
    
    # Load configuration
    config = load_config()
    
    # Override with command line options
    if base_url:
        config["base_url"] = base_url
    if api_key:
        config["api_key"] = api_key
    
    ctx.obj['config'] = config
    
    if verbose:
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.dev.ConsoleRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


@cli.command()
@click.pass_context
async def health(ctx):
    """Check API health status."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking API health...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.health_check()
                progress.update(task, description="✅ API is healthy")
                
                console.print(Panel(
                    f"Status: {result['status']}\nService: {result['service']}",
                    title="API Health Check",
                    border_style="green"
                ))
        except Exception as e:
            progress.update(task, description="❌ API health check failed")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@cli.group()
def plan():
    """Plan management commands."""
    pass


@plan.command()
@click.argument('idea')
@click.option('--project-id', default=None, help='Project ID')
@click.option('--output', '-o', type=click.Path(), help='Output file for plan JSON')
@click.pass_context
async def create(ctx, idea, project_id, output):
    """Create a new development plan from an idea."""
    config = ctx.obj['config']
    project_id = project_id or config.get("default_project_id", "default-project")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating development plan...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.create_plan(idea, project_id)
                progress.update(task, description="✅ Plan created successfully")
                
                plan_id = result["planId"]
                plan_data = result["plan"]
                
                # Display plan summary
                table = Table(title=f"Development Plan: {plan_data['title']}")
                table.add_column("Plan ID", style="cyan")
                table.add_column("Steps", style="green")
                table.add_column("Files", style="blue")
                table.add_column("Risks", style="red")
                
                table.add_row(
                    plan_id,
                    str(len(plan_data['steps'])),
                    str(len(plan_data['files'])),
                    str(len(plan_data['risks']))
                )
                
                console.print(table)
                
                # Save to file if requested
                if output:
                    with open(output, 'w') as f:
                        json.dump(result, f, indent=2)
                    console.print(f"[green]Plan saved to {output}[/green]")
                
                console.print(f"[cyan]Plan ID: {plan_id}[/cyan]")
                
        except Exception as e:
            progress.update(task, description="❌ Failed to create plan")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@plan.command()
@click.argument('plan_id')
@click.option('--output', '-o', type=click.Path(), help='Output file for plan JSON')
@click.pass_context
async def get(ctx, plan_id, output):
    """Get a plan by ID."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching plan...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.get_plan(plan_id)
                progress.update(task, description="✅ Plan fetched successfully")
                
                plan_data = result["plan_json"]
                
                # Display plan details
                console.print(Panel(
                    f"Title: {plan_data['title']}\n"
                    f"Steps: {len(plan_data['steps'])}\n"
                    f"Files: {len(plan_data['files'])}\n"
                    f"Risks: {len(plan_data['risks'])}\n"
                    f"Tests: {len(plan_data['tests'])}",
                    title="Plan Details",
                    border_style="blue"
                ))
                
                # Show steps
                if plan_data['steps']:
                    steps_table = Table(title="Development Steps")
                    steps_table.add_column("Kind", style="cyan")
                    steps_table.add_column("Target", style="green")
                    steps_table.add_column("Summary", style="white")
                    
                    for step in plan_data['steps']:
                        steps_table.add_row(step['kind'], step['target'], step['summary'])
                    
                    console.print(steps_table)
                
                # Show files
                if plan_data['files']:
                    files_table = Table(title="Files to Create")
                    files_table.add_column("Path", style="cyan")
                    files_table.add_column("Content Preview", style="white")
                    
                    for file_data in plan_data['files']:
                        preview = file_data['content'][:100] + "..." if len(file_data['content']) > 100 else file_data['content']
                        files_table.add_row(file_data['path'], preview)
                    
                    console.print(files_table)
                
                # Save to file if requested
                if output:
                    with open(output, 'w') as f:
                        json.dump(result, f, indent=2)
                    console.print(f"[green]Plan saved to {output}[/green]")
                
        except Exception as e:
            progress.update(task, description="❌ Failed to fetch plan")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@cli.group()
def copilot():
    """Copilot interaction commands."""
    pass


@copilot.command()
@click.argument('plan_id')
@click.argument('node_path')
@click.argument('user_question')
@click.option('--selection-text', default="", help='Selected text from the plan')
@click.pass_context
async def ask(ctx, plan_id, node_path, user_question, selection_text):
    """Ask the copilot for suggestions about a plan."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Asking copilot...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.ask_copilot(plan_id, node_path, selection_text, user_question)
                progress.update(task, description="✅ Copilot response received")
                
                console.print(Panel(
                    result["rationale"],
                    title="Copilot Response",
                    border_style="green"
                ))
                
                if result["patch"]:
                    console.print(Panel(
                        JSON(json.dumps(result["patch"], indent=2)),
                        title="Suggested Changes (JSON Patch)",
                        border_style="yellow"
                    ))
                
        except Exception as e:
            progress.update(task, description="❌ Failed to get copilot response")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@cli.group()
def cursor():
    """Cursor IDE integration commands."""
    pass


@cursor.command()
@click.argument('plan_id')
@click.pass_context
async def link(ctx, plan_id):
    """Generate a Cursor deep link for a plan."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating Cursor link...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.create_cursor_link(plan_id)
                progress.update(task, description="✅ Cursor link generated")
                
                link = result["link"]
                console.print(Panel(
                    link,
                    title="Cursor Deep Link",
                    border_style="blue"
                ))
                
                console.print("[yellow]Click the link above to open the plan in Cursor IDE[/yellow]")
                
        except Exception as e:
            progress.update(task, description="❌ Failed to generate Cursor link")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@cli.group()
def preferences():
    """Coding preferences management commands."""
    pass


@preferences.command()
@click.argument('category')
@click.argument('preference_text')
@click.option('--context', help='Additional context for the preference')
@click.option('--strength', type=click.Choice(['weak', 'moderate', 'strong', 'absolute']), default='moderate', help='Preference strength')
@click.pass_context
async def add(ctx, category, preference_text, context, strength):
    """Add a new coding preference."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Adding coding preference...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.create_coding_preference(category, preference_text, context, strength)
                progress.update(task, description="✅ Coding preference added")
                
                console.print(Panel(
                    f"ID: {result['id']}\n"
                    f"Category: {result['category']}\n"
                    f"Strength: {result['strength']}\n"
                    f"Text: {result['preference_text']}",
                    title="Coding Preference Added",
                    border_style="green"
                ))
                
        except Exception as e:
            progress.update(task, description="❌ Failed to add coding preference")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@preferences.command()
@click.option('--category', help='Filter by category')
@click.pass_context
async def list(ctx, category):
    """List coding preferences."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching coding preferences...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.get_coding_preferences(category)
                progress.update(task, description="✅ Coding preferences fetched")
                
                if not result:
                    console.print("[yellow]No coding preferences found[/yellow]")
                    return
                
                table = Table(title="Coding Preferences")
                table.add_column("ID", style="cyan")
                table.add_column("Category", style="green")
                table.add_column("Strength", style="yellow")
                table.add_column("Text", style="white")
                
                for pref in result:
                    table.add_row(
                        pref['id'][:8] + "...",
                        pref['category'],
                        pref['strength'],
                        pref['preference_text'][:50] + "..." if len(pref['preference_text']) > 50 else pref['preference_text']
                    )
                
                console.print(table)
                
        except Exception as e:
            progress.update(task, description="❌ Failed to fetch coding preferences")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@preferences.command()
@click.argument('query_text')
@click.option('--threshold', type=float, default=0.7, help='Similarity threshold (0.0-1.0)')
@click.option('--max-results', type=int, default=10, help='Maximum number of results')
@click.pass_context
async def search(ctx, query_text, threshold, max_results):
    """Search for similar coding preferences."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Searching similar preferences...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.search_similar_preferences(query_text, threshold, max_results)
                progress.update(task, description="✅ Search completed")
                
                preferences = result["preferences"]
                similarities = result["similarities"]
                
                if not preferences:
                    console.print("[yellow]No similar preferences found[/yellow]")
                    return
                
                table = Table(title=f"Similar Preferences for: '{query_text}'")
                table.add_column("Similarity", style="green")
                table.add_column("Category", style="cyan")
                table.add_column("Strength", style="yellow")
                table.add_column("Text", style="white")
                
                for pref, similarity in zip(preferences, similarities):
                    table.add_row(
                        f"{similarity:.2f}",
                        pref['category'],
                        pref['strength'],
                        pref['preference_text'][:50] + "..." if len(pref['preference_text']) > 50 else pref['preference_text']
                    )
                
                console.print(table)
                
        except Exception as e:
            progress.update(task, description="❌ Failed to search preferences")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@preferences.command()
@click.pass_context
async def summary(ctx):
    """Get coding style summary."""
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating coding style summary...", total=None)
        
        try:
            async with BlueprinterClient(config["base_url"], config["api_key"]) as client:
                result = await client.get_coding_style_summary()
                progress.update(task, description="✅ Summary generated")
                
                if not result:
                    console.print("[yellow]No coding style data available[/yellow]")
                    return
                
                table = Table(title="Coding Style Summary")
                table.add_column("Category", style="cyan")
                table.add_column("Preferences", style="green")
                table.add_column("Top Preferences", style="white")
                
                for summary in result:
                    top_prefs = ", ".join(summary['top_preferences'][:3])
                    table.add_row(
                        summary['category'],
                        str(summary['preference_count']),
                        top_prefs
                    )
                
                console.print(table)
                
        except Exception as e:
            progress.update(task, description="❌ Failed to generate summary")
            console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@click.option('--base-url', help='Set API base URL')
@click.option('--api-key', help='Set API key')
@click.option('--project-id', help='Set default project ID')
@click.pass_context
def set(ctx, base_url, api_key, project_id):
    """Set configuration values."""
    config = ctx.obj['config']
    
    if base_url:
        config["base_url"] = base_url
    if api_key:
        config["api_key"] = api_key
    if project_id:
        config["default_project_id"] = project_id
    
    save_config(config)
    console.print("[green]Configuration updated successfully[/green]")


@config.command()
@click.pass_context
def show(ctx):
    """Show current configuration."""
    config = ctx.obj['config']
    
    table = Table(title="Current Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    
    for key, value in config.items():
        # Mask API key for security
        display_value = "***" if key == "api_key" and value else str(value)
        table.add_row(key, display_value)
    
    console.print(table)


def main():
    """Main entry point for the CLI."""
    # Convert async commands to sync for click
    for command in [health, create, get, ask, link, add, list, search, summary]:
        if asyncio.iscoroutinefunction(command.callback):
            original_callback = command.callback
            
            def sync_wrapper(*args, **kwargs):
                return asyncio.run(original_callback(*args, **kwargs))
            
            command.callback = sync_wrapper
    
    cli()


if __name__ == "__main__":
    main()
