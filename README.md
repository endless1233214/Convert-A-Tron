# Convert-A-Tron

A privacy-focused, self-hosted file conversion web app built for Docker, home servers, and NAS platforms such as TrueNAS SCALE.

Convert images, audio, video, documents, and PDFs without uploading your files to a third-party service. All processing happens inside your own container, and temporary files are automatically removed.

## Features

### Images

* Convert between JPG, PNG, WebP, BMP, GIF, and TIFF
* Remove image metadata and EXIF data
* Browse supported image formats through dedicated converter pages

### Audio and video

* Convert audio and video files using FFmpeg
* Browse supported audio and video formats
* Process files entirely inside the container

### Documents and PDFs

* Convert supported Office documents to PDF using LibreOffice
* Merge multiple PDF files
* Convert PDF pages into PNG images packaged as a ZIP archive
* Process PDF files using Python libraries and Poppler

### Platform and security

* Dedicated pages for each supported input format
* Configurable upload limits
* Sanitized filenames
* Randomized, isolated job directories
* Automatic cleanup of expired jobs
* Built-in health endpoint
* Interactive API documentation
* Runs as a non-root user
* Drops unnecessary Linux capabilities
* Supports a read-only root filesystem
* Requires no database or user account

## Quick Start

### Docker Compose

Clone the repository and start the container:

```bash
git clone https://github.com/endless1233214/Convert-A-Tron.git
cd Convert-A-Tron
docker compose up -d --build
```

Open the app in your browser:

```text
http://YOUR-SERVER-IP:8080
```

To stop the container:

```bash
docker compose down
```

### Published Docker image

The latest multi-platform image is published to GitHub Container Registry:

```text
ghcr.io/endless1233214/convert-a-tron:latest
```

Example Compose configuration:

```yaml
services:
  convert-a-tron:
    image: ghcr.io/endless1233214/convert-a-tron:latest
    container_name: convert-a-tron
    restart: unless-stopped

    ports:
      - "${CONVERT_A_TRON_PORT:-8080}:8080"

    environment:
      MAX_UPLOAD_MB: "${MAX_UPLOAD_MB:-500}"
      JOB_TTL_MINUTES: "${JOB_TTL_MINUTES:-60}"

    volumes:
      - convert-a-tron-data:/data

    read_only: true

    tmpfs:
      - /tmp

    cap_drop:
      - ALL

volumes:
  convert-a-tron-data:
```

Start it with:

```bash
docker compose up -d
```

This same Compose configuration can be used with Docker management interfaces that accept standard Compose files.

## Configuration

Convert-A-Tron supports the following environment variables:

| Variable              | Default | Description                                     |
| --------------------- | ------: | ----------------------------------------------- |
| `CONVERT_A_TRON_PORT` |  `8080` | Host port used to access the web interface      |
| `MAX_UPLOAD_MB`       |   `500` | Maximum allowed upload size in megabytes        |
| `JOB_TTL_MINUTES`     |    `60` | Time abandoned jobs are retained before cleanup |

Example `.env` file:

```dotenv
CONVERT_A_TRON_PORT=8080
MAX_UPLOAD_MB=500
JOB_TTL_MINUTES=60
```

## Local Development

Create a Python virtual environment and install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the development server:

```bash
uvicorn app.main:app --reload --port 8080
```

The following system packages must be installed locally to enable their associated conversion features:

* **FFmpeg** for audio and video conversion
* **LibreOffice** for Office document conversion
* **Poppler** for converting PDF pages into images

Image conversion and PDF merging are handled directly through Python libraries.

## Privacy

Convert-A-Tron is designed to keep file processing under your control.

* No analytics
* No telemetry
* No advertisements
* No third-party conversion APIs
* No user database
* No account required
* No permanent file storage by default
* Each job is isolated inside a randomly generated directory
* Completed jobs are removed after their response is sent
* Abandoned jobs are automatically removed after the configured TTL

Files never need to leave the system running Convert-A-Tron.

> [!WARNING]
> Convert-A-Tron does not currently include built-in authentication. Do not expose it directly to the public internet.
>
> For remote access, place it behind a trusted reverse proxy with authentication, HTTPS, request-size limits, and rate limiting.

## Container Design

The container:

* Listens on port `8080`
* Runs as UID and GID `568`
* Stores temporary job data beneath `/data/jobs`
* Exposes a health endpoint at `/health`
* Requires no privileged mode
* Requires no host networking
* Requires no database
* Requires no outbound conversion service

The application is designed to work well on regular Docker hosts, home servers, and NAS systems such as TrueNAS SCALE.

## API

Interactive OpenAPI documentation is available at:

```text
http://YOUR-SERVER-IP:8080/docs
```

Primary endpoints include:

| Method | Endpoint                  | Description                                        |
| ------ | ------------------------- | -------------------------------------------------- |
| `GET`  | `/convert/{input_format}` | Open a converter page for a supported input format |
| `POST` | `/api/convert`            | Convert an uploaded file                           |
| `POST` | `/api/strip-metadata`     | Remove metadata from an image                      |
| `POST` | `/api/merge-pdf`          | Merge multiple PDF files                           |
| `POST` | `/api/pdf-to-images`      | Convert PDF pages into a ZIP of PNG images         |
| `GET`  | `/api/capabilities`       | List available conversion capabilities             |
| `GET`  | `/health`                 | Check application health                           |

## Updating

Pull the latest image and recreate the container:

```bash
docker compose pull
docker compose up -d
```

When building directly from the repository:

```bash
git pull
docker compose up -d --build
```

## Roadmap

Planned and potential improvements include:

* Batch conversion
* Drag-and-drop conversion queues
* Archive creation and extraction tools
* PDF splitting
* PDF compression
* OCR
* Conversion presets
* Optional watch folders
* API key support
* Additional format support
* Formal TrueNAS catalog integration

## Contributing

Issues, bug reports, feature requests, and pull requests are welcome.

When reporting a problem, include:

* The conversion type
* The input and output formats
* Relevant container logs
* Your Docker and host operating system versions
* Steps that reproduce the issue

## License

See the repository’s license file for usage and distribution terms.
