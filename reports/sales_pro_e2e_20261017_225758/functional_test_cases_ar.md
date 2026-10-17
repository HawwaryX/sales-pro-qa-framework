# حالات الاختبار الوظيفي العربية

التراكمي الوظيفي: PASS: 26؛ FAIL: 4؛ BLOCKED: 55؛ NOT RUN: 2؛ 87 حالة. تشخيص الشبكة مستقل تراكميًا: 4 PASS و4 FAIL بيئية و2 BLOCKED؛ نتائج NET01–09 تتضمن أدلة تاريخية، وNET10 بعد تغير السياسة. اختبارات pytest: 75 لكل نسخة Python منفصلة عن أعمال التطبيق.

## RT-01 — التثبيت

- الحالة: **PASS**

- الشروط: صورة AOSP API35 اكتمل إقلاعها

- الخطوات: انتظار boot_completed ثم تنفيذ pm install على نسخة APK

- المتوقع: Success وظهور الحزمة

- الفعلي: Success؛ pm path أعاد APK المثبت

- الدليل: [install_ready.txt](evidence/install_ready.txt)، [proxy_corrected_guest_state.txt](evidence/proxy_corrected_guest_state.txt)

## RT-02 — الإطلاق والرسم

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: إطلاق MainActivity ثم فحص الشاشة وPID وسجل crash

- المتوقع: تظهر واجهة التطبيق ولا يُرصد انهيار فوري

- الفعلي: ظهرت واجهة الترحيب ثم الدخول؛ لا انهيار Sales Pro مرصود في النافذة

- الدليل: [intro_ar.png](evidence/intro_ar.png)، [final_app_state.txt](evidence/final_app_state.txt)

## RT-03 — الترحيب العربي

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: قراءة صفحة الترحيب الأولى

- المتوقع: نص عربي مقروء وأزرار تنقل

- الفعلي: ظهرت الصفحة العربية وأزرارها

- الدليل: [intro_ar.png](evidence/intro_ar.png)، [intro_ui.xml](evidence/intro_ui.xml)

## RT-04 — لغة الترحيب

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: تبديل اللغة إلى الإنجليزية

- المتوقع: تتغير نصوص الترحيب

- الفعلي: ظهرت شاشة الترحيب الإنجليزية

- الدليل: [intro_language_toggle.png](evidence/intro_language_toggle.png)

## RT-05 — صفحات الترحيب

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على Next للوصول إلى الصفحة 2

- المتوقع: تظهر الصفحة التالية

- الفعلي: Plan and track visits

- الدليل: [intro_en_page_2.png](evidence/intro_en_page_2.png)

## RT-06 — صفحات الترحيب

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على Next للوصول إلى الصفحة 3

- المتوقع: تظهر الصفحة التالية

- الفعلي: Sell and collect with ease

- الدليل: [intro_en_page_3.png](evidence/intro_en_page_3.png)

## RT-07 — صفحات الترحيب

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على Next للوصول إلى الصفحة 4

- المتوقع: تظهر الصفحة التالية

- الفعلي: Ready when you are

- الدليل: [intro_en_page_4.png](evidence/intro_en_page_4.png)

## RT-08 — الرجوع في الترحيب

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على Previous في الصفحة الرابعة

- المتوقع: تعود الصفحة الثالثة

- الفعلي: ظهرت الصفحة الثالثة مجددًا

- الدليل: [intro_previous_to_page3.png](evidence/intro_previous_to_page3.png)

## RT-09 — استعادة العربية في الترحيب

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: العودة للرابعة ثم تبديل اللغة

- المتوقع: تظهر الصفحة الرابعة بالعربية

- الفعلي: ظهرت الصفحة العربية الرابعة

- الدليل: [intro_page4_ar.png](evidence/intro_page4_ar.png)

## RT-10 — بدء الاستخدام

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على بدء الاستخدام

- المتوقع: عرض نموذج الدخول

- الفعلي: ظهر نموذج الحساب والفرع والسنة

- الدليل: [login_initial.png](evidence/login_initial.png)

## RT-11 — منع نموذج فارغ

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: تقديم النموذج فارغًا

- المتوقع: منع التقدم مع توضيح المتطلب الناقص

- الفعلي: ظهرت اختر الفرع والسنة المالية؛ لا يثبت ذلك فحص حقلي الحساب

- الدليل: [login_empty_validation.png](evidence/login_empty_validation.png)

## RT-12 — إخفاء كلمة المرور

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: إدخال قيمة اصطناعية دون تقديم حساب بديل

- المتوقع: يُحجب الحقل

- الفعلي: ظهرت نقاط الإخفاء وpassword=true

- الدليل: [login_synthetic_masked.png](evidence/login_synthetic_masked.png)، [masked_before.xml](evidence/masked_before.xml)

