import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

SYSTEM_PROMPT = (
    "You are a data extraction assistant for court reporters. "
    "Extract job details from booking emails. "
    "Return ONLY a JSON object with these exact keys: "
    "case_number, case_caption, deponent, job_date (YYYY-MM-DD), "
    "job_time (HH:MM), timezone, location, delivery_intent, "
    "noticing_party_name, payer_email. "
    "If a field is not found, return null for that field. "
    "Do not include any explanation or text outside the JSON object. "
    "For delivery_intent, only use one of: standard, rough, expedited, same_day, next_day. If unclear, use null. "
    "For timezone, use IANA format like America/Los_Angeles, America/New_York, etc. If unclear, use null."
)

@app.route("/")
def index():
    return jsonify({"status": "CSR Suite Backend is running"})

@app.route("/extract-email", methods=["POST"])
def extract_email():
    try:
        data = request.get_json()
        email_text = data.get("emailText")
        if not email_text:
            return jsonify({"error": "emailText is required"}), 400

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\nEmail:\n" + email_text}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        res = requests.post(url, json=payload)
        res.raise_for_status()
        text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        extracted = json.loads(text)
        return jsonify({"extracted": extracted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
```

Also update `requirements.txt` to remove the google package entirely:
```
flask
flask-cors
requests
gunicorn
