# NeuroMatrix3D

A web application that converts text into 3D printable braille models for tactile reading.

## Project Overview

NeuroMatrix3D takes plain text input and generates downloadable STL files representing the text in braille format. The
3D models can be printed on standard 3D printers to create tactile reading materials.

## Tech Stack

- **[Flask](https://github.com/pallets/flask)**: Web framework
- **[liblouis](https://github.com/liblouis/liblouis)**: Braille translation
- **[OpenSCAD](https://github.com/openscad/openscad)**: 3D model generation

## Installation & Setup

### Local Development

```bash
apt update && apt install -y python3 python3-pip python3-louis openscad
pip install -r requirements.txt
python3 matrix_app.py
```

### Docker Deployment

```bash
docker compose up -d --build
```

### Accessing the Application

Access the application at `http://localhost:5000` and enter text to generate braille models.

## Architecture Overview

1. Text input is translated to braille using liblouis (UEB Grade 2)
2. Braille patterns are converted to dot position lists
3. OpenSCAD renders the 3D model with appropriate dot heights
4. STL file is generated for 3D printing

## Braille Standard

UEB Grade 2 (Unified English Braille Grade 2) is the standard contracted braille format that uses abbreviations and
contractions to reduce reading volume while maintaining readability.
