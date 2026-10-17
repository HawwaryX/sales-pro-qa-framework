# فحص Android APK الثابت على Windows

## المتطلبات

- Python 3.11 أو أحدث؛ Python 3.13 مدعوم دون مكتبات تشغيل إضافية.
- Android SDK Command-line Tools وBuild-Tools، وJava المتوافق مع إصدار أدوات SDK.
- المسارات النموذجية: SDK في `C:\Android`، وapkanalyzer في
  `C:\Android\cmdline-tools\latest\bin\apkanalyzer.bat`، وapksigner في
  `C:\Android\build-tools\36.0.0\apksigner.bat`.
- تُثبت أدوات SDK من المصدر الرسمي باستخدام Android Studio SDK Manager أو sdkmanager
  بعد مراجعة تراخيص Android. لا يتطلب الفحص ADB أو جهازًا أو محاكيًا.

## إعداد Python

من جذر المشروع في PowerShell، أنشئ بيئة افتراضية فقط إذا لم تكن موجودة:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest
```

إذا كان APK في Git LFS، نفذ `git lfs pull` قبل الفحص. تُرفض ملفات مؤشرات LFS
التي لم تُستبدل بمحتوى APK الفعلي.

## CLI المستقل

الأمر التالي لا يحتاج تفعيل البيئة أو تعديل PATH، ويحافظ على المسارات ذات المسافات:

```powershell
.\.venv\Scripts\python.exe -m sales_pro_qa.apk_cli --apk "apk-input\app-sales-pro-v8.apk" --android-sdk "C:\Android" --apkanalyzer "C:\Android\cmdline-tools\latest\bin\apkanalyzer.bat" --apksigner "C:\Android\build-tools\36.0.0\apksigner.bat" --timeout 60 --output "reports\android-apk-static-ar.md"
```

بعد تثبيت الحزمة يتوفر الأمر `sales-pro-apk` بالوسائط نفسها:

```powershell
.\.venv\Scripts\sales-pro-apk.exe --apk "C:\QA Files\app-sales-pro-v8.apk" --android-sdk "C:\Android" --output "C:\QA Reports\apk-static-ar.md"
```

تظل الواجهة القديمة `python -m sales_pro_qa.cli --apk ... --output ...` متاحة،
وكذلك سير تقارير التدقيق الأصلي باستخدام `--config` و`--input`.
استخدم وجهة تقرير جديدة لحفظ تقارير سابقة؛ يُرفض اختيار APK نفسه أو رابط إليه كوجهة.

## الأدوات والنتائج

- تحديد `--apkanalyzer` يختار `manifest print` لتحليل XML. وإلا يُفضل aapt عند توفره،
  ثم apkanalyzer عند غيابه. لا يُتجاهل فشل أداة اختيرت بالفعل بالانتقال إلى أداة أخرى.
- اكتشاف الأدوات: المسار الصريح، PATH، ثم مجلدات SDK المحدد عبر `--android-sdk`
  أو `ANDROID_SDK_ROOT` أو `ANDROID_HOME`. يبحث apkanalyzer داخل cmdline-tools/latest/bin،
  وبقية الأدوات داخل build-tools. القيم الغائبة في manifest تبقى غير متاحة.
- يُقرأ ZIP وتُراجع CRC لجميع عناصره دون استخراج أو تشغيل؛ تُرفض الأسماء المكررة
  والأرشيفات التي تتجاوز 100000 عنصر أو 2 GiB من الحجم غير المضغوط.
  هذه مراجعة بنية وليست ضمان قبول Android لتثبيت التطبيق.
- التوقيع يُفحص بواسطة `apksigner verify --verbose --print-certs`. غياب الأداة يعني
  NOT_RUN، والفشل FAIL، والمهلة أو مخرجات شهادة غير مكتملة ERROR. لا تعني NOT_RUN نجاح التوقيع.
- تُسجل صيغة الشهادة X.509 وخوارزمية المفتاح وحجمه وبصمة SHA-256 لكل موقّع.
  تُكتشف شهادة Debug بمطابقة اسم CN القياسي Android Debug؛ هذا مؤشر تسمية قابل للتقليد،
  وليس إثبات هوية أو فحص برمجيات خبيثة. عدم وجود هذا الاسم لا يثبت أن الشهادة إنتاجية.
- رمز خروج CLI: صفر عند إتمام الفحص (قد يكون التوقيع NOT_RUN)، 1 عند FAIL/ERROR
  للتوقيع مع حفظ التقرير، و2 عند فشل الملف أو الأداة أو تحليل manifest دون تقرير نجاح جديد.
  التقرير الموجود من تشغيل سابق لا يُحذف عند الفشل؛ افحص رمز الخروج لتجنب اعتباره نتيجة جديدة.

## الخصوصية والأمان وحدود الفحص

- لا يتم تعديل APK أو تثبيته أو تشغيله أو الاتصال بخدماته. لا تُستخدم أسرار أو بيانات عملاء.
- لا تُحفظ stdout/stderr الخام أو أسماء أصحاب الشهادات أو مسارات المجلدات في التقارير.
  تُعرض بيانات التطبيق المطلوبة، بصمات الشهادات العامة، أسماء ملفات الأوامر، ورموز الخروج.
  أسماء ملفات APK وبيانات التطبيق نفسها تظهر في التقرير؛ لا تستخدم أسماء أو بيانات حساسة فيها.
- تنفذ الأدوات الموثوقة بقائمة وسائط وsubprocess ومهلة محدودة، دون تركيب أوامر shell.
  على Windows، تُرفض محارف التحكم/التوسع مثل `% ! & | < > ^ ( )` وعلامات الاقتباس
  داخل مسارات ملفات batch أو وسائطها. المسافات مدعومة. لا تُشغل أدوات SDK من مصادر مجهولة.
- لكل صلاحية وصف وملاحظة مراجعة؛ الصلاحيات الجديدة والخاصة لا تُعطى دلالة مفترضة.
  الإعلان لا يثبت منح الصلاحية أو استخدامها؛ القيود الفعلية تعتمد على Android وSDK وسياسة المنح.
- التوقيع السليم لا يثبت موثوقية الناشر، والفحص الثابت لا يثبت سلامة التطبيق ولا يغني عن Runtime.
  التثبيت والشاشة الأولى وتسجيل الدخول وسير العمل تتطلب جهازًا أو محاكيًا مصرحًا به ومهمة منفصلة.
- اختبارات pytest تستخدم ZIP اصطناعيًا ومخرجات أدوات معزولة؛ لا تحتاج Android SDK في CI.
  اختبار تشغيل Windows الفعلي منفصل عن اختبارات اكتشاف مسارات Windows على Linux.
