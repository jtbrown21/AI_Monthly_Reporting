"""
HTML report template generation.
"""
from typing import Dict, Any
from datetime import datetime
from src.services.aggregator import AggregatedMetrics


class ReportTemplate:
    """HTML report template generator."""
    
    @staticmethod
    def generate_report(
        metrics: AggregatedMetrics,
        account_id: str,
        carrier_company: str,
        date_start: str,
        date_end: str,
        additional_data: Dict[str, Any] = None
    ) -> str:
        """
        Generate HTML report from aggregated metrics.
        
        Args:
            metrics: Aggregated metrics data
            account_id: Account identifier
            carrier_company: Carrier company name
            date_start: Report start date
            date_end: Report end date
            additional_data: Optional additional data to include
            
        Returns:
            Generated HTML report as string
        """
        # Format values for display
        formatted_cost = f"${metrics.cost:,.2f}"
        formatted_cpc = f"${metrics.cost_per_click:.2f}"
        
        # Generate metric cards
        metric_cards = ReportTemplate._generate_metric_cards(metrics)
        
        # Generate performance insights
        insights = ReportTemplate._generate_insights(metrics)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SF Domain Report - {account_id}</title>
    {ReportTemplate._get_styles()}
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1>SF Domain Performance Report</h1>
            <div class="header-info">
                <p><strong>Account:</strong> {account_id}</p>
                <p><strong>Carrier:</strong> {carrier_company}</p>
                <p><strong>Period:</strong> {date_start} to {date_end}</p>
            </div>
        </header>
        
        <section class="metrics-section">
            <h2>Performance Metrics</h2>
            <div class="metrics-grid">
                {metric_cards}
            </div>
        </section>
        
        <section class="insights-section">
            <h2>Key Insights</h2>
            {insights}
        </section>
        
        <footer class="report-footer">
            <p>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>Total records analyzed: {metrics.record_count}</p>
        </footer>
    </div>
</body>
</html>
"""
        return html
    
    @staticmethod
    def _generate_metric_cards(metrics: AggregatedMetrics) -> str:
        """Generate HTML for metric cards."""
        cards_data = [
            ("Total Clicks", f"{metrics.clicks:,}", "primary"),
            ("Conversions", f"{metrics.conversions:,}", "success"),
            ("Total Cost", f"${metrics.cost:,.2f}", "warning"),
            ("Cost Per Click", f"${metrics.cost_per_click:.2f}", "info"),
            ("Phone Clicks", f"{metrics.phone_clicks:,}", "primary"),
            ("SMS Clicks", f"{metrics.sms_clicks:,}", "primary"),
            ("Quote Starts", f"{metrics.quote_starts:,}", "success"),
            ("Conversion Rate", f"{metrics.conversion_rate:.1f}%", "info")
        ]
        
        cards_html = ""
        for label, value, theme in cards_data:
            cards_html += f"""
                <div class="metric-card metric-card-{theme}">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                </div>
            """
        
        return cards_html
    
    @staticmethod
    def _generate_insights(metrics: AggregatedMetrics) -> str:
        """Generate insights based on metrics."""
        insights_html = "<div class='insights-container'>"
        
        # Performance insight
        if metrics.conversion_rate > 3:
            performance = "excellent"
            icon = "✅"
        elif metrics.conversion_rate > 1:
            performance = "good"
            icon = "👍"
        else:
            performance = "needs improvement"
            icon = "⚠️"
        
        insights_html += f"""
            <div class="insight-card">
                <h3>{icon} Conversion Performance</h3>
                <p>Your conversion rate of <strong>{metrics.conversion_rate:.1f}%</strong> is {performance}.</p>
            </div>
        """
        
        # Cost efficiency insight
        if metrics.cost_per_click > 0:
            insights_html += f"""
                <div class="insight-card">
                    <h3>💰 Cost Efficiency</h3>
                    <p>Average cost per click: <strong>${metrics.cost_per_click:.2f}</strong></p>
                    <p>Total investment: <strong>${metrics.cost:,.2f}</strong> for <strong>{metrics.clicks:,}</strong> clicks</p>
                </div>
            """
        
        # Engagement insight
        phone_rate = (metrics.phone_clicks / metrics.clicks * 100) if metrics.clicks > 0 else 0
        if phone_rate > 0:
            insights_html += f"""
                <div class="insight-card">
                    <h3>📞 Customer Engagement</h3>
                    <p><strong>{phone_rate:.1f}%</strong> of clicks resulted in phone calls</p>
                    <p>Total phone interactions: <strong>{metrics.phone_clicks:,}</strong></p>
                </div>
            """
        
        insights_html += "</div>"
        return insights_html
    
    @staticmethod
    def _get_styles() -> str:
        """Get CSS styles for the report."""
        return """
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .report-header {
            background: linear-gradient(135deg, #2c3e50, #3498db);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .report-header h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
        }
        
        .header-info p {
            margin: 5px 0;
            font-size: 1.1em;
        }
        
        .metrics-section, .insights-section {
            background: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metrics-section h2, .insights-section h2 {
            color: #2c3e50;
            margin-bottom: 25px;
            font-size: 1.8em;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .metric-card {
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            transition: transform 0.2s;
            border: 2px solid #e0e0e0;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .metric-card-primary { border-color: #3498db; }
        .metric-card-success { border-color: #2ecc71; }
        .metric-card-warning { border-color: #f39c12; }
        .metric-card-info { border-color: #9b59b6; }
        
        .metric-label {
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .insights-container {
            display: grid;
            gap: 20px;
        }
        
        .insight-card {
            padding: 20px;
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 4px;
        }
        
        .insight-card h3 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .report-footer {
            text-align: center;
            color: #7f8c8d;
            padding: 20px;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .report-header h1 {
                font-size: 1.8em;
            }
        }
    </style>
    """