## RT-13 — زر إظهار كلمة المرور

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: تبديل الرؤية ثم إعادتها لقيمة اصطناعية فقط

- المتوقع: تتغير خاصية الإخفاء ثم تعود

- الفعلي: false/true ثم false/false ثم false/true لحقلي النموذج

- الدليل: [password_visibility_result.txt](evidence/password_visibility_result.txt)، [masked_before.xml](evidence/masked_before.xml)، [masked_after.xml](evidence/masked_after.xml)

## RT-14 — زر Back ولوحة المفاتيح

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الكتابة الاصطناعية ثم Back أثناء ظهور لوحة المفاتيح

- المتوقع: إغلاق اللوحة مع بقاء شاشة الدخول

- الفعلي: بقي النموذج ومحتواه الاصطناعي

- الدليل: [login_after_keyboard_back.png](evidence/login_after_keyboard_back.png)

## RT-15 — تذكر الدخول

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: إلغاء تحديد المربع

- المتوقع: تتغير حالة المربع محليًا

- الفعلي: أصبح غير محدد؛ حفظ جلسة بعد المصادقة غير مختبر

- الدليل: [remember_login_unchecked.png](evidence/remember_login_unchecked.png)، [login_lower_controls.xml](evidence/login_lower_controls.xml)

## RT-16 — خطأ انقطاع الشبكة

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: طلب تحديث القوائم أثناء العزل المؤقت

- المتوقع: رسالة خطأ مفهومة دون انهيار

- الفعلي: تعذر تحميل الفروع أو السنوات. تحقق من الاتصال بالخادم.

- الدليل: [lookup_refresh_offline.png](evidence/lookup_refresh_offline.png)، [network_isolation.txt](evidence/network_isolation.txt)

## RT-17 — تحميل القوائم بعد إعادة الشبكة

- الحالة: **BLOCKED**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: تحديث القوائم والحساب المحدد مُعبّأ، مع بقاء شبكة المحاكي والوكيل كما هما

- المتوقع: تحميل الفروع والسنوات من backend الاختبار

- الفعلي: بعد تطبيق السماح في revision3 أُعيد تحديث القوائم مرة واحدة بالحساب المحدد؛ بقي خطأ التحميل. DNS في Android ما زال يفشل بـUnknownHostException؛ نجاح HEAD من Linux لا يثبت اتصال التطبيق.

- الدليل: [online_lookup_unavailable.png](evidence/online_lookup_unavailable.png)، [final_guest_network_rules.txt](evidence/final_guest_network_rules.txt)، [dns_and_proxy_diagnosis_ar.txt](evidence/dns_and_proxy_diagnosis_ar.txt)، [lookup_with_account.xml](evidence/resume_20261018/login_with_branch_year/lookup_with_account.xml)، [observations.json](evidence/resume_20261018/login_with_branch_year/observations.json)، [environment_version_comparison.json](evidence/resume_20261018/environment_version_comparison.json)، [observations.json](evidence/resume_20261018/login_after_network_diagnosis/observations.json)، [lookup_with_account.xml](evidence/resume_20261018/login_after_network_diagnosis/lookup_with_account.xml)، [requested_options.xml](evidence/resume_20261018/login_after_network_diagnosis/requested_options.xml)، [login_result_lower_crop.png](evidence/resume_20261018/login_after_network_diagnosis/login_result_lower_crop.png)، [15_restore_and_app_logs.json](evidence/resume_20261018/connectivity/15_restore_and_app_logs.json)، [observations.json](evidence/followup_20261018/login_once/observations.json)، [requested_options.xml](evidence/followup_20261018/login_once/requested_options.xml)، [login_result_lower_crop.png](evidence/followup_20261018/login_once/login_result_lower_crop.png)، [android_dns_after_policy_update.json](evidence/followup_20261018/android_dns_after_policy_update.json)

## RT-18 — اختيار الفرع الاختباري

- الحالة: **BLOCKED**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: فتح قائمة الفروع ومحاولة اختيار المركز الرئيسي حرفيًا

- المتوقع: ظهور الفرع الاختباري المصرح به من بيانات الخادم

- الفعلي: بعد تغير السياسة لم يظهر المركز الرئيسي؛ ظل الفرع الافتراضي وحده. لا اختيار بديل أو حقن معرّف.

