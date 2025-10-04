#!/usr/bin/env python3
"""Demo script showing Blueprinter CLI usage."""

import asyncio
import json
import time
from pathlib import Path

# Add the CLI module to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.main import BlueprinterClient


async def demo_cli_usage():
    """Demonstrate CLI functionality."""
    print("🚀 Blueprinter CLI Demo")
    print("=" * 50)
    
    # Initialize client
    async with BlueprinterClient("http://localhost:8000") as client:
        
        # 1. Health Check
        print("\n1. Checking API health...")
        try:
            health = await client.health_check()
            print(f"✅ API Status: {health['status']}")
        except Exception as e:
            print(f"❌ API not available: {e}")
            return
        
        # 2. Create a Plan
        print("\n2. Creating a development plan...")
        try:
            plan_result = await client.create_plan(
                "Build a simple blog with user authentication",
                "demo-project"
            )
            plan_id = plan_result["planId"]
            plan_data = plan_result["plan"]
            print(f"✅ Plan created with ID: {plan_id}")
            print(f"   Title: {plan_data['title']}")
            print(f"   Steps: {len(plan_data['steps'])}")
            print(f"   Files: {len(plan_data['files'])}")
        except Exception as e:
            print(f"❌ Failed to create plan: {e}")
            return
        
        # 3. Get Plan Details
        print("\n3. Retrieving plan details...")
        try:
            plan_details = await client.get_plan(plan_id)
            print(f"✅ Plan retrieved successfully")
            print(f"   Project ID: {plan_details.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"❌ Failed to get plan: {e}")
        
        # 4. Ask Copilot
        print("\n4. Asking copilot for suggestions...")
        try:
            copilot_response = await client.ask_copilot(
                plan_id=plan_id,
                node_path="/steps/0",
                selection_text="user authentication",
                user_question="How can I make this more secure?"
            )
            print(f"✅ Copilot response received")
            print(f"   Rationale: {copilot_response['rationale'][:100]}...")
            print(f"   Patch operations: {len(copilot_response['patch'])}")
        except Exception as e:
            print(f"❌ Failed to get copilot response: {e}")
        
        # 5. Create Cursor Link
        print("\n5. Generating Cursor deep link...")
        try:
            cursor_link = await client.create_cursor_link(plan_id)
            print(f"✅ Cursor link generated")
            print(f"   Link: {cursor_link['link'][:50]}...")
        except Exception as e:
            print(f"❌ Failed to generate Cursor link: {e}")
        
        # 6. Add Coding Preferences
        print("\n6. Adding coding preferences...")
        try:
            preference = await client.create_coding_preference(
                category="frontend_framework",
                preference_text="Use React with TypeScript for all frontend projects",
                context="Modern web applications",
                strength="strong"
            )
            print(f"✅ Coding preference added")
            print(f"   ID: {preference['id']}")
            print(f"   Category: {preference['category']}")
        except Exception as e:
            print(f"❌ Failed to add coding preference: {e}")
        
        # 7. List Preferences
        print("\n7. Listing coding preferences...")
        try:
            preferences = await client.get_coding_preferences()
            print(f"✅ Found {len(preferences)} coding preferences")
            for pref in preferences[:3]:  # Show first 3
                print(f"   - {pref['category']}: {pref['preference_text'][:50]}...")
        except Exception as e:
            print(f"❌ Failed to list preferences: {e}")
        
        # 8. Search Similar Preferences
        print("\n8. Searching for similar preferences...")
        try:
            search_results = await client.search_similar_preferences(
                "React TypeScript components",
                similarity_threshold=0.5,
                max_results=3
            )
            print(f"✅ Found {len(search_results['preferences'])} similar preferences")
            for pref, similarity in zip(search_results['preferences'], search_results['similarities']):
                print(f"   - Similarity: {similarity:.2f} - {pref['preference_text'][:50]}...")
        except Exception as e:
            print(f"❌ Failed to search preferences: {e}")
        
        # 9. Get Style Summary
        print("\n9. Getting coding style summary...")
        try:
            summary = await client.get_coding_style_summary()
            print(f"✅ Style summary generated")
            for item in summary:
                print(f"   - {item['category']}: {item['preference_count']} preferences")
        except Exception as e:
            print(f"❌ Failed to get style summary: {e}")
        
        # 10. Create Coding Signal
        print("\n10. Creating coding signal...")
        try:
            signal = await client.create_coding_signal(
                signal_type="file_created",
                signal_data={
                    "file_path": "src/components/Button.tsx",
                    "file_type": "typescript",
                    "lines_of_code": 45
                },
                confidence_score=0.9
            )
            print(f"✅ Coding signal created")
            print(f"   ID: {signal['id']}")
        except Exception as e:
            print(f"❌ Failed to create coding signal: {e}")
    
    print("\n🎉 Demo completed!")
    print("\nTo use the CLI interactively, run:")
    print("  blueprinter --help")
    print("  blueprinter health")
    print("  blueprinter plan create 'Your idea here'")


def demo_configuration():
    """Demonstrate configuration management."""
    print("\n⚙️  Configuration Demo")
    print("=" * 30)
    
    from cli.utils import load_config, save_config, get_config_path
    
    # Show current config
    config = load_config()
    print(f"Current config file: {get_config_path()}")
    print(f"Current config: {json.dumps(config, indent=2)}")
    
    # Demo config update
    config["demo_setting"] = "demo_value"
    save_config(config)
    print("✅ Configuration updated")
    
    # Reload and show
    new_config = load_config()
    print(f"Updated config: {json.dumps(new_config, indent=2)}")


if __name__ == "__main__":
    print("Blueprinter CLI Demo Script")
    print("Make sure the backend server is running on http://localhost:8000")
    print("You can start it with: cd backend && python app/main.py")
    
    response = input("\nStart the demo? (y/N): ")
    if response.lower() == 'y':
        # Run configuration demo
        demo_configuration()
        
        # Run async demo
        asyncio.run(demo_cli_usage())
    else:
        print("Demo cancelled.")
