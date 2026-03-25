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

### Configuration

NeuroMatrix3D loads `MATRIX_DEBUG`, `MATRIX_PORT`, `MATRIX_HOST`, and `MATRIX_SESSION_SIGNING_KEY` from `.env`.

Copy `.env.example` to `.env` and adjust the values as needed:

```bash
cp .env.example .env
```

`MATRIX_PORT` controls both the host- and container-side ports so Docker mappings stay in sync.

Example `.env.example`:

```dotenv
MATRIX_DEBUG="false"
MATRIX_PORT="5000"
MATRIX_HOST="0.0.0.0"
MATRIX_SESSION_SIGNING_KEY="changeme"
```

### Environment Variables

| Variable                     | Default    | Purpose                                             |
|------------------------------|------------|-----------------------------------------------------|
| `MATRIX_DEBUG`               | `false`    | Flask debug mode                                    |
| `MATRIX_PORT`                | `5000`     | Port Flask listens on and the port Docker publishes |
| `MATRIX_HOST`                | `0.0.0.0`  | Network interface Flask binds to                    |
| `MATRIX_SESSION_SIGNING_KEY` | `changeme` | Flask session-signing secret                        |

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

Access the application at `http://localhost:5000` and enter text to generate braille models (or
`http://localhost:<MATRIX_PORT>` when overridden via `.env`).

## Architecture Overview

1. Text input is translated to braille using liblouis (UEB Grade 2)
2. Braille patterns are converted to dot position lists
3. OpenSCAD renders the 3D model with appropriate dot heights
4. STL file is generated for 3D printing

## Braille Standard

UEB Grade 2 (Unified English Braille Grade 2) is the standard contracted braille format that uses abbreviations and
contractions to reduce reading volume while maintaining readability.

## License

NeuroMatrix3D is licensed under the [MIT License](./LICENSE).
