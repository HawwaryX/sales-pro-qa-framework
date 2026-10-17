from dataclasses import dataclass, field
from typing import Literal

TestStatus = Literal["PASS", "FAIL", "BLOCKED", "NOT_RUN"]
Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]

@dataclass
class TestCase:
    test_id: str
    title: str
    module: str
    preconditions: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    expected: str = ""
    actual: str = ""
    status: TestStatus = "NOT_RUN"
    severity: Severity = "MEDIUM"
    priority: str = "P2"
    evidence: list[str] = field(default_factory=list)

@dataclass
class Defect:
    defect_id: str
    title: str
    module: str
    severity: Severity
    steps: list[str]
    expected: str
    actual: str
    evidence: list[str] = field(default_factory=list)
    status: str = "OPEN"
    environment: str = "Not specified"
    notes: str = ""

@dataclass
class PermissionRecord:
    permission: str
    dot_x_pro: bool | None
    sales_pro: bool | None
    expected: bool | None = None
    evidence: list[str] = field(default_factory=list)
    module: str = "عام"
