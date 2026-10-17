import json
from pathlib import Path

REQUIRED_KEYS = {"project_name", "language", "evidence_root"}

def load_config(path: str | Path) -> dict:
    config_path = Path(path)
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Config file not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in config: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a JSON object.")
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"Missing required config keys: {', '.join(sorted(missing))}")
    if not isinstance(data["project_name"], str) or not data["project_name"].strip():
        raise ValueError("'project_name' must be a non-empty string.")
    if data["language"] not in {"ar", "en"}:
        raise ValueError("'language' must be 'ar' or 'en'.")
    if not isinstance(data["evidence_root"], str) or not data["evidence_root"].strip():
        raise ValueError("'evidence_root' must be a non-empty path string.")
    return data
