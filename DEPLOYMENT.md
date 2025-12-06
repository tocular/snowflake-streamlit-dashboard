# Deployment Guide

## Quick Start: Deploy to Streamlit Community Cloud

### Prerequisites
- GitHub account
- Snowflake account with access to SNOWFLAKE_SAMPLE_DATA
- Rotated Snowflake password (see SECURITY_INSTRUCTIONS.md)

### Step 1: Push to GitHub

```bash
# Already initialized and committed locally
# Now push to your GitHub repo:

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io
   - Click "Sign in with GitHub"
   - Authorize Streamlit to access your GitHub account

2. **Create New App**
   - Click "New app" button
   - Select your repository from the dropdown
   - Branch: `main`
   - Main file path: `dashboard.py`
   - Click "Advanced settings"

3. **Add Secrets**
   In the "Secrets" section, paste:
   ```toml
   SNOWFLAKE_USER = "OCTOPYTH0N"
   SNOWFLAKE_PASSWORD = "your_rotated_password_here"
   SNOWFLAKE_ACCOUNT = "RWIKFED-VYC30016"
   SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"
   SNOWFLAKE_DATABASE = "SNOWFLAKE_SAMPLE_DATA"
   SNOWFLAKE_SCHEMA = "TPCH_SF1"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait 2-3 minutes for initial deployment
   - Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

### Step 3: Verify Deployment

Check that:
- [ ] Dashboard loads without errors
- [ ] All three visualizations appear
- [ ] Geographic anomaly map displays correctly
- [ ] Product revenue chart shows data
- [ ] Time series chart renders
- [ ] Raw data tabs are accessible

### Troubleshooting

**"Error loading data" messages:**
- Check that all CSV files committed successfully
- Verify the compressed .gz file is present in repository

**Connection errors:**
- Verify Snowflake credentials in Streamlit Cloud secrets
- Check that credentials match TOML format exactly
- Ensure password has been rotated and is correct

**App won't start:**
- Check requirements.txt includes all dependencies
- Verify Python version compatibility (3.8+)
- Check Streamlit Cloud logs for specific errors

### Updating Your Deployed App

To update the dashboard after deployment:

```bash
# Make your changes locally
git add .
git commit -m "Description of changes"
git push

# Streamlit Cloud will automatically redeploy
```

### Custom Domain (Optional)

To add a custom domain:
1. Go to app settings in Streamlit Cloud
2. Click "Custom domain"
3. Follow instructions to configure DNS

### App Settings

Recommended settings in Streamlit Cloud dashboard:
- **Python version**: 3.10+
- **Resources**: Default (should be sufficient)
- **Always on**: Enable if you have a paid plan

### Monitoring

Monitor your app:
- View logs in Streamlit Cloud dashboard
- Check "Analytics" tab for usage stats
- Set up uptime monitoring (optional): UptimeRobot, Pingdom

### Security Checklist

Before making repository public:
- [ ] .env file is gitignored
- [ ] No credentials in code
- [ ] Secrets configured in Streamlit Cloud only
- [ ] Snowflake password rotated
- [ ] SECURITY_INSTRUCTIONS.md followed

---

## Alternative: Deploy to Other Platforms

See README.md for deployment instructions for:
- Heroku
- AWS/GCP/Azure
- DigitalOcean/Linode
- Render

---

**Questions?** Check the README.md or Streamlit documentation at https://docs.streamlit.io
