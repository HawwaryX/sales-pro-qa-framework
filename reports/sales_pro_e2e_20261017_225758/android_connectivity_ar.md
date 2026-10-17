# إثبات اتصال Android وتشخيصه — 18أكتوبر2026

## الاستنتاج المتحقق

**تغيرت السياسة الفعلية منذ الالتزام `d806c3974482c577d4389781998f49eef7d5eb95`**: المراجعة الحالية3 تتضمن `sales.infinity-tech.sa` مع observations_current=true وrestricted/enforced. لم يُعدل إعداد أو يُكرر حفظ السماح في هذه المتابعة. لا ينطبق استنتاج غياب السماح أو ضرورة ترحيل المهمة من الدفعة السابقة على الحالة الحالية.

أُعيد اختبار المضيف مرة واحدة بعد هذا التغير عبر الوكيل الموروث: CONNECT200 ثم TLS موثّق وHTTP404 من الأصل لطلب HEAD على `/`، دون إعادة توجيه. **حاجز CONNECT403 السابق زال في مسار Linux المعتمد**. لا تثبت404 من الجذر عيب API أو صحة مسار API أو هوية قاعدة TEST.

بقي DNS الافتراضي فاشلًا في Linux وAndroid. نجاح المسار المعتمد في المضيف لا يثبت أن تطبيق Android يستخدمه أو يثق بسلسلته. فشل ثقة Android الافتراضية السابق كان في اختبار تحكم، ولم يُعدل مخزن ثقة النظام أو التطبيق أو يُعطل تحقق TLS.

| التحقق بعد تغير السياسة | النتيجة | الدليل |
|---|---|---|
| السياسة الفعلية | المراجعة3؛ المضيف مسموح؛ لا تعديل إعداد في المتابعة | [effective_policy.json](evidence/followup_20261018/effective_policy.json) |
| HEAD واحد عبر وكيل الجلسة | CONNECT200؛origin HTTP404؛ssl_verify_result0؛curl exit0؛لا redirect | [backend_targeted_retest.json](evidence/followup_20261018/backend_targeted_retest.json) |
| DNS Linux للمضيف | DNS_FAILURE؛errno=-3 | [host_dns_after_policy_update.json](evidence/followup_20261018/host_dns_after_policy_update.json) |
| DNS Android للمضيف | UnknownHostException/GaiException | [android_dns_after_policy_update.json](evidence/followup_20261018/android_dns_after_policy_update.json) |

## النتائج السابقة المحفوظة في الالتزام d806c39

الجدول التالي سجل تاريخي قبل تغير السياسة، وليس وصفًا لرفض الوكيل الحالي. يثبت أيضًا أن Android متصل بشبكة وأن HTTPS لوجهة تحكم نجح عبر الوكيل وثقة الجلسة في المسبار.

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

الفحص السابق داخل Android أثبت403 من الوكيل مرة واحدة. أعيد HEAD من Linux فقط بعد تغير السياسة، فنجح CONNECT كما هو موثق أعلاه. لا origin401/403 مثبت. إصدارTLS/cipher في الجدول للمسبار إلى وجهة التحكم فقط، وليس قياس اتصال Sales Pro أو تفسيرًا لشارة256-bit في UI.

## محاولة الإصلاح السابقة الآمنة وحدودها

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
- «backend يرجع403»: غير مثبت؛403 التاريخي من CONNECT الوكيل قبل الأصل. الفحص الأحدث وصل إلى الأصل وأعاد404 لطلب HEAD على الجذر فقط.
- لا رد API أو دليل مصادقة أو فشل كلمة المرور. المضيف مرتبط بتحميل القوائم برصد DNS السابق؛أسماء المسارات في APK و404 الجذر لا تكفي لإثبات URL API كامل أو هوية TEST.

كان اختلاف الإعداد/السياسة مثبتًا في الدفعة السابقة، لكن السياسة الفعلية الآن تتضمن القاعدة. المتطلب المتبقي هو مسار DNS/proxy وثقة صالح لتطبيق Android عبر آليات المنصة، أو جهاز اختبار مصرح بشبكة backend عاملة. لا حاجة لإعادة السماح أو بيانات الحساب، ولا لتجاوز سياسة أو حماية شهادات APK.

## المسارات المعتمدة المتاحة وحدّ التنفيذ

السياسة الحالية restricted/enforced وتسمح بالمضيف. لا VPN مهيأ أو منحة TCP معتمدة تتيح مسارًا مباشرًا بديلًا؛ سجل مراجعة المسارات السابق يحدد vpn_configured=false وtcp_network_access.domains=[] وip_ranges=[]. الوكيل الموروث هو مسار HTTP المعتمد، وقد نجح عبره فحص المضيف الجديد. تغيير route أو تعطيل proxy لا يمنح وصولًا مصرحًا به.

لا أداة متاحة هنا لتوفير مسار Android DNS/proxy/trust مدعوم أو منح اتصال مباشر. لم يُعدل ملف السياسة أو يُحفظ السماح مجددًا؛ تغير المراجعة رُصد من البيئة. [سجل المسارات السابق](evidence/resume_20261018/approved_route_review.json) و[السياسة الحالية](evidence/followup_20261018/effective_policy.json).

