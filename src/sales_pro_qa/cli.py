import argparse
import json
from pathlib import Path
from .config import load_config
from .permissions import compare_permissions
from .models import PermissionRecord
from .report import write_report
from .apk import inspect_apk, render_apk_report
from .apk_cli import add_tool_arguments, validate_output

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Sales Pro Arabic QA report.")
    parser.add_argument("--config")
    parser.add_argument("--input", help="Synthetic or verified audit JSON.")
    parser.add_argument("--apk", help="Read-only static inspection using Android SDK aapt.")
    add_tool_arguments(parser)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.apk:
        if args.config or args.input:
            parser.error("--apk cannot be combined with --config or --input")
        try:
            output = validate_output(args.apk, args.output)
            metadata = inspect_apk(args.apk, aapt=args.aapt, apkanalyzer=args.apkanalyzer, apksigner=args.apksigner,
                                   sdk_root=args.android_sdk, timeout=args.timeout)
            report = render_apk_report(metadata)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(report, encoding="utf-8")
        except (ValueError, OSError) as exc:
            parser.error(str(exc))
        print(f"Report written: {args.output}")
        if metadata.get("signature", {}).get("status") in {"FAIL", "ERROR"}:
            raise SystemExit(1)
        return
    if not args.config or not args.input:
        parser.error("--config and --input are required unless --apk is used")
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
