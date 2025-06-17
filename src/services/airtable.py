"""
Airtable service for interacting with Airtable API.
"""
from typing import Dict, List, Any, Optional
from pyairtable import Api
from pyairtable.formulas import match
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ReportRecord:
    """Data class for report records."""
    report_url: str
    status: str
    linked_report_id: str
    account_id: str
    date_range: str
    generated_at: str
    aggregated_metrics: str


class AirtableService:
    """Service for Airtable operations."""
    
    def __init__(self, api_key: str, base_id: str):
        """Initialize Airtable service."""
        self.api = Api(api_key)
        self.base_id = base_id
        logger.info(f"Initialized Airtable service for base: {base_id}")
    
    def get_linked_keyword_performance(
        self, 
        report_id: str, 
        table_name: str = "Keyword Performance"
    ) -> List[Dict[str, Any]]:
        """
        Get all keyword performance records linked to a report.
        
        Args:
            report_id: The SF Domain Report record ID
            table_name: Name of the keyword performance table
            
        Returns:
            List of keyword performance records
        """
        try:
            table = self.api.table(self.base_id, table_name)
            formula = match({"My SF Domain Report": report_id})
            
            logger.info(f"Querying {table_name} for report: {report_id}")
            records = table.all(formula=formula)
            
            logger.info(f"Found {len(records)} linked records")
            return records
            
        except Exception as e:
            logger.error(f"Error fetching keyword performance: {str(e)}")
            raise
    
    def create_report_record(
        self, 
        report_data: ReportRecord,
        table_name: str = "My SF Domain Reports"
    ) -> Dict[str, Any]:
        """
        Create a new report record in Airtable.
        
        Args:
            report_data: Report data to create
            table_name: Name of the reports table
            
        Returns:
            Created record data
        """
        try:
            table = self.api.table(self.base_id, table_name)
            
            fields = {
                'Report URL': report_data.report_url,
                'Status': report_data.status,
                'My SF Domain Report': [report_data.linked_report_id],
                'Account ID': report_data.account_id,
                'Date Range': report_data.date_range,
                'Generated At': report_data.generated_at,
                'Aggregated Metrics': report_data.aggregated_metrics
            }
            
            logger.info(f"Creating report record in {table_name}")
            record = table.create(fields)
            
            logger.info(f"Created report record: {record['id']}")
            return record
            
        except Exception as e:
            logger.error(f"Error creating report record: {str(e)}")
            raise
    
    def get_record_by_id(
        self, 
        record_id: str, 
        table_name: str
    ) -> Optional[Dict[str, Any]]:
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