from sales_pro_qa.report import render_arabic_report

def test_report_contains_arabic_summary_and_limits():
    report = render_arabic_report({
        "project_name": "Demo",
        "tests": [{"test_id": "T-1", "status": "FAIL", "module": "الفواتير"}],
        "permissions": [],
        "defects": [],
        "limitations": "بيانات اصطناعية فقط"
    })
    assert "تقرير ضمان الجودة" in report
    assert "فاشل: **1**" in report
    assert "بيانات اصطناعية فقط" in report