المسار الأرجح والمدعوم هو تمكين Android من استخدام وكيل الجلسة مع DNS والثقة الصحيحة دون تعديل APK أو تعطيل التحقق، أو استخدام جهاز اختبار مصرح متصل بالخادم. لا تتيح الأدوات الحالية إتمام هذه التهيئة للتطبيق. لا فائدة من إعادة HEAD الناجح أو إعادة حفظ القاعدة؛ لا طلبات متكررة إلى مسار لم يتغير.

تُستكمل فقط فجوات UI الآمنة غير المنفذة دون backend؛ نتائجها الفعلية في [الدفتر](test_ledger.json). جُرّبت حالة جديدة للتخطي بمستخدم مؤقت؛ بقي الاختبار BLOCKED ولم يظهر الخيار ضمن المهلة، ثم نُظف المستخدم المؤقت. TalkBack غير مهيأ، والبيومتري الحقيقي غير متاح وزر التطبيق يعرض «قريبًا». لا تتحول اختبارات الواجهة المحلية إلى إثبات دخول أو تنفيذ أعمال.

## مصدر المسبار والأدلة

لا curl أو nslookup داخل صورة Android. بُني مسبار Java مستقل من مصدرنا وشغّل عبر app_process وADB؛ لا تثبيت تطبيق بديل أو تعديل APK. R8/D8 9.5.26 من مستودع Google الرسمي تحقق SHA-256 له من الملف المنشور عبرTLS. source وmetadata والنتائج تمكن مراجعة الفحص، ولا يُعد exit0 للمسبار PASS: **category** يحدد نتيجة الشبكة.

المصدر: [NetworkProbe.java](../../tools/android-network/NetworkProbe.java). الأوامر ونسخ الملفات المؤقتة موضحة في [توثيق المسبار](../../tools/android-network/README.md). لم تُحفظ أجسام HTTP أو headers تفويض/cookies أو حسابات أو رموز أو شهادة CA ضمن Git. مخرجات Wi-Fi حُجبت أسطر الحقول الحساسة.

الحالات NET-01 إلىNET-09 أدناه توثق نافذة الدفعة السابقة؛ لا تعني أن CONNECT403 ما زال قائمًا بعد تغير السياسة. إعادة الاختبار الأحدث موضحة في بداية التقرير والدفتر.

| المعرّف | الحالة التاريخية | المتوقع | الفعلي | الدليل |
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

## متابعة التنفيذ بعد تطبيق المراجعة 3

المراجعة 3 تسمح بالمضيف؛ CONNECT200 وTLS موثق ثم HTTP404 للجذر من Linux. DNS في Android ما زال يفشل بـUnknownHostException؛ القوائم لم تُحمّل ولا دخول مصادق. نجحت RT-33–35 (تكبير الخط وTab ونص 1024 حرفًا دون تقديم)، وحالة تخطي الترحيب BLOCKED في مستخدم مؤقت حُذف بعد العودة للأصلي. الدفتر: PASS: 26؛ FAIL: 4؛ BLOCKED: 55؛ NOT RUN: 2؛ 87 حالة. لا معاملات أو مزامنة أعمال. لا إعادة للطلب المحجوب أو الفحص الثابت.

[محاولة القوائم](evidence/followup_20261018/login_once/observations.json)؛[فحوص UI](evidence/followup_20261018/ui_additional_ready/followup_observations.json)؛[اختبار التخطي](evidence/followup_20261018/skip_isolated_user/result.json).

الدفتر الشبكي التراكمي: **4 PASS و4 FAIL بيئية و2 BLOCKED** في10 حالات؛ NET-10 يثبت وصول Linux بعد تغير السياسة. تبقى NET-04 ونتائج التحكم السابقة موصوفة بتاريخها، ولا تعني استمرار403 حاليًا. [الدفتر](test_ledger.json).

## المراجعة الذاتية اللاحقة دون تكرار الطلبات

بقيت السياسة enforced في المراجعة3 والمضيف مسموحًا. تغير عنوان resolver المحلي المرصود إلى172.31.1.173؛ أُجري فحص getaddrinfo واحد في عامل بمهلة8ثوانٍ، فعاد DNS_FAILURE errno=-3. اكتمال العامل ليس نجاح DNS. لم يُكرر HEAD أو تسجيل الدخول. [القياس المحدود](evidence/autonomous_20261018/dns_resolver_change_check.json).

راجعت خيارات المحاكي المثبت: dns-server يستلزم خادم DNS قابلًا للوصول ومعتمدًا؛ لا يوفره بنفسه. http-proxy يوجه TCP وهو مستخدم بالفعل. لا DNS بديل عامل مهيأ ولا VPN أو منح TCP، وأداة الإعداد تحفظ مسودة دون توفير هذا المسار للتطبيق. لم تُغير DNS أو سياسة أو ثقة TLS تجريبيًا. المتطلب الخارجي المحدد: مسار Android DNS/HTTPS مدعوم من المنصة، أو جهاز اختبار مصرح بشبكة عاملة. [مراجعة القدرات](evidence/autonomous_20261018/supported_remediation_review.json) و[السياسة](evidence/autonomous_20261018/policy_capabilities.json).
