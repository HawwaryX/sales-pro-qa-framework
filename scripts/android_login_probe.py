"""Optional, bounded pre-authentication UI probe; credentials arrive on stdin.

The worker needs adbutils, uiautomator2 and Pillow in an isolated tools environment.
It neither creates business records nor changes the backend or app data.
"""
import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


def exact_option_selected(description: str, prefix: str, requested: str) -> bool:
    """Match an entire option; a similar branch name or year is insufficient."""
    return description.startswith(prefix) and description[len(prefix):].strip() == requested


def worker(out: Path, serial: str, account: dict) -> int:
    import io
    import adbutils
    import uiautomator2 as u2
    from PIL import Image

    secrets = [account["username"], account["password"]]
    result = {"login_submitted": False, "authenticated": None,
              "ui_url_candidates": []}
    started = time.monotonic()

    def stage(name):
        with (out / "progress.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"stage": name, "elapsed": round(time.monotonic()-started, 2)})+"\n")

    def snapshot(name):
        root = ET.fromstring(d.dump_hierarchy())
        for node in root.iter("node"):
            for value in (node.get("text", ""), node.get("content-desc", "")):
                for url in re.findall(r"https?://[^\s<>\"']+", value):
                    try:
                        u = urlsplit(url)
                        candidate = {"scheme": u.scheme, "hostname": u.hostname,
                                     "path": u.path}
                        if candidate not in result["ui_url_candidates"]:
                            result["ui_url_candidates"].append(candidate)
                    except ValueError:
                        pass
        # Never serialize an EditText value or the exact supplied account.
        for node in root.iter("node"):
            if node.get("class") == "android.widget.EditText":
                node.set("text", "[REDACTED]")
                node.set("content-desc", "")
            for key in ("text", "content-desc"):
                value = node.get(key, "")
                for secret in sorted(secrets, key=len, reverse=True):
                    value = value.replace(secret, "[REDACTED]")
                # URL queries/userinfo may contain secrets: keep those in memory only.
                value = re.sub(r"https?://[^\s<>\"']+", "[URL REDACTED]", value)
                node.set(key, value)
        (out / (name + ".xml")).write_text(ET.tostring(root, encoding="unicode"), encoding="utf-8")
        labels = [n.get("text") or n.get("content-desc") for n in root.iter("node")
                  if n.get("package") == "com.infinity.sales.app" and
                  n.get("class") != "android.widget.EditText"]
        return root, [x for x in labels if x]

    try:
        stage("connect")
        client = adbutils.AdbClient(host="127.0.0.1", port=5037, socket_timeout=8)
        dev = client.device(serial)
        if dev.shell("getprop sys.boot_completed", timeout=10).strip() != "1":
            raise RuntimeError("Android boot is not ready")
        # TCG exceeded the library's 30-second startup window. This change is
        # local to this worker; the supervising process still caps total time.
        def wait_ready(server, launch_timeout=90):
            server._wait_app_process_ready(launch_timeout)
        u2.core.BasicUiautomatorServer._wait_ready = wait_ready
        d = u2.connect(dev)
        d.settings["wait_timeout"] = 5
        d.jsonrpc.setConfigurator({"waitForIdleTimeout": 1000,
                                   "waitForSelectorTimeout": 5000})
        stage("launch")
        dev.shell("am start -n com.infinity.sales.app/.MainActivity", timeout=20)
        if d(text="System UI isn't responding").exists and d(text="Wait").exists:
            d(text="Wait").click(timeout=3)
            result["system_ui_wait"] = True
        if not d(className="android.widget.EditText").wait(timeout=60):
            snapshot("launch_not_ready")
            raise RuntimeError("Login fields did not render within wait")
        fields = d(className="android.widget.EditText")
        if fields.count != 2:
            raise RuntimeError("Unexpected login structure")
        fields[0].set_text(account["username"])
        fields[1].set_text(account["password"])
        if fields[0].get_text() != account["username"]:
            raise RuntimeError("Exact input verification failed")
        raw = ET.fromstring(d.dump_hierarchy())
        if raw.find(".//node[@class='android.widget.EditText'][@password='true']") is None:
            raise RuntimeError("Password masking not verified")
        result["exact_account_input_verified"] = True
        stage("refresh_with_account")
        d(description="تحديث الفروع والسنوات").click(timeout=5)
        d(description="تعذر تحميل الفروع أو السنوات. تحقق من الاتصال بالخادم.").wait(timeout=40)
        _, result["lookup_labels"] = snapshot("lookup_with_account")
        stage("select_requested_branch_year")
        selected = {}
        for key, prefix in [("branch", "الفرع *"), ("year", "السنة المالية *")]:
            value = account.get(key)
            if not value:
                continue
            button = d(descriptionStartsWith=prefix)
            selected[key] = False
            if not button.exists:
                continue
            if exact_option_selected(button.info.get("contentDescription", ""), prefix, value):
                selected[key] = True
                continue
            if not button.info.get("clickable"):
                continue
            button.click(timeout=5)
            if d(description=value).exists:
                d(description=value).click(timeout=5)
                selected[key] = True
            elif d(text=value).exists:
                d(text=value).click(timeout=5)
                selected[key] = True
            else:
                snapshot(key + "_options")
                if d(description="رفض").exists:
                    d.press("back")
            if selected[key]:
                current = d(descriptionStartsWith=prefix)
                selected[key] = current.exists and exact_option_selected(
                    current.info.get("contentDescription", ""), prefix, value)
        result["requested_options_selected"] = selected
        _, result["selection_labels"] = snapshot("requested_options")
        stage("evaluate_submit")
        if selected and not all(selected.values()):
            result["submit_blocker"] = "الفرع أو السنة المطلوبة غير متاحين؛ لم يُرسل نموذج بفرع بديل"
        else:
            d(description="تسجيل الدخول").click(timeout=5)
            result["login_submitted"] = True
            d(description="اختر الفرع والسنة المالية.").wait(timeout=10)
        raw = ET.fromstring(d.dump_hierarchy())
        _, result["after_form_action_labels"] = snapshot("after_form_action")
        fields_nodes = raw.findall(".//node[@class='android.widget.EditText']")
        if len(fields_nodes) == 2:
            result["authenticated"] = False
            # Crop below both account fields. Do not save a full credential screenshot.
            below = max(int(re.findall(r"\d+", n.get("bounds"))[3]) for n in fields_nodes)
            remote = "/data/local/tmp/sales_qa_resume_capture.png"
            try:
                dev.shell(["screencap", "-p", remote], timeout=20)
                im = Image.open(io.BytesIO(dev.sync.read_bytes(remote)))
                if 0 < below < im.height:
                    im.crop((0, below+1, im.width, im.height)).save(out / "login_result_lower_crop.png")
            finally:
                dev.shell(["rm", "-f", remote], timeout=8)
            # Clear only the two form fields after preserving the actual result.
            d(className="android.widget.EditText", instance=0).set_text("")
            d(className="android.widget.EditText", instance=1).set_text("")
            stage("environment_control")
            d.swipe(.5, .85, .5, .35, duration=.4)
            if d(description="تغيير").exists:
                d(description="تغيير").click(timeout=5)
                _, result["environment_labels"] = snapshot("environment_control")
        stage("complete")
        code = 0
    except Exception as exc:
        # Exceptions from UI libraries can contain arguments: save only the class.
        result["worker_error_class"] = type(exc).__name__
        stage("worker_error")
        code = 1
    (out / "observations.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--serial", default="emulator-5554")
    parser.add_argument("--timeout", type=float, default=240)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("timeout must be finite and positive")
    try:
        payload = sys.stdin.readline()
        account = json.loads(payload)
        if not isinstance(account, dict) or not all(isinstance(account.get(k), str) and account[k]
                                                   for k in ["username", "password", "branch", "year"]):
            raise ValueError()
    except (ValueError, TypeError):
        parser.error("stdin must provide username/password/branch/year JSON; values are never printed")
    if args.worker:
        raise SystemExit(worker(args.output, args.serial, account))
    from sales_pro_qa.runtime_probe import run_bounded_probe
    try:
        args.output.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        parser.error("Cannot create a new evidence directory: " + type(exc).__name__)
    result = run_bounded_probe([sys.executable, str(Path(__file__).resolve()), "--worker",
                               "--output", str(args.output), "--serial", args.serial],
                              timeout=args.timeout, stdin_text=payload,
                              redactions=[account["username"], account["password"]])
    (args.output / "supervision.json").write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"worker_state": result.state, "elapsed_seconds": round(result.elapsed_seconds, 2)}))
    raise SystemExit(0 if result.state == "COMPLETED" else 1)


if __name__ == "__main__":
    main()
