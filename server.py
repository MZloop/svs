from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import uuid

app = Flask(__name__)

# Create 'Saved' directory if it doesn't exist
SAVE_FOLDER = os.path.join(os.getcwd(), 'Saved')
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return "Flask video converter server running."

@app.route("/convert", methods=["POST"])
def convert_video():
    try:
        data = request.get_json()
        video_url = data.get("url")
        print(f"[DEBUG] Received video URL: {video_url}")  # Debug print

        if not video_url:
            return jsonify({"error": "Missing 'url' in request"}), 400

        # Unique filename to avoid collisions
        filename = f"video_{uuid.uuid4().hex[:8]}.mp4"
        full_path = os.path.join(SAVE_FOLDER, filename)

        # Streamlink command to download m3u8 as mp4
        result = subprocess.run(
            [
                "streamlink",
                "--stream-segment-attempts", "10",
                "--stream-segment-threads", "4",
                video_url,
                "best",
                "-o", full_path
            ],
            capture_output=True,
            text=True
        )

        print("[DEBUG] Streamlink stdout:", result.stdout)
        print("[DEBUG] Streamlink stderr:", result.stderr)

        if result.returncode != 0:
            return jsonify({
                "error": "Failed to convert video",
                "details": result.stderr
            }), 500

        # Return the download link to the client
        return jsonify({
            "download_url": f"http://{request.host}/Saved/{filename}",
            "filename": filename
        })

    except Exception as e:
        print("[ERROR] Server exception:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/Saved/<path:filename>", methods=["GET"])
def serve_video(filename):
    return send_from_directory(SAVE_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
