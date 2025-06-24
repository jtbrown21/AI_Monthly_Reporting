# SF Domain Reports

A modular webhook handler for generating and managing SF Domain performance reports. This application receives webhooks from Airtable, reads rollup values directly from the My SF Domain Reports record, generates HTML reports, and hosts them on a custom domain (https://app.agentinsider.co). The generated report URL is written back to the same Airtable record.

> **Note:** As of June 2025, reports are no longer hosted at the default GitHub Pages domain. All reports are now available at your custom domain: https://app.agentinsider.co

## Features

- **Simple Workflow**: Reads rollup fields from a single Airtable record, generates a report, and updates that record
- **No Aggregation Logic**: All aggregation is handled by Airtable rollup fields
- **No New Records**: The report URL is written back to the triggering record
- **Modular Architecture**: Clean separation of concerns with services, handlers, and templates
- **Flexible Configuration**: Environment-based configuration
- **Custom Domain Hosting**: Automatic report hosting at https://app.agentinsider.co
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Type Safety**: Python type hints throughout

## Project Structure

```
sf-domain-reports/
├── app.py                      # Main Flask application
├── config/                     # Configuration management
├── src/
│   ├── handlers/              # Request handlers
│   ├── services/              # Business logic services
│   ├── templates/             # Report templates
│   └── utils/                 # Utility functions
└── tests/                     # Unit tests
```

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sf-domain-reports.git
cd sf-domain-reports
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Airtable Configuration
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_base_id

# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=username/reports-repo

# Application Configuration
PORT=5000
LOG_LEVEL=INFO
```

### 4. Setup GitHub Repository

1. Create a new repository for hosting reports
2. Enable GitHub Pages in repository settings
3. Create a personal access token with `repo` permissions

### 5. Deploy to Render

1. Connect your GitHub repository to Render
2. Configure environment variables in Render dashboard
3. Deploy with:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

## Usage

### Webhook Endpoint

The application exposes a webhook endpoint at `/webhook` that expects the following payload:

```json
{
  "body": {
    "MySFDomainReportRecordID": "recXXXXXXXXXXXXXX",
    "DateStart": "2025-05-01",
    "DateEnd": "2025-05-31",
    "AccountID": ["538-684-0631"],
    "CarrierCompany": ["State Farm"]
  }
}
```

### Report Generation Flow

1. Webhook received with report parameters
2. Read rollup values (Cost, Clicks, Conversions, etc.) from the My SF Domain Reports record
3. Generate responsive HTML report
4. Upload to your custom domain (https://app.agentinsider.co)
5. Update the same Airtable record with the generated report URL

## Development

### Running Locally

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Testing Webhooks Locally

Use ngrok to expose your local server:

```bash
ngrok http 5000
```

### Customizing Reports

Edit `src/templates/report_html.py` to modify:
- Report layout and design
- Metrics displayed (uses keys like 'Cost', 'Clicks', etc.)
- Insights and calculations
- CSS styling

## Report Template System (Jinja2)

This project now uses [Jinja2](https://palletsprojects.com/p/jinja/) for HTML report generation. The Python logic and HTML template are separated for maintainability and flexibility.

- **Python Logic:** All report generation logic is in `src/templates/report_html.py`.
- **HTML Template:** The HTML structure is in `src/templates/report_template.html`.

### How It Works

1. The `ReportTemplate.generate_report(data)` method loads and renders the HTML template using Jinja2.
2. Pass a dictionary with your report data (e.g., `month`, `total_sales`, etc.) to this method.
3. The template uses Jinja2 variables (e.g., `{{ month }}`) to display dynamic content.

#### Example Usage

```python
from src.templates.report_html import ReportTemplate

data = {
    "month": "June 2025",
    "total_sales": 10000,
    "new_customers": 25
}
html_report = ReportTemplate.generate_report(data)
print(html_report)
```

#### Customizing the Template
- Edit `src/templates/report_template.html` to change the HTML structure or add new variables.
- Do not include Python code in the HTML file—use Jinja2 template variables instead.

#### Dependencies
- Jinja2 is required. Install with:
  ```bash
  pip install jinja2
  ```

### Mapping Additional Values to the HTML Template

To add new dynamic values to your report:

1. **Add a Jinja2 variable in your HTML template**
   - Open `src/templates/report_template.html` and insert a variable using double curly braces, e.g.:
     ```html
     <div>{{ my_new_value }}</div>
     ```

2. **Pass the value from Python**
   - In your Python code (e.g., in `src/templates/report_html.py`), add the new value to the data dictionary:
     ```python
     data = {
         # ...existing values...
         "my_new_value": value_from_airtable_or_logic,
     }
     html_report = ReportTemplate.generate_report(data)
     ```

3. **Map Airtable fields to template variables**
   - Use readable variable names in your template and map them from Airtable fields in Python:
     ```python
     data = {
         "cost": record['fields'].get('Cost (from Keyword Performance)', 0),
         "phone_clicks": record['fields'].get('Phone Clicks (from Keyword Performance)', 0),
         # Add more mappings as needed
     }
     ```

4. **Preview the result**
   - Render the report and open the generated HTML in your browser to verify the new value appears as expected.

**Tip:**
- Only use Jinja2 variables (e.g., `{{ variable_name }}`) in the HTML template. All logic and data preparation should be done in Python.

### Report Variable Mapping and Calculations

The following variables are passed from Python to the Jinja2 HTML template:

- `report_month`: The month and year of the report, formatted as "Month YYYY" (e.g., "June 2025").
- `quote_starts`: Number of quote starts (from Airtable field).
- `phone_clicks`: Number of website phone clicks (from Airtable field).
- `sms_clicks`: Number of website SMS clicks (from Airtable field).
- `conversions`: Number of conversions (from Airtable field).
- `cost`: Total investment (from Airtable field, rounded up to nearest integer).
- `total_leads`: The sum of `quote_starts`, `phone_clicks`, `sms_clicks`, and `conversions`. This is shown as "New Leads Generated" in the report.
- `cost_per_lead`: Calculated as `cost` divided by `total_leads` (rounded up to nearest integer). If `total_leads` is zero, this will be 0.

#### Example Calculation

If your Airtable record has:
- Quote Starts: 3
- Phone Clicks: 5
- SMS Clicks: 2
- Conversions: 7
- Cost: 123

Then:
- `total_leads = 3 + 5 + 2 + 7 = 17`
- `cost_per_lead = 123 / 17 ≈ 8` (rounded up)

All these variables are available for use in the HTML template as `{{ variable_name }}`.

---

## API Reference

### POST /webhook
Processes report generation request

### GET /health
Health check endpoint

### GET /
Service information endpoint

## Monitoring

- All operations are logged with timestamps
- Check Render logs for webhook processing details
- Failed uploads are logged with full error details

## Future Enhancements

- Email automation with Postmark
- Additional report customization options

## Contributing

1. Create a feature branch
2. Make your changes with proper type hints
3. Add unit tests for new functionality
4. Submit a pull request

## License

[Your License Here]