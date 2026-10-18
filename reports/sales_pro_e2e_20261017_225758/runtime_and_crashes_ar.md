# التشغيل والسجلات

## البيئة الفعلية

Linux في cloud، لا وصول Windows VPS مثبت في هذه الجلسة. emulator37.3.4 وplatform-tools37.0.1 وصورة AOSP Android15/API35 x86_64 من Google، تم فحص الحجم وSHA-1 من metadata الأصلية عبر TLS. لا /dev/kvm ولا vmx/svm؛ accel-check خرج3. شُغل TCG/SwiftShader بنواتين و3072MiB بدل ادعاء تسريع.

أوامر التشغيل الرئيسية الفعلية: emulator مع `-accel off -gpu swiftshader -no-window -no-audio -no-snapshot -cores 2 -port 5554`؛ الصورة والـAVD تحت /workspace/android-runtime. العمليات طويلة البدء انتُظرت حتى `getprop sys.boot_completed=1`.

تعذر adb native أولًا بسبب ~/.android للقراءة فقط. نجح adb-shell عبر loopback، ثم شُغل adb الرسمي في حاوية محلية ذات مجلد مستخدم قابل للكتابة لتشغيل UIAutomator2 وإدخال العربية حرفيًا. بُنيت الحاوية محليًا دون تنزيل، واستُخدم host networking للوصول إلى محاكينا المحلي فقط، مع بقاء الوكيل والسياسة دون تجاوز. أدوات التشغيل محلية اختيارية ولم تُضف dependencies للمشروع.

## أدلة النجاح المحدد

- `pm install -r /data/local/tmp/sales-pro-qa.apk`: Success بعد اكتمال boot؛ [النص](evidence/install_ready.txt).
- `am start -W -n com.infinity.sales.app/.MainActivity`: عملية وشاشة فعلية؛ بعض انتظار am انتهى ببطء TCG، فاعتمد التحقق على الرسم وPID بدل اختزال timeout إلى crash.
- ظهرت أربع صفحات ترحيب والدخول ومكوناته، ثم عاد الدخول بعد Back وإعادة فتح دون clear-data: [الصورة](evidence/login_reopened_rendered.png).
- [حالة العملية وcrash](evidence/final_app_state.txt): Sales Pro PID مرصود وActivity في المقدمة؛ لا اسم حزمته في crash buffer المفحوص. هذا رصد زمني محدود، لا إثبات خلو التطبيق من الانهيارات.
- أعطال Bluetooth وANR في System UI على صورة TCG منفصلة. صورة launch_stable.png تتضمن ANR نظاميًا؛ ليست دليل crash Sales Pro. android_before_application.png شاشة Android قبل الإطلاق، وcold_restart.png وlogin_reopened_without_data_reset.png لقطات splash مبكرة، لا نجاح نموذج مكتمل.
- أخطاء GoogleFonts كانت Failed host lookup / errno7 لـfonts.gstatic.com مع بقاء نص عربي مرسوم؛ لا تعني خطأ تسجيل دخول.

## الشبكة والأمان

منافذ5554/5555 و5037 رُصدت على127.0.0.1/::1 فقط؛ لم ينشر ADB على الإنترنت. عُزلت الشبكة أولًا قبل تثبيت التطبيق، ثم أزيلت قواعد REJECT الخاصة بالاختبار فقط وأعيد تشغيل نفس AVD بالوكيل الموروث الصحيح دون مسح بيانات. [القواعد النهائية](evidence/final_guest_network_rules.txt) تثبت إزالة العزل، ولا تثبت اتصال backend. أوقف Bluetooth في صورة الاختبار بعد أعطاله النظامية لتقليل الضوضاء؛ لم تعطل حماية أو TLS أو مصادقة التطبيق.

لا logcat خام بعد إدخال الحساب في Git؛ أُخرجت أسماء مضيفين/أنواع أخطاء فقط. الحقول حُجبت في XML؛ لقطة خطأ القوائم مقصوصة من المنطقة أسفل الحقول، ثم أُفرغت حقول النموذج فقط قبل تصوير الفحوص التالية. لم تمسح بيانات التطبيق أو قواعده. مفاتيح ADB خارج المستودع.

## استئناف18أكتوبر

شُغل AVD المحفوظ بعد توقف عملياته؛ لا إعادة تثبيت أو clear-data. فشل بدء UIAutomator الأول قبل الإدخال، ثم نجح العامل بعد ضبط مهلة البدء والسقف الإجمالي؛ لا يساوي نجاح العامل نجاح المصادقة. السجل الحالي لا يحتوي crash لحزمة Sales Pro، وواجهتنا System UI ANR عولج بزر Wait داخل المحاكي. لا إعادة لعزل الشبكة. [النتائج الجديدة](resume_20261018_ar.md).

## تشخيص Android اللاحق

أُثبت HTTPS فعلي داخل Android عبر وكيل الجلسة وCA المناسبة للمسبار: TLS1.3 وHTTP200. DNS الافتراضي فاشل، ووجهة التطبيق ترد عند الوكيل CONNECT403 قبل TLS مع الأصل. تجربة proxy نظامي مؤقت لم تفتح القوائم، وأعيد الإعداد الأصلي. لا مصادقة أو أعمال إضافية. تشخيص البيئة منفصل:3 PASS و4 FAIL و2 BLOCKED؛الوظائف تبقى23 PASS و4 FAIL و54 BLOCKED و3 NOT RUN. [التفاصيل والأدلة](android_connectivity_ar.md).

