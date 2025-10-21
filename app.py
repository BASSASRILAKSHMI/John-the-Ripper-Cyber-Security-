from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os
import re
import tempfile
import sys

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Use env var for portability; fallback to your hardcoded path
JOHN_PATH = os.environ.get('JOHN_PATH', r"C:\Users\DEVI B\Downloads\john-1.9.0-jumbo-1-win64\john-1.9.0-jumbo-1-win64\run\john.exe")
WORDLIST_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "rockyou.txt"))  # Absolute path

# Small fallback wordlist (common passwords for demo)
FALLBACK_WORDS = [
    "password", "123456", "12345678", "qwerty", "abc123", "Password1", "admin", "letmein",
    "welcome", "monkey", "dragon", "master", "hello", "freedom", "whatever", "qazwsx",
    "trustno1", "ninja", "abcde", "000000"
]

def get_wordlist_path():
    """Return absolute wordlist path; create fallback if rockyou missing."""
    if os.path.exists(WORDLIST_PATH):
        print("Using rockyou.txt wordlist")
        return WORDLIST_PATH
    else:
        # Create temp fallback
        fallback_path = os.path.join(UPLOAD_FOLDER, "fallback_wordlist.txt")
        with open(fallback_path, 'w') as f:
            f.write('\n'.join(FALLBACK_WORDS) + '\n')
        abs_fallback = os.path.abspath(fallback_path)  # Make absolute
        print("Using fallback wordlist (small, 20 common passwords)")
        return abs_fallback

def detect_format(line):
    """Detect hash type based on line content."""
    hash_part = line.split(':', 1)[1] if ':' in line else line
    if hash_part.startswith('$1$'):
        return 'md5crypt'
    elif re.match(r'^[0-9a-fA-F]{32}$', hash_part):
        return 'raw-md5'
    elif hash_part.startswith('$6$'):
        return 'sha512crypt'
    else:
        return None

def clean_and_split_hash_file(filepath):
    """Clean and split into format-specific temp files."""
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    formats = {
        'md5crypt': [],
        'raw-md5': [],
        'sha512crypt': []
    }
    for line in lines:
        fmt = detect_format(line)
        if fmt and fmt in formats:
            formats[fmt].append(line)
        else:
            print(f"Skipping unsupported line: {line}")
    
    temp_files = {}
    for fmt, flines in formats.items():
        if flines:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.txt', dir=UPLOAD_FOLDER)
            with os.fdopen(temp_fd, 'w') as tf:
                tf.write('\n'.join(flines) + '\n')
            temp_files[fmt] = temp_path
            print(f"Created temp for {fmt}: {len(flines)} lines")
    
    print(f"Split into {len(temp_files)} format files")
    return temp_files

@app.route("/")
def index():
    """Serve the frontend index.html at root."""
    return send_from_directory(os.path.join(os.path.dirname(__file__), "../frontend"), "index.html")

@app.route("/crack", methods=["POST"])
def crack():
    if 'hashfile' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['hashfile']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    temp_files = clean_and_split_hash_file(filepath)  # Split by format

    if not temp_files:
        return jsonify({"error": "No supported hashes found."})

    # Get absolute wordlist
    wordlist = get_wordlist_path()

    # Force fresh crack: Delete pot file
    pot_dir = os.path.dirname(JOHN_PATH)
    pot_path = os.path.join(pot_dir, "john.pot")
    if os.path.exists(pot_path):
        os.remove(pot_path)
        print("Deleted john.pot for fresh run")

    all_results = []
    for fmt, temp_path in temp_files.items():
        try:
            # Run cracking (no check=True; always complete) with absolute wordlist
            cmd_crack = [JOHN_PATH, f"--wordlist={wordlist}", f"--format={fmt}", temp_path]
            print(f"Running crack cmd for {fmt}: {' '.join(cmd_crack)}")  # Debug cmd
            result_crack = subprocess.run(
                cmd_crack, 
                capture_output=True, 
                text=True, 
                stdin=subprocess.DEVNULL,  # Prevent interactive hangs
                cwd=UPLOAD_FOLDER  # Session files in uploads
            )
            print(f"Crack returncode ({fmt}): {result_crack.returncode}")
            print(f"Crack output ({fmt}): {result_crack.stdout}")
            if result_crack.stderr:
                print(f"Crack stderr ({fmt}): {result_crack.stderr}")
            
            # Always get results
            cmd_show = [JOHN_PATH, "--show", f"--format={fmt}", temp_path]
            result_show = subprocess.check_output(
                cmd_show, 
                text=True, 
                stderr=subprocess.STDOUT, 
                stdin=subprocess.DEVNULL,
                cwd=UPLOAD_FOLDER
            )
            print(f"Show output ({fmt}):\n{result_show}")
            all_results.append(result_show)
            
            # Cleanup temp
            os.unlink(temp_path)
        except Exception as e:
            print(f"Unexpected error ({fmt}): {str(e)}")
            all_results.append(f"Unexpected error in {fmt}: {str(e)}")

    combined_result = '\n'.join(all_results)
    return jsonify({"result": combined_result})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
