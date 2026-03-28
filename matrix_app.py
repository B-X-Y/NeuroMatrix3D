import os
import secrets
import time
import uuid
from threading import Semaphore

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request, send_file, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from matrix_pipeline import generate_braille_model_from_text

load_dotenv()


def _get_env_str(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or not value.strip():
        return None
    return value.strip()


def _parse_bool_env(name: str, default: bool) -> bool:
    stripped_value = _get_env_str(name)
    if stripped_value is None:
        return default
    return stripped_value.lower() == "true"


def _parse_int_env(name: str, default: int) -> int:
    stripped_value = _get_env_str(name)
    if stripped_value is None:
        return default
    try:
        return int(stripped_value)
    except ValueError:
        return default


app = Flask(__name__)
app.config["SECRET_KEY"] = _get_env_str("MATRIX_SESSION_SIGNING_KEY") or secrets.token_urlsafe(32)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
gen_semaphore = Semaphore(2)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
TEMP_FILE_TTL_SECONDS = 600
MAX_TEXT_LENGTH = 800


def _cleanup_expired_temporary_models() -> None:
    os.makedirs(MODELS_DIR, exist_ok=True)
    cutoff = time.time() - TEMP_FILE_TTL_SECONDS

    for entry in os.scandir(MODELS_DIR):
        if not entry.is_file() or not entry.name.endswith(".stl"):
            continue

        try:
            if entry.stat().st_mtime < cutoff:
                os.remove(entry.path)
        except FileNotFoundError:
            continue


def _get_or_create_session_id() -> str:
    existing_session_id = session.get("session_id")
    if isinstance(existing_session_id, str) and existing_session_id.strip():
        return existing_session_id

    new_session_id = uuid.uuid4().hex
    session["session_id"] = new_session_id
    return new_session_id


@app.route("/")
@limiter.limit("300/minute", error_message="Please try again later.")
def index():
    _cleanup_expired_temporary_models()
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
@limiter.limit("120/hour", error_message="Please try again later.")
@limiter.limit("20/hour;2/minute", key_func=_get_or_create_session_id, error_message="Please try again later.")
def generate():
    _cleanup_expired_temporary_models()
    text = request.form.get("text", "")
    if len(text) > MAX_TEXT_LENGTH:
        abort(400, description="Text exceeds maximum length.")
    semaphore_acquired = gen_semaphore.acquire(blocking=False)
    if not semaphore_acquired:
        abort(503, description="Please try again later.")
    session_id = _get_or_create_session_id()
    generation_id = uuid.uuid4().hex[:7]
    output_filename = f"braille_model_{session_id[:7]}_{generation_id}.stl"
    output_path = os.path.join(MODELS_DIR, output_filename)

    def get_float_or_none(key):
        value = request.form.get(key, "")
        return float(value) if value.strip() else None

    try:
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
    finally:
        gen_semaphore.release()

    generated_files = session.get("generated_files")
    if not isinstance(generated_files, list):
        generated_files = []
    generated_files.append(output_filename)
    session["generated_files"] = generated_files[-3:]

    return render_template("download.html", filename=output_filename)


@app.route("/download/<filename>")
@limiter.limit("120/minute", error_message="Please try again later.")
@limiter.limit("20/minute", key_func=_get_or_create_session_id, error_message="Please try again later.")
def download(filename):
    _cleanup_expired_temporary_models()
    generated_files = session.get("generated_files")
    if not isinstance(generated_files, list) or filename not in generated_files:
        abort(404)

    return send_file(os.path.join(MODELS_DIR, filename), as_attachment=True)


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)
    host = os.getenv("MATRIX_HOST", "0.0.0.0")
    port = _parse_int_env("MATRIX_PORT", 5000)
    debug = _parse_bool_env("MATRIX_DEBUG", False)
    app.run(host=host, port=port, debug=debug)
