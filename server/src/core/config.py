from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

upload_dir_value = os.getenv("UPLOAD_DIR")
if upload_dir_value:
    upload_dir_path = Path(upload_dir_value).expanduser()
    if not upload_dir_path.is_absolute():
        upload_dir_path = BASE_DIR / upload_dir_path
    UPLOAD_DIR = upload_dir_path
else:
    UPLOAD_DIR = BASE_DIR / "data" / "uploads"

UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
