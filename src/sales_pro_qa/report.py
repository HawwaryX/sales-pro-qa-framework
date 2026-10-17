from collections import Counter
from pathlib import Path

AR_STATUS = {"PASS": "ناجح", "FAIL": "فاشل", "BLOCKED": "متعذر", "NOT_RUN": "لم يُنفذ"}

def render_arabic_report(audit: dict) -> str:
    tests = audit.get("tests", [])
    defects = audit.get("defects", [])
    permissions = audit.get("permissions", [])
    counts = Counter(t.get("status", "NOT_RUN") for t in tests)
    lines = [
        f"# تقرير ضمان الجودة — {audit.get('project_name', 'Sales Pro')}",
        "",
        f"- **تاريخ التقرير:** {audit.get('date', 'غير محدد')}",
        f"- **البيئة:** {audit.get('environment', 'غير محددة')}",
        "- **مصدر البيانات:** بيانات اختبار/نتائج مقدمة؛ لم يتم التحقق تلقائيًا من الأنظمة الحية.",
        "",
        "## ملخص الاختبارات",
        "",
        f"- إجمالي الحالات: **{len(tests)}**",
        f"- ناجح: **{counts['PASS']}**",
        f"- فاشل: **{counts['FAIL']}**",
        f"- متعذر: **{counts['BLOCKED']}**",
        f"- لم يُنفذ: **{counts['NOT_RUN']}**",
        "",
        "## تفاصيل الاختبارات",
        "",
        "| المعرّف | الحالة | الوحدة | النتيجة المتوقعة | النتيجة الفعلية |",
        "|---|---|---|---|---|",
    ]
    for test in tests:
        lines.append(
            f"| {test.get('test_id','—')} | {AR_STATUS.get(test.get('status','NOT_RUN'), test.get('status'))} "
            f"| {test.get('module','—')} | {test.get('expected','—')} | {test.get('actual','—')} |"
        )
    lines += ["", "## مقارنة الصلاحيات", ""]
    if permissions:
        lines += [
            "| الوحدة | الصلاحية | Dot X Pro | Sales Pro | الحالة |",
            "|---|---|---|---|---|",
        ]
        for p in permissions:
            def fmt(value):
                return "مسموح" if value is True else "ممنوع" if value is False else "غير معروف"
            lines.append(
                f"| {p.get('module','—')} | {p.get('permission','—')} | {fmt(p.get('dot_x_pro'))} "
                f"| {fmt(p.get('sales_pro'))} | {p.get('status','غير محدد')} |"
            )
    else:
        lines.append("لم تُرفق نتائج مقارنة صلاحيات. لا يُعد ذلك تدقيقًا مباشرًا للنظام.")
    lines += ["", "## العيوب", ""]
    if defects:
        for defect in defects:
            lines += [
                f"### {defect.get('defect_id','—')} — {defect.get('title','بدون عنوان')}",
                f"- الوحدة: {defect.get('module','—')}",
                f"- الخطورة: {defect.get('severity','غير محددة')}",
                f"- الحالة: {defect.get('status','غير محددة')}",
                f"- المتوقع: {defect.get('expected','—')}",
                f"- الفعلي: {defect.get('actual','—')}",
                "",
            ]
    else:
        lines.append("لا توجد عيوب مرفقة في بيانات التقرير.")
    lines += ["", "## حدود التحقق", "", audit.get(
        "limitations", "يعكس هذا التقرير البيانات المُدخلة فقط؛ يلزم التحقق من الأدلة قبل اعتبار أي نتيجة عيبًا مؤكدًا."
    ), ""]
    return "\n".join(lines)

def write_report(audit: dict, output: str | Path) -> None:
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(render_arabic_report(audit), encoding="utf-8")
