"""Bounded Android readiness checks, independent of an Android SDK or UI library."""
from dataclasses import dataclass
import math
import time
from typing import Callable


MAIN_ACTIVITY = "com.infinity.sales.app/.MainActivity"


@dataclass(frozen=True)
class AndroidReadiness:
    boot_completed: bool = False
    user_id: int | None = None
    user_state: str = "UNKNOWN"
    activity_resolved: bool = False


class AndroidReadinessTimeout(TimeoutError):
    """A deadline expired; only the sanitized last observation is retained."""

    def __init__(self, observation: AndroidReadiness):
        super().__init__("Android user or application is not ready within the deadline")
        self.observation = observation


def wait_for_android_ready(
    shell: Callable,
    *,
    timeout: float = 60,
    command_timeout: float = 5,
    poll_interval: float = 1,
    clock: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> AndroidReadiness:
    """Wait for boot, an unlocked current user, and the known launch activity.

    ``shell`` receives an argument list and a timeout, as adbutils.device.shell
    does. It must honor that timeout; the outer worker deadline remains a second
    safeguard. No unlock action, credential handling or setting changes occur.
    Command output and exception messages are never retained.
    """
    for name, value in (("timeout", timeout), ("command_timeout", command_timeout),
                        ("poll_interval", poll_interval)):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")
    deadline = clock() + timeout
    observation = AndroidReadiness()

    def run(arguments: list[str]) -> str:
        remaining = deadline - clock()
        if remaining <= 0:
            raise AndroidReadinessTimeout(observation)
        return shell(arguments, timeout=min(command_timeout, remaining)).strip()

    while clock() < deadline:
        boot_completed = False
        user_id = None
        user_state = "UNKNOWN"
        activity_resolved = False
        try:
            boot_completed = run(["getprop", "sys.boot_completed"]) == "1"
            if boot_completed:
                current_user = run(["am", "get-current-user"])
                # Never forward arbitrary shell output into another command.
                if current_user.isascii() and current_user.isdecimal():
                    user_id = int(current_user)
                    state = run(["am", "get-started-user-state", str(user_id)])
                    if state in {"BOOTING", "RUNNING_LOCKED", "RUNNING_UNLOCKING",
                                 "RUNNING_UNLOCKED", "STOPPING", "SHUTDOWN"}:
                        user_state = state
                    if user_state == "RUNNING_UNLOCKED":
                        resolved = run(["cmd", "package", "resolve-activity", "--brief",
                                        "--user", str(user_id), "-n", MAIN_ACTIVITY])
                        # Android may print diagnostic lines before the component.
                        component = resolved.splitlines()[-1] if resolved else ""
                        activity_resolved = component in {
                            MAIN_ACTIVITY,
                            "com.infinity.sales.app/com.infinity.sales.app.MainActivity",
                        }
        except AndroidReadinessTimeout:
            raise AndroidReadinessTimeout(AndroidReadiness(
                boot_completed, user_id, user_state, activity_resolved)) from None
        except Exception:
            # ADB exceptions may include command output. Retry without storing it.
            pass
        observation = AndroidReadiness(boot_completed, user_id, user_state, activity_resolved)
        if activity_resolved and clock() <= deadline:
            return observation
        remaining = deadline - clock()
        if remaining > 0:
            sleep(min(poll_interval, remaining))
    raise AndroidReadinessTimeout(observation)
