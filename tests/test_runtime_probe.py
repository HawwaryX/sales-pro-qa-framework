import os
import sys
import time
from pathlib import Path
import runpy
import io
import json

import pytest

from sales_pro_qa.runtime_probe import run_bounded_probe


def test_worker_completion_is_not_application_pass():
    result = run_bounded_probe([sys.executable, "-c", "print('worker finished')"], timeout=5)
    assert result.state == "COMPLETED"
    assert result.returncode == 0
    assert result.stdout == "worker finished\n"
    assert result.state != "PASS"


def test_nonzero_worker_exit_remains_failed():
    result = run_bounded_probe([sys.executable, "-c", "raise SystemExit(7)"], timeout=5)
    assert result.state == "FAILED"
    assert result.returncode == 7


def test_worker_timeout_retains_partial_output_and_ends_wait():
    start = time.monotonic()
    result = run_bounded_probe([sys.executable, "-c",
                               "import time; print('started', flush=True); time.sleep(60)"],
                              timeout=.3)
    assert time.monotonic() - start < 5
    assert result.state == "TIMED_OUT"
    assert "started" in result.stdout
    assert result.returncode != 0


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group cleanup")
def test_timeout_stops_descendant_holding_output_pipe():
    script = ("import subprocess,sys; "
              "subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
              "print('parent exited',flush=True)")
    start = time.monotonic()
    result = run_bounded_probe([sys.executable, "-c", script], timeout=.3)
    assert time.monotonic() - start < 5
    assert result.state == "TIMED_OUT"
    assert "parent exited" in result.stdout


def test_credentials_use_stdin_and_are_redacted_before_output_limit():
    secret = "synthetic-\u0633\u0631-0123456789"
    script = "import sys; s=sys.stdin.read(); print(s); print(s,file=sys.stderr)"
    result = run_bounded_probe([sys.executable, "-c", script], timeout=5,
                              stdin_text=secret, redactions=[secret], output_limit=12)
    assert result.state == "COMPLETED"
    assert result.stdout == "[REDACTED]\n"
    assert result.stderr == "[REDACTED]\n"
    assert secret not in repr(result)


@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan")])
def test_invalid_timeout_never_starts_worker(timeout):
    with pytest.raises(ValueError, match="finite and positive"):
        run_bounded_probe(["unused-synthetic-worker"], timeout=timeout)


def test_missing_worker_is_explicit_error():
    result = run_bounded_probe(["nonexistent-sales-qa-synthetic-worker"], timeout=1)
    assert result.state == "ERROR"
    assert result.returncode is None
    assert "FileNotFoundError" in result.stderr


@pytest.mark.parametrize("description,prefix,requested,expected", [
    ("الفرع *\nفرع تجريبي", "الفرع *", "فرع تجريبي", True),
    ("الفرع *\nفرع تجريبي آخر", "الفرع *", "فرع تجريبي", False),
    ("السنة المالية *\n2026", "السنة المالية *", "2026", True),
    ("السنة المالية *\n20260", "السنة المالية *", "2026", False),
    ("الفرع *", "الفرع *", "فرع تجريبي", False),
])
def test_branch_and_year_selection_requires_exact_option(description, prefix, requested, expected):
    module = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts/android_login_probe.py"))
    assert module["exact_option_selected"](description, prefix, requested) is expected


def test_ui_probe_rejects_invalid_deadline_before_creating_evidence(tmp_path, monkeypatch, capsys):
    script = Path(__file__).resolve().parents[1] / "scripts/android_login_probe.py"
    monkeypatch.setattr(sys, "argv", [str(script), "--output", str(tmp_path/"new"), "--timeout", "nan"])
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(script), run_name="__main__")
    assert error.value.code == 2
    assert "finite and positive" in capsys.readouterr().err
    assert not (tmp_path/"new").exists()


def test_ui_probe_preserves_existing_evidence_without_sdk(tmp_path, monkeypatch, capsys):
    script = Path(__file__).resolve().parents[1] / "scripts/android_login_probe.py"
    evidence = tmp_path/"evidence"; evidence.mkdir()
    existing = evidence/"user.txt"; existing.write_text("preserve me")
    monkeypatch.setattr(sys, "argv", [str(script), "--output", str(evidence)])
    payload = dict(username="synthetic", password="synthetic-secret", branch="test", year="2026")
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    with pytest.raises(SystemExit) as error:
        runpy.run_path(str(script), run_name="__main__")
    assert error.value.code == 2
    assert "new evidence directory" in capsys.readouterr().err
    assert existing.read_text() == "preserve me"
