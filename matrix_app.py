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

    def get_float_or_none(key):
        value = request.form.get(key, "")
        return float(value) if value.strip() else None

    generate_braille_model_from_text(
        text,
        output_path,
        dot_radius=get_float_or_none("dot_radius"),
        dot_spacing=get_float_or_none("dot_spacing"),
        row_spacing=get_float_or_none("row_spacing"),
        column_spacing=get_float_or_none("column_spacing"),
        page_thickness=get_float_or_none("page_thickness"),
        max_page_width=get_float_or_none("max_page_width"),
    )

    return render_template("download.html", filename=output_filename)


@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(MODELS_DIR, filename), as_attachment=True)


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)
    app.run(debug=True, host="0.0.0.0")