- الدليل: [branch_available_options.png](evidence/branch_available_options.png)، [branch_available_options.xml](evidence/branch_available_options.xml)، [branch_options.xml](evidence/resume_20261018/login_with_branch_year/branch_options.xml)، [requested_options.xml](evidence/resume_20261018/login_with_branch_year/requested_options.xml)، [observations.json](evidence/resume_20261018/login_with_branch_year/observations.json)، [observations.json](evidence/resume_20261018/login_after_network_diagnosis/observations.json)، [lookup_with_account.xml](evidence/resume_20261018/login_after_network_diagnosis/lookup_with_account.xml)، [requested_options.xml](evidence/resume_20261018/login_after_network_diagnosis/requested_options.xml)، [login_result_lower_crop.png](evidence/resume_20261018/login_after_network_diagnosis/login_result_lower_crop.png)، [15_restore_and_app_logs.json](evidence/resume_20261018/connectivity/15_restore_and_app_logs.json)، [observations.json](evidence/followup_20261018/login_once/observations.json)، [requested_options.xml](evidence/followup_20261018/login_once/requested_options.xml)، [login_result_lower_crop.png](evidence/followup_20261018/login_once/login_result_lower_crop.png)، [android_dns_after_policy_update.json](evidence/followup_20261018/android_dns_after_policy_update.json)

## RT-19 — السنة المالية

- الحالة: **BLOCKED**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: محاولة اختيار السنة المالية2026 من القائمة الفعلية

- المتوقع: ظهور السنوات الفعلية من الخادم

- الفعلي: بعد تغير السياسة ظلت 2026 غير متاحة والحقل فارغًا؛ لا قيمة أو معرّف مصطنع.

- الدليل: [year_options_unavailable.png](evidence/year_options_unavailable.png)، [year_options_unavailable.xml](evidence/year_options_unavailable.xml)، [requested_options.xml](evidence/resume_20261018/login_with_branch_year/requested_options.xml)، [login_result_lower_crop.png](evidence/resume_20261018/login_with_branch_year/login_result_lower_crop.png)، [observations.json](evidence/resume_20261018/login_after_network_diagnosis/observations.json)، [lookup_with_account.xml](evidence/resume_20261018/login_after_network_diagnosis/lookup_with_account.xml)، [requested_options.xml](evidence/resume_20261018/login_after_network_diagnosis/requested_options.xml)، [login_result_lower_crop.png](evidence/resume_20261018/login_after_network_diagnosis/login_result_lower_crop.png)، [15_restore_and_app_logs.json](evidence/resume_20261018/connectivity/15_restore_and_app_logs.json)، [observations.json](evidence/followup_20261018/login_once/observations.json)، [requested_options.xml](evidence/followup_20261018/login_once/requested_options.xml)، [login_result_lower_crop.png](evidence/followup_20261018/login_once/login_result_lower_crop.png)، [android_dns_after_policy_update.json](evidence/followup_20261018/android_dns_after_policy_update.json)

## RT-20 — الدخول بالحساب المحدد

- الحالة: **BLOCKED**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: إدخال الحساب حرفيًا ثم محاولة اختيار الفرع المركز الرئيسي والسنة2026؛ التقديم بالقيم المطابقة فقط

- المتوقع: ظهور المنزل المصادق عليه وهوية الحساب

- الفعلي: بعد تغير السياسة تحقق إدخال الحساب المحدد، لكن القيم المطلوبة لم تتح؛ login_submitted=false وauthenticated=false. تقديم النموذج التاريخي توقف محليًا عند شرط الفرع والسنة؛ لا رفض كلمة مرور مثبت.

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)، [exact_login_sanitized.xml](evidence/exact_login_sanitized.xml)، [observations.json](evidence/resume_20261018/login_with_branch_year/observations.json)، [after_form_action.xml](evidence/resume_20261018/login_with_branch_year/after_form_action.xml)، [login_result_lower_crop.png](evidence/resume_20261018/login_with_branch_year/login_result_lower_crop.png)، [observations.json](evidence/resume_20261018/login_after_network_diagnosis/observations.json)، [lookup_with_account.xml](evidence/resume_20261018/login_after_network_diagnosis/lookup_with_account.xml)، [requested_options.xml](evidence/resume_20261018/login_after_network_diagnosis/requested_options.xml)، [login_result_lower_crop.png](evidence/resume_20261018/login_after_network_diagnosis/login_result_lower_crop.png)، [15_restore_and_app_logs.json](evidence/resume_20261018/connectivity/15_restore_and_app_logs.json)، [observations.json](evidence/followup_20261018/login_once/observations.json)، [requested_options.xml](evidence/followup_20261018/login_once/requested_options.xml)، [login_result_lower_crop.png](evidence/followup_20261018/login_once/login_result_lower_crop.png)، [android_dns_after_policy_update.json](evidence/followup_20261018/android_dns_after_policy_update.json)

## RT-21 — استعادة كلمة المرور

- الحالة: **FAIL**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على نسيت كلمة المرور وإعادة المحاولة

- المتوقع: فتح مسار استعادة أو تعليمات عملية

- الفعلي: استعادة كلمة المرور قريبًا؛ لا مسار استعادة متاح

- الدليل: [forgot_password.png](evidence/forgot_password.png)، [forgot_password_repeat.png](evidence/forgot_password_repeat.png)

