"""
Airtable service for interacting with Airtable API.
"""
from typing import Dict, Any, Optional
from pyairtable import Api
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AirtableService:
    """Service for Airtable operations."""
    
    def __init__(self, api_key: str, base_id: str):
        """Initialize Airtable service."""
        self.api = Api(api_key)
        self.base_id = base_id
        logger.info(f"Initialized Airtable service for base: {base_id}")

    def update_report_url(
        self, 
        record_id: str,
        report_url: str,
        table_name: str = "My SF Domain Reports"
    ) -> Any:  # Accept pyairtable's RecordDict
        """
        Update the report URL in an existing record.
        
        Args:
            record_id: The record ID to update
            report_url: The generated report URL
            table_name: Name of the reports table
            
        Returns:
            Updated record data
        """
        try:
            table = self.api.table(self.base_id, table_name)
            fields: Dict[str, Any] = {
                'Monthly Performance Report URL': report_url
            }
            logger.info(f"Updating record {record_id} with report URL")
            record = table.update(record_id, fields)
            logger.info(f"Updated record with report URL: {report_url}")
            return record
        except Exception as e:
            logger.error(f"Error updating record: {str(e)}")
            raise

    def get_record_by_id(
        self, 
        record_id: str, 
        table_name: str
    ) -> Optional[Any]:  # Accept pyairtable's RecordDict or None
        """
        Get a single record by ID.
        
        Args:
            record_id: The record ID to fetch
            table_name: Name of the table
            
        Returns:
            Record data or None if not found
        """
        try:
            table = self.api.table(self.base_id, table_name)
            record = table.get(record_id)
            return record
        except Exception as e:
            logger.error(f"Error fetching record {record_id}: {str(e)}")
            return None