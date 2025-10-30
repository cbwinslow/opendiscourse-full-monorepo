#!/usr/bin/env python3
"""
Database Connection Test Script
Tests connectivity to the OpenDiscourse PostgreSQL database.
"""

import os
import sys
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv('database_config.env')

def test_database_connection():
    """Test database connectivity with the configured connection details."""
    
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
        
        # Test table existence
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables in the database:")
        
        for table in tables:
            print(f"  - {table[0]}")
        
        # Test specific OpenDiscourse tables
        print("\nChecking for OpenDiscourse-specific tables...")
        opencivic_tables = ['opencivicdata_bill', 'opencivicdata_person', 'opencivicdata_organization']
        federal_tables = ['federal_members', 'federal_bills', 'federal_committees']
        
        all_tables = opencivic_tables + federal_tables
        existing_tables = []
        missing_tables = []
        
        for table in all_tables:
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
        print("Connection Test Summary")
        print("=" * 60)
        print(f"Connection: ✅ SUCCESS")
        print(f"Existing tables: {len(existing_tables)}/{len(all_tables)}")
        print(f"Missing tables: {len(missing_tables)}")
        
        if missing_tables:
            print("\n⚠️  Missing tables detected. Run migration scripts to create them.")
            print("Missing tables:", ", ".join(missing_tables))
            return False
        else:
            print("\n✅ All expected tables found. Database is ready for ingestion!")
            return True
            
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check if database server is running")
        print("2. Verify connection details in database_config.env")
        print("3. Ensure firewall allows connection on port 5432")
        print("4. Check if database 'opendiscourse' exists")
        print("5. Verify user 'opendiscourse' has proper permissions")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    success = test_database_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()