## RT-22 — الدخول البيومتري

- الحالة: **FAIL**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على زر البصمة في نموذج الدخول

- المتوقع: بدء إعداد/فحص بيومتري أو إرشاد لحساب محفوظ

- الفعلي: الدخول بالبصمة قريبًا؛ لم يُستدع اختبار مستشعر أو تحقق هوية فعلي

- الدليل: [biometric_without_saved_account.png](evidence/biometric_without_saved_account.png)، [biometric_without_saved_account.xml](evidence/biometric_without_saved_account.xml)

## RT-23 — تطابق نسخة التطبيق

- الحالة: **FAIL**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: قراءة تذييل الشاشة ومقارنته ببيانات APK المتحققة

- المتوقع: نسخة UI متسقة مع manifest أو مميزة بوضوح

- الفعلي: UI:2.4.0 Enterprise Build؛ manifest:0.1.0 code1

- الدليل: [login_lower_controls.png](evidence/login_lower_controls.png)، [login_lower_controls.xml](evidence/login_lower_controls.xml)

## RT-24 — توطين رسالة الخطأ

- الحالة: **FAIL**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: إبقاء خطأ القوائم ثم تبديل الدخول للإنجليزية

- المتوقع: تتسق رسالة الحالة مع لغة الواجهة

- الفعلي: Labels إنجليزية لكن خطأ القوائم بقي عربيًا

- الدليل: [login_language_english.png](evidence/login_language_english.png)، [login_language_english.xml](evidence/login_language_english.xml)

## RT-25 — استعادة اللغة العربية

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على Arabic

- المتوقع: تعود الواجهة للعربية

- الفعلي: عادت النصوص للعربية

- الدليل: [login_language_arabic_restored.png](evidence/login_language_arabic_restored.png)

## RT-26 — زر تغيير البيئة

- الحالة: **BLOCKED**

- الشروط: خادم القوائم غير متاح؛ السلوك يحتاج إعادة تحقق بعد إزالة عائق الاتصال

- الخطوات: ضغط تغيير بعد محاولة القوائم والاختيارات المحددة

- المتوقع: تظهر نتيجة قابلة للملاحظة أو اختيار البيئة

- الفعلي: أُعيد الضغط فعلًا؛ لم يُرصد حوار أو عنوان API في UI. السلوك ما زال يحتاج تحققًا بعد إتاحة backend

- الدليل: [environment_change_observed.png](evidence/environment_change_observed.png)، [environment_change_observed.xml](evidence/environment_change_observed.xml)، [environment_tap_repeat.png](evidence/environment_tap_repeat.png)، [environment_control.xml](evidence/resume_20261018/login_with_branch_year/environment_control.xml)، [observations.json](evidence/resume_20261018/login_with_branch_year/observations.json)

## RT-27 — زر الدعم

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: الضغط على تواصل مع الدعم

- المتوقع: استجابة مرئية للزر

- الفعلي: ظهرت رسالة تكرر نص التواصل؛ وسيلة اتصال عملية غير متحققة

- الدليل: [support.png](evidence/support.png)، [support.xml](evidence/support.xml)

## RT-28 — الخلفية والعودة

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: Home ثم إعادة فتح التطبيق

- المتوقع: العودة لنموذج الدخول دون فقدان مرحلة الترحيب

- الفعلي: ظهر النموذج دون إعادة صفحات الترحيب

- الدليل: [background_foreground_return.png](evidence/background_foreground_return.png)، [background_foreground_return.xml](evidence/background_foreground_return.xml)

## RT-29 — تدوير الشاشة

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: تدوير إلى landscape ثم portrait

- المتوقع: استمرار رسم النموذج دون انهيار

- الفعلي: ظهر النموذج في الاتجاهين؛ لم تُختبر كل عناصر التمرير في landscape

- الدليل: [login_landscape.png](evidence/login_landscape.png)، [login_portrait_restored.png](evidence/login_portrait_restored.png)

## RT-30 — Back من جذر الدخول وإعادة الفتح

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: Back دون لوحة مفاتيح ثم إعادة تشغيل Activity وانتظار الحقول

- المتوقع: الخروج الطبيعي ثم إعادة رسم الدخول دون مسح البيانات

- الفعلي: ظهر Launcher ثم عادت حقول الدخول؛ العربية ومرحلة الترحيب محفوظتان

- الدليل: [login_reopened_rendered.png](evidence/login_reopened_rendered.png)، [login_reopened_rendered.xml](evidence/login_reopened_rendered.xml)، [navigation_state_ar.txt](evidence/navigation_state_ar.txt)

## RT-31 — التقاط عنوان أثناء تحديث القوائم

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: رصد أسماء DNS فقط أثناء تحديث الفروع والسنوات

