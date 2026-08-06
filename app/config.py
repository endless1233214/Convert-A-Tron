from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "Convert-A-Tron"
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "500"))
JOB_TTL_MINUTES = int(os.getenv("JOB_TTL_MINUTES", "60"))
DATA_DIR = Path(os.getenv("DATA_DIR", "/data" if Path("/data").exists() else "data"))
JOBS_DIR = DATA_DIR / "jobs"
JOBS_DIR.mkdir(parents=True, exist_ok=True)
