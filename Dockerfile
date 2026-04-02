FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-louis \
    openscad \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY matrix_pipeline.py .
COPY matrix_generator.scad .
COPY matrix_app.py .
COPY static ./static
COPY templates ./templates

CMD ["python3", "matrix_app.py"]