- المتوقع: تحديد المضيف الذي يحاول التطبيق الوصول إليه

- الفعلي: رُصد sales.infinity-tech.sa؛ لم تُرصد استجابة DNS أو HTTP من الخادم

- الدليل: [runtime_dns_observed.jsonl](evidence/runtime_dns_observed.jsonl)، [dns_and_proxy_diagnosis_ar.txt](evidence/dns_and_proxy_diagnosis_ar.txt)

## RT-32 — العودة من العزل

- الحالة: **PASS**

- الشروط: التطبيق مثبت في محاكي الاختبار، دون جلسة مصادق عليها

- الخطوات: فحص قواعد OUTPUT النهائية

- المتوقع: إزالة قواعد REJECT التي أضفناها فقط

- الفعلي: عادت سلاسل Android الأصلية دون قواعد العزل الخاصة بنا؛ وصول backend ما زال محجوبًا

- الدليل: [final_guest_network_rules.txt](evidence/final_guest_network_rules.txt)، [network_isolation_restored.txt](evidence/network_isolation_restored.txt)

## RT-33 — تكبير خط نموذج الدخول العربي

- الحالة: **PASS**

- الشروط: نموذج دخول فعلي بحقلين فارغين؛ محاكي الاختبار نفسه دون مصادقة؛ الشبكة مفعلة

- الخطوات: حفظ font_scale؛ ضبطه على 2.0؛ التمرير لأعلى وأسفل وقراءة العناصر؛ إعادة القيمة الأصلية

- المتوقع: حقول وأزرار أساسية مقروءة ويمكن الوصول إليها، مع استعادة الإعداد

- الفعلي: ضُبط على 2.0 فعليًا؛ رُوجعت اللقطتان وظهرت الحقول والتحديث والدخول والبصمة؛ عاد إلى 1.0. النتيجة لا تعمم على كل إعدادات الوصولية.

- الدليل: [font_top.png](evidence/followup_20261018/ui_additional_ready/font_top.png)، [font_bottom.png](evidence/followup_20261018/ui_additional_ready/font_bottom.png)، [font_top.xml](evidence/followup_20261018/ui_additional_ready/font_top.xml)، [font_bottom.xml](evidence/followup_20261018/ui_additional_ready/font_bottom.xml)، [outer_guard_restore.json](evidence/followup_20261018/ui_additional_ready/outer_guard_restore.json)، [font_visual_review.json](evidence/followup_20261018/font_visual_review.json)

## RT-34 — Tab بين حقلي الحساب وكلمة المرور

- الحالة: **PASS**

- الشروط: نموذج دخول فعلي بحقلين فارغين؛ محاكي الاختبار نفسه دون مصادقة؛ الشبكة مفعلة

- الخطوات: تركيز اسم المستخدم الفارغ؛ إرسال 4 ضغطات Tab دون Enter أو تقديم

- المتوقع: ينتقل التركيز أولًا من اسم المستخدم إلى كلمة المرور دون إرسال

- الفعلي: التركيز [true,false] ثم [false,true]، ثم عناصر غير تحريرية؛ لا Enter أو تقديم. هذا ليس فحص TalkBack أو إثبات دعم كل مفاتيح الواجهة.

- الدليل: [followup_observations.json](evidence/followup_20261018/ui_additional_ready/followup_observations.json)، [focus_order.xml](evidence/followup_20261018/ui_additional_ready/focus_order.xml)

## RT-35 — نص اصطناعي طويل مختلط الاتجاه دون تقديم

- الحالة: **PASS**

- الشروط: نموذج دخول فعلي بحقلين فارغين؛ محاكي الاختبار نفسه دون مصادقة؛ الشبكة مفعلة

- الخطوات: إدخال 1024 حرفًا اصطناعيًا عربيًا/لاتينيًا في كل حقل؛ قراءة التطابق والإخفاء؛ مسح إدخالاتنا فقط

- المتوقع: حفظ النص واستجابة الحقول وإخفاء كلمة المرور وتنظيفها، دون طلب مصادقة

- الفعلي: قُرئ 1024 حرفًا مطابقًا في كل حقل؛ password=true؛ form_submitted=false؛ synthetic_fields_cleared=true. لم تُختبر قواعد الخادم أو تخزين الأسرار، ولا تُعد بيانات مصادقة بديلة.

- الدليل: [followup_observations.json](evidence/followup_20261018/ui_additional_ready/followup_observations.json)، [long_input.xml](evidence/followup_20261018/ui_additional_ready/long_input.xml)، [final_empty_fields.xml](evidence/followup_20261018/ui_additional_ready/final_empty_fields.xml)

