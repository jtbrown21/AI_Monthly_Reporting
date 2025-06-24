"""
Test script for validating report_month logic and template variable mapping.
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

def run_report_month_tests():
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'test_reports')
    os.makedirs(REPORTS_DIR, exist_ok=True)
    mock_airtable = MagicMock()
    mock_github = MagicMock()
    mock_airtable.update_report_url.return_value = {}
    mock_github.upload_report.return_value = 'https://example.com/test-report.html'

    test_cases = [
        # Full month (June 2025)
        {
            'date_start': '2025-06-01',
            'date_end': '2025-06-30',
            'expected': 'June 2025',
            'fields': {
                'Cost (from Keyword Performance)': 100,
                'Phone Clicks (from Keyword Performance)': 10,
                'SMS Clicks (from Keyword Performance)': 5,
                'Quote Starts (from Keyword Performance)': 2,
                'Conversions (from Keyword Performance)': 1,
                'Client Name': ['Jane Doe']
            }
        },
        # Partial month
        {
            'date_start': '2025-06-01',
            'date_end': '2025-06-15',
            'expected': '06-01-2025-06-15-2025',
            'fields': {
                'Cost (from Keyword Performance)': 100,
                'Phone Clicks (from Keyword Performance)': 10,
                'SMS Clicks (from Keyword Performance)': 5,
                'Quote Starts (from Keyword Performance)': 2,
                'Conversions (from Keyword Performance)': 1,
                'Client Name': ['Jane Doe']
            }
        },
        # February non-leap year
        {
            'date_start': '2025-02-01',
            'date_end': '2025-02-28',
            'expected': 'February 2025',
            'fields': {
                'Cost (from Keyword Performance)': 100,
                'Phone Clicks (from Keyword Performance)': 10,
                'SMS Clicks (from Keyword Performance)': 5,
                'Quote Starts (from Keyword Performance)': 2,
                'Conversions (from Keyword Performance)': 1,
                'Client Name': ['Jane Doe']
            }
        },
        # February leap year
        {
            'date_start': '2024-02-01',
            'date_end': '2024-02-29',
            'expected': 'February 2024',
            'fields': {
                'Cost (from Keyword Performance)': 100,
                'Phone Clicks (from Keyword Performance)': 10,
                'SMS Clicks (from Keyword Performance)': 5,
                'Quote Starts (from Keyword Performance)': 2,
                'Conversions (from Keyword Performance)': 1,
                'Client Name': ['Jane Doe']
            }
        }
    ]

    for i, case in enumerate(test_cases, 1):
        mock_airtable.get_record_by_id.return_value = {'fields': case['fields']}
        result = process_report(
            report_id=f'recTEST{i}',
            date_start=case['date_start'],
            date_end=case['date_end'],
            account_id='TEST-ACCOUNT',
            carrier='TestCarrier',
            airtable_service=mock_airtable,
            github_service=mock_github
        )
        template_data = result['metrics']
        print(f"Test {i}: {case['date_start']} to {case['date_end']}")
        print(f"  Expected report_month: {case['expected']}")
        print(f"  Actual report_month:   {template_data['report_month']}")
        assert template_data['report_month'] == case['expected'], f"Mismatch in report_month for test {i}"
        print(f"  total_leads: {template_data['total_leads']}  cost_per_lead: {template_data['cost_per_lead']}\n")
    print("All tests passed!")

if __name__ == '__main__':
    run_report_month_tests()
