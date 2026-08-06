from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormatSpec:
    slug: str
    label: str
    category: str
    description: str
    extensions: tuple[str, ...]
    outputs: tuple[str, ...]

    @property
    def accept(self) -> str:
        return ",".join(f".{extension}" for extension in self.extensions)


OUTPUT_LABELS = {
    "jpg": "JPG",
    "png": "PNG",
    "webp": "WebP",
    "bmp": "BMP",
    "gif": "GIF",
    "tiff": "TIFF",
    "mp3": "MP3",
    "wav": "WAV",
    "flac": "FLAC",
    "ogg": "OGG",
    "m4a": "M4A",
    "aac": "AAC",
    "mp4": "MP4",
    "mkv": "MKV",
    "mov": "MOV",
    "webm": "WebM",
    "avi": "AVI",
    "pdf": "PDF",
}

IMAGE_OUTPUTS = ("jpg", "png", "webp", "bmp", "gif", "tiff")
MEDIA_OUTPUTS = ("mp3", "wav", "flac", "ogg", "m4a", "aac", "mp4", "mkv", "mov", "webm", "avi")


def _image(slug: str, label: str, description: str, extensions: tuple[str, ...] | None = None) -> FormatSpec:
    return FormatSpec(
        slug=slug,
        label=label,
        category="Images",
        description=description,
        extensions=extensions or (slug,),
        outputs=tuple(output for output in IMAGE_OUTPUTS if output != slug),
    )


def _media(slug: str, label: str, category: str, description: str) -> FormatSpec:
    return FormatSpec(
        slug=slug,
        label=label,
        category=category,
        description=description,
        extensions=(slug,),
        outputs=tuple(output for output in MEDIA_OUTPUTS if output != slug),
    )


def _office(slug: str, label: str, description: str) -> FormatSpec:
    return FormatSpec(
        slug=slug,
        label=label,
        category="Documents",
        description=description,
        extensions=(slug,),
        outputs=("pdf",),
    )


FORMAT_SPECS = (
    _image("jpg", "JPG / JPEG", "Convert a JPEG photo into another common image format.", ("jpg", "jpeg")),
    _image("png", "PNG", "Convert a PNG image while keeping control of its output format."),
    _image("webp", "WebP", "Turn a WebP image into a widely compatible image file."),
    _image("bmp", "BMP", "Convert an uncompressed bitmap into a more practical format."),
    _image("gif", "GIF", "Convert a GIF image into another supported image format."),
    _image("tiff", "TIFF", "Convert a TIFF scan or image into a common image format."),
    _media("mp3", "MP3", "Audio", "Convert an MP3 audio file into another audio or media container."),
    _media("wav", "WAV", "Audio", "Convert an uncompressed WAV recording into another format."),
    _media("flac", "FLAC", "Audio", "Convert lossless FLAC audio into another supported format."),
    _media("ogg", "OGG", "Audio", "Convert an OGG audio file into another supported format."),
    _media("m4a", "M4A", "Audio", "Convert an M4A audio file into another supported format."),
    _media("aac", "AAC", "Audio", "Convert an AAC audio file into another supported format."),
    _media("mp4", "MP4", "Video", "Convert an MP4 video or extract its audio."),
    _media("mkv", "MKV", "Video", "Convert an MKV video or extract its audio."),
    _media("mov", "MOV", "Video", "Convert a QuickTime MOV video or extract its audio."),
    _media("webm", "WebM", "Video", "Convert a WebM video or extract its audio."),
    _media("avi", "AVI", "Video", "Convert an AVI video or extract its audio."),
    _office("doc", "DOC", "Convert a legacy Microsoft Word document to PDF."),
    _office("docx", "DOCX", "Convert a Microsoft Word document to PDF."),
    _office("odt", "ODT", "Convert an OpenDocument text file to PDF."),
    _office("ppt", "PPT", "Convert a legacy PowerPoint presentation to PDF."),
    _office("pptx", "PPTX", "Convert a PowerPoint presentation to PDF."),
    _office("xls", "XLS", "Convert a legacy Excel spreadsheet to PDF."),
    _office("xlsx", "XLSX", "Convert an Excel spreadsheet to PDF."),
)

FORMATS = {spec.slug: spec for spec in FORMAT_SPECS}
CATEGORIES = tuple(dict.fromkeys(spec.category for spec in FORMAT_SPECS))
