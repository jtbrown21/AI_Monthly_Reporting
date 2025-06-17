#!/usr/bin/env python3
"""
Script to verify Airtable setup and configuration.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()

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

    # Check Keyword Performance table (where we READ from)
    try:
        kp_table = base.table(config.AIRTABLE_KEYWORD_PERF_TABLE)
        kp_records = kp_table.all(max_records=1)
        print(f"✅ Table '{config.AIRTABLE_KEYWORD_PERF_TABLE}' accessible")
    except Exception as e:
        print(f"❌ Table '{config.AIRTABLE_KEYWORD_PERF_TABLE}' error: {e}")
        return False

    # Check Reports table (where we WRITE to)
    try:
        reports_table = base.table(config.AIRTABLE_REPORTS_TABLE)
        # Just check if we can access it
        reports_table.all(max_records=1)
        print(f"✅ Table '{config.AIRTABLE_REPORTS_TABLE}' accessible (for writing reports)")
    except Exception as e:
        print(f"❌ Table '{config.AIRTABLE_REPORTS_TABLE}' error: {e}")
        print("   → This table is where we'll CREATE new report records")
        return False

    print("\n3. Checking table fields...")

    # Check My SF Domain Reports table fields
    try:
        reports_table = base.table(config.AIRTABLE_REPORTS_TABLE)
        reports_records = reports_table.all(max_records=1)
        
        print(f"\n   My SF Domain Reports table fields:")
        required_fields = [
            'Cost (from Keyword Performance)',
            'Phone Clicks (from Keyword Performance)',
            'SMS Clicks (from Keyword Performance)',
            'Quote Starts (from Keyword Performance)',
            'Conversions (from Keyword Performance)',
            'Monthly Performance Report URL'
        ]
        
        if reports_records:
            fields = list(reports_records[0]['fields'].keys())
            for field in required_fields:
                if field in fields:
                    print(f"   ✅ {field}")
                else:
                    print(f"   ⚠️  {field} (not found - verify exact field name)")
        else:
            print("   ⚠️  No records to verify fields")
            print("   Required rollup fields:")
            for field in required_fields:
                print(f"   - {field}")
    except Exception as e:
        print(f"   ❌ Error checking table fields: {e}")

    print("\n✅ Airtable setup verification complete!")
    print("\n📝 Summary:")
    print("- Webhook provides: MySFDomainReportRecordID")
    print("- We read: Rollup values from that record")
    print("- We update: The same record with the generated report URL")

    return True
    
if __name__ == '__main__':
    verify_airtable_setup()