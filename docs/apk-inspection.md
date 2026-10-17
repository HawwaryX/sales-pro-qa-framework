# فحص Android APK الثابت

توفر الوحدة فحصًا للبيانات الوصفية وصلاحيات Android Manifest وسلامة ZIP وCRC،
مع حساب SHA-256 والحجم والتحقق الاختياري من التوقيع. لا تعدل APK أو تثبته أو تشغله.
يتطلب المشروع Python 3.11+ دون تبعيات Python إضافية للتشغيل.

## التثبيت والتشغيل

استخدم البيئة الافتراضية الموجودة، أو أنشئها مرة واحدة عند الحاجة:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pip check
python -m pytest
```

ثبّت Android SDK Command-line Tools وBuild-Tools من المصدر الرسمي مع مراجعة
التراخيص. على Debian يمكن توفير aapt من المستودعات الموقعة:

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends aapt apksigner
aapt version
```

إذا كان APK مخزنًا في Git LFS، نفذ `git lfs pull` أولًا. لا تضف ملفات APK أخرى
أو أسرارًا أو بيانات عملاء إلى Git ضمن أعمال الفحص.

```bash
sales-pro-apk --apk apk-input/app-sales-pro-v8.apk --output /tmp/apk-report.md
python -m sales_pro_qa.apk_cli --apk apk-input/app-sales-pro-v8.apk --output /tmp/apk-report-module.md
```

تظل الواجهة السابقة متاحة:

```bash
python -m sales_pro_qa.cli --apk apk-input/app-sales-pro-v8.apk --output /tmp/apk-report-legacy.md
```

استخدم `--android-sdk` لتحديد جذر SDK، أو `--aapt` و`--apkanalyzer` و`--apksigner`
لتحديد الأدوات صراحة. يدعم `--apksigner` ملف JAR عند توفر Java. تضبط `--timeout`
المهلة لكل أداة (الافتراضي 60 ثانية). تُدعم المسارات ذات المسافات.

راجع [الدليل العربي لـ Windows](android-static-inspection-windows.md) للمسارات
والأوامر ونتائج الخروج وسياسة اكتشاف الأدوات.

## النتائج والحدود

- يعرض التقرير الحزمة والإصدار وقيم SDK والصلاحيات ودلالاتها وقيود manifest المتاحة.
  القيم الغائبة غير متاحة ولا تُستنتج؛ القوائم لا تثبت منح الصلاحيات أو استخدامها.
- فحص التوقيع عند توفر apksigner يسجل بصمة الشهادة العامة وخوارزمية المفتاح.
  غياب الأداة يعني NOT_RUN، والفشل FAIL، وفشل التشغيل أو المهلة ERROR.
  تحذير اسم شهادة Debug ليس دليلًا على برمجية خبيثة أو إثباتًا لهوية الناشر.
- تتطلب نتيجة تحليل ناجحة تنفيذ أداة Android بنجاح ومخرجات قابلة للتحليل؛
  لا يكفي وجود الملف. أخطاء الملف أو التحليل تنتج رمز خروج غير صفري دون تقرير نجاح جديد.
- التقارير لا تحفظ stdout/stderr الخام أو أسماء أصحاب الشهادات أو مسارات المجلدات.
  استخدم أسماء ملفات وبيانات تطبيق لا تتضمن معلومات حساسة.
- اختبارات الوحدة تستخدم ZIP ومخرجات أدوات اصطناعية معزولة؛ لا تحتاج Android SDK
  في CI، ولا تثبت نجاح APK حقيقي أو إمكانية تثبيته.
- الفحص الثابت لا يثبت سلامة التطبيق ولا يحلل سلوك الشبكة أو الشيفرة المحمية.
  التثبيت والتشغيل والمصادقة وسلوك الصلاحيات تحتاج جهازًا أو محاكيًا مصرحًا به
  وبيانات اصطناعية، دون تجاوز المصادقة أو صلاحيات التطبيق.
