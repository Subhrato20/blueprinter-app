#!/usr/bin/env python3
"""
Environment setup script for Blueprinter
Creates .env file with OpenAI configuration
"""

import os

def create_env_file():
    """Create .env file with OpenAI configuration"""
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5

# Supabase Configuration (optional)
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
"""
    
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created {env_path}")
        print("📝 Please edit the file and add your OpenAI API key")
    else:
        print(f"⚠️  {env_path} already exists")
    
    return env_path

def main():
    print("🚀 Setting up Blueprinter environment...")
    env_path = create_env_file()
    
    print("\n📋 Next steps:")
    print("1. Edit the .env file and add your OpenAI API key")
    print("2. Restart the backend server")
    print("3. Test the integration")
    
    print(f"\n🔧 Environment file: {env_path}")

if __name__ == "__main__":
    main()
