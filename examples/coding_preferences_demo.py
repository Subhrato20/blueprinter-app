#!/usr/bin/env python3
"""
Demo script showing how to use the coding preferences vector database system.

This script demonstrates:
1. Adding coding preferences with automatic embedding generation
2. Searching for similar preferences using vector similarity
3. Tracking coding signals (behaviors)
4. Learning patterns from signals
"""

import asyncio
import json
from typing import Dict, Any, List
import httpx
from supabase import create_client, Client

# Configuration
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-anon-key"
API_BASE_URL = "http://localhost:8000/api"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class CodingPreferencesDemo:
    """Demo class for the coding preferences system."""
    
    def __init__(self, api_base_url: str, supabase_client: Client):
        self.api_base_url = api_base_url
        self.supabase = supabase_client
        self.auth_token = None
    
    async def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with Supabase."""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                self.auth_token = response.session.access_token
                print(f"✅ Authenticated as {response.user.email}")
                return True
            else:
                print("❌ Authentication failed")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    async def add_coding_preferences(self) -> None:
        """Add some example coding preferences."""
        print("\n📝 Adding coding preferences...")
        
        preferences = [
            {
                "category": "frontend_framework",
                "preference_text": "Use TypeScript for all frontend code",
                "context": "Always prefer TypeScript over JavaScript for type safety and better IDE support",
                "strength": "strong"
            },
            {
                "category": "backend_pattern",
                "preference_text": "Follow Uncle Bob principles - one class should do one thing",
                "context": "Apply Single Responsibility Principle consistently in all backend code",
                "strength": "strong"
            },
            {
                "category": "code_style",
                "preference_text": "Use meaningful variable names",
                "context": "Avoid abbreviations and use descriptive names that explain intent",
                "strength": "moderate"
            },
            {
                "category": "architecture",
                "preference_text": "Prefer composition over inheritance",
                "context": "Use composition patterns for better flexibility and testability",
                "strength": "moderate"
            },
            {
                "category": "testing",
                "preference_text": "Write tests before implementation (TDD)",
                "context": "Follow Test-Driven Development approach for better code quality",
                "strength": "strong"
            },
            {
                "category": "naming_convention",
                "preference_text": "Use camelCase for variables and functions",
                "context": "Consistent naming convention across the codebase",
                "strength": "moderate"
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for pref in preferences:
                try:
                    response = await client.post(
                        f"{self.api_base_url}/coding-preferences/",
                        headers={
                            "Authorization": f"Bearer {self.auth_token}",
                            "Content-Type": "application/json"
                        },
                        json=pref
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  ✅ Added: {pref['preference_text']}")
                    else:
                        print(f"  ❌ Failed to add: {pref['preference_text']} - {response.text}")
                        
                except Exception as e:
                    print(f"  ❌ Error adding preference: {e}")
    
    async def search_similar_preferences(self, query: str) -> List[Dict[str, Any]]:
        """Search for similar preferences using vector similarity."""
        print(f"\n🔍 Searching for preferences similar to: '{query}'")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base_url}/coding-preferences/search",
                    headers={
                        "Authorization": f"Bearer {self.auth_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query_text": query,
                        "similarity_threshold": 0.7,
                        "max_results": 5
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  Found {len(result['preferences'])} similar preferences:")
                    
                    for i, (pref, similarity) in enumerate(zip(result['preferences'], result['similarities'])):
                        print(f"    {i+1}. {pref['preference_text']} (similarity: {similarity:.3f})")
                    
                    return result['preferences']
                else:
                    print(f"  ❌ Search failed: {response.text}")
                    return []
                    
            except Exception as e:
                print(f"  ❌ Search error: {e}")
                return []
    
    async def track_coding_signals(self) -> None:
        """Track some example coding signals (behaviors)."""
        print("\n📊 Tracking coding signals...")
        
        signals = [
            {
                "signal_type": "file_created",
                "signal_data": {
                    "file_path": "src/components/UserProfile.tsx",
                    "language": "typescript",
                    "timestamp": "2024-12-20T10:00:00Z"
                },
                "confidence_score": 1.0
            },
            {
                "signal_type": "code_pattern_used",
                "signal_data": {
                    "pattern_type": "react_hooks",
                    "context": "Used useState and useEffect hooks",
                    "timestamp": "2024-12-20T10:05:00Z"
                },
                "confidence_score": 0.9
            },
            {
                "signal_type": "refactor_applied",
                "signal_data": {
                    "refactor_type": "extract_method",
                    "trigger": "Long method detected",
                    "timestamp": "2024-12-20T10:10:00Z"
                },
                "confidence_score": 0.8
            },
            {
                "signal_type": "test_written",
                "signal_data": {
                    "test_type": "unit_test",
                    "framework": "jest",
                    "timestamp": "2024-12-20T10:15:00Z"
                },
                "confidence_score": 1.0
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for signal in signals:
                try:
                    response = await client.post(
                        f"{self.api_base_url}/coding-preferences/signals",
                        headers={
                            "Authorization": f"Bearer {self.auth_token}",
                            "Content-Type": "application/json"
                        },
                        json=signal
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"  ✅ Tracked: {signal['signal_type']}")
                    else:
                        print(f"  ❌ Failed to track: {signal['signal_type']} - {response.text}")
                        
                except Exception as e:
                    print(f"  ❌ Error tracking signal: {e}")
    
    async def get_coding_style_summary(self) -> None:
        """Get a summary of coding style preferences."""
        print("\n📈 Getting coding style summary...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_base_url}/coding-preferences/summary",
                    headers={
                        "Authorization": f"Bearer {self.auth_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    summary = response.json()
                    print("  Coding Style Summary:")
                    
                    for item in summary:
                        print(f"    {item['category']}: {item['preference_count']} preferences")
                        for pref in item['top_preferences'][:2]:
                            print(f"      - {pref}")
                else:
                    print(f"  ❌ Failed to get summary: {response.text}")
                    
            except Exception as e:
                print(f"  ❌ Error getting summary: {e}")
    
    async def run_demo(self) -> None:
        """Run the complete demo."""
        print("🚀 Starting Coding Preferences Vector Database Demo")
        print("=" * 60)
        
        # Note: You'll need to replace these with actual credentials
        print("⚠️  Note: Update SUPABASE_URL, SUPABASE_KEY, and credentials in the script")
        
        # Uncomment and update these lines to run the demo:
        # if await self.authenticate("your-email@example.com", "your-password"):
        #     await self.add_coding_preferences()
        #     await self.track_coding_signals()
        #     await self.get_coding_style_summary()
        #     
        #     # Test similarity search
        #     await self.search_similar_preferences("TypeScript frontend development")
        #     await self.search_similar_preferences("clean code principles")
        #     await self.search_similar_preferences("testing methodology")
        
        print("\n✅ Demo completed!")
        print("\nNext steps:")
        print("1. Update the configuration variables at the top of this script")
        print("2. Create a user account in your Supabase project")
        print("3. Uncomment the demo execution code")
        print("4. Run the script to see the vector database in action!")


async def main():
    """Main function to run the demo."""
    demo = CodingPreferencesDemo(API_BASE_URL, supabase)
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())