## BUS-HOME — المنزل والمؤشرات

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: فتح المنزل والتحقق من هوية الحساب وأرقام الملخص

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: لم ينفذ؛ تعذر اجتياز شرط الفرع والسنة والمصادقة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-NOTIF — الإشعارات

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: فتح القائمة وقراءة إشعار اختباري والتحقق من العدد

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: لم ينفذ؛ تعذر اجتياز شرط الفرع والسنة والمصادقة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-GOALS — الأهداف والأداء

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: فتح أهداف المبيعات ومقارنتها ببيانات اختبار معروفة

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: لم ينفذ؛ تعذر اجتياز شرط الفرع والسنة والمصادقة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-PRODUCT — المنتجات والأسعار

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: البحث عن منتج والتحقق من السعر والمخزون

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: لم ينفذ؛ تعذر اجتياز شرط الفرع والسنة والمصادقة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-MASTER — تحديث البيانات الأساسية

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: طلب تحديث البيانات ومراجعة نتائج التحميل

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: لم ينفذ؛ تعذر اجتياز شرط الفرع والسنة والمصادقة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-STATEMENT — كشف الحساب

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: فتح كشف حساب عميل اختباري ومقارنة الإجمالي بالمرجع

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: لم ينفذ؛ تعذر اجتياز شرط الفرع والسنة والمصادقة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-LANG — لغة القوائم بعد الدخول

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: تبديل لغة القوائم ثم إعادة فتحها

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: لم ينفذ؛ تعذر اجتياز شرط الفرع والسنة والمصادقة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-LOGOUT — الخروج وانتهاء الجلسة

- الحالة: **BLOCKED**

- الشروط: خادم TEST مطابق ومتاح وقوائم فرع/سنة صحيحة وجلسة مصادق عليها

- الخطوات: التحقق من حالة الجلسة قبل تنفيذ تسجيل الخروج المطلوب

- المتوقع: بيانات ونتيجة صحيحة محفوظة في backend الاختبار

- الفعلي: الشاشة الحالية نموذج دخول، وauthenticated=false؛ لم توجد جلسة مصادق عليها مرصودة أو زر خروج يمكن تنفيذه. لم ينفذ logout أو إبطال جلسة backend

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)، [current_session_lower_screen.png](evidence/resume_20261018/current_session_lower_screen.png)، [observations.json](evidence/resume_20261018/login_with_branch_year/observations.json)

## BUS-CUS-CREATE — العملاء — إنشاء

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إنشاء سجل QA فريد ببيانات اصطناعية ثم حفظه

- المتوقع: حفظ سجل واحد والحسابات والحقول صحيحة

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-CUS-VIEW — العملاء — عرض واستمرار

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إغلاق السجل وفتحه والبحث عنه مجددًا

- المتوقع: تطابق القيم المحفوظة ومعرّف السجل دون فقد

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-CUS-EDIT — العملاء — تعديل

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تعديل سجل أنشأه الاختبار فقط ثم إعادة فتحه

- المتوقع: استمرار التعديل وفق صلاحيات ونوع المستند المدعوم

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-CUS-DELETE — العملاء — حذف

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: حذف سجل الاختبار فقط إن كانت العملية مدعومة وآمنة ثم البحث عنه

- المتوقع: يتسق الحذف/الإلغاء مع قواعد النظام دون حذف سجلات أخرى

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-CUS-VALIDATE — العملاء — تحقق مدخلات

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تجربة حقول مطلوبة وقيم غير صالحة على نموذج اختبار

- المتوقع: منع الحفظ غير الصحيح ورسائل محددة دون تغيير بيانات فعلية

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-QUO-CREATE — عروض الأسعار — إنشاء

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إنشاء سجل QA فريد ببيانات اصطناعية ثم حفظه

- المتوقع: حفظ سجل واحد والحسابات والحقول صحيحة

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-QUO-VIEW — عروض الأسعار — عرض واستمرار

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إغلاق السجل وفتحه والبحث عنه مجددًا

- المتوقع: تطابق القيم المحفوظة ومعرّف السجل دون فقد

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-QUO-EDIT — عروض الأسعار — تعديل

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تعديل سجل أنشأه الاختبار فقط ثم إعادة فتحه

- المتوقع: استمرار التعديل وفق صلاحيات ونوع المستند المدعوم

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-QUO-DELETE — عروض الأسعار — حذف

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: حذف سجل الاختبار فقط إن كانت العملية مدعومة وآمنة ثم البحث عنه

- المتوقع: يتسق الحذف/الإلغاء مع قواعد النظام دون حذف سجلات أخرى

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-QUO-VALIDATE — عروض الأسعار — تحقق مدخلات

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تجربة حقول مطلوبة وقيم غير صالحة على نموذج اختبار

- المتوقع: منع الحفظ غير الصحيح ورسائل محددة دون تغيير بيانات فعلية

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-ORD-CREATE — طلبات العملاء — إنشاء

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إنشاء سجل QA فريد ببيانات اصطناعية ثم حفظه

