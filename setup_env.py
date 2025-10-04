#!/usr/bin/env python3
"""
Blueprint Snap Environment Setup Script
Dev DNA Edition

This script helps set up the development environment for Blueprint Snap.
"""

import os
import sys
import subprocess
import secrets
import string
from pathlib import Path

def generate_secret(length=32):
    """Generate a secure random secret."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_python_version():
    """Check if Python version is 3.11 or higher."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_node_version():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js is not installed")
    print("Please install Node.js 18 or higher from https://nodejs.org/")
    return False

def check_npm_version():
    """Check if npm is installed."""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ npm is not installed")
    return False

def create_env_file():
    """Create .env file from template."""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return
    
    # Read template
    with open(env_example, 'r') as f:
        content = f.read()
    
    # Generate secrets
    hmac_secret = generate_secret()
    
    # Replace placeholders
    content = content.replace('sk-...', 'sk-your-openai-api-key-here')
    content = content.replace('https://your-project.supabase.co', 'https://your-project.supabase.co')
    content = content.replace('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', 'your-supabase-service-role-key-here')
    content = content.replace('change-me-to-a-secure-random-string', hmac_secret)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Created .env file with generated secrets")
    print("⚠️  Please update the .env file with your actual API keys and Supabase credentials")

def install_backend_dependencies():
    """Install Python dependencies for backend."""
    print("\n📦 Installing backend dependencies...")
    
    backend_dir = Path('backend')
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Install in development mode
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-e', '.'
        ], cwd=backend_dir, check=True)
        print("✅ Backend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install Node.js dependencies for frontend."""
    print("\n📦 Installing frontend dependencies...")
    
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        print("✅ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return False

def install_extension_dependencies():
    """Install Node.js dependencies for VS Code extension."""
    print("\n📦 Installing extension dependencies...")
    
    extension_dir = Path('cursor-extension')
    if not extension_dir.exists():
        print("❌ Extension directory not found")
        return False
    
    try:
        subprocess.run(['npm', 'install'], cwd=extension_dir, check=True)
        print("✅ Extension dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install extension dependencies: {e}")
        return False

def install_root_dependencies():
    """Install root workspace dependencies."""
    print("\n📦 Installing root dependencies...")
    
    try:
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Root dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install root dependencies: {e}")
        return False

def create_supabase_config():
    """Create Supabase configuration files."""
    print("\n🗄️  Setting up Supabase configuration...")
    
    supabase_dir = Path('supabase')
    if not supabase_dir.exists():
        print("❌ Supabase directory not found")
        return False
    
    # Create config.toml if it doesn't exist
    config_file = supabase_dir / 'config.toml'
    if not config_file.exists():
        config_content = """# Supabase configuration
project_id = "your-project-id"
api_url = "https://your-project.supabase.co"
db_url = "postgresql://postgres:[password]@db.your-project.supabase.co:5432/postgres"
studio_url = "https://supabase.com/dashboard/project/your-project-id"
inbucket_url = "https://your-project.supabase.co"
"""
        with open(config_file, 'w') as f:
            f.write(config_content)
        print("✅ Created Supabase config.toml")
    
    print("⚠️  Please update Supabase configuration with your project details")
    return True

def main():
    """Main setup function."""
    print("🚀 Blueprint Snap - Dev DNA Edition Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    check_python_version()
    
    node_ok = check_node_version()
    npm_ok = check_npm_version()
    
    if not node_ok or not npm_ok:
        print("\n❌ Please install Node.js and npm before continuing")
        sys.exit(1)
    
    # Create environment file
    print("\n🔧 Setting up environment...")
    create_env_file()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    
    success = True
    success &= install_root_dependencies()
    success &= install_backend_dependencies()
    success &= install_frontend_dependencies()
    success &= install_extension_dependencies()
    
    if not success:
        print("\n❌ Some dependencies failed to install")
        sys.exit(1)
    
    # Setup Supabase
    create_supabase_config()
    
    # Final instructions
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your actual API keys and Supabase credentials")
    print("2. Set up your Supabase project and run the SQL scripts:")
    print("   - supabase/schema.sql")
    print("   - supabase/policies.sql")
    print("3. Deploy the Supabase Edge Function:")
    print("   - supabase/functions/analyze_repo")
    print("4. Start the development servers:")
    print("   - npm run dev")
    print("\n🔗 Useful commands:")
    print("  - npm run dev          # Start all services")
    print("  - npm run dev:backend  # Start backend only")
    print("  - npm run dev:frontend # Start frontend only")
    print("  - npm run build        # Build for production")
    print("  - npm run package:extension # Package VS Code extension")

if __name__ == '__main__':
    main()
