# التحليل الثابت التفصيلي

## سلامة الملف والبيانات

PASS: الملف موجود ومحتوى Git LFS فعلي. SHA-256 `ae8c3cece95a8f00516045974e96749ef1fb005bfd6e86b9a0b4a1c03c667d11`، الحجم 68663473، وCRC لجميع 292 عناصر ناجح. لا يُعد هذا وحده ضمان قابلية التثبيت. تفاصيل الحزمة والتوقيع في framework_inspection_ar.md.

## manifest والمكونات

الدليل المفكوك الفعلي: evidence/manifest_aapt.txt؛ أرقام الأسطر تشير إلى manifest المدمج داخل APK، لا إلى مشروع مصدر Android غير متاح.

| النوع | المكون | exported | الحماية/الحالة | سطر manifest |
|---|---|---|---|---|
| activity | `com.infinity.sales.app.MainActivity` | true | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 94 |
| provider | `io.flutter.plugins.imagepicker.ImagePickerFileProvider` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 128 |
| service | `com.google.android.gms.metadata.ModuleDependencies` | false | `لا يوجد إذن مكون صريح`؛ enabled=false | 137 |
| service | `com.baseflow.geolocator.GeolocatorLocationService` | false | `لا يوجد إذن مكون صريح`؛ enabled=true | 149 |
| provider | `com.crazecoder.openfile.FileProvider` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 155 |
| provider | `net.nfet.flutter.printing.PrintFileProvider` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 164 |
| provider | `dev.fluttercommunity.plus.share.ShareFileProvider` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 177 |
| receiver | `dev.fluttercommunity.plus.share.SharePlusPendingIntent` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 190 |
| activity | `io.flutter.plugins.urllauncher.WebViewActivity` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 198 |
| activity | `com.google.android.gms.common.api.GoogleApiActivity` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 202 |
| provider | `androidx.startup.InitializationProvider` | false | `لا يوجد إذن مكون صريح`؛ enabled=الافتراضي true | 211 |
| receiver | `androidx.profileinstaller.ProfileInstallReceiver` | true | `android.permission.DUMP`؛ enabled=true | 233 |


- المصدّر فعليًا: MainActivity لواجهة LAUNCHER؛ وProfileInstallReceiver محمي بـandroid.permission.DUMP، وليس استقبالًا عامًا غير محمي.
- لا توجد intent filters من نوع VIEW/BROWSABLE داخل مكونات التطبيق، ولا app links أو custom schemes مسجلة كواجهات دخول. وجود http/https في queries يصف رؤية تطبيقات أخرى ولا يسجل deep link.
- لا android:debuggable صريح؛ الافتراضي false. شهادة Debug لا تساوي debuggable=true.
- لا سياسة نسخ احتياطي صريحة؛ الافتراضي allowBackup=true مع اختلاف آليات النقل عبر Android/OEM. الأثر الحقيقي يحتاج فحص تخزين واستعادة.
- MainActivity: taskAffinity فارغ وlaunchMode=singleTop؛ لا launchMode=singleTask مثبت. لا استغلال task hijacking مثبت.
- لا boot receiver للتطبيق أو إذن تثبيت حزم أو قراءة رسائل أو وصول Accessibility Service معلن.

## الصلاحيات ومستويات الحماية

المستويات القياسية توضيح لمعاني Android وليست قياسًا لمنح فعلي على جهاز. الصلاحية الخاصة عُرّفت بمستوى 0x2 أي signature.

- `android.permission.ACCESS_COARSE_LOCATION` — dangerous وفق تعريفات Android القياسية.
- `android.permission.ACCESS_FINE_LOCATION` — dangerous وفق تعريفات Android القياسية.
- `android.permission.ACCESS_NETWORK_STATE` — normal.
- `android.permission.CAMERA` — dangerous وفق تعريفات Android القياسية.
- `android.permission.INTERNET` — normal.
- `android.permission.READ_EXTERNAL_STORAGE` — dangerous وفق تعريفات Android القياسية.
- `android.permission.READ_MEDIA_AUDIO` — dangerous وفق تعريفات Android القياسية.
- `android.permission.READ_MEDIA_IMAGES` — dangerous وفق تعريفات Android القياسية.
- `android.permission.READ_MEDIA_VIDEO` — dangerous وفق تعريفات Android القياسية.
- `com.infinity.sales.app.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION` — signature؛ مؤكد من تعريف manifest.

READ_EXTERNAL_STORAGE مقيد بـmaxSdkVersion=32. الاستخدام ومنح/رفض الإذن وضرورة الصوت والفيديو تحتاج اختبارات وظائف فعلية.

## إعداد الشبكة ومشاركة الملفات

