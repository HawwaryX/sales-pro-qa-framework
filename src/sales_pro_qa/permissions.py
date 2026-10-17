from .models import PermissionRecord

def compare_permissions(records: list[PermissionRecord]) -> list[dict]:
    results = []
    for record in records:
        mismatch = (
            record.dot_x_pro is not None
            and record.sales_pro is not None
            and record.dot_x_pro != record.sales_pro
        )
        policy_mismatch = (
            record.expected is not None
            and (
                (record.dot_x_pro is not None and record.dot_x_pro != record.expected)
                or (record.sales_pro is not None and record.sales_pro != record.expected)
            )
        )
        results.append({
            "module": record.module,
            "permission": record.permission,
            "dot_x_pro": record.dot_x_pro,
            "sales_pro": record.sales_pro,
            "expected": record.expected,
            "system_mismatch": mismatch,
            "policy_mismatch": policy_mismatch,
            "evidence": list(record.evidence),
            "status": "REVIEW_REQUIRED" if mismatch or policy_mismatch else (
                "INCOMPLETE" if record.dot_x_pro is None or record.sales_pro is None else "CONSISTENT"
            ),
        })
    return results
