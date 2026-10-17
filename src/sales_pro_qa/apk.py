"""Read-only APK metadata inspection through Android SDK aapt."""
import hashlib
import html
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zlib
import zipfile

from .apk_permissions import describe_permission


def parse_badging(text: str) -> dict:
    """Parse aapt dump badging output; preserve unknown SDK values as None."""
    package = next((line for line in text.splitlines() if line.startswith("package: ")), None)
    if package is None:
        raise ValueError("aapt output has no package metadata")
    attributes = dict(re.findall(r"(\w+)='([^']*)'", package))
    if not attributes.get("name"):
        raise ValueError("aapt output has no package name")
    def field(name):
        match = re.search(r"^" + name + r":'([^']*)'", text, re.MULTILINE)
        return match.group(1) if match else None
    return {
        "package_name": attributes["name"],
        "version_name": attributes.get("versionName"),
        "version_code": attributes.get("versionCode"),
        "min_sdk": field("sdkVersion"),
        "target_sdk": field("targetSdkVersion"),
        "label": field("application-label"),
        "permissions": sorted(set(re.findall(
            r"^uses-permission(?:-sdk-\d+)?: name='([^']+)'", text, re.MULTILINE
        ))),
    }


def find_android_tool(name: str, explicit: str | None = None,
                      sdk_root: str | None = None) -> str | None:
    """Prefer explicit paths, then PATH, then SDK build-tools (including Windows)."""
    if explicit:
        candidate = Path(explicit).expanduser()
        if not candidate.is_file():
            raise ValueError(f"{name} tool path does not exist: {candidate}")
        return str(candidate.resolve())
    found = shutil.which(name)
    if found:
        return found
    for root in [sdk_root, os.environ.get("ANDROID_SDK_ROOT"), os.environ.get("ANDROID_HOME")]:
        if not root:
            continue
        parent = "cmdline-tools" if name == "apkanalyzer" else "build-tools"
        directories = list((Path(root) / parent).glob("*"))
        directories.sort(key=lambda p: tuple(int(x) for x in re.findall(r"\d+", p.name)), reverse=True)
        if name == "apkanalyzer":
            directories.sort(key=lambda p: p.name == "latest", reverse=True)
        for directory in directories:
            if name == "apkanalyzer":
                directory = directory / "bin"
            for suffix in ("", ".exe", ".bat"):
                candidate = directory / (name + suffix)
                if candidate.is_file():
                    return str(candidate.resolve())
    return None


