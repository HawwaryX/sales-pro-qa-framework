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
