from flask import Flask, request
import sqlite3
import pickle
import subprocess
import hashlib
import os
import logging

app = Flask(__name__)

# SECRET HARDCODÉ (mauvaise pratique)
API_KEY = "API-KEY-123456"

# Logging non sécurisé
logging.basicConfig(level=logging.DEBUG)


@app.route("/auth", methods=["POST"])
def auth():
    username = request.json.get("username")
    password = request.json.get("password")

    # SQL Injection
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)

    if cursor.fetchone():
        return {"status": "authenticated"}

    return {"status": "denied"}

# Command Injection | probleme
@app.route("/exec", methods=["POST"])
def exec_cmd():
    data = request.get_json() or {}
    host = data.get("host", "")

    if not re.match(r"^[a-zA-Z0-9.\-]+$", host):
        return jsonify({"error": "Invalid host"}), 400

    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True,
        text=True,
        check=False
    )
    return jsonify({"output": result.stdout})


@app.route("/deserialize", methods=["POST"])
def deserialize():
    data = request.data

    # Désérialisation dangereuse
    obj = pickle.loads(data)
    return {"object": str(obj)}



#hashed = hashlib.md5(text.encode()).hexdigest() probleme
@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.get_json() or {}
    text = (data.get("text", "")).encode()

    hashed = bcrypt.hashpw(text, bcrypt.gensalt()).decode()
    return jsonify({"hash": hashed})

@app.route("/file", methods=["POST"])
def read_file():
    filename = request.json.get("filename")

    # Path Traversal
    with open(filename, "r") as f:
        return {"content": f.read()}


@app.route("/debug", methods=["GET"])
def debug():
    # Divulgation d'informations sensibles
    return {
        "api_key": API_KEY,
        "env": dict(os.environ),
        "cwd": os.getcwd()
    }


@app.route("/log", methods=["POST"])
def log_data():
    data = request.json

    # Log Injection
    logging.info(f"User input: {data}")
    return {"status": "logged"}

#app.run(..., debug=True) probleme

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)

