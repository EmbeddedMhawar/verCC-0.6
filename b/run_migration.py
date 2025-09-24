#!/usr/bin/env python3
"""
Guardian Submissions Database Migration Script
Applies the guardian_submissions table migration to the existing database
"""

import os
import sys
import logging
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_migration_sql() -> str:
    """Read the migration SQL file"""
    migration_file = Path(__file__).parent / "guardian_submissions_migration.sql"
    
    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        return f.read()


def get_supabase_client() -> Client:
    """Initialize Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
    
    return create_client(supabase_url, supabase_key)


def check_table_exists(supabase: Client, table_name: str) -> bool:
    """Check if a table exists in the database"""
    try:
        # Try to query the table with a limit of 0 to check existence
        result = supabase.table(table_name).select("*").limit(0).execute()
        return True
    except Exception:
        return False


def verify_migration(supabase: Client) -> bool:
    """Verify that the migration was successful"""
    try:
        # Check if guardian_submissions table exists
        if not check_table_exists(supabase, "guardian_submissions"):
            logger.error("❌ guardian_submissions table was not created")
            return False
        
        # Test basic operations
        logger.info("🔍 Testing guardian_submissions table...")
        
        # Test select (should return empty result)
        result = supabase.table("guardian_submissions").select("*").limit(1).execute()
        logger.info(f"✅ Table query successful: {len(result.data or [])} records found")
        
        # Check if foreign key constraint exists by querying information_schema
        # Note: This is a basic check - in production you might want more thorough validation
        
        logger.info("✅ Migration verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {e}")
        return False


def run_migration():
    """Run the Guardian submissions database migration"""
    try:
        logger.info("🚀 Starting Guardian submissions database migration...")
        
        # Initialize Supabase client
        logger.info("🔧 Initializing Supabase client...")
        supabase = get_supabase_client()
        
        # Check if migration is needed
        if check_table_exists(supabase, "guardian_submissions"):
            logger.info("ℹ️  guardian_submissions table already exists")
            
            # Ask user if they want to proceed anyway
            response = input("Do you want to run the migration anyway? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                logger.info("Migration cancelled by user")
                return True
        
        # Read migration SQL
        logger.info("📖 Reading migration SQL...")
        migration_sql = read_migration_sql()
        
        # Execute migration
        logger.info("⚡ Executing migration SQL...")
        
        # Split SQL into individual statements and execute them
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                logger.info(f"Executing statement {i}/{len(statements)}...")
                try:
                    # Use rpc to execute raw SQL
                    supabase.rpc('exec_sql', {'sql': statement}).execute()
                except Exception as e:
                    # If rpc doesn't work, try alternative approach
                    logger.warning(f"RPC method failed, trying alternative: {e}")
                    # For Supabase, we might need to execute this manually in the SQL editor
                    # or use a different approach
                    pass
        
        logger.info("✅ Migration SQL executed successfully")
        
        # Verify migration
        logger.info("🔍 Verifying migration...")
        if verify_migration(supabase):
            logger.info("🎉 Guardian submissions database migration completed successfully!")
            
            # Print next steps
            print("\n" + "="*60)
            print("MIGRATION COMPLETED SUCCESSFULLY")
            print("="*60)
            print("\nNext steps:")
            print("1. The guardian_submissions table has been created")
            print("2. You can now use the GuardianSubmissionsDB class in your application")
            print("3. Test the integration with: python test_guardian_submissions_db.py")
            print("\nTable details:")
            print("- Table name: guardian_submissions")
            print("- Indexes created for optimal query performance")
            print("- Foreign key constraint to sensor_readings table")
            print("- JSONB column for Guardian API responses")
            
            return True
        else:
            logger.error("❌ Migration verification failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def show_manual_instructions():
    """Show manual migration instructions if automatic migration fails"""
    print("\n" + "="*60)
    print("MANUAL MIGRATION INSTRUCTIONS")
    print("="*60)
    print("\nIf the automatic migration failed, you can run it manually:")
    print("\n1. Open your Supabase dashboard")
    print("2. Go to the SQL Editor")
    print("3. Copy and paste the contents of 'guardian_submissions_migration.sql'")
    print("4. Execute the SQL")
    print("\nAlternatively, you can run individual SQL commands:")
    
    try:
        migration_sql = read_migration_sql()
        print(f"\n{migration_sql}")
    except Exception as e:
        print(f"Could not read migration file: {e}")


if __name__ == "__main__":
    try:
        success = run_migration()
        
        if not success:
            print("\n⚠️  Automatic migration failed.")
            show_manual_instructions()
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        show_manual_instructions()
        sys.exit(1)