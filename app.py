"""
TechHelp - Flask backend powered by the Gemini API.
Serves the chat UI and proxies chat messages to the Gemini model,
using the system prompt defined in chatbot_config.py to keep the
bot restricted to its topic.
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import BOT_NAME, SYSTEM_PROMPT, GREETING_MESSAGE

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.6-flash"

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", bot_name=BOT_NAME, greeting=GREETING_MESSAGE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message first."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text if response and response.text else \
            "Sorry, I couldn't generate a response. Please try again."
    except Exception as exc:
        reply_text = f"Something went wrong talking to the model: {exc}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
