import unittest
from unittest.mock import patch, MagicMock
from src.handlers.webhook import process_report

class TestWebhookReportGeneration(unittest.TestCase):
    @patch('src.handlers.webhook.ReportTemplate')
    @patch('src.handlers.webhook.GitHubService')
    @patch('src.handlers.webhook.AirtableService')
    def test_generate_report_uses_default_template(self, MockAirtableService, MockGitHubService, MockReportTemplate):
        # Arrange
        mock_airtable = MockAirtableService.return_value
        mock_github = MockGitHubService.return_value
        mock_report_template = MockReportTemplate
        mock_airtable.get_record_by_id.return_value = {
            'fields': {
                'Cost (from Keyword Performance)': 100,
                'Phone Clicks (from Keyword Performance)': 10,
                'SMS Clicks (from Keyword Performance)': 5,
                'Quote Starts (from Keyword Performance)': 2,
                'Conversions (from Keyword Performance)': 1
            }
        }
        mock_report_template.generate_report.return_value = '<html>report</html>'
        mock_github.upload_report.return_value = 'https://example.com/report.html'
        # Act
        result = process_report(
            report_id='rec123',
            date_start='2025-06-01',
            date_end='2025-06-30',
            account_id='128-903-1394',
            carrier='TestCarrier',
            airtable_service=mock_airtable,
            github_service=mock_github
        )
        # Assert
        mock_report_template.generate_report.assert_called_once()
        template_data = mock_report_template.generate_report.call_args[0][0]
        self.assertNotIn('128-903-1394', template_data.values(), "Account ID should not be used as template value")
        self.assertIn('cost', template_data)
        self.assertEqual(result['report_url'], 'https://example.com/report.html')

    @patch('src.handlers.webhook.ReportTemplate')
    @patch('src.handlers.webhook.GitHubService')
    @patch('src.handlers.webhook.AirtableService')
    def test_variable_mapping_and_template_data(self, MockAirtableService, MockGitHubService, MockReportTemplate):
        # Arrange
        mock_airtable = MockAirtableService.return_value
        mock_github = MockGitHubService.return_value
        mock_report_template = MockReportTemplate
        mock_airtable.get_record_by_id.return_value = {
            'fields': {
                'Cost (from Keyword Performance)': 200,
                'Phone Clicks (from Keyword Performance)': 20,
                'SMS Clicks (from Keyword Performance)': 10,
                'Quote Starts (from Keyword Performance)': 4,
                'Conversions (from Keyword Performance)': 2
            }
        }
        mock_report_template.generate_report.return_value = '<html>report</html>'
        mock_github.upload_report.return_value = 'https://example.com/report.html'
        # Act
        result = process_report(
            report_id='rec456',
            date_start='2025-06-01',
            date_end='2025-06-30',
            account_id='999-888-7777',
            carrier='TestCarrier',
            airtable_service=mock_airtable,
            github_service=mock_github
        )
        # Assert
        mock_report_template.generate_report.assert_called_once()
        template_data = mock_report_template.generate_report.call_args[0][0]
        self.assertEqual(template_data['cost'], 200)
        self.assertEqual(template_data['phone_clicks'], 20)
        self.assertEqual(template_data['sms_clicks'], 10)
        self.assertEqual(template_data['quote_starts'], 4)
        self.assertEqual(template_data['conversions'], 2)
        self.assertEqual(template_data['cost_per_lead'], 100.0)
        self.assertEqual(template_data['report_month'], 'June 2025')
        self.assertEqual(result['report_url'], 'https://example.com/report.html')

if __name__ == '__main__':
    unittest.main()
