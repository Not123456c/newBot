# ⚡ تعليمات التثبيت السريعة

## 🎯 الخطوات الـ 3 الأساسية فقط!

### ✅ الخطوة الأولى: إنشاء الجداول (5 دقائق)

1. افتح المرابط هنا: https://app.supabase.com
2. اختر مشروعك (Database)
3. اذهب إلى **SQL Editor** (يسار الشاشة)
4. **انسخ هذا الكود كاملاً:**

```sql
-- جدول تسجيل الطلبات
CREATE TABLE IF NOT EXISTS request_log (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
    request_type TEXT DEFAULT 'search',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_request_log_user ON request_log(user_id);
CREATE INDEX IF NOT EXISTS idx_request_log_time ON request_log(request_time);

-- جدول المستخدمين المحظورين
CREATE TABLE IF NOT EXISTS blocked_users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT UNIQUE NOT NULL,
    reason TEXT DEFAULT 'طلبات متتالية',
    blocked_at TIMESTAMP DEFAULT NOW(),
    unblock_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    unblocked_at TIMESTAMP,
    admin_decision TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_blocked_users_active ON blocked_users(is_active);
CREATE INDEX IF NOT EXISTS idx_blocked_users_user_id ON blocked_users(user_id);

-- جدول حوادث الرسائل المزعجة
CREATE TABLE IF NOT EXISTS spam_incidents (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    request_count INT NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending',
    admin_decision TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_spam_incidents_status ON spam_incidents(status);
CREATE INDEX IF NOT EXISTS idx_spam_incidents_user_id ON spam_incidents(user_id);
```

5. اضغط **"Run"** ✅
6. انتظر رسالة النجاح

---

### ✅ الخطوة الثانية: اختبار الكود (2 دقيقة)

افتح Terminal وشغّل:

```bash
cd "c:\Users\NVT\Downloads\Telegram Desktop\‏‏Bot - نسخة"
python test_spam_protection.py
```

يجب أن ترى:
```
✅ جميع الاختبارات نجحت!
```

إذا حصلت على تحذيرات 🟡 فقط = لا مشكلة ✅

---

### ✅ الخطوة الثالثة: إعادة تشغيل البوت (1 دقيقة)

```bash
python final_bot_with_image.py
```

هذا كل شيء! 🎉

---

## 🧪 اختبار بسيط

1. افتح telegram
2. أرسل رسائل سريعة متتالية للبوت (6+ رسائل في 30 ثانية)
3. يجب أن ترى ⚠️ تحذير من البوت
4. يجب أن يستقبل المسؤول 🚨 إشعار مع أزرار

---

## 🎛️ حيث تجد الأوامر الجديدة

```
أرسل: /admin

اختر:
  ✅ 🚫 إدارة المحظورين
  ✅ 🚨 حوادث مزعجة معلقة
```

---

## ❓ حل المشاكل الشائعة

### المشكلة: "خطأ في الاتصال بـ Supabase"
**الحل:** تحقق من:
- اسم المشروع صحيح ✅
- توكن API صحيح ✅
- الجداول موجودة ✅

---

### المشكلة: "الإشعارات لا تصل"
**الحل:** تأكد أن `ADMIN_IDS` في `.env` صحيح:
```
ADMIN_IDS=123456789,987654321
```

---

### المشكلة: "الأزرار لا تعمل"
**الحل:** 
1. أعد تشغيل البوت
2. جرّب مرة أخرى
3. تحقق من الـ Logs

---

## 📁 الملفات المضافة

| الملف | الحجم | الوصف |
|------|--------|-------|
| spam_protection.py | 4 KB | نظام الحماية الرئيسي |
| SQL_SPAM_PROTECTION.md | 2 KB | أوامر قاعدة البيانات |
| SPAM_PROTECTION_GUIDE.md | 8 KB | دليل شامل |
| test_spam_protection.py | 2.5 KB | اختبارات |
| SPAM_PROTECTION_SUMMARY.md | 6 KB | الملخص |

**الإجمالي:** ~22 KB فقط ✨

---

## 🎯 ما الذي يحدث الآن؟

```
المستخدم يرسل طلب
        ↓
البوت يفحص الطلب
        ↓
هل طلبات كثيرة؟ ❓
        ↙ نعم         ↘ لا
    إشعار للمسؤول    معالجة عادية
        ↓
    [✅ حظر] [❌ تجاهل]
```

---

## 📊 الإحصائيات الجديدة

المسؤول يستطيع الآن رؤية:
- ✅ عدد المستخدمين المحظورين
- ✅ أسباب الحظر
- ✅ الحوادث المعلقة
- ✅ التاريخ والوقت

---

## 🔐 الأمان

✅ كل الحظرات محفوظة في قاعدة البيانات
✅ لا يناً تحذفها عند إعادة تشغيل البوت
✅ انتقال آمن الـ Supabase
✅ لا توجد بيانات حساسة في الملفات

---

## 💡 نصائح مهمة

1. **قابل للتخصيص:**
   ```python
   # في spam_protection.py
   self.MAX_REQUESTS_PER_MINUTE = 5  # غيّره!
   ```

2. **الحظر يرفع آلياً:**
   - بعد 30 دقيقة افتراضياً
   - يمكن فكه يدوياً قبل ذلك

3. **الحوادث محفوظة:**
   - في `spam_incidents` جدول
   - يمكنك عرض التاريخ كاملاً

---

## 🚀 اعتبارات الأداء

- ✅ لا تأثير على سرعة البوت
- ✅ استهلاك ذاكرة منخفض
- ✅ فهارس محسّنة في قاعدة البيانات

---

## 📞 الدعم والمساجعة

اطلع على:
- 📖 `SPAM_PROTECTION_GUIDE.md` - دليل مفصل
- 📋 `SQL_SPAM_PROTECTION.md` - معلومات قاعدة البيانات
- 📊 `SPAM_PROTECTION_SUMMARY.md` - ملخص شامل

---

## ✨ تم بنجاح!

أنت الآن محمي من الطلبات المزعجة! 🎉

**مدة التثبيت الإجمالية:** ~8 دقائق فقط! ⏱️

