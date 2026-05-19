import csv
import os
from pathlib import Path

from src.config import MAX_FILE_SIZE_BYTES

ALLOWED_EXTENSIONS = {".txt", ".csv", ".md"}


def read_file(file_path: str) -> dict:
    """
    Read a .txt, .csv, or .md file and return its contents as a string.

    For CSV files the rows are formatted as a readable table.
    Returns a dict with 'content' on success or 'error' on failure.
    """
    path = Path(file_path).resolve()

    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return {
            "error": (
                f"Unsupported file type '{path.suffix}'. "
                f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        }

    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return {"error": f"File exceeds the {MAX_FILE_SIZE_BYTES // 1_000_000} MB size limit"}

    try:
        if path.suffix.lower() == ".csv":
            return _read_csv(path)
        return _read_text(path)
    except PermissionError:
        return {"error": f"Permission denied: {file_path}"}
    except UnicodeDecodeError:
        return {"error": "File is not valid UTF-8 text"}


def _read_text(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    return {"content": content, "file": str(path), "type": "text"}


def _read_csv(path: Path) -> dict:
    lines = []
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = list(reader)

    if not rows:
        return {"content": "(empty CSV)", "file": str(path), "type": "csv"}

    col_widths = [max(len(str(row[i])) for row in rows if i < len(row)) for i in range(len(rows[0]))]
    separator = "-+-".join("-" * w for w in col_widths)

    for idx, row in enumerate(rows):
        line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        lines.append(line)
        if idx == 0:
            lines.append(separator)

    return {"content": "\n".join(lines), "file": str(path), "type": "csv", "rows": len(rows) - 1}
