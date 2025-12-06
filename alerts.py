"""
Slack alerting for severe anomalies.
Runs as part of the data refresh workflow.
"""

import os
import pandas as pd
import requests


def send_slack_alert(webhook_url: str, anomalies: list[dict]) -> bool:
    """Send alert to Slack when severe anomalies are detected."""
    if not anomalies:
        return False

    anomaly_text = "\n".join([
        f"  - *{a['country']}*: Score {a['score']:.1f}/100 (${a['revenue']:,.0f})"
        for a in anomalies
    ])

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "Anomaly Alert"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(anomalies)} severe anomalies detected:*\n{anomaly_text}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "View the dashboard for details"
                    }
                ]
            }
        ]
    }

    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200


def check_and_alert(csv_path: str, webhook_url: str) -> None:
    """Check for severe anomalies and send Slack alert if found."""
    df = pd.read_csv(csv_path)
    df['month'] = pd.to_datetime(df['month'])

    latest_month = df['month'].max()
    severe = df[
        (df['month'] == latest_month) &
        (df['anomaly_severity'] == 'Severe')
    ]

    if len(severe) == 0:
        print(f"No severe anomalies found for {latest_month.strftime('%B %Y')}")
        return

    anomalies = [
        {
            'country': row['country'],
            'score': row['anomaly_score'],
            'revenue': row['total_revenue']
        }
        for _, row in severe.iterrows()
    ]

    print(f"Found {len(anomalies)} severe anomalies, sending Slack alert...")

    if send_slack_alert(webhook_url, anomalies):
        print("Alert sent successfully")
    else:
        print("Failed to send alert")


if __name__ == "__main__":
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    if not webhook_url:
        print("SLACK_WEBHOOK_URL not set, skipping alerts")
    else:
        check_and_alert("tables/geographic_anomalies.csv", webhook_url)
