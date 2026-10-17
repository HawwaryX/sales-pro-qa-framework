# مسبار اتصال Android المستقل

هذا المصدر ينفذ DNS وCONNECT وTLS وHEAD داخل Android عبر app_process، عندما
تغيب curl وnslookup. لا يعيد توقيع APK أو يثبّت حزمة، ولا يرسل حسابات أو يقرأ
أجسام HTTP. الروابط المقبولة HTTPS دون userinfo أو query أو fragment.

المصدر نُفذ فعليًا على صورة AOSP API35. نتيجة العملية0 تعني اكتمال إخراج
التشخيص؛ **category** هي نتيجة الاتصال، ولا تُترجم تلقائيًا إلى PASS.
لكل socket مهلة8ثوانٍ وللمهمة سقف22ثانية. أوامر ADB استُدعيت بحد30ثانية.

## البناء الذي استُخدم في هذه البيئة

JRE المتاح يحتوي jdk.compiler دون ملف javac مستقل أو ct.sym، لذلك استُخدم
تشغيل وحدة compiler مع source/target8؛ لا ادعاء اختبار Android قديم أو CI Java.
R8/D8 9.5.26 نُزل من Google الرسمي وتحققت بصمته مقابل الملف المنشور عبرTLS:

```text
https://dl.google.com/dl/android/maven2/com/android/tools/r8/9.5.26/r8-9.5.26.jar
https://dl.google.com/dl/android/maven2/com/android/tools/r8/9.5.26/r8-9.5.26.jar.sha256
SHA-256: 3502f087388ce95bbf5254555927f09385dc2636873964d0bd53f3eaf4fb49ad
```

الأوامر الفعلية، مع مجلدات مؤقتة خارج المستودع:

```bash
java -m jdk.compiler/com.sun.tools.javac.Main -source 8 -target 8 \
  -d /workspace/android-runtime/network-classes tools/android-network/NetworkProbe.java
java -cp /workspace/android-runtime/r8-9.5.26.jar com.android.tools.r8.D8 \
  --min-api 24 --output /workspace/android-runtime/network-dex \
  /workspace/android-runtime/network-classes/*.class
```

غُلّف classes.dex في network-probe.jar بواسطة zipfile، ثم نُسخ بـADB إلى
`/data/local/tmp/sales_qa_network_probe.jar`. مثال DNS:

```bash
adb shell env CLASSPATH=/data/local/tmp/sales_qa_network_probe.jar \
  app_process /system/bin NetworkProbe dns sales.infinity-tech.sa
```

فحص HTTPS الافتراضي يستخدم `- 0 -` بعد URL. لفحص وكيل الجلسة، مرر عنوانه
ومنفذه المعتمدين بدل أول وسيطين؛ لا تستخدم عنوانًا بديلًا لتجاوز السياسة.
الوسيط الأخير `-` يعني جذور Android الافتراضية. يمكن تمرير ملف CA العام
الذي وفرته المنصة ليُضاف إلى الثقة في عملية المسبار فقط؛ يبقى تحقق اسم
المضيف HTTPS وSNI مفعّلًا، ولا تُغير ثقة النظام أو التطبيق.

استُخدمت وجهة تحكم مسموحة `https://dl.google.com/android/repository/repository2-3.xml`
لتمييز انعدام الوصول عن حظر مضيف التطبيق. لا يُعد نجاحها نجاح API أو TLS
لتطبيق Sales Pro. لا تعِد الوجهات المحجوبة بلا تغير ذي صلة أو تشخيص جديد.

النتائج العربية والأوامر والمراحل ومقارنة Linux في
`reports/sales_pro_e2e_20261017_225758/android_connectivity_ar.md`.
لم تُحفظ ملفات R8 أو DEX أو JAR أو CA في Git؛ حُذفت الملفات المؤقتة من الجهاز
بعد التشخيص، وأعيد إعداد http_proxy النظامي إلى قيمته الأصلية.
