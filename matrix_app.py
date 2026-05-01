import os
import secrets
import subprocess
import time
import uuid
from threading import Lock, Semaphore, Thread

from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, render_template, request, send_file, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

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
server_name = _get_env_str("MATRIX_SERVER_NAME")
if server_name:
    app.config["SERVER_NAME"] = server_name
url_scheme = _get_env_str("MATRIX_URL_SCHEME")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
if _parse_bool_env("MATRIX_RATE_LIMIT_ENABLED", True):
    limiter = Limiter(get_remote_address, app=app, default_limits=[])
else:
    class UnlimitedLimiter:
        @staticmethod
        def limit(*args, **kwargs):
            return lambda f: f


    limiter = UnlimitedLimiter()
MAX_CONCURRENT_GENERATIONS = 2
MAX_QUEUE_SIZE = 5

gen_semaphore = Semaphore(MAX_CONCURRENT_GENERATIONS)
job_lock = Lock()
generation_jobs: dict[str, dict[str, float | str | None]] = {}

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
TEMP_FILE_TTL_SECONDS = 600
GEN_TIMEOUT_SECONDS = 180
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

    with job_lock:
        expired_job_ids: list[str] = []
        for job_id, job in list(generation_jobs.items()):
            created_at = job.get("created_at")
            status = job.get("status")
            if isinstance(created_at, (int, float)) and created_at < cutoff and status != "running":
                expired_job_ids.append(job_id)

        for job_id in expired_job_ids:
            generation_jobs.pop(job_id, None)


def _get_or_create_session_id() -> str:
    existing_session_id = session.get("session_id")
    if isinstance(existing_session_id, str) and existing_session_id.strip():
        return existing_session_id

    new_session_id = uuid.uuid4().hex
    session["session_id"] = new_session_id
    return new_session_id


def _run_generation_job(
        job_id: str,
        text: str,
        output_path: str,
        dot_radius: float | None,
        dot_spacing: float | None,
        row_spacing: float | None,
        column_spacing: float | None,
        page_thickness: float | None,
        max_page_width: float | None,
) -> None:
    gen_semaphore.acquire()

    with job_lock:
        job = generation_jobs.get(job_id)
        if job is None:
            gen_semaphore.release()
            return
        job["status"] = "running"

    try:
        generate_braille_model_from_text(
            text,
            output_path,
            dot_radius=dot_radius,
            dot_spacing=dot_spacing,
            row_spacing=row_spacing,
            column_spacing=column_spacing,
            page_thickness=page_thickness,
            max_page_width=max_page_width,
            gen_timeout_seconds=GEN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        if os.path.exists(output_path):
            os.remove(output_path)
        with job_lock:
            job = generation_jobs.get(job_id)
            if job is not None:
                job["status"] = "error"
                job["error"] = "Generation timed out."
    except Exception:
        if os.path.exists(output_path):
            os.remove(output_path)
        with job_lock:
            job = generation_jobs.get(job_id)
            if job is not None:
                job["status"] = "error"
                job["error"] = "Generation failed."
    else:
        with job_lock:
            job = generation_jobs.get(job_id)
            if job is not None:
                job["status"] = "done"
                job["error"] = None
    finally:
        gen_semaphore.release()


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
    session_id = _get_or_create_session_id()
    generation_id = uuid.uuid4().hex[:7]
    job_id = uuid.uuid4().hex
    output_filename = f"braille_model_{session_id[:7]}_{generation_id}.stl"
    output_path = os.path.join(MODELS_DIR, output_filename)

    def get_float_or_none(key):
        value = request.form.get(key, "").strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            abort(400, description="Invalid value.")

    dot_radius = get_float_or_none("dot_radius")
    dot_spacing = get_float_or_none("dot_spacing")
    row_spacing = get_float_or_none("row_spacing")
    column_spacing = get_float_or_none("column_spacing")
    page_thickness = get_float_or_none("page_thickness")
    max_page_width = get_float_or_none("max_page_width")

    with job_lock:
        pending_jobs = sum(1 for job in generation_jobs.values() if job.get("status") == "pending")
        if pending_jobs >= MAX_QUEUE_SIZE:
            abort(503, description="Generation queue is full. Please try again later.")

        generation_jobs[job_id] = {
            "status": "pending",
            "error": None,
            "filename": output_filename,
            "session_id": session_id,
            "created_at": time.time(),
        }

    generation_thread = Thread(
        target=_run_generation_job,
        args=(
            job_id,
            text,
            output_path
        ),
        kwargs={
            "dot_radius": dot_radius,
            "dot_spacing": dot_spacing,
            "row_spacing": row_spacing,
            "column_spacing": column_spacing,
            "page_thickness": page_thickness,
            "max_page_width": max_page_width,
        },
        daemon=True
    )
    generation_thread.start()

    generated_files = session.get("generated_files")
    if not isinstance(generated_files, list):
        generated_files = []
    generated_files.append(output_filename)
    session["generated_files"] = generated_files[-3:]

    return render_template("download.html", filename=output_filename, job_id=job_id)


@app.route("/status/<job_id>")
@limiter.limit("420/minute", error_message="Please try again later.")
@limiter.limit("70/minute", key_func=_get_or_create_session_id, error_message="Please try again later.")
def generation_status(job_id):
    _cleanup_expired_temporary_models()
    session_id = _get_or_create_session_id()
    with job_lock:
        job = generation_jobs.get(job_id)

    if job is None or job.get("session_id") != session_id:
        return jsonify({"status": "expired", "error": "Generation job not found."})

    status = job.get("status")
    if not isinstance(status, str):
        status = "error"

    error = job.get("error")
    if error is not None and not isinstance(error, str):
        error = "Generation failed."

    return jsonify(
        {
            "status": status,
            "error": error
        }
    )


@app.route("/download/<filename>")
@limiter.limit("120/minute", error_message="Please try again later.")
@limiter.limit("20/minute", key_func=_get_or_create_session_id, error_message="Please try again later.")
def download(filename):
    _cleanup_expired_temporary_models()
    generated_files = session.get("generated_files")
    if not isinstance(generated_files, list) or filename not in generated_files:
        abort(404, description="File not found or no longer available.")

    try:
        return send_file(os.path.join(MODELS_DIR, filename), as_attachment=True)
    except FileNotFoundError:
        abort(404, description="File expired or already removed.")


@app.route("/robots.txt")
def robots():
    sitemap_url = url_for("sitemap", _scheme=url_scheme, _external=True)
    return Response(
        render_template("robots.txt", sitemap_url=sitemap_url),
        mimetype="text/plain"
    )


@app.route("/sitemap.xml")
def sitemap():
    pages = [
        url_for("index", _scheme=url_scheme, _external=True),
    ]
    return Response(
        render_template("sitemap.xml", pages=pages),
        mimetype="application/xml"
    )


if __name__ == "__main__":
    os.makedirs(MODELS_DIR, exist_ok=True)
    host = os.getenv("MATRIX_HOST", "0.0.0.0")
    port = _parse_int_env("MATRIX_PORT", 5000)
    debug = _parse_bool_env("MATRIX_DEBUG", False)
    app.run(host=host, port=port, debug=debug)
