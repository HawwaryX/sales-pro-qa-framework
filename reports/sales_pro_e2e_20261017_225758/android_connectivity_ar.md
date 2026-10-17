# إثبات اتصال Android وتشخيصه — 18أكتوبر2026

## الاستنتاج المتحقق

Android **متصل بشبكة**، ويستطيع الوصول إلى الإنترنت عبر وكيل الجلسة وثقة CA المناسبة: نفّذ المسبار داخل Android تفاوض TLS1.3 وطلب HEAD فعليًا وحصل على HTTP200 من dl.google.com. لا يصح وصف الجهاز بأنه بلا أي اتصال بالإنترنت، أو تفسير403 كدليل على ذلك.

لكن **المسار الافتراضي غير صالح لطلبات التطبيق الحالية**: resolver الافتراضي يفشل، وثقة Android الافتراضية فشلت مع شهادة مسار الوكيل في اختبار التحكم. وفوق ذلك يرفض الوكيل CONNECT لمضيف التطبيق برمز403 قبل TLS مع الأصل. هذه حواجز مستقلة؛ لم تصل استجابة backend ولم تثبت هوية TEST أو المسار الكامل لـAPI.

## النتائج بالترتيب المطلوب

| الفحص | النتيجة الفعلية | التفسير |
|---|---|---|
| واجهات وعناوين | eth0 UP،10.0.2.15/24؛default عبر10.0.2.2 | لا انقطاع رابط شبكي مثبت |
| dumpsys connectivity | MOBILE HSPA CONNECTED،DNS10.0.2.3،بلا VALIDATED | لا يثبت VALIDATED=false وحده انعدام الإنترنت لكل وجهة |
| dumpsys wifi | Wi-Fi غير متصل | مسار MOBILE/eth0 هو القائم؛Wi-Fi ليس شرطًا في المحاكي |
| DNS Android لمضيف التطبيق | UnknownHostException/GaiException | فشل resolver؛لا نتيجة مصادقة |
| HTTPS افتراضي لمضيف التطبيق | UnknownHostException عندDNS_OR_TCP | لم يحدث TLS أو HTTP من الأصل |
| HTTPS عبر وكيل الجلسة إلى المضيف | CONNECT403؛TLS=false | رفض وكيل؛لا HTTP403 صادر من التطبيق أو backend |
| وجهة مسموحة عبر الوكيل بثقة Android الافتراضية | CONNECT200 ثم SSLHandshakeException/CertPathValidatorException | فشل ثقة شهادة في هذا المسار، لا فشل رابط |
| الوجهة نفسها مع CA الجلسة العامة في المسبار | TLSv1.3،TLS_AES_128_GCM_SHA256،HTTP200 | نجاح HTTPS موثّق مع تحقق اسم المضيف والشهادة |
| DNS Android لوجهة التحكم | UnknownHostException/GaiException | فشل resolver لا يقتصر على مضيف التطبيق |
| Linux DNS لمضيف التطبيق | getaddrinfo gaierror(-3) | المسار الافتراضي يفشل في المضيف أيضًا |
| Linux HTTPS لوجهة التحكم عبر الوكيل | CONNECT200،HTTP200،ssl_verify_result0 | اتصال الإنترنت عبر المسار المعتمد يعمل |

الفحص الحالي داخل Android أثبت403 من الوكيل مرة واحدة؛ لم يكرر فحص HEAD المرفوض القديم من Linux. لا redirect من backend أو origin401/403 مثبت. إصدارTLS/cipher أعلاه للمسبار إلى وجهة التحكم فقط، وليس قياس اتصال Sales Pro أو تفسيرًا لشارة256-bit في UI.

## محاولة إصلاح آمنة وما أعيد اختباره

1. استُخدم عنوان وكيل الجلسة المعتمد نفسه، دون VPN أو DNS خارجي أو hosts مصطنع أو تجاوز سياسة. الوكيل يطبق قائمة الوجهات كما هي.
2. أضيفت CA العامة الموفرة للجلسة إلى SSLContext المسبار **فقط** مع الاحتفاظ بجذور Android والتحقق من اسم المضيف. لم يوقف تحقق TLS، ولم تُغير شهادات Android أو التطبيق أو APK. نجح اختبار التحكم بعدها200؛ هذا إصلاح لنطاق المسبار لا ادعاء إصلاح ثقة التطبيق.
3. حُفظ http_proxy النظامي مؤقتًا على وكيل الجلسة نفسه. تأكدت قيمة setting؛ لا ادعاء أن Dart استخدمها أو أن كل طبقات Android احترمتها.
4. أُعيد إدخال الحساب المحدد وتحديث القوائم واختبار اختيار المركز الرئيسي و2026 فعليًا. بقي الفرع الافتراضي والسنة الفارغة ورسالة تعذر تحميل القوائم. لم يُستخدم فرع بديل ولم يُحقن معرف، ولم تُرسل مصادقة بإعدادات غير مطابقة.
5. أعيد http_proxy إلى قيمته الأصلية، ولم تُعطل الشبكة. حذفت ملفات المسبار وCA المؤقتة من الجهاز. لا clear-data أو تغيير إنتاج أو معاملة. [إثبات الاستعادة والسجلات](evidence/resume_20261018/connectivity/15_restore_and_app_logs.json).

