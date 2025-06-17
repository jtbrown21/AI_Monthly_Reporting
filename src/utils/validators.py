"""
Input validation utilities.
"""
from typing import Dict, List, Any
from datetime import datetime


def validate_webhook_payload(payload: Dict[str, Any]) -> List[str]:
    """
    Validate webhook payload structure and content.
    
    Args:
        payload: Webhook payload body
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Required fields
    required_fields = [
        'MySFDomainReportRecordID',
        'DateStart',
        'DateEnd'
    ]
    
    for field in required_fields:
        if field not in payload:
            errors.append(f"Missing required field: {field}")
    
    # Validate record ID format
    if 'MySFDomainReportRecordID' in payload:
        record_id = payload['MySFDomainReportRecordID']
        if not isinstance(record_id, str) or not record_id.startswith('rec'):
            errors.append("Invalid MySFDomainReportRecordID format")
    
    # Validate date formats
    for date_field in ['DateStart', 'DateEnd']:
        if date_field in payload:
            try:
                datetime.strptime(payload[date_field], '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format for {date_field}. Expected: YYYY-MM-DD")
    
    # Validate date range
    if 'DateStart' in payload and 'DateEnd' in payload:
        try:
            start_date = datetime.strptime(payload['DateStart'], '%Y-%m-%d')
            end_date = datetime.strptime(payload['DateEnd'], '%Y-%m-%d')
            
            if start_date > end_date:
                errors.append("DateStart must be before or equal to DateEnd")
        except ValueError:
            pass  # Already handled above
    
    # Validate array fields
    array_fields = ['AccountID', 'CarrierCompany']
    for field in array_fields:
        if field in payload:
            if not isinstance(payload[field], list):
                errors.append(f"{field} must be an array")
            elif len(payload[field]) == 0:
                errors.append(f"{field} array cannot be empty")
    
    return errors


def validate_airtable_record(record: Dict[str, Any]) -> bool:
    """
    Validate Airtable record structure.
    
    Args:
        record: Airtable record
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(record, dict):
        return False
    
    if 'id' not in record or 'fields' not in record:
        return False
    
    if not isinstance(record['fields'], dict):
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    safe_filename = filename
    
    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    safe_filename = safe_filename.strip(' .')
    
    # Limit length
    max_length = 100
    if len(safe_filename) > max_length:
        safe_filename = safe_filename[:max_length]
    
    return safe_filename