"""Readiness regressions use only synthetic ADB output and a virtual clock."""
import pytest

from sales_pro_qa.android_readiness import (
    MAIN_ACTIVITY,
    AndroidReadinessTimeout,
    wait_for_android_ready,
)


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class Shell:
    def __init__(self, *, user="0", state="RUNNING_UNLOCKED", component=MAIN_ACTIVITY):
        self.user = user
        self.state = state
        self.component = component
        self.calls = []

    def __call__(self, arguments, *, timeout):
        self.calls.append((arguments, timeout))
        if arguments == ["getprop", "sys.boot_completed"]:
            return "1\n"
        if arguments == ["am", "get-current-user"]:
            return self.user + "\n"
        if arguments[:2] == ["am", "get-started-user-state"]:
            return self.state + "\n"
        if arguments[:3] == ["cmd", "package", "resolve-activity"]:
            return self.component + "\n"
        raise AssertionError("Unexpected command")


def test_boot_completed_does_not_make_unlocking_user_ready():
    clock = Clock()
    shell = Shell(state="RUNNING_UNLOCKING")
    with pytest.raises(AndroidReadinessTimeout) as error:
        wait_for_android_ready(shell, timeout=3, clock=clock, sleep=clock.sleep)
    assert error.value.observation.boot_completed is True
    assert error.value.observation.user_state == "RUNNING_UNLOCKING"
    assert error.value.observation.activity_resolved is False
    assert not any(args[0] == "cmd" for args, _ in shell.calls)
    assert clock.now == 3


@pytest.mark.parametrize("component", [
    MAIN_ACTIVITY,
    "com.infinity.sales.app/com.infinity.sales.app.MainActivity",
])
def test_unlocked_current_user_and_exact_activity_are_ready(component):
    shell = Shell(user="10", component=component)
    clock = Clock()
    result = wait_for_android_ready(shell, clock=clock, sleep=clock.sleep)
    assert result.boot_completed is True
    assert result.user_id == 10
    assert result.user_state == "RUNNING_UNLOCKED"
    assert result.activity_resolved is True
    assert shell.calls[-1][0] == ["cmd", "package", "resolve-activity", "--brief",
                                   "--user", "10", "-n", MAIN_ACTIVITY]
    assert clock.now == 0


@pytest.mark.parametrize("component", ["No activity found", "", "other.app/.MainActivity"])
def test_missing_or_different_activity_does_not_allow_ui_start(component):
    clock = Clock()
    with pytest.raises(AndroidReadinessTimeout) as error:
        wait_for_android_ready(Shell(component=component), timeout=1,
                               clock=clock, sleep=clock.sleep)
    assert error.value.observation.activity_resolved is False
    assert error.value.observation.user_state == "RUNNING_UNLOCKED"


@pytest.mark.parametrize("user", ["", "-1", "Error: unavailable", "0; synthetic-command", "٠"])
def test_invalid_user_id_is_never_forwarded_to_shell(user):
    clock = Clock()
    shell = Shell(user=user)
    with pytest.raises(AndroidReadinessTimeout) as error:
        wait_for_android_ready(shell, timeout=1, clock=clock, sleep=clock.sleep)
    assert error.value.observation.user_id is None
    assert all(args[0] != "cmd" and args[:2] != ["am", "get-started-user-state"]
               for args, _ in shell.calls)


def test_deadline_limits_each_command_and_preserves_partial_observation():
    clock = Clock()
    calls = []

    def slow_shell(arguments, *, timeout):
        calls.append(timeout)
        assert timeout <= 1 - clock.now
        clock.now += timeout
        return "1"

    with pytest.raises(AndroidReadinessTimeout) as error:
        wait_for_android_ready(slow_shell, timeout=1, command_timeout=10,
                               clock=clock, sleep=clock.sleep)
    assert calls == [1]
    assert clock.now == 1
    assert error.value.observation.boot_completed is True


def test_adb_timeout_is_bounded_and_raw_error_is_not_retained():
    clock = Clock()
    budgets = []

    def failing_shell(arguments, *, timeout):
        budgets.append(timeout)
        clock.now += timeout
        raise OSError("synthetic-sensitive-output")

    with pytest.raises(AndroidReadinessTimeout) as error:
        wait_for_android_ready(failing_shell, timeout=3, command_timeout=2,
                               poll_interval=.5, clock=clock, sleep=clock.sleep)
    assert budgets == [2, .5]
    assert clock.now == 3
    assert "synthetic-sensitive-output" not in str(error.value)
    assert "synthetic-sensitive-output" not in repr(error.value.observation)


def test_wait_rechecks_until_user_finishes_unlocking():
    clock = Clock()
    shell = Shell(state="RUNNING_UNLOCKING")

    def finish_unlocking(seconds):
        clock.sleep(seconds)
        shell.state = "RUNNING_UNLOCKED"

    result = wait_for_android_ready(shell, timeout=3, clock=clock, sleep=finish_unlocking)
    assert result.activity_resolved is True
    assert clock.now == 1


@pytest.mark.parametrize("name,value", [("timeout", 0), ("timeout", float("nan")),
                                        ("command_timeout", -1), ("poll_interval", float("inf"))])
def test_invalid_limits_do_not_run_commands(name, value):
    shell = Shell()
    with pytest.raises(ValueError, match="finite and positive"):
        wait_for_android_ready(shell, **{name: value})
    assert shell.calls == []
