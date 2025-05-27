from flask import Flask, request, jsonify, send_from_directory
import os
import subprocess
import uuid
from threading import Thread

app = Flask(__name__)

SAVE_DIR = "Saved"
os.makedirs(SAVE_DIR, exist_ok=True)

def run_conversion(url, filename):
    full_path = os.path.join(SAVE_DIR, filename)
    cmd = [
        "streamlink", url, "best",
        "-o", full_path
    ]
    print(f"[DEBUG] Running streamlink command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[DEBUG] streamlink finished with return code {result.returncode}")
        if result.stdout:
            print("[STDOUT]", result.stdout.decode())
        if result.stderr:
            print("[STDERR]", result.stderr.decode())
    except Exception as e:
        print(f"[ERROR] streamlink crashed: {e}")

@app.route("/")
def home():
    return jsonify({"status": "Video Converter Server is running."})

@app.route("/convert", methods=["POST"])
def convert_video():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' field"}), 400

    print(f"[DEBUG] Received video URL: {url}")

    # Generate unique filename
    filename = f"{uuid.uuid4().hex}.mp4"

    # Start background thread
    Thread(target=run_conversion, args=(url, filename)).start()

    download_url = f"{request.url_root}Saved/{filename}"
    return jsonify({
        "message": "Conversion started.",
        "download_url": download_url
    })

@app.route("/Saved/<path:filename>")
def serve_file(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

