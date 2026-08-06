from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Callable

from PIL import Image, ImageOps
from pypdf import PdfReader, PdfWriter
from pillow_heif import register_heif_opener

register_heif_opener()

IMAGE_FORMATS = {"heif", "heic", "hif", "jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff"}
AUDIO_FORMATS = {"mp3", "wav", "flac", "ogg", "m4a", "aac"}
VIDEO_FORMATS = {"mp4", "mkv", "mov", "webm", "avi"}


def _run(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=3600)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "conversion command failed").strip()
        raise ValueError(detail[-2000:]) from exc
    except FileNotFoundError as exc:
        raise ValueError(f"Required converter is not installed: {command[0]}") from exc


def convert_image(source: Path, destination: Path, output_format: str) -> None:
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        if output_format in {"jpg", "jpeg"} and image.mode not in {"RGB", "L"}:
            background = Image.new("RGB", image.size, "white")
            if "A" in image.getbands():
                background.paste(image, mask=image.getchannel("A"))
            else:
                background.paste(image.convert("RGB"))
            image = background
        image.save(destination, format="JPEG" if output_format in {"jpg", "jpeg"} else output_format.upper())


def strip_image_metadata(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        clean = Image.new(image.mode, image.size)
        clean.putdata(list(image.getdata()))
        clean.save(destination, format=image.format)


def pdf_merge(sources: list[Path], destination: Path) -> None:
    writer = PdfWriter()
    for source in sources:
        reader = PdfReader(str(source))
        for page in reader.pages:
            writer.add_page(page)
    with destination.open("wb") as handle:
        writer.write(handle)


def pdf_to_images(source: Path, output_dir: Path) -> list[Path]:
    prefix = output_dir / "page"
    _run(["pdftoppm", "-png", str(source), str(prefix)])
    return sorted(output_dir.glob("page-*.png"))


def office_to_pdf(source: Path, output_dir: Path) -> Path:
    _run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(source)])
    result = output_dir / f"{source.stem}.pdf"
    if not result.exists():
        raise ValueError("LibreOffice did not produce a PDF")
    return result


def ffmpeg_convert(source: Path, destination: Path) -> None:
    _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), str(destination)])


def convert_single(source: Path, destination: Path, output_format: str) -> None:
    input_format = source.suffix.lower().lstrip(".")
    output_format = output_format.lower().lstrip(".")
    if input_format in IMAGE_FORMATS and output_format in IMAGE_FORMATS:
        convert_image(source, destination, output_format)
        return
    if input_format in AUDIO_FORMATS | VIDEO_FORMATS and output_format in AUDIO_FORMATS | VIDEO_FORMATS:
        ffmpeg_convert(source, destination)
        return
    if output_format == "pdf" and input_format in {"doc", "docx", "odt", "ppt", "pptx", "xls", "xlsx"}:
        produced = office_to_pdf(source, destination.parent)
        if produced != destination:
            shutil.move(produced, destination)
        return
    raise ValueError(f"Unsupported conversion: {input_format or 'unknown'} → {output_format}")
