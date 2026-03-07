from __future__ import annotations

import os
from pathlib import Path
from shutil import which

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_ENTREE_DIR = BASE_DIR / "data_entree"
DATA_SORTIE_DIR = BASE_DIR / "data_sortie"
TEMPLATE_PATH = BASE_DIR / "Test_PlaceHolder.docx"
BAREMES_PATH = BASE_DIR / "Baremes_Extrapoles_CP.csv"
ENV_PATH = BASE_DIR / ".env"
DEFAULT_MODEL = "gemini-2.5-flash"

COMMON_POPPLER_DIRS = (
    Path(r"C:\poppler\Library\bin"),
    Path(r"C:\poppler-25.12.0\Library\bin"),
    Path(r"C:\Program Files\poppler\Library\bin"),
    Path(r"C:\Program Files (x86)\poppler\Library\bin"),
)

load_dotenv(ENV_PATH)


def ensure_runtime_directories():
    DATA_ENTREE_DIR.mkdir(exist_ok=True)
    DATA_SORTIE_DIR.mkdir(exist_ok=True)


def get_api_key():
    return os.getenv("GOOGLE_API_KEY", "").strip()


def get_model_name():
    value = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
    return value or DEFAULT_MODEL


def resolve_poppler_path():
    candidates = []
    env_value = os.getenv("POPPLER_PATH", "").strip().strip('"')
    if env_value:
        candidates.append(Path(env_value))

    pdftoppm_path = which("pdftoppm")
    if pdftoppm_path:
        candidates.append(Path(pdftoppm_path).resolve().parent)

    candidates.extend(COMMON_POPPLER_DIRS)

    executable_name = "pdftoppm.exe" if os.name == "nt" else "pdftoppm"
    seen = set()
    for candidate in candidates:
        normalized = str(candidate).lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        if candidate.is_dir() and (candidate / executable_name).exists():
            return str(candidate)
    return None


def get_pdf_conversion_kwargs():
    poppler_path = resolve_poppler_path()
    return {"poppler_path": poppler_path} if poppler_path else {}


def get_setup_issues():
    issues = []
    if not get_api_key():
        issues.append("La variable GOOGLE_API_KEY est absente du fichier .env.")
    if not TEMPLATE_PATH.exists():
        issues.append(f"Modele Word introuvable: {TEMPLATE_PATH.name}.")
    if not BAREMES_PATH.exists():
        issues.append(f"Fichier de baremes introuvable: {BAREMES_PATH.name}.")
    if resolve_poppler_path() is None:
        issues.append(
            "Poppler est introuvable. Installez-le puis ajoutez-le au PATH ou renseignez POPPLER_PATH dans .env."
        )
    return issues
