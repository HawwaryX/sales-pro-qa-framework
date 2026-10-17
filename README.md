# Sales Pro QA Framework

إطار عمل لتوثيق وتنفيذ اختبارات ضمان الجودة لتطبيق Sales Pro ومقارنة نتائج الاختبار مع Dot X Pro.

> الاختبارات المرفقة تستخدم بيانات اصطناعية فقط. لا يتصل المشروع افتراضيًا بأي نظام إنتاج ولا ينفذ معاملات مالية حقيقية.

## المتطلبات
- Python 3.11+
- pytest

## التثبيت والتشغيل
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
python -m sales_pro_qa.cli --config config/sample_config.json --input examples/sample_audit.json --output reports/sample_arabic_report.md
```

## المكونات
- التحقق من إعدادات المشروع.
- نماذج حالات الاختبار والعيوب.
- مقارنة الصلاحيات بين Dot X Pro وSales Pro.
- إنشاء Evidence Manifest بمراجع نسبية للملفات.
- إنشاء تقرير Markdown باللغة العربية.
- اختبارات pytest ببيانات اصطناعية.

## بيانات الدخول والأسرار
لا تحفظ كلمات المرور أو الرموز أو بيانات العملاء داخل المستودع أو ملفات التقارير أو السجلات. استخدم آلية أسرار معتمدة فقط عند الحاجة. لا يقرأ المشروع بيانات دخول من ملفات الإعدادات ولا يتصل بالتطبيقات تلقائيًا.

## تدقيق الصلاحيات المباشر
هذا المشروع يوفر محرك مقارنة وقالب تدقيق. لا يدّعي الوصول إلى سطح مكتب Windows أو تطبيق Android. أدخل نتائج موثقة يدويًا أو من تكامل مصرح به، وأرفق الأدلة الفعلية فقط.

## حالات الاختبار
الحالات المدعومة: `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`.
مستويات الخطورة: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`.

## CI
يشغّل GitHub Actions الاختبارات تلقائيًا عند فتح Pull Request أو الدفع إلى `main`.
