#!/usr/bin/env python3
"""
Test script for sending webhook requests to the local development server.
"""
import requests
import json
import argparse
from datetime import datetime, timedelta


def send_test_webhook(url: str, report_id: str = None):
    """
    Send a test webhook to the specified URL.
    
    Args:
        url: Webhook endpoint URL
        report_id: Optional report ID (generates test ID if not provided)
    """
    # Generate test data
    if not report_id:
        report_id = f"recTEST{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Create test payload matching n8n format
    payload = [
        {
            "headers": {
                "host": "localhost",
                "content-type": "application/json"
            },
            "params": {},
            "query": {},
            "body": {
                "MySFDomainReportRecordID": report_id,
                "ReportCSV": [
                    "https://example.com/test-report.csv"
                ],
                "DateStart": start_date.strftime("%Y-%m-%d"),
                "DateEnd": end_date.strftime("%Y-%m-%d"),
                "AccountID": [
                    "TEST-123-456"
                ],
                "MAASSReport": [],
                "YextReport": [],
                "CarrierCompany": [
                    "Test Insurance Co"
                ]
            },
            "webhookUrl": url,
            "executionMode": "test"
        }
    ]
    
    print(f"Sending test webhook to: {url}")
    print(f"Report ID: {report_id}")
    print(f"Date Range: {start_date} to {end_date}")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Webhook processed successfully!")
            data = response.json().get('data', {})
            if 'report_url' in data:
                print(f"📊 Report URL: {data['report_url']}")
        else:
            print("\n❌ Webhook processing failed!")
            
    except Exception as e:
        print(f"\n❌ Error sending webhook: {str(e)}")


def main():
    """Main function for CLI."""
    parser = argparse.ArgumentParser(
        description='Test webhook for SF Domain Reports'
    )
    parser.add_argument(
        '--url',
        default='http://localhost:5000/webhook',
        help='Webhook endpoint URL (default: http://localhost:5000/webhook)'
    )
    parser.add_argument(
        '--report-id',
        help='Specific report ID to use (generates test ID if not provided)'
    )
    
    args = parser.parse_args()
    send_test_webhook(args.url, args.report_id)


if __name__ == '__main__':
    main()