هذه المحاولة الإضافية أكملت عامل UI في58.29ثانية، مع authenticated=false وlogin_submitted=false. لا جلسة مصادق عليها للخروج منها، ولا أعمال أو مزامنة نُفذت.

## حدود الفحص وتصنيف الأخطاء

- «لا شبكة»: غير مثبت، بل الرابط والعنوان والمسار قائمون.
- «شبكة بلا أي إنترنت»: غير صحيح على إطلاقه؛ HTTPS نجح عبر المسار المعتمد للمسبار.
- «فشل DNS»: مؤكد في resolver الافتراضي داخل Android ولـLinux للمضيف المختبر.
- «فشل TLS/الشهادة»: مؤكد في اختبار التحكم بثقة Android الافتراضية، وعولج في المسبار بCA المشروعة؛TLS تطبيق Sales Pro مع backend غير مختبر.
- «backend متاح ويرجع403»: غير مثبت؛403 الحالي من CONNECT الوكيل، قبل الوصول إلى الأصل.
- لا رد API ولا دليل مصادقة أو فشل كلمة المرور. المضيف مرتبط بتحميل القوائم برصد DNS السابق؛أسماء المسارات في APK لا تكفي لاختلاق URL كامل أو إثبات هوية TEST.

الإعداد المقروء يتضمن قاعدة المضيف لكن هذه المهمة تعمل على source_version آخر بسياسة لا تتضمنه. يلزم تشغيل/ربط المهمة بالنسخة التي تحتوي القاعدة، مع مسار DNS/proxy وثقة صالحين للتطبيق عبر آليات المنصة أو بناء اختبار مصرح به. لا إعادة طلب بيانات الحساب أو إدخال السماح مرة أخرى، ولا تجاوز لسياسة أو حماية شهادات APK.

## المسارات المعتمدة المتاحة وحدّ التنفيذ

مراجعة السياسة والقدرات النهائية، دون طلب جديد للمضيف، أكدت بقاء restricted/enforced وغياب المضيف من القائمة الفعلية. ملف السياسة يحدد vpn_configured=false وtcp_network_access.domains=[] وip_ranges=[]؛لا مسار VPN مهيأ أو منحة TCP يمكن استخدامها للوصول إلى backend. الوكيل الموروث هو مسار HTTP المعتمد، ولا تتيح بنية هذه البيئة اتصال إنترنت عامًا مباشرًا. تغيير route أو تعطيل proxy لا يمنح وصولًا مصرحًا به.

واجهة الإعداد تدعم حفظ قائمة المضيفين في مسودة، لكنها لا تطبقها أو تنشرها أو تعيد تشغيل/ترحّل هذه المهمة. القاعدة موجودة في الإعداد المقروء أصلًا، ولذلك لم تُحفظ قاعدة مكررة ولم يُعدل ملف السياسة. لا توجد أداة متاحة هنا لمنح مسار مباشر أو تطبيق النسخة على المهمة. [سجل المراجعة](evidence/resume_20261018/approved_route_review.json).

تستلزم متابعة backend إجراء منصة خارجيًا: ربط التنفيذ بالنسخة التي تحتوي القاعدة أو إصلاح تطبيقها، ثم توفير مسار DNS/proxy وثقة مدعوم للتطبيق. هذا تحديد لحاجز التنفيذ، وليس طلبًا لإعادة إعداد السماح أو بيانات الحساب. لا طلبات متكررة للمضيف بعد هذه المراجعة، ولا تعطيل تحقق TLS.

كل اختبارات شاشة الدخول المتاحة دون backend موثقة سابقًا؛ لم تُكرر لمجرد زيادة العدّ. الباقي قبل المصادقة: تخطي الترحيب يحتاج حالة جهاز جديدة دون مسح الحالية، وTalkBack غير مهيأ، والبيومتري الحقيقي غير متاح وزر التطبيق يعرض «قريبًا». تظل هذه NOT RUN، وتظل الأعمال المقيدة بالمصادقة BLOCKED.

