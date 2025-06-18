"""
HTML report template generation using Jinja2.
"""
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
import os


class ReportTemplate:
    """HTML report template generator using Jinja2."""

    @staticmethod
    def generate_report(
        data: Dict[str, Any],
        template_name: str = "report_template.html"
    ) -> str:
        """
        Render the HTML report from the template and data.

        Args:
            data: Dictionary with report data (e.g., month, total_sales, new_customers, etc.)
            template_name: Name of the HTML template file
        Returns:
            Rendered HTML report as a string
        """
        # Set up Jinja2 environment to load templates from the current directory
        template_dir = os.path.dirname(os.path.abspath(__file__))
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        html = template.render(**data)
        return html

# Example usage:
# data = {"month": "June 2025", "total_sales": 10000, "new_customers": 25}
# html_report = ReportTemplate.generate_report(data)
# print(html_report)