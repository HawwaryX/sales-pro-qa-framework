from pathlib import Path
from datetime import datetime, timezone
import json

def build_manifest(items: list[dict], base_dir: str | Path) -> dict:
    base = Path(base_dir).resolve()
    entries = []
    for item in items:
        raw_path = Path(item["path"])
        resolved = (base / raw_path).resolve() if not raw_path.is_absolute() else raw_path.resolve()
        try:
            relative = resolved.relative_to(base).as_posix()
        except ValueError as exc:
            raise ValueError(f"Evidence path must stay inside evidence root: {raw_path}") from exc
        entries.append({
            "test_id": str(item["test_id"]),
            "path": relative,
            "description": str(item.get("description", "")),
            "exists": resolved.is_file(),
        })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evidence_root": ".",
        "items": entries,
    }

def write_manifest(manifest: dict, output: str | Path) -> None:
    Path(output).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
