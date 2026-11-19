from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parents[3]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR / 'civicpulse.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
UPLOAD_MAX_BYTES = int(os.getenv("UPLOAD_MAX_BYTES", "5242880"))
ADMIN_ACCESS_KEY = os.getenv("ADMIN_ACCESS_KEY", "9099")
