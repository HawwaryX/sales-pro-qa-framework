from sales_pro_qa.report import render_arabic_report, write_report

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


def test_written_report_contains_actual_line_breaks(tmp_path):
    output = tmp_path / "report.md"
    write_report({"project_name": "Demo"}, output)

    report = output.read_text(encoding="utf-8")
    assert report.startswith("# تقرير ضمان الجودة — Demo\n\n")
    assert "\n\n## ملخص الاختبارات\n\n" in report
    assert "\\n" not in report
