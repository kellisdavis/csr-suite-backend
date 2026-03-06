import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai

app = Flask(__name__)
CORS(app)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=SYSTEM_PROMPT + "\n\nEmail:\n" + email_text,
            config={"response_mime_type": "application/json"}
        )
        extracted = json.loads(response.text)
        return jsonify({"extracted": extracted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
