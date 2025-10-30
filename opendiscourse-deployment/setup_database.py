#!/usr/bin/env python3
"""
Database Setup Script
Sets up the database by running migrations and testing connectivity.
"""

import os
import sys
import psycopg2
from psycopg2 import OperationalError, sql
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv('database_config.env')

def run_migration():
    """Run the consolidated database migration."""
    
    # Read the migration SQL file
    try:
        with open('consolidated_database_migration.sql', 'r') as f:
            migration_sql = f.read()
    except FileNotFoundError:
        print("❌ Migration file 'consolidated_database_migration.sql' not found!")
        return False
    
    # Database connection parameters
    db_config = {
        'host': os.getenv('DB_HOST', '172.28.82.205'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'opendiscourse'),
        'user': os.getenv('DB_USER', 'opendiscourse'),
        'password': os.getenv('DB_PASSWORD', 'opendiscourse123')
    }
    
    print("Running database migration...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_config)
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Execute the migration in a transaction
        cursor.execute(migration_sql)
        
        # Commit the transaction
        conn.commit()
        
        print("✅ Database migration completed successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def test_database_connection():
    """Test database connectivity and schema."""
    
    # Database connection parameters
    db_config = {
        'host': os.getenv('DB_HOST', '172.28.82.205'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'opendiscourse'),
        'user': os.getenv('DB_USER', 'opendiscourse'),
        'password': os.getenv('DB_PASSWORD', 'opendiscourse123')
    }
    
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    print(f"Host: {db_config['host']}")
    print(f"Port: {db_config['port']}")
    print(f"Database: {db_config['database']}")
    print(f"User: {db_config['user']}")
    print("-" * 60)
    
    try:
        # Test connection
        print("Testing database connection...")
        conn = psycopg2.connect(**db_config)
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Check for required tables
        required_tables = [
            'opencivicdata_jurisdiction',
            'opencivicdata_person',
            'opencivicdata_bill',
            'federal_members',
            'federal_bills',
            'federal_committees',
            'govinfo_bill',
            'master_ingestion_status',
            'federal_member_ingestion_status'
        ]
        
        print("\nChecking for required tables...")
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            
            if cursor.fetchone()[0]:
                existing_tables.append(table)
                print(f"  ✅ {table} - EXISTS")
            else:
                missing_tables.append(table)
                print(f"  ❌ {table} - MISSING")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Setup Test Summary")
        print("=" * 60)
        print(f"Connection: ✅ SUCCESS")
        print(f"Existing tables: {len(existing_tables)}/{len(required_tables)}")
        print(f"Missing tables: {len(missing_tables)}")
        
        if missing_tables:
            print("\n⚠️  Missing tables detected.")
            print("Missing tables:", ", ".join(missing_tables))
            return False, missing_tables
        else:
            print("\n✅ All required tables found. Database is ready for ingestion!")
            return True, []
            
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if database server is running")
        print("2. Verify connection details in database_config.env")
        print("3. Ensure firewall allows connection on port 5432")
        print("4. Check if database 'opendiscourse' exists")
        print("5. Verify user 'opendiscourse' has proper permissions")
        return False, []
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, []

def main():
    """Main function."""
    print("OpenDiscourse Database Setup")
    print("=" * 40)
    
    # First, test if we can connect
    connection_ok, missing_tables = test_database_connection()
    
    if not connection_ok:
        print("\n❌ Cannot proceed without database connection.")
        print("Please check your database configuration and try again.")
        sys.exit(1)
    
    # If tables are missing, run migration
    if missing_tables:
        print("\n🔄 Running database migration to create missing tables...")
        migration_ok = run_migration()
        
        if not migration_ok:
            print("\n❌ Migration failed. Please check the error messages above.")
            sys.exit(1)
        
        # Test connection again after migration
        print("\n🔄 Testing connection after migration...")
        connection_ok, missing_tables = test_database_connection()
        
        if not connection_ok:
            print("\n❌ Connection test failed after migration.")
            sys.exit(1)
        
        if missing_tables:
            print("\n❌ Some tables are still missing after migration.")
            print("Please check the migration script and database permissions.")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Database setup completed successfully!")
    print("=" * 60)
    print("Your database is ready for data ingestion workflows.")
    print("\nNext steps:")
    print("1. Configure API keys in database_config.env")
    print("2. Run individual ingestion scripts")
    print("3. Use the orchestration script to run all workflows")

if __name__ == "__main__":
    main()