- التطبيق usesCleartextTraffic=false، وbase-config يمنع cleartext. res/8G.xml يسمح به فقط لـlocalhost وتوابعه و127.0.0.1 و10.0.2.2. لا trust-anchors خاصة أو debug-overrides أو pin-set في هذا الملف؛ غياب pinning ليس بحد ذاته ثغرة.
- res/oS.xml يتضمن root-path وexternal-path وfiles-path وcache-path مع path= `.` كما في evidence/openfile_paths.txt؛ المزود غير مصدّر ويعتمد منح URI.
- ImagePicker يشارك cache كاملًا؛ printing يحدد /share/؛ share_plus يحدد share_plus/. لم يُختبر منح URI أو قراءة ملف فعليًا.

## DEX وJava وFlutter

- classes.dex واحد، 1,061,252 بايت. JADX 1.5.3 أنتج 1082 ملف Java مع أخطاء جزئية موثقة؛ توجد أسماء defpackage تدل على تقليل/تعمية أسماء Java، وليس دليلًا على برمجية خبيثة.
- MainActivity.java:8 يرث غلاف Flutter ولا يحتوي منطق أعمال ظاهرًا. منطق التطبيق Dart AOT في libapp.so؛ لم يُستعد بالكامل إلى مصدر Dart.
- WebViewActivity.java:34–52 يأخذ URL وإعداد JavaScript/DOM من Intent داخلي، والقيمة الافتراضية false، والمكون غير مصدّر. وجود setJavaScriptEnabled لا يثبت XSS أو استقبال URL من تطبيق آخر.
- defpackage/va.java:284 يستخدم PendingIntent لبث إلى SharePlusPendingIntent صريح وغير مصدّر. القيمة 33554432 تشير إلى FLAG_MUTABLE في أحد مسارات المكتبة؛ لا يوجد مسار استغلال مثبت من ذلك وحده.
- أجزاء secure storage في defpackage/gi.java:125–139 وat.java تستخدم AndroidKeyStore وAES/GCM/NoPadding. RSA/ECB/OAEPPadding اسم Java لا يعني تشفير كتلي ECB غير آمن لبيانات التطبيق. لا تثبت المكتبة أن جميع الرموز تستخدمها.
- أظهرت سلاسل Dart وجود dio وhttp وsqflite وflutter_secure_storage وواجهات العملاء والفواتير والعروض والحسابات؛ هذه أدلة وظائف مرشحة، وليست شاشات جرى تشغيلها أو إثبات تخزين حساس بنص واضح.
- بحث Java لم يثبت callback ثقة عامة أو تعطيل hostname verification. غياب النمط في Java لا يغطي Dart AOT أو جميع الشيفرة الأصلية.

## الشبكة والأسرار والمؤشرات

- يظهر أصل HTTPS مضمّن `sales.infinity-tech.sa` في lib/arm64-v8a/libapp.so عند إزاحة بايت 850080 (وفي x86_64 عند 850237، وarmeabi-v7a عند 3944892). رُصد لاحقًا DNS لهذا المضيف أثناء تحديث القوائم. فحص HEAD توقف عند الوكيل CONNECT403 قبل origin؛ لا HTTP API أو هوية TEST مثبتة.
- سلاسل مسارات API تشمل auth/login وcustomers وinvoices وquotations؛ لا توجد استجابات API فعلية أو حالة مصادقة مثبتة.
- توجد نطاقات توثيق Flutter/GitHub وfonts.gstatic.com. وجودها لا يثبت سمعة أمنية؛ رُصدت لاحقًا محاولات GoogleFonts فاشلة في DNS دون رفع بيانات إلى خدمات تحليل.
- فُحصت جميع عناصر الأرشيف بنماذج private-key وGoogle API key وAWS access key وJWT وcredential assignment؛ لم تطابق هذه النماذج قيمة محتملة. لا يعني ذلك خلو APK من الأسرار أو القيم المشفرة/المجزأة.
- لم يُنفذ محرك مكافحة برمجيات خبيثة بتعريفات حديثة؛ النتيجة تحليل مؤشرات فقط. لا حكم سلامة أو خبث.

## المكتبات الأصلية

توجد 9 ملفات ELF لثلاث معماريات، لكل منها libapp/libflutter/libdartjni. GNU_STACK غير تنفيذي ولا LOAD من نوع W+X أو TEXTREL مثبت في الفحص؛ غياب RELRO في libapp لا يُصنّف وحده ثغرة بسبب بنية Dart AOT الخاصة.

