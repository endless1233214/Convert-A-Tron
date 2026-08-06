# Convert-A-Tron

A privacy-first, self-hosted file conversion web app designed for Docker and NAS systems such as TrueNAS SCALE. Files are processed inside your own container and temporary job directories are deleted after download.

## Included MVP tools

- Dedicated converter pages for each supported input format
- Browsable image, audio, video, and document format catalog
- Image conversion: JPG, PNG, WebP, BMP, GIF, TIFF
- Image metadata/EXIF removal
- Audio/video conversion through FFmpeg
- Office documents to PDF through LibreOffice
- Merge multiple PDF files
- PDF pages to PNG ZIP through Poppler
- Upload limits, sanitized filenames, health endpoint, automatic stale-job cleanup
- Non-root container, dropped Linux capabilities, read-only root filesystem in Compose

## Run with Docker Compose

```bash
docker compose up -d --build
```

Open `http://YOUR-SERVER-IP:8080`.

## Run with Dockge

The `compose.dockge.yml` file pulls the published multi-platform image from GitHub Container Registry and does not require the source repository on the Docker host.

1. Create a stack named `convert-a-tron` in Dockge.
2. Paste the contents of `compose.dockge.yml` into the Compose editor.
3. Optionally paste the following into the `.env` editor:

```dotenv
CONVERT_A_TRON_PORT=8080
MAX_UPLOAD_MB=500
JOB_TTL_MINUTES=60
```

4. Deploy the stack and open `http://YOUR-SERVER-IP:8080`.

The GitHub Actions workflow publishes `ghcr.io/endless1233214/convert-a-tron:latest` whenever the `main` branch is updated. The package must be public for Dockge to pull it without registry credentials.

## Run locally for development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

FFmpeg, LibreOffice, and Poppler must be installed locally for their associated conversions. Image conversion and PDF merging use Python libraries directly.

## TrueNAS design notes

The container listens on port `8080`, runs as UID/GID `568`, stores only temporary jobs beneath `/data/jobs`, exposes `/health`, and requires no database, account, privileged mode, host networking, or outbound API service. A future TrueNAS catalog chart can expose `MAX_UPLOAD_MB`, `JOB_TTL_MINUTES`, port, resource limits, and `/data` storage.

## Privacy model

- No analytics or telemetry
- No third-party conversion APIs
- No user database
- Files are scoped to random job directories
- Completed jobs are removed after their response is sent
- Abandoned jobs are pruned after the configured TTL

Do not expose the app directly to the public internet without adding authentication and a trusted reverse proxy with request-size and rate limits.

## API

Interactive documentation is available at `/docs`. Primary endpoints:

- `GET /convert/{input_format}`
- `POST /api/convert`
- `POST /api/strip-metadata`
- `POST /api/merge-pdf`
- `POST /api/pdf-to-images`
- `GET /api/capabilities`
- `GET /health`

## Roadmap

Batch conversion, archive tools, PDF split/compression, OCR, drag-and-drop queues, conversion presets, optional watch folders, API keys, and a formal TrueNAS catalog chart.
