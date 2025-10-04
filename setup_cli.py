#!/usr/bin/env python3
"""Setup script for Blueprinter CLI."""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command: str, cwd: Path = None) -> bool:
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error output: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command {command}: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Blueprinter CLI...")
    
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: You're not in a virtual environment.")
        print("   It's recommended to create and activate a virtual environment first:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            sys.exit(0)
    
    # Install the package in development mode
    print("\n📦 Installing Blueprinter backend package...")
    if not run_command("pip install -e .", cwd=backend_dir):
        print("❌ Failed to install the package.")
        sys.exit(1)
    
    # Install CLI dependencies
    print("\n🔧 Installing CLI dependencies...")
    cli_deps = ["click>=8.1.0", "rich>=13.0.0", "httpx>=0.25.0"]
    
    for dep in cli_deps:
        if not run_command(f"pip install '{dep}'"):
            print(f"❌ Failed to install {dep}")
            sys.exit(1)
    
    # Create CLI configuration directory
    config_dir = Path.home() / ".blueprinter"
    config_dir.mkdir(exist_ok=True)
    print(f"📁 Created configuration directory: {config_dir}")
    
    # Test CLI installation
    print("\n🧪 Testing CLI installation...")
    if run_command("blueprinter --help"):
        print("✅ CLI installed successfully!")
    else:
        print("❌ CLI test failed. Please check the installation.")
        sys.exit(1)
    
    # Setup configuration
    print("\n⚙️  Setting up CLI configuration...")
    try:
        from cli.utils import interactive_setup
        interactive_setup()
    except Exception as e:
        print(f"⚠️  Configuration setup failed: {e}")
        print("   You can run 'blueprinter config set' later to configure the CLI.")
    
    print("\n🎉 Blueprinter CLI setup complete!")
    print("\nNext steps:")
    print("1. Start the backend server: python backend/app/main.py")
    print("2. Test the CLI: blueprinter health")
    print("3. Create your first plan: blueprinter plan create 'Build a todo app'")
    print("\nFor more help, run: blueprinter --help")

if __name__ == "__main__":
    main()
