"""Standalone read-only APK inspection CLI."""
import argparse
from pathlib import Path

from .apk import inspect_apk, render_apk_report


def add_tool_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--aapt', help='Trusted aapt executable path.')
    parser.add_argument('--apkanalyzer', help='Trusted apkanalyzer executable or .bat path.')
    parser.add_argument('--apksigner', help='Trusted apksigner executable, .bat or .jar path.')
    parser.add_argument('--android-sdk', help='Android SDK root; paths with spaces supported.')
    parser.add_argument('--timeout', type=float, default=60, help='Per-tool timeout, in seconds.')


def validate_output(source: str, output: str) -> Path:
    apk = Path(source).resolve()
    target = Path(output).resolve()
    if target == apk or (apk.exists() and target.exists() and apk.samefile(target)):
        raise ValueError('Report output must not overwrite the original APK')
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect Android APK without installing or running it.')
    parser.add_argument('--apk', required=True)
    parser.add_argument('--output', required=True)
    add_tool_arguments(parser)
    args = parser.parse_args()
    try:
        output = validate_output(args.apk, args.output)
        data = inspect_apk(args.apk, aapt=args.aapt, apkanalyzer=args.apkanalyzer,
                           apksigner=args.apksigner, sdk_root=args.android_sdk, timeout=args.timeout)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_apk_report(data), encoding='utf-8')
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f'Report written: {output}')
    if data['signature']['status'] in {'FAIL', 'ERROR'}:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
