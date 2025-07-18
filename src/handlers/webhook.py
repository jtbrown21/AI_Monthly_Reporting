"""
Webhook handler for processing SF Domain Report requests.
"""
from dotenv import load_dotenv
load_dotenv()

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import json
import logging
from datetime import datetime, timedelta
import math

from config.settings import config
from src.services.airtable import AirtableService
from src.services.github import GitHubService
from src.templates.report_html import ReportTemplate
from src.utils.validators import validate_webhook_payload

logger = logging.getLogger(__name__)


def create_webhook_blueprint() -> Blueprint:
    """Create webhook blueprint with routes."""
    webhook_bp = Blueprint('webhook', __name__)
    
    # Initialize services
    airtable_service = AirtableService(
        config.AIRTABLE_API_KEY,
        config.AIRTABLE_BASE_ID
    )
    
    github_service = GitHubService(
        config.GITHUB_TOKEN,
        config.GITHUB_REPO,
        config.GITHUB_BRANCH
    )
    
    @webhook_bp.route('/webhook', methods=['POST'])
    def handle_webhook():
        """Handle incoming webhook from n8n/Airtable."""
        try:
            # Extract payload
            payload = request.json
            if isinstance(payload, list) and len(payload) > 0:
                payload = payload[0]
            if not isinstance(payload, dict):
                logger.error("Invalid payload format: expected dict, got %s", type(payload).__name__)
                return jsonify({
                    'success': False,
                    'error': 'Invalid payload format'
                }), 400

            body = payload.get('body', {})
            
            # Validate payload
            validation_errors = validate_webhook_payload(body)
            if validation_errors:
                logger.error(f"Validation errors: {validation_errors}")
                return jsonify({
                    'success': False,
                    'errors': validation_errors
                }), 400
            
            # Extract data
            report_id = body['MySFDomainReportRecordID']
            date_start = body['DateStart']
            date_end = body['DateEnd']
            account_id = body['AccountID'][0] if body.get('AccountID') else 'Unknown'
            carrier = body['CarrierCompany'][0] if body.get('CarrierCompany') else 'Unknown'
            
            logger.info(f"Processing webhook for report: {report_id}")
            
            # Process report
            result = process_report(
                report_id=report_id,
                date_start=date_start,
                date_end=date_end,
                account_id=account_id,
                carrier=carrier,
                airtable_service=airtable_service,
                github_service=github_service
            )
            
            return jsonify({
                'success': True,
                'data': result
            }), 200
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return webhook_bp


def process_report(
    report_id: str,
    date_start: str,
    date_end: str,
    account_id: str,
    carrier: str,
    airtable_service: AirtableService,
    github_service: GitHubService
) -> Dict[str, Any]:
    """
    Process a report request.
    
    Args:
        report_id: SF Domain Report record ID
        date_start: Report start date
        date_end: Report end date
        account_id: Account identifier
        carrier: Carrier company name
        airtable_service: Airtable service instance
        github_service: GitHub service instance
        
    Returns:
        Processing result dictionary
    """
    try:
        # Step 1: Get the record from My SF Domain Reports
        logger.info(f"Fetching record: {report_id}")
        record = airtable_service.get_record_by_id(
            report_id,
            config.AIRTABLE_REPORTS_TABLE
        )
        if not record:
            raise ValueError(f"Record not found: {report_id}")
        # Step 2: Extract rollup values from the record
        fields = record.get('fields', {})
        # Map Airtable fields to template variables (lowercase, underscores)
        cost = fields.get('Cost (from Keyword Performance)', 0)
        phone_clicks = fields.get('Phone Clicks (from Keyword Performance)', 0)
        sms_clicks = fields.get('SMS Clicks (from Keyword Performance)', 0)
        quote_starts = fields.get('Quote Starts (from Keyword Performance)', 0)
        conversions = fields.get('Conversions (from Keyword Performance)', 0)
        # Format report_month based on Date Start and Date End
        try:
            start_dt = datetime.strptime(date_start, '%Y-%m-%d')
            end_dt = datetime.strptime(date_end, '%Y-%m-%d')
            # Check if the range covers the full month
            first_of_month = start_dt.replace(day=1)
            # Find last day of month
            if start_dt.month == 12:
                next_month = start_dt.replace(year=start_dt.year+1, month=1, day=1)
            else:
                next_month = start_dt.replace(month=start_dt.month+1, day=1)
            last_of_month = next_month - timedelta(days=1)
            if start_dt == first_of_month and end_dt == last_of_month:
                report_month = start_dt.strftime('%B %Y')
            else:
                report_month = f"{start_dt.strftime('%m-%d-%Y')}-{end_dt.strftime('%m-%d-%Y')}"
        except Exception:
            report_month = f"{date_start}-{date_end}"
        # Normalize numerical fields to 0 decimal places (round up)
        def round_up(val):
            try:
                return int(math.ceil(float(val)))
            except Exception:
                return val
        cost = round_up(cost)
        phone_clicks = round_up(phone_clicks)
        sms_clicks = round_up(sms_clicks)
        quote_starts = round_up(quote_starts)
        conversions = round_up(conversions)
        # Calculate total_leads as the aggregate of quote_starts, phone_clicks, sms_clicks, conversions
        total_leads = quote_starts + phone_clicks + sms_clicks + conversions
        # Calculate cost_per_lead using total_leads (avoid division by zero)
        try:
            cost_per_lead = round(float(cost) / float(total_leads), 2) if float(total_leads) else 0.0
        except Exception:
            cost_per_lead = 0.0
        cost_per_lead = round_up(cost_per_lead)
        # Prepare data for template
        template_data = {
            'report_month': report_month,
            'total_leads': total_leads,
            'conversions': conversions,
            'cost': cost,
            'cost_per_lead': cost_per_lead,
            'quote_starts': quote_starts,
            'phone_clicks': phone_clicks,
            'sms_clicks': sms_clicks
        }
        logger.info(f"Extracted metrics for template: {template_data}")
        # Step 3: Generate HTML report
        logger.info("Generating HTML report")
        html_content = ReportTemplate.generate_report(
            template_data
        )
        # Step 4: Upload to GitHub Pages
        logger.info("Uploading report to GitHub Pages")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Get client name and extract last name (handle Airtable lookup/array fields)
        client_name = fields.get('Client Name', 'Client')
        # Airtable lookup fields are always lists, even if single value
        if isinstance(client_name, list):
            # Remove empty/None values, join if multiple names (rare)
            client_name = ' '.join([str(x) for x in client_name if x]) if client_name else 'Client'
        client_name = str(client_name)
        last_name = client_name.strip().split(' ')[-1] if client_name.strip() else 'Client'
        # Format report_month for filename (e.g., June-2025)
        safe_report_month = report_month.replace(' ', '-')
        # Build filename as {last_name}_{report_month}.html
        filename = f"{last_name}_{safe_report_month}.html"
        report_url = github_service.upload_report(
            content=html_content,
            filename=filename,
            path=config.GITHUB_REPORTS_PATH
        )
        # Step 5: Update the record with the report URL
        logger.info("Updating record with report URL")
        updated_record = airtable_service.update_report_url(
            record_id=report_id,
            report_url=report_url
        )
        logger.info(f"Report processing complete. URL: {report_url}")
        return {
            'report_url': report_url,
            'record_id': report_id,
            'metrics': template_data,
            'processing_time': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing report: {str(e)}", exc_info=True)
        raise