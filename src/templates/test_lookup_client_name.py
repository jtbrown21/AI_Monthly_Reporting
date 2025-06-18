"""
Test script for process_report with Airtable lookup-style Client Name field.
"""
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

# Ensure project root is in sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.handlers.webhook import process_report

def run_lookup_client_name_test():
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'test_reports')
    os.makedirs(REPORTS_DIR, exist_ok=True)
    mock_airtable = MagicMock()
    mock_github = MagicMock()
    # Simulate Airtable lookup field (list with one name)
    mock_airtable.get_record_by_id.return_value = {
        'fields': {
            'Cost (from Keyword Performance)': 100,
            'Phone Clicks (from Keyword Performance)': 10,
            'SMS Clicks (from Keyword Performance)': 5,
            'Quote Starts (from Keyword Performance)': 2,
            'Conversions (from Keyword Performance)': 1,
            'Client Name': ['Jane Doe']
        }
    }
    mock_github.upload_report.return_value = 'https://example.com/test-report.html'
    mock_airtable.update_report_url.return_value = {}

    result = process_report(
        report_id='recLOOKUP1',
        date_start='2025-06-01',
        date_end='2025-06-30',
        account_id='TEST-ACCOUNT',
        carrier='TestCarrier',
        airtable_service=mock_airtable,
        github_service=mock_github
    )
    html_content = mock_github.upload_report.call_args[1]['content']
    filename = mock_github.upload_report.call_args[1]['filename']
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Test report generated: {filepath}")
    print(f"Report URL (mocked): {result['report_url']}")
    print(f"Filename used: {filename}")

if __name__ == '__main__':
    run_lookup_client_name_test()
