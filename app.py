from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os
import re
import logging

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to strip ANSI escape sequences
def strip_ansi_sequences(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the root route
@app.route('/')
def home():
    return "Nuclei Web GUI Backend is running!"

# Define the /run-nuclei route
@app.route('/run-nuclei', methods=['POST'])
def run_nuclei():
    data = request.json
    urls = data.get('urls')

    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    try:
        # Step 1: Save the URLs to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(urls)
            temp_file_path = temp_file.name

        # Step 2: Specify the full path to the nuclei executable
        # nuclei_path = "C:\\Users\\Muhammad Waseem\\go\\bin\\nuclei.exe"  # Your Nuclei path
        nuclei_path = "/root/go/bin/nuclei"  # Your Nuclei path

        # Step 3: Construct the Nuclei command
        command_list = [
            nuclei_path,
            "-l", temp_file_path,  # Use the temporary file as the URL list
            "-s", "low,medium,high,critical",  # Specify severity levels
            "-verbose"  # Enable verbose output
        ]

        # Step 4: Execute the Nuclei command
        result = subprocess.run(command_list, capture_output=True, text=True)

        # Step 5: Delete the temporary file
        os.remove(temp_file_path)

        # Step 6: Strip ANSI escape sequences from the output
        cleaned_stdout = strip_ansi_sequences(result.stdout)
        cleaned_stderr = strip_ansi_sequences(result.stderr)

        # Step 7: Log the output for debugging
        logging.debug(f"stdout: {cleaned_stdout}")
        logging.debug(f"stderr: {cleaned_stderr}")

        # Step 8: Return the cleaned output
        return jsonify({
            "stdout": cleaned_stdout,
            "stderr": cleaned_stderr,
            "returncode": result.returncode
        })
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)