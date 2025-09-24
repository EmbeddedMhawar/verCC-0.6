#!/usr/bin/env python3
"""
Database Setup Script
Creates the required tables in Supabase database
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Set up the database schema and tables"""
    
    print("🔧 Setting up VerifiedCC Database Schema...")
    print("=" * 50)
    
    # Get Supabase credentials
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Missing Supabase credentials")
        return False
    
    try:
        # Initialize Supabase client
        print("🔗 Connecting to Supabase...")
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Connected to Supabase")
        
        # Read the SQL schema file
        print("\n📄 Reading database schema...")
        with open('setup_database_schema.sql', 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema (Note: Supabase Python client doesn't support raw SQL)
        # We'll need to use the REST API or recommend manual execution
        print("\n⚠️  IMPORTANT: Manual Setup Required")
        print("=" * 50)
        print("The Supabase Python client doesn't support executing raw SQL.")
        print("Please follow these steps:")
        print()
        print("1. Go to your Supabase dashboard:")
        print(f"   {SUPABASE_URL.replace('/rest/v1', '')}")
        print()
        print("2. Navigate to 'SQL Editor' in the left sidebar")
        print()
        print("3. Create a new query and paste the following SQL:")
        print()
        print("-" * 50)
        print(schema_sql)
        print("-" * 50)
        print()
        print("4. Click 'Run' to execute the schema")
        print()
        print("5. Then run this test script again:")
        print("   python test_database_connection.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_database()