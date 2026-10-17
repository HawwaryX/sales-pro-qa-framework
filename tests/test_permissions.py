from sales_pro_qa.models import PermissionRecord
from sales_pro_qa.permissions import compare_permissions

def test_detects_system_mismatch():
    result = compare_permissions([PermissionRecord(
        permission="View invoices", dot_x_pro=True, sales_pro=False
    )])
    assert result[0]["system_mismatch"] is True
    assert result[0]["status"] == "REVIEW_REQUIRED"

def test_unknown_permissions_are_incomplete():
    result = compare_permissions([PermissionRecord(
        permission="Delete returns", dot_x_pro=None, sales_pro=None
    )])
    assert result[0]["status"] == "INCOMPLETE"

def test_policy_mismatch():
    result = compare_permissions([PermissionRecord(
        permission="View customers", dot_x_pro=True, sales_pro=True, expected=False
    )])
    assert result[0]["policy_mismatch"] is True
