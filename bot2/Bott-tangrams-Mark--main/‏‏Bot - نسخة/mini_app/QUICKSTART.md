# 🚀 دليل التشغيل السريع - Mini App

## ⚡ البدء السريع (3 خطوات)

### 1️⃣ إنشاء جدول قاعدة البيانات
افتح **Supabase → SQL Editor** ونفذ:
```sql
-- انسخ والصق محتوى ملف SQL_MINI_APP.sql
```

### 2️⃣ تشغيل الاختبار
```bash
cd mini_app
python3 test_miniapp.py
```

### 3️⃣ تشغيل التطبيق
```bash
python3 app.py
```
أو:
```bash
./start.sh
```

---

## 🔍 استكشاف المشاكل

### ❌ المشكلة: "database: disconnected"
**الحل:**
```bash
# تحقق من .env
cat .env

# يجب أن يحتوي على:
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
BOT_TOKEN=123456...
```

### ❌ المشكلة: "جاري التحميل..." لا ينتهي
**السبب المحتمل:**
1. Flask Server غير يعمل
2. جدول `mini_app_profiles` غير موجود
3. مشكلة في الاتصال

**الحل:**
```bash
# 1. تأكد أن Flask يعمل
curl http://localhost:5000/api/health

# 2. نفذ SQL للجداول
# SQL_MINI_APP.sql في Supabase

# 3. افتح console في Telegram
# اضغط Ctrl+Shift+I (Windows) أو Cmd+Option+I (Mac)
```

### ❌ المشكلة: "CORS Error"
**الحل:** CORS مفعّل تلقائياً في app.py

### ❌ المشكلة: "لا توجد بيانات"
**الحل:** تحقق أن الطالب موجود في جدول `all_marks`

---

## 🌐 للوصول من Telegram

### الطريقة 1: ngrok (الأسهل)
```bash
# 1. ثبت ngrok من https://ngrok.com
# 2. شغّله
ngrok http 5000

# 3. انسخ الرابط (مثل: https://abc123.ngrok.io)
# 4. ضعه في .env البوت الرئيسي:
MINI_APP_URL=https://abc123.ngrok.io
```

### الطريقة 2: سيرفر حقيقي
```bash
# رفع على Heroku, Railway, أو أي سيرفر
# ثم تحديث MINI_APP_URL
```

---

## 📱 الاختبار في Telegram

### 1. في البوت الرئيسي:
```
/app
```

### 2. في Telegram Desktop:
- افتح Developer Tools: `Ctrl+Shift+I`
- تبويب **Console** - شاهد الأخطاء
- تبويب **Network** - شاهد API calls

### 3. في المتصفح (للتطوير):
```
http://localhost:5000
```

---

## 🎯 الملفات المهمة

| الملف | الوصف |
|-------|-------|
| `app.py` | Flask Server |
| `static/js/app.js` | JavaScript محسّن ✅ |
| `static/css/style.css` | التصميم |
| `templates/index.html` | HTML |
| `.env` | الإعدادات |
| `SQL_MINI_APP.sql` | قاعدة البيانات |
| `test_miniapp.py` | الاختبار |
| `start.sh` | سكريبت التشغيل |
| `FIX_LOADING_ISSUE.md` | شرح الحل |

---

## ✅ ما تم إصلاحه

- ✅ إضافة Timeout (5-10 ثواني)
- ✅ نظام Cache في localStorage
- ✅ Fallback عند فشل الاتصال
- ✅ رسائل خطأ واضحة
- ✅ Console logging تفصيلي
- ✅ دعم offline mode

---

## 💡 نصائح

### للمطورين:
```javascript
// في console المتصفح:

// عرض البيانات المحفوظة
JSON.parse(localStorage.getItem('cached_results'))

// مسح البيانات
localStorage.clear()

// إعادة التحميل
location.reload()
```

### للمستخدمين:
- التطبيق الآن يعمل حتى بدون اتصال
- البيانات تُحفظ تلقائياً
- إذا ظهر "وضع عدم الاتصال" - البيانات من الذاكرة

---

## 📞 المساعدة

إذا استمرت المشكلة:

```bash
# 1. شغّل الاختبار
python3 test_miniapp.py

# 2. شاهد logs
python3 app.py

# 3. افتح console في Telegram
# 4. التقط screenshot للخطأ
```

---

**الحالة:** ✅ تم الإصلاح  
**التاريخ:** 2026-03-25  
**الملفات المعدلة:** `static/js/app.js`

🎉 **التطبيق الآن يعمل بشكل موثوق حتى مع اتصال ضعيف!**
