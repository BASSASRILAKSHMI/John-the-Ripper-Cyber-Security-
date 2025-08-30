from flask import Flask, request, jsonify
from flask_cors import CORS   # <-- add this
import subprocess
import os

app = Flask(__name__)
CORS(app)   # <-- enable CORS

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

JOHN_PATH = r"C:\Users\DEVI B\Downloads\john-1.9.0-jumbo-1-win64\john-1.9.0-jumbo-1-win64\run\john.exe"

@app.route("/crack", methods=["POST"])
def crack():
    file = request.files['hashfile']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        subprocess.run([JOHN_PATH, filepath], check=True, capture_output=True, text=True)
        result = subprocess.check_output([JOHN_PATH, "--show", filepath], text=True)
        return jsonify({"result": result})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr or str(e)})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
