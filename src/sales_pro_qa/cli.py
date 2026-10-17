import argparse
import json
from pathlib import Path
from .config import load_config
from .permissions import compare_permissions
from .models import PermissionRecord
from .report import write_report

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Sales Pro Arabic QA report.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--input", required=True, help="Synthetic or verified audit JSON.")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    audit = json.loads(Path(args.input).read_text(encoding="utf-8"))
    audit.setdefault("project_name", config["project_name"])
    raw_permissions = audit.get("permissions", [])
    records = [PermissionRecord(**p) for p in raw_permissions]
    audit["permissions"] = compare_permissions(records)
    write_report(audit, args.output)
    print(f"Report written: {args.output}")

if __name__ == "__main__":
    main()
