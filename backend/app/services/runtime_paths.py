import os
import shutil
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_TESSDATA_DIR = BACKEND_ROOT / "ocr_data" / "tessdata"


def find_executable(name: str, candidates: list[Path]) -> Path | None:
    found = shutil.which(name)
    if found:
        return Path(found)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_tesseract_cmd() -> Path | None:
    env_value = os.getenv("TESSERACT_CMD")
    candidates = []
    if env_value:
        candidates.append(Path(env_value))
    candidates.extend(
        [
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
        ]
    )
    return find_executable("tesseract", candidates)


def find_tessdata_dir() -> Path | None:
    env_value = os.getenv("TESSDATA_PREFIX")
    candidates = []
    if env_value:
        candidates.append(Path(env_value))
    candidates.extend(
        [
            PROJECT_TESSDATA_DIR,
            Path(r"C:\Program Files\Tesseract-OCR\tessdata"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tessdata"),
        ]
    )
    for candidate in candidates:
        if candidate.exists() and any(candidate.glob("*.traineddata")):
            return candidate
    return None


def find_poppler_path() -> Path | None:
    env_value = os.getenv("POPPLER_PATH")
    candidates = []
    if env_value:
        candidates.append(Path(env_value))

    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        winget_root = (
            Path(local_app_data)
            / "Microsoft"
            / "WinGet"
            / "Packages"
            / "oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
        )
        candidates.extend(winget_root.glob("poppler-*\\Library\\bin"))

    candidates.extend(
        [
            Path(r"C:\Program Files\poppler\Library\bin"),
            Path(r"C:\Program Files\poppler\bin"),
            Path(r"C:\Program Files (x86)\poppler\Library\bin"),
            Path(r"C:\Program Files (x86)\poppler\bin"),
        ]
    )

    for candidate in candidates:
        if (candidate / "pdfinfo.exe").exists() and (candidate / "pdftoppm.exe").exists():
            return candidate

    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        return Path(pdfinfo).parent
    return None