| الملف | W+X | RELRO | BIND_NOW | TEXTREL |
|---|---|---|---|---|
| `lib/arm64-v8a/libapp.so` | False | False | False | False |
| `lib/arm64-v8a/libdartjni.so` | False | True | True | False |
| `lib/arm64-v8a/libflutter.so` | False | True | True | False |
| `lib/armeabi-v7a/libapp.so` | False | False | False | False |
| `lib/armeabi-v7a/libdartjni.so` | False | True | True | False |
| `lib/armeabi-v7a/libflutter.so` | False | True | True | False |
| `lib/x86_64/libapp.so` | False | False | False | False |
| `lib/x86_64/libdartjni.so` | False | True | True | False |
| `lib/x86_64/libflutter.so` | False | True | True | False |


## جرد نسخ التبعيات

القيم من metadata المضمّنة وليست SBOM موثّقة بالسلسلة الكاملة. نسخة Flutter ومكتبات Dart الدقيقة غير مثبتة. طلب OSV آمن بمعلومة Maven عامة اصطدم بـproxy CONNECT 403؛ لا مطابقة CVE مكتملة لمكتبات APK، ولا استنتاج أن النسخة القديمة قابلة للاستغلال.

| موضع بيانات النسخة | القيمة المعلنة |
|---|---|
| `META-INF/androidx.activity_activity.version` | `1.13.0` |
| `META-INF/androidx.annotation_annotation-experimental.version` | `1.4.1` |
| `META-INF/androidx.appcompat_appcompat-resources.version` | `1.6.1` |
| `META-INF/androidx.appcompat_appcompat.version` | `1.6.1` |
| `META-INF/androidx.arch.core_core-runtime.version` | `task ':arch:core:core-runtime:writeVersionFile' property 'version'` |
| `META-INF/androidx.browser_browser.version` | `1.9.0` |
| `META-INF/androidx.compose.runtime_runtime-annotation.version` | `1.9.0` |
| `META-INF/androidx.core_core-ktx.version` | `1.18.0` |
| `META-INF/androidx.core_core-viewtree.version` | `1.0.0` |
| `META-INF/androidx.core_core.version` | `1.18.0` |
| `META-INF/androidx.cursoradapter_cursoradapter.version` | `1.0.0` |
| `META-INF/androidx.customview_customview.version` | `1.0.0` |
| `META-INF/androidx.drawerlayout_drawerlayout.version` | `1.0.0` |
| `META-INF/androidx.emoji2_emoji2-views-helper.version` | `1.2.0` |
| `META-INF/androidx.emoji2_emoji2.version` | `1.2.0` |
| `META-INF/androidx.exifinterface_exifinterface.version` | `1.4.2` |
| `META-INF/androidx.fragment_fragment.version` | `1.7.1` |
| `META-INF/androidx.interpolator_interpolator.version` | `1.0.0` |
| `META-INF/androidx.lifecycle_lifecycle-livedata-core-ktx.version` | `2.10.0` |
| `META-INF/androidx.lifecycle_lifecycle-livedata-core.version` | `2.10.0` |
| `META-INF/androidx.lifecycle_lifecycle-livedata.version` | `2.10.0` |
| `META-INF/androidx.lifecycle_lifecycle-process.version` | `2.10.0` |
| `META-INF/androidx.lifecycle_lifecycle-runtime.version` | `2.10.0` |
| `META-INF/androidx.lifecycle_lifecycle-viewmodel-savedstate.version` | `2.10.0` |
| `META-INF/androidx.lifecycle_lifecycle-viewmodel.version` | `2.10.0` |
| `META-INF/androidx.loader_loader.version` | `1.0.0` |
| `META-INF/androidx.navigationevent_navigationevent.version` | `1.0.0` |
| `META-INF/androidx.profileinstaller_profileinstaller.version` | `1.4.0` |
| `META-INF/androidx.savedstate_savedstate.version` | `1.4.0` |
| `META-INF/androidx.startup_startup-runtime.version` | `1.1.1` |
| `META-INF/androidx.tracing_tracing.version` | `1.2.0` |
| `META-INF/androidx.vectordrawable_vectordrawable-animated.version` | `1.1.0` |
| `META-INF/androidx.vectordrawable_vectordrawable.version` | `1.1.0` |
| `META-INF/androidx.versionedparcelable_versionedparcelable.version` | `1.1.1` |
| `META-INF/androidx.viewpager_viewpager.version` | `1.0.0` |
| `META-INF/androidx.window.extensions.core_core.version` | `1.0.0` |
| `META-INF/androidx.window_window-java.version` | `1.2.0` |
| `META-INF/androidx.window_window.version` | `1.2.0` |
| `META-INF/kotlinx_coroutines_android.version` | `1.11.0` |
| `META-INF/kotlinx_coroutines_core.version` | `1.11.0` |
| `play-services-base.properties` | `version=18.3.0` |
| `play-services-basement.properties` | `version=18.3.0` |
| `play-services-location.properties` | `version=21.2.0` |
| `play-services-tasks.properties` | `version=18.1.0` |
