import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

PINTEREST_TOKEN = os.getenv("PINTEREST_TOKEN")

def get_data(days):
    start = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.utcnow().strftime("%Y-%m-%d")

    url = "https://api.pinterest.com/v5/user_account/analytics"

    headers = {
        "Authorization": f"Bearer {PINTEREST_TOKEN}"
    }

    params = {
        "start_date": start,
        "end_date": end,
        "granularity": "TOTAL",
        "metric_types": "IMPRESSION,OUTBOUND_CLICK,SAVE,ENGAGEMENT"
    }

    r = requests.get(url, headers=headers, params=params)
    return r.json()

def format_data(data, label):
    stats = data.get("items", [{}])[0]

    impressions = stats.get("IMPRESSION", 0)
    clicks = stats.get("OUTBOUND_CLICK", 0)
    saves = stats.get("SAVE", 0)
    engagement = stats.get("ENGAGEMENT", 0)

    ctr = (clicks / impressions * 100) if impressions else 0

    return (
        f"📌 Pinterest Analytics ({label})\n\n"
        f"👁️ Impressions: {impressions}\n"
        f"🔗 Clicks: {clicks}\n"
        f"💾 Saves: {saves}\n"
        f"📊 Engagement: {engagement}\n"
        f"📈 CTR: {ctr:.2f}%"
    )

@app.route("/slack", methods=["POST"])
def slack():
    command = request.form.get("command")

    if command == "/latest":
        return jsonify({"text": format_data(get_data(1), "Yesterday")})

    if command == "/weekly":
        return jsonify({"text": format_data(get_data(7), "Last 7 Days")})

    if command == "/monthly":
        return jsonify({"text": format_data(get_data(30), "Last 30 Days")})

    if command == "/2months":
        return jsonify({"text": format_data(get_data(60), "Last 60 Days")})

    return jsonify({"text": "Unknown command"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)