def parse_manifest(text: str) -> dict:
    """Parse apkanalyzer manifest print XML, without inferring omitted SDKs."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError("apkanalyzer returned invalid manifest XML") from exc
    if root.tag != "manifest" or not root.get("package"):
        raise ValueError("Manifest has no package name")
    android = "{http://schemas.android.com/apk/res/android}"
    sdk = root.find("uses-sdk")
    app = root.find("application")
    permissions = []
    constraints = []
    for element in root:
        if element.tag not in {"uses-permission", "uses-permission-sdk-23"}:
            continue
        name = element.get(android + "name")
        if not name:
            raise ValueError("Manifest permission has no name")
        permissions.append(name)
        if element.get(android + "maxSdkVersion"):
            constraints.append(f"{name}: maxSdkVersion={element.get(android + 'maxSdkVersion')}")
        if element.tag == "uses-permission-sdk-23":
            constraints.append(f"{name}: SDK >= 23")
    return {"package_name": root.get("package"),
            "version_name": root.get(android + "versionName"),
            "version_code": root.get(android + "versionCode"),
            "min_sdk": sdk.get(android + "minSdkVersion") if sdk is not None else None,
            "target_sdk": sdk.get(android + "targetSdkVersion") if sdk is not None else None,
            "label": app.get(android + "label") if app is not None else None,
            "permissions": sorted(set(permissions)), "permission_constraints": constraints}


def parse_signature(text: str) -> dict:
    """Keep public certificate attributes, without persisting certificate DNs."""
    certificates = []
    for number in sorted(set(re.findall(r"^Signer #(\d+) certificate", text, re.MULTILINE)), key=int):
        def field(label):
            match = re.search(r"^Signer #" + number + " " + re.escape(label) + r": (.+)$", text, re.MULTILINE)
            return match.group(1).strip() if match else None
        dn = field("certificate DN") or ""
        fingerprint = field("certificate SHA-256 digest")
        if fingerprint and not re.fullmatch(r"[0-9a-fA-F]{64}", fingerprint):
            raise ValueError("Invalid certificate SHA-256 fingerprint")
        certificates.append({"signer": number, "format": "X.509",
                             "sha256": fingerprint, "key_algorithm": field("key algorithm"),
                             "key_size": field("key size (bits)"),
                             "debug": bool(re.search(r"(?:^|,)\s*CN\s*=\s*Android Debug\s*(?:,|$)", dn, re.I))})
    schemes = re.findall(r"^Verified using (.+?): (true|false)$", text, re.MULTILINE)
    return {"certificates": certificates, "schemes": dict(schemes)}


def run_tool(command: list[str], timeout: float) -> dict:
    """Run a trusted SDK tool without a shell; retain its actual outcome."""
    if os.name == "nt" and command[0].lower().endswith((".bat", ".cmd")):
        # Windows implicitly invokes cmd.exe for batch files even with shell=False.
        # Reject expansion/control characters rather than interpolate untrusted paths.
        if any(any(c in arg for c in '%!^&|<>\r\n"()') for arg in command):
            raise ValueError("Batch tool paths/arguments contain unsupported Windows shell characters")
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"command": command, "status": "ERROR", "returncode": None,
                "stdout": "", "stderr": f"Tool exceeded {timeout:g} seconds", "error_kind": "timeout"}
    except OSError as exc:
        return {"command": command, "status": "ERROR", "returncode": None,
                "stdout": "", "stderr": str(exc), "error_kind": "execution"}
    return {"command": command, "status": "PASS" if result.returncode == 0 else "FAIL",
            "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
            "error_kind": None if result.returncode == 0 else "exit_code"}


def inspect_apk(path: str | Path, *, aapt: str | None = None, apkanalyzer: str | None = None,
                apksigner: str | None = None, sdk_root: str | None = None,
                timeout: float = 60) -> dict:
    """Never install or execute the APK. Fail explicitly if tooling fails."""
    apk = Path(path).resolve(strict=True)
    if not apk.is_file() or apk.suffix.lower() != ".apk":
        raise ValueError("Expected an APK file")
    if not 0 < timeout <= 3600:
        raise ValueError("Timeout must be between 0 and 3600 seconds")
    try:
        with zipfile.ZipFile(apk) as archive:
            if "AndroidManifest.xml" not in archive.namelist():
                raise ValueError("APK ZIP has no AndroidManifest.xml")
            entries = archive.infolist()
            if len(entries) > 100000 or sum(e.file_size for e in entries) > 2 * 1024**3:
                raise ValueError("APK exceeds ZIP inspection limits (100000 entries / 2 GiB expanded)")
            if len({e.filename for e in entries}) != len(entries):
                raise ValueError("APK ZIP contains duplicate entry names")
            if archive.testzip() is not None:
                raise ValueError("APK ZIP CRC verification failed")
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, zlib.error) as exc:
        raise ValueError("Invalid APK ZIP (possibly an unresolved Git LFS pointer)") from exc
    tool = find_android_tool("aapt", aapt, sdk_root) if not apkanalyzer else None
    backend = "aapt"
    if not tool:
        tool = find_android_tool("apkanalyzer", apkanalyzer, sdk_root)
        backend = "apkanalyzer"
    if not tool:
        raise ValueError("Android SDK aapt/apkanalyzer unavailable; specify --aapt or --apkanalyzer")
    args = ["dump", "badging"] if backend == "aapt" else ["manifest", "print"]
    evidence = run_tool([tool, *args, str(apk)], timeout)
    if evidence["status"] != "PASS":
        raise ValueError(f"{backend} inspection {evidence['status']}: exit={evidence['returncode']}; "
                         + (evidence["stderr"] if evidence["stderr"].startswith("Tool exceeded ") else "tool execution failed"))
    metadata = parse_badging(evidence["stdout"]) if backend == "aapt" else parse_manifest(evidence["stdout"])
    if backend == "aapt":
        metadata["permission_constraints"] = [line for line in evidence["stdout"].splitlines()
                                               if line.startswith("uses-permission") and
                                               ("maxSdkVersion=" in line or "uses-permission-sdk-" in line)]
    signer = find_android_tool("apksigner", apksigner, sdk_root)
    signature = {"status": "NOT_RUN", "command": [], "returncode": None,
                 "stdout": "", "stderr": "apksigner unavailable"}
    if signer:
        command = [signer]
        if signer.lower().endswith(".jar"):
            java = shutil.which("java")
            if not java:
                raise ValueError("Java is required for apksigner.jar")
            command = [java, "-jar", signer]
        signature = run_tool(command + ["verify", "--verbose", "--print-certs", str(apk)], timeout)
        if signature["status"] == "PASS":
            signature.update(parse_signature(signature["stdout"]))
            if not signature["certificates"] or any(not cert["sha256"] for cert in signature["certificates"]):
                signature["status"] = "ERROR"
                signature["stderr"] = "apksigner output has no complete certificate fingerprint"
                signature["error_kind"] = "certificate_parse"
    with apk.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"filename": apk.name, "sha256": digest, "size_bytes": apk.stat().st_size,
            "structure": "PASS", "zip_entries": len(entries), "backend": backend,
            "signature": signature, "evidence": [evidence], **metadata}


def render_apk_report(metadata: dict) -> str:
    """Render static evidence separately from runtime checks and authorization."""
    def safe(value):
        if value is None:
            return "غير متاح"
        return html.escape(str(value)).replace("\n", " ").replace("\r", " ").replace("|", "\\|").replace("`", "&#96;")
    manifest_status = "PASS" if metadata.get("evidence") and all(
        e.get("status") == "PASS" for e in metadata["evidence"]) else "NOT_RUN"
    lines = ["# تقرير فحص APK الثابت", "", "## ملخص الفحص", "",
             f"- نتيجة قراءة manifest: {manifest_status}",
             f"- تحليل البيانات: {safe(metadata.get('backend', 'غير متاح'))}؛ نتيجة التوقيع: {safe(metadata.get('signature', {}).get('status', 'NOT_RUN'))}",
             f"- سلامة ZIP وCRC: {safe(metadata.get('structure'))}؛ عدد العناصر: {safe(metadata.get('zip_entries'))}",
             "- فحص ثابت فقط؛ لا يتضمن تثبيت التطبيق أو تشغيله.", "", "## بيانات التطبيق", ""]
    labels = {"filename": "الملف", "size_bytes": "الحجم بالبايت", "sha256": "SHA-256", "package_name": "الحزمة",
              "version_name": "الإصدار", "version_code": "رمز الإصدار",
              "min_sdk": "أدنى SDK", "target_sdk": "SDK المستهدف", "label": "اسم التطبيق"}
    lines.extend(f"- {label}: {safe(metadata.get(key))}" for key, label in labels.items())
    lines += ["", "## الصلاحيات المطلوبة", ""]
    for permission in metadata["permissions"]:
        meaning, risk = describe_permission(permission)
        lines.append(f"- {safe(permission)}: {meaning}. {risk}")
    lines.extend(f"- قيد manifest: {safe(c)}" for c in metadata.get("permission_constraints", []))
    if not metadata["permissions"]:
        lines.append("لم يسرد aapt صلاحيات مطلوبة.")
    signature = metadata.get("signature", {"status": "NOT_RUN", "command": []})
    lines += ["", "## التحقق من التوقيع", "",
              f"- النتيجة: {safe(signature['status'])}",
              "- نجاح التحقق يثبت سلامة التوقيع تقنيًا؛ لا يثبت هوية الناشر أو خلو التطبيق من البرمجيات الخبيثة."]
    for cert in signature.get("certificates", []):
        lines += [f"- الموقّع {safe(cert['signer'])}: {safe(cert['format'])}؛ خوارزمية المفتاح: {safe(cert['key_algorithm'])}؛ الحجم: {safe(cert['key_size'])}",
                  f"- بصمة الشهادة SHA-256: {safe(cert['sha256'])}",
                  "- نوع الشهادة: " + ("Debug وفق اسم الشهادة. تحذير: يُراجع إعداد توقيع الإصدار؛ هذا ليس دليلًا على برمجية خبيثة."
                                         if cert['debug'] else "لم يُتعرف على اسم Debug القياسي؛ لا يثبت ذلك أنها شهادة إنتاج موثوقة.")]
    for scheme, verified in signature.get("schemes", {}).items():
        lines.append(f"- {safe(scheme)}: {safe(verified)}")
    lines += ["", "## الأدلة والأوامر المستخدمة", ""]
    for evidence in [*metadata.get("evidence", []), signature]:
        if evidence.get("command"):
            # Do not save arbitrary tool output, certificate DNs, or local directory names.
            command = [arg.replace('\\', '/').rsplit('/', 1)[-1] if '/' in arg or '\\' in arg else arg
                       for arg in evidence['command']]
            lines += [f"- الأمر (أسماء الملفات فقط؛ مسارات المجلدات محذوفة): {safe(repr(command))}",
                      f"- النتيجة: {safe(evidence['status'])}؛ رمز الخروج: {safe(evidence.get('returncode'))}"]
        if evidence.get('status') in {'FAIL', 'ERROR'}:
            reason = {"timeout": "انتهت مهلة الأداة", "execution": "تعذر تشغيل الأداة",
                      "exit_code": "أرجعت الأداة رمز فشل", "certificate_parse": "تعذر استخراج بصمة الشهادة"}.get(
                          evidence.get('error_kind'), "تعذر التحقق")
            lines.append(f"- {reason}؛ أُهملت المخرجات الخام لحماية البيانات الحساسة.")
    if signature['status'] == 'NOT_RUN':
        lines.append("- apksigner غير متاح؛ لم يُنفذ فحص التوقيع.")
    lines += ["", "## نتائج الفحص وحدوده", "",
              f"- {manifest_status}: قراءة بيانات الحزمة والصلاحيات بأداة Android؛ القيم الغائبة تبقى غير متاحة.",
              "- NOT_RUN: التثبيت والتشغيل وتسجيل الدخول وسلوك منح ورفض الصلاحيات؛ تتطلب محاكيًا أو جهازًا مصرحًا به.",
              "- نتيجة التوقيع موضحة أعلاه؛ لم يُفحص سلوك الشبكة أو وظائف التطبيق.",
              "- الصلاحيات المعلنة لا تثبت منحها أو استخدامها؛ راجع ضرورتها وفق سياسة التطبيق.",
              "- قد تغيب بعض قيم SDK أو بيانات التطبيق؛ لا تُستنتج قيم غير معروضة.",
              "- لا تعني نتيجة الفحص الثابت أن التطبيق آمن أو خالٍ من العيوب.",
              "", "## الخطوات التالية", "",
              "- راجع الصلاحيات وقيم SDK مع مالك التطبيق، ثم اختبر على جهاز معزول ببيانات اصطناعية.",
              "- تحقق من التوقيع والتثبيت والتوافق ومنح ورفض الصلاحيات دون تجاوز المصادقة.", ""]
    return "\n".join(lines)
