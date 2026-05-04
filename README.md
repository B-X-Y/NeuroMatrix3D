<h1 align="center">NeuroMatrix3D</h1>

<h4 align="center">⠠⠝⠑⠥⠗⠕⠠⠍⠁⠞⠗⠊⠭⠼⠉⠰⠠⠙</h4>

<p align="center">
    <i>A web application that converts text into 3D printable braille models for tactile reading.</i>
</p>

<p align="center">
    <img src="assets/icon-light.svg" alt="NeuroMatrix3D Logo" width="300">
</p>

---

## Project Overview
[Open STL](./NeuroMatrix3D.stl)
NeuroMatrix3D takes plain text input and generates downloadable STL files representing the text in braille format. The
3D models can be printed on standard 3D printers to create tactile reading materials.

## Tech Stack

- **[Flask](https://github.com/pallets/flask)**: Web framework
- **[liblouis](https://github.com/liblouis/liblouis)**: Braille translation
- **[OpenSCAD](https://github.com/openscad/openscad)**: 3D model generation

## Installation & Setup

### Configuration

NeuroMatrix3D loads `MATRIX_SERVER_NAME`, `MATRIX_URL_SCHEME`, `MATRIX_DEBUG`, `MATRIX_PORT`, `MATRIX_HOST`,
`MATRIX_SESSION_SIGNING_KEY`, and `MATRIX_RATE_LIMIT_ENABLED` from `.env`.

Copy `.env.example` to `.env` and adjust the values as needed:

```bash
cp .env.example .env
```

`MATRIX_PORT` controls both the host- and container-side ports so Docker mappings stay in sync.

Example `.env.example`:

```dotenv
MATRIX_SERVER_NAME="localhost"
MATRIX_URL_SCHEME="http"
MATRIX_DEBUG="false"
MATRIX_PORT="5000"
MATRIX_HOST="0.0.0.0"
MATRIX_SESSION_SIGNING_KEY="changeme"
MATRIX_RATE_LIMIT_ENABLED="true"
```

### Environment Variables

| Variable                     | Default     | Purpose                                                         |
|------------------------------|-------------|-----------------------------------------------------------------|
| `MATRIX_SERVER_NAME`         | `localhost` | Public hostname or domain used by the application               |
| `MATRIX_URL_SCHEME`          | `http`      | URL scheme (`http` or `https`) used to construct external links |
| `MATRIX_DEBUG`               | `false`     | Flask debug mode                                                |
| `MATRIX_PORT`                | `5000`      | Port Flask listens on and the port Docker publishes             |
| `MATRIX_HOST`                | `0.0.0.0`   | Network interface Flask binds to                                |
| `MATRIX_SESSION_SIGNING_KEY` | `changeme`  | Flask session-signing secret                                    |
| `MATRIX_RATE_LIMIT_ENABLED`  | `true`      | Enables or disables Flask request rate limiting                 |

### Local Development

```bash
apt update && apt install -y git python3 python3-pip python3-louis openscad

git clone https://github.com/B-X-Y/NeuroMatrix3D.git
cd NeuroMatrix3D

python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python3 matrix_app.py
```

### Docker Deployment

```bash
apt update && apt install -y git

git clone https://github.com/B-X-Y/NeuroMatrix3D.git
cd NeuroMatrix3D

docker compose up -d --build
```

### Accessing the Application

Access the application at `http://localhost:5000` and enter text to generate braille models (or
`http://<MATRIX_SERVER_NAME>:<MATRIX_PORT>` when overridden via `.env`).

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
