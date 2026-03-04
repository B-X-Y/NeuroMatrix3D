FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3 \
    python3-louis \
    openscad \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY matrix_pipeline.py .
COPY matrix_generator.scad .

CMD ["python3", "matrix_pipeline.py"]
