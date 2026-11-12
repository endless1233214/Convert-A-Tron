FROM ubuntu:26.04@sha256:c098726dd9b9733f3e885f8de0ef375206a311b0a317eadc40d347b1115fb944
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    PATH=/opt/venv/bin:$PATH
# The Ubuntu base includes the Pebble service manager, but this image starts
# Uvicorn directly. Remove the unused Go binary from the runtime/CVE surface.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv \
    ffmpeg libreoffice-core libreoffice-writer libreoffice-calc libreoffice-impress \
    poppler-utils ca-certificates fonts-dejavu-core \
    && rm -f /usr/bin/pebble \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv /opt/venv \
    && pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN mkdir -p /data/jobs && chown -R 568:568 /app /data
USER 568:568
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080","--proxy-headers"]
