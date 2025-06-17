#!/usr/bin/env python3
"""
Script to verify Airtable setup and configuration.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pyairtable import Api
from config.settings import config


def verify_airtable_setup():
    """Verify Airtable configuration and table structure."""
    print("🔍 Verifying Airtable Setup...\n")
    
    # Check configuration
    print("1. Checking configuration...")
    errors = config.validate()
    if errors:
        print("❌ Configuration errors found:")
        for error in errors:
            print(f"   - {error}")
        return False
    print("✅ Configuration valid\n")
    
    # Initialize Airtable API
    try:
        api = Api(config.AIRTABLE_API_KEY)
        base = api.base(config.AIRTABLE_BASE_ID)
        print("✅ Connected to Airtable\n")
    except Exception as e:
        print(f"❌ Failed to connect to Airtable: {e}")
        return False
    
    # Check tables
    print("2. Checking required tables...")
    required_tables = [
        config.AIRTABLE_KEYWORD_PERF_TABLE,
        config.AIRTABLE_REPORTS_TABLE
    ]
    
    for table_name in required_tables:
        try:
            table = base.table(table_name)
            # Try to fetch one record to verify access
            records = table.all(max_records=1)
            print(f"✅ Table '{table_name}' accessible")
        except Exception as e:
            print(f"❌ Table '{table_name}' error: {e}")
            return False
    
    print("\n3. Checking table fields...")
    
    # Check Keyword Performance table fields
    try:
        kp_table = base.table(config.AIRTABLE_KEYWORD_PERF_TABLE)
        kp_records = kp_table.all(max_records=1)
        
        if kp_records:
            fields = kp_records[0]['fields'].keys()
            required_fields = [
                'My SF Domain Report',
                'Conversions',
                'Phone Clicks',
                'Cost',
                'SMS Clicks',
                'Clicks',
                'Quote Starts'
            ]
            
            print(f"\n   Keyword Performance table fields:")
            for field in required_fields:
                if field in fields:
                    print(f"   ✅ {field}")
                else:
                    print(f"   ⚠️  {field} (not found - verify field name)")
        else:
            print("   ⚠️  No records in Keyword Performance table to verify fields")
    except Exception as e:
        print(f"   ❌ Error checking Keyword Performance fields: {e}")
    
    # Check Reports table fields
    try:
        reports_table = base.table(config.AIRTABLE_REPORTS_TABLE)
        reports_records = reports_table.all(max_records=1)
        
        required_fields = [
            'Report URL',
            'Status',
            'Account ID',
            'Date Range',
            'Generated At',
            'Aggregated Metrics'
        ]
        
        print(f"\n   Reports table fields needed:")
        for field in required_fields:
            print(f"   📋 {field}")
        
    except Exception as e:
        print(f"   ❌ Error checking Reports table: {e}")
    
    print("\n✅ Airtable setup verification complete!")
    print("\nNext steps:")
    print("1. Ensure all required fields exist in your Airtable tables")
    print("2. Create a test webhook using scripts/test_webhook.py")
    print("3. Deploy to Render when ready")
    
    return True


if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    verify_airtable_setup()