from flask import Flask, request, jsonify
import sqlite3
import subprocess
import bcrypt
import os
import logging
import re

app = Flask(__name__)

# ==============================
# 🔐 Secure configuration
# ==============================

API_KEY = os.getenv("API_KEY", "default-key")  # secret via env var

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DATABASE = "users.db"

# ==============================
# 🗄 Database helper
# ==============================

def get_db():
    return sqlite3.connect(DATABASE)

# ==============================
# 🔐 Auth endpoint (SQL Injection FIX)
# ==============================

@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "").encode()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password, row[0]):
        return jsonify({"status": "authenticated"})

    return jsonify({"status": "denied"}), 401

# ==============================
# 🚫 Command Injection FIX
# ==============================

@app.route("/ping", methods=["POST"])
def ping():
    data = request.get_json()
    host = data.get("host", "")

    # validation stricte
    if not re.match(r"^[a-zA-Z0-9.\-]+$", host):
        return jsonify({"error": "Invalid host"}), 400

    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True
    )

    return jsonify({"output": result.stdout})

# ==============================
# 🔐 Strong hashing (MD5 FIX)
# ==============================

@app.route("/hash", methods=["POST"])
def hash_text():
    text = request.get_json().get("text", "").encode()

    hashed = bcrypt.hashpw(text, bcrypt.gensalt())
    return jsonify({"bcrypt": hashed.decode()})

# ==============================
# 🚫 Path Traversal FIX
# ==============================

@app.route("/file", methods=["POST"])
def read_file():
    filename = request.get_json().get("filename", "")

    # whitelist
    allowed_files = ["example.txt"]

    if filename not in allowed_files:
        return jsonify({"error": "Access denied"}), 403

    with open(filename, "r", encoding="utf-8") as f:
        return jsonify({"content": f.read()})

# ==============================
# 🚫 Info disclosure FIX
# ==============================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# ==============================
# 🚫 Log Injection FIX
# ==============================

@app.route("/log", methods=["POST"])
def log_data():
    data = request.get_json()
    logging.info("User request received")
    return jsonify({"status": "logged"})

# ==============================
# 🚀 App start
# ==============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