- المتوقع: حفظ سجل واحد والحسابات والحقول صحيحة

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-ORD-VIEW — طلبات العملاء — عرض واستمرار

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إغلاق السجل وفتحه والبحث عنه مجددًا

- المتوقع: تطابق القيم المحفوظة ومعرّف السجل دون فقد

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-ORD-EDIT — طلبات العملاء — تعديل

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تعديل سجل أنشأه الاختبار فقط ثم إعادة فتحه

- المتوقع: استمرار التعديل وفق صلاحيات ونوع المستند المدعوم

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-ORD-DELETE — طلبات العملاء — حذف

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: حذف سجل الاختبار فقط إن كانت العملية مدعومة وآمنة ثم البحث عنه

- المتوقع: يتسق الحذف/الإلغاء مع قواعد النظام دون حذف سجلات أخرى

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-ORD-VALIDATE — طلبات العملاء — تحقق مدخلات

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تجربة حقول مطلوبة وقيم غير صالحة على نموذج اختبار

- المتوقع: منع الحفظ غير الصحيح ورسائل محددة دون تغيير بيانات فعلية

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-INV-CREATE — الفواتير — إنشاء

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إنشاء سجل QA فريد ببيانات اصطناعية ثم حفظه

- المتوقع: حفظ سجل واحد والحسابات والحقول صحيحة

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-INV-VIEW — الفواتير — عرض واستمرار

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إغلاق السجل وفتحه والبحث عنه مجددًا

- المتوقع: تطابق القيم المحفوظة ومعرّف السجل دون فقد

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-INV-EDIT — الفواتير — تعديل

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تعديل سجل أنشأه الاختبار فقط ثم إعادة فتحه

- المتوقع: استمرار التعديل وفق صلاحيات ونوع المستند المدعوم

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-INV-DELETE — الفواتير — حذف

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: حذف سجل الاختبار فقط إن كانت العملية مدعومة وآمنة ثم البحث عنه

- المتوقع: يتسق الحذف/الإلغاء مع قواعد النظام دون حذف سجلات أخرى

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-INV-VALIDATE — الفواتير — تحقق مدخلات

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تجربة حقول مطلوبة وقيم غير صالحة على نموذج اختبار

- المتوقع: منع الحفظ غير الصحيح ورسائل محددة دون تغيير بيانات فعلية

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-REC-CREATE — سندات التحصيل — إنشاء

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إنشاء سجل QA فريد ببيانات اصطناعية ثم حفظه

- المتوقع: حفظ سجل واحد والحسابات والحقول صحيحة

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-REC-VIEW — سندات التحصيل — عرض واستمرار

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إغلاق السجل وفتحه والبحث عنه مجددًا

- المتوقع: تطابق القيم المحفوظة ومعرّف السجل دون فقد

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-REC-EDIT — سندات التحصيل — تعديل

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تعديل سجل أنشأه الاختبار فقط ثم إعادة فتحه

- المتوقع: استمرار التعديل وفق صلاحيات ونوع المستند المدعوم

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-REC-DELETE — سندات التحصيل — حذف

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: حذف سجل الاختبار فقط إن كانت العملية مدعومة وآمنة ثم البحث عنه

- المتوقع: يتسق الحذف/الإلغاء مع قواعد النظام دون حذف سجلات أخرى

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-REC-VALIDATE — سندات التحصيل — تحقق مدخلات

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تجربة حقول مطلوبة وقيم غير صالحة على نموذج اختبار

- المتوقع: منع الحفظ غير الصحيح ورسائل محددة دون تغيير بيانات فعلية

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-RET-CREATE — مرتجعات المبيعات — إنشاء

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إنشاء سجل QA فريد ببيانات اصطناعية ثم حفظه

- المتوقع: حفظ سجل واحد والحسابات والحقول صحيحة

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-RET-VIEW — مرتجعات المبيعات — عرض واستمرار

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: إغلاق السجل وفتحه والبحث عنه مجددًا

- المتوقع: تطابق القيم المحفوظة ومعرّف السجل دون فقد

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-RET-EDIT — مرتجعات المبيعات — تعديل

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تعديل سجل أنشأه الاختبار فقط ثم إعادة فتحه

- المتوقع: استمرار التعديل وفق صلاحيات ونوع المستند المدعوم

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-RET-DELETE — مرتجعات المبيعات — حذف

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: حذف سجل الاختبار فقط إن كانت العملية مدعومة وآمنة ثم البحث عنه

- المتوقع: يتسق الحذف/الإلغاء مع قواعد النظام دون حذف سجلات أخرى

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-RET-VALIDATE — مرتجعات المبيعات — تحقق مدخلات

- الحالة: **BLOCKED**

- الشروط: جلسة TEST موثقة وسجل مميز QA عند الحاجة؛ أي حذف يقتصر على ما أنشأه الاختبار

