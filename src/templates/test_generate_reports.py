"""
Local test script to generate HTML reports using the actual process_report logic from webhook.py.
Saves generated reports to /src/templates/test_reports/.
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

def run_local_report_test():
    # Create test_reports directory if it doesn't exist
    REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'test_reports')
    os.makedirs(REPORTS_DIR, exist_ok=True)
    # Mock AirtableService and GitHubService
    mock_airtable = MagicMock()
    mock_github = MagicMock()
    # Provide test data as returned from Airtable
    mock_airtable.get_record_by_id.return_value = {
        'fields': {
            'Cost (from Keyword Performance)': 123.45,
            'Phone Clicks (from Keyword Performance)': 12,
            'SMS Clicks (from Keyword Performance)': 7,
            'Quote Starts (from Keyword Performance)': 3,
            'Conversions (from Keyword Performance)': 4
        }
    }
    # GitHub upload just returns a fake URL
    mock_github.upload_report.return_value = 'https://example.com/test-report.html'
    mock_airtable.update_report_url.return_value = {}

    # Call the real process_report function
    result = process_report(
        report_id='recTEST123',
        date_start='2025-06-01',
        date_end='2025-06-30',
        account_id='TEST-ACCOUNT',
        carrier='TestCarrier',
        airtable_service=mock_airtable,
        github_service=mock_github
    )
    # The HTML is generated inside process_report and passed to upload_report
    html_content = mock_github.upload_report.call_args[1]['content']
    # Save the HTML to a file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'test_report_{timestamp}.html'
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Test report generated: {filepath}")
    print(f"Report URL (mocked): {result['report_url']}")

if __name__ == '__main__':
    run_local_report_test()