## متابعة التنفيذ بعد تطبيق المراجعة 3

المراجعة 3 تسمح بالمضيف؛ CONNECT200 وTLS موثق ثم HTTP404 للجذر من Linux. DNS في Android ما زال يفشل بـUnknownHostException؛ القوائم لم تُحمّل ولا دخول مصادق. نجحت RT-33–35 (تكبير الخط وTab ونص 1024 حرفًا دون تقديم)، وحالة تخطي الترحيب BLOCKED في مستخدم مؤقت حُذف بعد العودة للأصلي. الدفتر: PASS: 26؛ FAIL: 4؛ BLOCKED: 55؛ NOT RUN: 2؛ 87 حالة. لا معاملات أو مزامنة أعمال. لا إعادة للطلب المحجوب أو الفحص الثابت.

[محاولة القوائم](evidence/followup_20261018/login_once/observations.json)؛[فحوص UI](evidence/followup_20261018/ui_additional_ready/followup_observations.json)؛[اختبار التخطي](evidence/followup_20261018/skip_isolated_user/result.json).

## جاهزية فحوص UI الجديدة وحدودها

توقف عاملان مبكران قبل أي تغيير لأن شجرة العرض لم تُظهر نموذج الدخول؛ فرضية التمرير وحدها لم تثبت. في الفحص الأخير رُصد حوار عدم استجابة System UI: صفر عقد للتطبيق، ثم بعد ضغط Wait مرة واحدة ظهرت28 عقدة وحقلان. أُنجزت الفحوص الثلاثة في107.13 ثانية مع استعادة الخط وتنظيف المدخلات. هذا حاجز أداة/نظام، وليس عيبًا جديدًا في Sales Pro. [تسلسل الجاهزية](evidence/followup_20261018/ui_additional_ready/followup_observations.json).

الأوامر النظامية للفحوص المحددة: `settings get system font_scale`، ثم `settings put system font_scale 2.0` وإعادة القيمة الأصلية؛ `input keyevent KEYCODE_TAB` دون Enter. النص الطويل اصطناعي ولم يُقدم. بعد تجربة المستخدم المؤقت تحقق الرجوع للمستخدم0 وحذف المؤقت، وبقاء التطبيق عاملًا والخط1.0 والوكيل النظاميnull، دون اسم حزمة Sales Pro في crash buffer. [الحالة النهائية](evidence/followup_20261018/final_runtime_state.json).

## متابعة دورة الحياة وجاهزية Android

الدفتر الوظيفي: **PASS: 28؛ FAIL: 4؛ BLOCKED: 55؛ NOT RUN: 2**؛ 89 حالة. نجحت RT-36 وRT-37 محليًا، ولا دخول أو عمليات أعمال أو مزامنة مالية منفذة. سُجلت8 قواعد NEEDS BUSINESS RULE CONFIRMATION منفصلة عن العدّ الوظيفي. أُصلح حارس جاهزية Android؛ **93 passed** على Python3.12 و93 على3.13. لم يُكرر طلب HTTP أو إدخال الحساب مع بقاء عائق DNS.

رُصد boot_completed=1 قبل اكتمال RUNNING_UNLOCKED؛ لم تُعد تثبيت الحزمة لأنها كانت موجودة. انتهت الحالة طبيعيًا دون فتح مستخدم أو تغيير قفل. فحص النوم والإيقاظ لم يعرض قفلًا؛ لا نجاح مختلق لاختبار PIN. [النتيجة الفعلية](evidence/autonomous_20261018/lifecycle_ready/observations.json).


## متابعة اختبار التطبيق فقط — 18 أكتوبر 2026

نجحت RT-38: تركيز الحقلين فارغين في landscape مع لوحة مفاتيح ظاهرة، ثم الوصول بالتمرير إلى زر الدخول كاملًا فوقها دون الضغط. عاد الوضع الرأسي وأُخفيت اللوحة واستُعيدت الإعدادات. التراكمي الحالي: **PASS: 29؛ FAIL: 4؛ BLOCKED: 55؛ NOT RUN: 2**؛ 90 حالة. لا عيب تطبيق جديد مثبت. [المراجعة والأدلة](evidence/application_only_20261018/application_review.json).

ظل تحذير تحميل الفروع أو السنوات ظاهرًا؛ لم تُستخدم قيمة الفرع الافتراضي بدل المركز الرئيسي و2026، ولم يُرسل الدخول أو تُثبت TEST أو تُنفذ عمليات أعمال. تغيّرت البيئة إلى revision4 ففُحص الوصول مرة واحدة: سماح المضيف فعال، DNS من المضيف فاشل، CONNECT200 وTLS ناجحان، وHEAD للجذر HTTP404 دون تحويل. ليس ذلك عنوان API كاملًا أو اختبار مصادقة؛ CONNECT403 تاريخي. لا مسار Android بديل معتمد متاح، ولا تكرار للطلب المحجوب. [الفحص المحدود](evidence/application_only_20261018/access_revision4.json).

تعثر بدء الأتمتة مع حوار System UI؛ استُخدم «انتظار» مرة واحدة وعملت بعدها. انقطعت عملية التقاط صورة أثناء فحص الحقل الثاني بـAdbTimeout؛ حُفظ XML الحقيقي واستُكمل الزر وحده دون صور، مع انتظار محدود لهندسة IME. لا تُحسب أعطال أدوات الاختبار كعيوب Sales Pro. لم يتغير كود الإطار أو APK، فلم تُعد pytest أو الفحوص الثابتة.
