"""Bounded supervision for optional device/UI workers; no Android dependency.

A completed worker is not evidence that an application test passed. Credentials
belong in stdin, never command arguments. Workers must also sanitize evidence
before writing it; output redaction cannot protect files written by the worker.
"""
from dataclasses import dataclass
import math
import os
import signal
import subprocess
import time
from collections.abc import Sequence


@dataclass(frozen=True)
class ProbeResult:
    state: str
    returncode: int | None
    elapsed_seconds: float
    stdout: str
    stderr: str


def run_bounded_probe(command: Sequence[str], *, timeout: float,
                      stdin_text: str = "", redactions: Sequence[str] = (),
                      output_limit: int = 16000) -> ProbeResult:
    """Run a trusted worker without shell, with an absolute wall-time limit.

    On POSIX the worker gets its own session and its descendants are killed on
    timeout. Pipe cleanup has a separate two-second limit. On Windows the direct
    worker is killed; descendant termination is not guaranteed. All states are
    process outcomes (COMPLETED/FAILED/TIMED_OUT/ERROR), never application PASS.
    """
    if isinstance(command, (str, bytes)) or not command:
        raise ValueError("command must be a nonempty argument sequence")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be finite and positive")
    if not isinstance(output_limit, int) or output_limit < 1:
        raise ValueError("output_limit must be a positive integer")
    started = time.monotonic()

    def clean(value: bytes) -> str:
        text = value.decode("utf-8", errors="replace")
        for secret in sorted(set(redactions) - {""}, key=len, reverse=True):
            text = text.replace(secret, "[REDACTED]")
        return text[:output_limit]

    try:
        proc = subprocess.Popen(list(command), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=False, start_new_session=os.name == "posix")
    except OSError as exc:
        return ProbeResult("ERROR", None, time.monotonic() - started, "",
                           type(exc).__name__ + ": unable to start worker")
    try:
        stdout, stderr = proc.communicate(stdin_text.encode("utf-8"), timeout=timeout)
        state = "COMPLETED" if proc.returncode == 0 else "FAILED"
    except subprocess.TimeoutExpired:
        state = "TIMED_OUT"
        if os.name == "posix":
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        if proc.poll() is None:
            proc.kill()
        try:
            stdout, stderr = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired as exc:
            stdout, stderr = exc.output or b"", exc.stderr or b""
            for pipe in (proc.stdin, proc.stdout, proc.stderr):
                if pipe is not None:
                    pipe.close()
    return ProbeResult(state, proc.returncode, time.monotonic() - started,
                       clean(stdout), clean(stderr))
