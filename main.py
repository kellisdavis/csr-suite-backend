import os
import json
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a data extraction assistant for court reporters. Extract job details from booking emails. Return ONLY a JSON object with these exact keys: case_number, case_caption, deponent, job_date (YYYY-MM-DD), job_time (HH:MM), timezone, location, delivery_intent, noticing_party_name, payer_email. If a field is not found, return null for that field. Do not include any explanation or text outside the JSON object.

For delivery_intent, only use one of: standard, rough, expedited, same_day, next_day. If unclear, use null.
For timezone, use IANA format like America/Los_Angeles, America/New_York, etc. If unclear, use null."""

@app.route("/")
def index():
    return jsonify({"status": "CSR Suite Backend is running"})

@app.route("/extract-email", methods=["POST", "OPTIONS"])
def extract_email():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response
    try:
        data = request.get_json()
        email_text = data.get("emailText")
        if not email_text:
            return jsonify({"error": "emailText is required"}), 400
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            f"{SYSTEM_PROMPT}\n\nEmail:\n{email_text}",
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        extracted = json.loads(response.text)
        resp = jsonify({"extracted": extracted})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