- الخطوات: تجربة حقول مطلوبة وقيم غير صالحة على نموذج اختبار

- المتوقع: منع الحفظ غير الصحيح ورسائل محددة دون تغيير بيانات فعلية

- الفعلي: لم يفتح النموذج أو ينفذ الطلب؛ المصادقة وTEST غير متحققين

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-VIS-START — بدء زيارة وموقع GPS

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: بدء زيارة عميل QA وطلب الموقع عند الحاجة

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-VIS-CONT — استمرار الزيارة

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: إغلاق وإعادة فتح زيارة QA نشطة

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-VIS-END — إكمال الزيارة

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: إكمال الزيارة والتحقق من السجل

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-VIS-CANCEL — إلغاء الزيارة

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: إلغاء زيارة QA أخرى والتحقق من التاريخ

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-CAM — التقاط الصور

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: فتح كاميرا من وظيفة Sales Pro وحفظ صورة اصطناعية

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-LOC — منح ورفض الموقع

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: تجربة رفض ومنح إذن الموقع من وظيفة الزيارة

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-PRINT — الطباعة والمشاركة

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: معاينة وطباعة/مشاركة مستند اختباري دون عنوان حقيقي

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-OFF-WRITE — حفظ أعمال دون اتصال

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: بعد اختبار online ناجح افصل الشبكة واحفظ سجل QA واحدًا

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-SYNC-RECOVER — استعادة المزامنة

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: أعد الشبكة وتحقق من استمرار سجل offline في الخادم

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-SYNC-DUP — منع تكرار المزامنة

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: كرر محاولة المزامنة للسجل نفسه وتحقق من نسخة واحدة

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## BUS-CALC — حسابات المستندات

- الحالة: **BLOCKED**

- الشروط: جلسة مصادق عليها وTEST مطابق ومتصل؛ تبدأ اختبارات offline بعد online ناجح

- الخطوات: تحقق من خصم وضريبة وكسور وإجمالي مستند اصطناعي

- المتوقع: سلوك صحيح قابل للتحقق من التطبيق والخادم الاختباري

- الفعلي: لم ينفذ؛ لا وصول مصادق عليه لهذه الوظيفة

- الدليل: [exact_login_result.txt](evidence/exact_login_result.txt)

## NR-01 — تخطي الترحيب

- الحالة: **BLOCKED**

- الشروط: مستخدم Android اختباري مؤقت مستقل؛ الحزمة القائمة مسجلة له دون مسح بيانات المستخدم الأصلي

- الخطوات: إنشاء مستخدم مؤقت؛ فتح الترحيب؛ الضغط على خيار التخطي المرصود إن ظهر؛ العودة للمستخدم الأصلي وحذف المؤقت فقط

- المتوقع: تخطي الترحيب إلى نموذج الدخول مع حفظ حالة المستخدم الأصلي وتنظيف المؤقت

- الفعلي: سُجلت الحزمة القائمة في مستخدم مؤقت، لكن خيار التخطي لم يظهر ضمن الانتظار المحدود؛ لم يُضغط أو يُثبت تخطي الترحيب. تعذر تنظيف أول بمهلة ADB، ثم تحقق الرجوع للمستخدم0 وحذف المستخدم10 فقط. لم تُمسح بيانات المستخدم الأصلي أو يُرسل حساب.

- الدليل: [result.json](evidence/followup_20261018/skip_isolated_user/result.json)، [created_user.json](evidence/followup_20261018/skip_isolated_user/created_user.json)، [cleanup_recheck.json](evidence/followup_20261018/skip_isolated_user/cleanup_recheck.json)

## NR-02 — قارئ TalkBack فعلي

- الحالة: **NOT RUN**

- الشروط: ميزة/حالة جهاز مناسبة

- الخطوات: لم ينفذ؛ خطة لاحقة عند توفر شرطها

- المتوقع: التحقق وفق جهاز اختبار مناسب

- الفعلي: لا TalkBack مثبت أو مهيأ؛ accessibilitymenu وحده ليس قارئ TalkBack. لم تُنفذ تجربة قارئ شاشة.

- الدليل: [remaining_runtime_prerequisites.json](evidence/followup_20261018/remaining_runtime_prerequisites.json)

## NR-03 — بيومتري بمستشعر حقيقي

- الحالة: **NOT RUN**

- الشروط: ميزة/حالة جهاز مناسبة

- الخطوات: لم ينفذ؛ خطة لاحقة عند توفر شرطها

- المتوقع: التحقق وفق جهاز اختبار مناسب

- الفعلي: زر التطبيق يعرض قريبًا؛ لم تجر مصادقة بمستشعر فعلي

- الدليل: لا دليل تنفيذ؛ انظر القيد أعلاه
