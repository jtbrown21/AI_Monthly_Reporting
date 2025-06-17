"""
Data aggregation service for keyword performance metrics.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class AggregatedMetrics:
    """Data class for aggregated metrics."""
    conversions: float = 0.0
    phone_clicks: float = 0.0
    cost: float = 0.0
    sms_clicks: float = 0.0
    clicks: float = 0.0
    quote_starts: float = 0.0
    record_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'Conversions': self.conversions,
            'Phone Clicks': self.phone_clicks,
            'Cost': self.cost,
            'SMS Clicks': self.sms_clicks,
            'Clicks': self.clicks,
            'Quote Starts': self.quote_starts,
            'Record Count': self.record_count
        }
    
    @property
    def cost_per_click(self) -> float:
        """Calculate cost per click."""
        return self.cost / self.clicks if self.clicks > 0 else 0.0
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        return (self.conversions / self.clicks * 100) if self.clicks > 0 else 0.0


class AggregatorService:
    """Service for aggregating keyword performance data."""
    
    # Mapping of field names to metric attributes
    FIELD_MAPPING = {
        'Conversions': 'conversions',
        'Phone Clicks': 'phone_clicks',
        'Cost': 'cost',
        'SMS Clicks': 'sms_clicks',
        'Clicks': 'clicks',
        'Quote Starts': 'quote_starts'
    }
    
    def aggregate_keyword_performance(
        self, 
        records: List[Dict[str, Any]]
    ) -> AggregatedMetrics:
        """
        Aggregate keyword performance metrics from records.
        
        Args:
            records: List of Airtable records with performance data
            
        Returns:
            Aggregated metrics
        """
        metrics = AggregatedMetrics()
        metrics.record_count = len(records)
        
        logger.info(f"Aggregating {len(records)} keyword performance records")
        
        for record in records:
            fields = record.get('fields', {})
            
            for field_name, attr_name in self.FIELD_MAPPING.items():
                value = self._parse_numeric_value(fields.get(field_name, 0))
                current_value = getattr(metrics, attr_name)
                setattr(metrics, attr_name, current_value + value)
        
        logger.info(f"Aggregation complete: {metrics.record_count} records processed")
        return metrics
    
    def _parse_numeric_value(self, value: Any) -> float:
        """
        Parse a numeric value from various formats.
        
        Args:
            value: Value to parse (could be string with $, comma, etc.)
            
        Returns:
            Parsed float value
        """
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common formatting characters
            cleaned = value.replace('$', '').replace(',', '').strip()
            try:
                return float(cleaned)
            except ValueError:
                logger.warning(f"Could not parse numeric value: {value}")
                return 0.0
        
        return 0.0
    
    def calculate_summary_stats(
        self, 
        metrics: AggregatedMetrics
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics from aggregated metrics.
        
        Args:
            metrics: Aggregated metrics
            
        Returns:
            Dictionary of summary statistics
        """
        return {
            'total_metrics': metrics.to_dict(),
            'calculated_metrics': {
                'cost_per_click': round(metrics.cost_per_click, 2),
                'conversion_rate': round(metrics.conversion_rate, 2),
                'average_cpc': round(metrics.cost_per_click, 2),
                'phone_click_rate': round(
                    (metrics.phone_clicks / metrics.clicks * 100) 
                    if metrics.clicks > 0 else 0, 2
                )
            },
            'record_count': metrics.record_count
        }