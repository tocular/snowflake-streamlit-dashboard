# Snowflake Analytics Dashboard

Executive analytics dashboard built with Streamlit and Snowflake, featuring geographic anomaly detection, product revenue analysis, and time series trends.

## Features

- **Geographic Anomaly Detection**: Interactive world map showing revenue anomalies by country with severity scoring
- **Product Revenue Analysis**: Multi-product comparison across countries with revenue share visualization
- **Monthly Revenue Trends**: Time series analysis with 3-month moving averages
- **Raw Data Explorer**: Tabbed interface to browse underlying datasets

## Data Source

This dashboard uses Snowflake's sample TPC-H dataset (`SNOWFLAKE_SAMPLE_DATA.TPCH_SF1`), which simulates an industrials firm with global operations in the 1990s.

## Local Development

### Prerequisites

- Python 3.8+
- Snowflake account with access to `SNOWFLAKE_SAMPLE_DATA`
- pip or conda

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd snowflake_tutorial
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Snowflake credentials
```

4. Generate data files:
```bash
jupyter nbconvert --to notebook --execute dashboard.ipynb
```

5. Run the dashboard:
```bash
streamlit run dashboard.py
```

The dashboard will be available at `http://localhost:8501`

## Deployment to Streamlit Community Cloud

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Configure Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository and branch
5. Set main file path: `dashboard.py`

### Step 3: Add Secrets

In the Streamlit Cloud dashboard, go to **App settings > Secrets** and add:

```toml
# Snowflake connection credentials
SNOWFLAKE_USER = "your_username"
SNOWFLAKE_PASSWORD = "your_password"
SNOWFLAKE_ACCOUNT = "your_account"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
SNOWFLAKE_DATABASE = "SNOWFLAKE_SAMPLE_DATA"
SNOWFLAKE_SCHEMA = "TPCH_SF1"
```

### Step 4: Deploy

Click "Deploy" and your app will be live in a few minutes!

## Project Structure

```
snowflake_tutorial/
├── dashboard.py              # Main Streamlit dashboard
├── dashboard.ipynb           # Jupyter notebook for data generation
├── snowflake_engine.py       # Snowflake connection wrapper
├── alerts.py                 # Slack alerting for severe anomalies
├── requirements.txt          # Python dependencies
├── .gitignore
├── .env                      # Local environment variables (not committed)
├── .github/
│   └── workflows/
│       └── refresh_data.yml  # Automated monthly data refresh
├── .streamlit/
│   ├── config.toml           # Streamlit configuration
│   └── secrets.toml.example  # Secrets template
└── tables/                   # Generated CSV data files
    ├── geographic_anomalies.csv
    ├── product_revenue_by_country.csv
    ├── product_revenue_by_country.csv.gz
    ├── revenue_trend.csv
    ├── customer_segments.csv
    ├── fulfillment_metrics.csv
    ├── geographic_revenue.csv
    └── top_customers.csv
```

## Configuration

### Environment Variables

Required environment variables (stored in `.env` locally, or Streamlit Cloud secrets):

- `SNOWFLAKE_USER`: Your Snowflake username
- `SNOWFLAKE_PASSWORD`: Your Snowflake password
- `SNOWFLAKE_ACCOUNT`: Your Snowflake account identifier
- `SNOWFLAKE_WAREHOUSE`: Warehouse name (default: COMPUTE_WH)
- `SNOWFLAKE_DATABASE`: Database name (default: SNOWFLAKE_SAMPLE_DATA)
- `SNOWFLAKE_SCHEMA`: Schema name (default: TPCH_SF1)

### Streamlit Configuration

Dashboard settings are in `.streamlit/config.toml`:
- Page title and icon
- Theme colors
- Cache TTL
- Server settings

## Data Pipeline

The dashboard uses pre-generated CSV files for performance. To refresh data:

1. Open `dashboard.ipynb` in Jupyter
2. Run all cells to regenerate CSV files in `tables/`
3. Restart the Streamlit app to load fresh data

### Automated Data Refresh

A GitHub Actions workflow (`.github/workflows/refresh_data.yml`) automates data refresh on a monthly schedule:

1. Executes the data generation notebook
2. Checks for severe anomalies and sends Slack alerts
3. Commits updated CSV files to the repository
4. Streamlit Cloud auto-redeploys on commit

To enable automated refresh:

1. Add the following repository secrets in GitHub:
   - `SNOWFLAKE_USER`
   - `SNOWFLAKE_PASSWORD`
   - `SNOWFLAKE_ACCOUNT`
   - `SNOWFLAKE_WAREHOUSE`
   - `SNOWFLAKE_DATABASE`
   - `SNOWFLAKE_SCHEMA`
   - `SLACK_WEBHOOK_URL` (optional, for alerts)

2. The workflow runs automatically on the 1st of each month, or can be triggered manually from the Actions tab.

### Slack Alerting

When severe anomalies are detected during data refresh, the system sends a Slack notification with:
- Number of severe anomalies
- Affected countries with scores and revenue figures

To set up Slack alerts:
1. Create an Incoming Webhook in your Slack workspace
2. Add the webhook URL as `SLACK_WEBHOOK_URL` in GitHub repository secrets

### Anomaly Detection Algorithm

Geographic anomalies are calculated using:
- **Z-scores**: Statistical deviation from country mean
- **Month-over-Month changes**: Revenue growth rate analysis
- **Correlation breakdown**: Pattern deviation detection
- **IQR outliers**: Interquartile range anomaly identification

Severity categories (quartile-based):
- **Normal** (0-25): Typical variation
- **Minor** (25-50): Slight deviation
- **Moderate** (50-75): Notable anomaly
- **Severe** (75-100): Significant deviation

## Security

- Credentials are never committed to git (see `.gitignore`)
- Environment variables are loaded via `python-dotenv`
- Streamlit Cloud secrets are encrypted at rest
- Follow `SECURITY_INSTRUCTIONS.md` for credential rotation

## Performance

- CSV caching with 1-hour TTL (`@st.cache_data`)
- Product data aggregation to reduce dataset size
- Natural Earth projection for optimized map rendering
- Efficient Plotly visualizations

## Troubleshooting

### "Error loading data" message

Run the data generation notebook:
```bash
jupyter nbconvert --to notebook --execute dashboard.ipynb
```

### Connection timeout errors

Check your Snowflake credentials in `.env` or Streamlit Cloud secrets.

### Missing dependencies

Reinstall requirements:
```bash
pip install -r requirements.txt --upgrade
```

## Contributing

This is a demo project for educational purposes. Feel free to fork and adapt for your own use cases.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Data from [Snowflake Sample Datasets](https://docs.snowflake.com/en/user-guide/sample-data.html)
- Visualizations powered by [Plotly](https://plotly.com/python/)
