FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-louis \
    openscad \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY matrix_pipeline.py .
COPY matrix_generator.scad .
COPY matrix_app.py .
COPY static ./static
COPY templates ./templates

CMD ["bash", "-c", "gunicorn -w 1 --threads 2 -b ${MATRIX_HOST:-0.0.0.0}:${MATRIX_PORT:-5000} matrix_app:app"]
