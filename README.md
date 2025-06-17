# SF Domain Reports

A modular webhook handler for generating and managing SF Domain performance reports. This application receives webhooks from Airtable, reads rollup values directly from the My SF Domain Reports record, generates HTML reports, and hosts them on GitHub Pages. The generated report URL is written back to the same Airtable record.

## Features

- **Simple Workflow**: Reads rollup fields from a single Airtable record, generates a report, and updates that record
- **No Aggregation Logic**: All aggregation is handled by Airtable rollup fields
- **No New Records**: The report URL is written back to the triggering record
- **Modular Architecture**: Clean separation of concerns with services, handlers, and templates
- **Flexible Configuration**: Environment-based configuration
- **GitHub Pages Integration**: Automatic report hosting
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
4. Upload to GitHub Pages
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