import os
import uuid

from flask import Flask, render_template, request, send_file

from matrix_pipeline import generate_braille_model_from_text

app = Flask(__name__)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    text = request.form.get("text", "")
    session_id = str(uuid.uuid4())
    output_filename = f"braille_model_{session_id}.stl"
    output_path = os.path.join(MODELS_DIR, output_filename)

    generate_braille_model_from_text(text, output_path)

    return render_template("download.html", filename=output_filename)


@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(MODELS_DIR, filename), as_attachment=True)


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)
    app.run(debug=True, host="0.0.0.0")
