from __future__ import annotations

import json
import shutil
import time
import uuid
import zipfile
from html import escape
from pathlib import Path
from string import Template

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import APP_NAME, JOBS_DIR, JOB_TTL_MINUTES, MAX_UPLOAD_MB
from .converters import convert_single, pdf_merge, pdf_to_images, strip_image_metadata
from .formats import CATEGORIES, FORMATS, OUTPUT_LABELS

app = FastAPI(title=APP_NAME, version="0.3.0")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_template(name: str, **context: str) -> str:
    template = Template((TEMPLATES_DIR / name).read_text())
    return template.safe_substitute(context)


def safe_name(name: str) -> str:
    cleaned = Path(name).name.replace("\x00", "").strip()
    return cleaned or "upload.bin"


def cleanup_job(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def prune_old_jobs() -> None:
    cutoff = time.time() - JOB_TTL_MINUTES * 60
    for path in JOBS_DIR.iterdir():
        try:
            if path.is_dir() and path.stat().st_mtime < cutoff:
                cleanup_job(path)
        except FileNotFoundError:
            pass


async def save_upload(upload: UploadFile, destination: Path) -> None:
    size = 0
    with destination.open("wb") as handle:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_MB * 1024 * 1024:
                raise HTTPException(413, f"File exceeds {MAX_UPLOAD_MB} MB limit")
            handle.write(chunk)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    sections = []
    for category in CATEGORIES:
        cards = []
        for spec in FORMATS.values():
            if spec.category != category:
                continue
            cards.append(
                f'<a class="format-card" href="/convert/{spec.slug}">'
                f'<span class="format-icon">.{escape(spec.slug)}</span>'
                f'<span><strong>{escape(spec.label)}</strong><small>{escape(spec.description)}</small></span>'
                '<span class="arrow" aria-hidden="true">→</span></a>'
            )
        sections.append(
            f'<section class="format-section"><div class="section-heading"><h2>{escape(category)}</h2>'
            f'<span>{len(cards)} formats</span></div><div class="format-grid">{"".join(cards)}</div></section>'
        )
    return render_template("index.html", format_sections="".join(sections))


@app.get("/convert/{input_format}", response_class=HTMLResponse)
def converter_page(input_format: str) -> str:
    spec = FORMATS.get(input_format.lower())
    if spec is None:
        raise HTTPException(404, "That input format is not supported")
    options = "".join(
        f'<option value="{escape(output)}">{escape(OUTPUT_LABELS[output])}</option>' for output in spec.outputs
    )
    return render_template(
        "convert.html",
        format_slug=escape(spec.slug),
        format_label=escape(spec.label),
        category=escape(spec.category),
        description=escape(spec.description),
        accept=escape(spec.accept),
        output_options=options,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME}


@app.get("/api/capabilities")
def capabilities() -> dict:
    return {
        "privacy": {"third_party_uploads": False, "telemetry": False, "job_ttl_minutes": JOB_TTL_MINUTES},
        "max_upload_mb": MAX_UPLOAD_MB,
        "operations": ["convert", "strip-metadata", "merge-pdf", "pdf-to-images"],
        "input_formats": list(FORMATS),
    }


@app.post("/api/convert")
async def convert(background_tasks: BackgroundTasks, file: UploadFile = File(...), output_format: str = Form(...)):
    prune_old_jobs()
    job = JOBS_DIR / uuid.uuid4().hex
    job.mkdir(parents=True)
    source = job / safe_name(file.filename or "upload.bin")
    await save_upload(file, source)
    ext = output_format.lower().lstrip(".")
    destination = job / f"{source.stem}.{ext}"
    try:
        convert_single(source, destination, ext)
    except ValueError as exc:
        cleanup_job(job)
        raise HTTPException(400, str(exc)) from exc
    background_tasks.add_task(cleanup_job, job)
    return FileResponse(destination, filename=destination.name, background=background_tasks)


@app.post("/api/strip-metadata")
async def strip_metadata(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job = JOBS_DIR / uuid.uuid4().hex
    job.mkdir(parents=True)
    source = job / safe_name(file.filename or "image.png")
    await save_upload(file, source)
    destination = job / f"{source.stem}-clean{source.suffix}"
    try:
        strip_image_metadata(source, destination)
    except Exception as exc:
        cleanup_job(job)
        raise HTTPException(400, f"Could not clean image: {exc}") from exc
    background_tasks.add_task(cleanup_job, job)
    return FileResponse(destination, filename=destination.name, background=background_tasks)


@app.post("/api/merge-pdf")
async def merge_pdf(background_tasks: BackgroundTasks, files: list[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(400, "Choose at least two PDF files")
    job = JOBS_DIR / uuid.uuid4().hex
    job.mkdir(parents=True)
    sources = []
    for index, upload in enumerate(files):
        source = job / f"{index:03d}-{safe_name(upload.filename or 'document.pdf')}"
        await save_upload(upload, source)
        sources.append(source)
    destination = job / "merged.pdf"
    try:
        pdf_merge(sources, destination)
    except Exception as exc:
        cleanup_job(job)
        raise HTTPException(400, f"Could not merge PDFs: {exc}") from exc
    background_tasks.add_task(cleanup_job, job)
    return FileResponse(destination, filename="merged.pdf", background=background_tasks)


@app.post("/api/pdf-to-images")
async def pdf_images(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job = JOBS_DIR / uuid.uuid4().hex
    job.mkdir(parents=True)
    source = job / safe_name(file.filename or "document.pdf")
    await save_upload(file, source)
    try:
        images = pdf_to_images(source, job)
        archive = job / "pdf-images.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
            for image in images:
                bundle.write(image, image.name)
    except Exception as exc:
        cleanup_job(job)
        raise HTTPException(400, f"Could not render PDF: {exc}") from exc
    background_tasks.add_task(cleanup_job, job)
    return FileResponse(archive, filename=archive.name, background=background_tasks)