## مصدر المسبار والأدلة

لا curl أو nslookup داخل صورة Android. بُني مسبار Java مستقل من مصدرنا وشغّل عبر app_process وADB؛ لا تثبيت تطبيق بديل أو تعديل APK. R8/D8 9.5.26 من مستودع Google الرسمي تحقق SHA-256 له من الملف المنشور عبرTLS. source وmetadata والنتائج تمكن مراجعة الفحص، ولا يُعد exit0 للمسبار PASS: **category** يحدد نتيجة الشبكة.

المصدر: [NetworkProbe.java](../../tools/android-network/NetworkProbe.java). الأوامر ونسخ الملفات المؤقتة موضحة في [توثيق المسبار](../../tools/android-network/README.md). لم تُحفظ أجسام HTTP أو headers تفويض/cookies أو حسابات أو رموز أو شهادة CA ضمن Git. مخرجات Wi-Fi حُجبت أسطر الحقول الحساسة.

| المعرّف | الحالة | المتوقع | الفعلي | الدليل |
|---|---|---|---|---|
| NET-01 | PASS | عنوان ومسار افتراضي واتصال شبكة قائم | eth0 UP؛10.0.2.15/24؛default10.0.2.2؛MOBILE CONNECTED؛Wi-Fi غير متصل؛لا VALIDATED | [01_interfaces.txt](evidence/resume_20261018/connectivity/01_interfaces.txt)، [02_routes.txt](evidence/resume_20261018/connectivity/02_routes.txt)، [03_connectivity.txt](evidence/resume_20261018/connectivity/03_connectivity.txt)، [04_wifi.txt](evidence/resume_20261018/connectivity/04_wifi.txt) |
| NET-02 | FAIL | حل الاسم عبر resolver الافتراضي | UnknownHostException مع GaiException؛لا إجابة DNS ناجحة | [06_android_backend_dns.txt](evidence/resume_20261018/connectivity/06_android_backend_dns.txt) |
| NET-03 | BLOCKED | إتمام DNS وTLS ثم قراءة HTTP | توقف عند DNS_OR_TCP بسبب UnknownHostException؛لا TLS أو HTTP أصل | [07_android_backend_default_https.txt](evidence/resume_20261018/connectivity/07_android_backend_default_https.txt) |
| NET-04 | BLOCKED | سماح CONNECT قبل فحص TLS والأصل | proxy CONNECT403؛tls_negotiated=false؛ليست HTTP403 من backend | [08_android_backend_managed_proxy.txt](evidence/resume_20261018/connectivity/08_android_backend_managed_proxy.txt) |
| NET-05 | FAIL | TLS موثوق إلى الوجهة المسموحة | CONNECT200 ثم SSLHandshakeException/CertificateException/CertPathValidatorException | [09_android_control_managed_proxy.txt](evidence/resume_20261018/connectivity/09_android_control_managed_proxy.txt) |
| NET-06 | PASS | TLS مع تحقق اسم المضيف ثم HTTP من الأصل | TLSv1.3؛TLS_AES_128_GCM_SHA256؛origin HTTP200؛لا تعطيل تحقق أو تعديل ثقة النظام | [10_android_control_session_ca.txt](evidence/resume_20261018/connectivity/10_android_control_session_ca.txt) |
| NET-07 | FAIL | حل dl.google.com بالمسار الافتراضي | UnknownHostException/GaiException أيضًا؛فشل المسار لا يقتصر على اسم backend | [11_android_control_dns.txt](evidence/resume_20261018/connectivity/11_android_control_dns.txt) |
| NET-08 | FAIL | نجاح getaddrinfo | gaierror errno=-3؛العامل اكتمل ولم تنجح عملية الحل | [12_host_backend_dns.txt](evidence/resume_20261018/connectivity/12_host_backend_dns.txt) |
| NET-09 | PASS | وصول مسموح مع تحقق TLS | proxy CONNECT200؛origin HTTP200؛ssl_verify_result0 | [13_host_allowed_control_https.txt](evidence/resume_20261018/connectivity/13_host_allowed_control_https.txt) |

تنسيق الأدلة النصية: أزيلت مسافات نهايات الأسطر فقط من مخرجات interfaces/routes/connectivity/wifi قبل Git؛حُفظ المحتوى التشخيصي، مع الحجب المذكور لحقول Wi-Fi الحساسة.
