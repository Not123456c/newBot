# دليل التحقق من الإصلاحات

## ✅ كيفية التحقق من أن الإصلاحات تعمل

### 1. الفحص الأولي (Initial Check)

عند بدء تشغيل البوت، يجب أن ترى:

```
Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.
Google Gemini API متصل: gemini-flash-lite-latest
جاري تفعيل نظام الإشعارات التلقائية...
⏱️ تم تشغيل نظام الإشعارات التلقائية (كل 60 دقيقة).
البوت المطور يعمل الآن!
```

✅ **النتيجة الإيجابية**: لا توجد أخطاء startup

---

### 2. اختبار مستخدم جديد (New User Test)

**الخطوات**:
1. ابدأ محادثة جديدة مع البوت من من حساب لم تستخدمه مع البوت من قبل
2. أرسل `/start`
3. راقب السجلات في الـ terminal

**يجب أن تراه في السجلات**:
```
✅ تم تسجيل المستخدم XXXXXXX في bot_users
ℹ️ تسجيل مستخدم جديد: XXXXXXX
✅ نجح الفحص مع: @channel_name
```

❌ **إذا رأيت**:
```
Key (chat_id)=(...) is not present in table "bot_users"
```
→ هذا يعني الإصلاح لم يُطبق بشكل صحيح

---

### 3. اختبار الاشتراك (Subscription Test)

إذا كان `REQUIRE_CHANNEL_SUBSCRIPTION=true`:

**السيناريو أ**: المستخدم مشترك في القناة
```
✅ نجح الفحص مع: @Resultsbot12
✅ {chat_id} مشترك حسب قاعدة البيانات
```
→ المستخدم يستطيع الوصول للبوت ✅

**السيناريو ب**: المستخدم غير مشترك
```
⚠️ {chat_id} status: left (not subscribed)
❌ عذراً، يجب الاشتراك في قناة البوت أولاً
```
→ يظهر رسالة طلب الاشتراك ✅

---

### 4. اختبار الاستقرار (Stability Test)

**الخطوات**:
1. اترك البوت يعمل لمدة 15 دقيقة
2. أرسل 10-15 رسائل متتالية

**الملاحظة المتوقعة**:
- كل الرسائل تُمعالجة بنجاح
- لا يوجد "polling exited" error
- بدون انهيارات (crashes)

❌ **إذا رأيت**:
```
ERROR - TeleBot: "Infinity polling: polling exited"
```
→ معالجة الأخطاء في polling لم تعمل

---

## 🔍 استكشاف الأخطاء (Troubleshooting)

### المشكلة: Foreign Key Error اليزال يظهر

```
violates foreign key constraint "channel_subscriptions_chat_id_fkey"
```

**خطوات الحل**:

```python
# 1. تحقق من قاعدة البيانات
import subprocess
subprocess.run([
    "psql", 
    "-h", "your_host",
    "-U", "your_user", 
    "-d", "your_db",
    "-c", "SELECT chat_id FROM bot_users WHERE chat_id = XXXXXXX;"
])

# 2. إذا لم تجد السجل، سجله يدوياً
# أو شغّل البوت وأرسل /start من جديد
```

### المشكلة: "Infinity polling: polling exited" لازال يظهر

**التشخيص**:
```
# 1. ابحث عن رسالة الخطأ الفعلية قبل polling error
grep "ERROR\|Traceback" bot_output.log

# 2. أضف debugging في handle_all
@bot.message_handler(func=lambda m: True)
def handle_all(msg):
    try:
        save_user(msg.chat.id)
        # ... rest of code
    except Exception as e:
        print(f"DEBUG: handle_all exception: {e}")
        traceback.print_exc()
        raise  # أعد رفع الخطأ ليتم اكتشافه في polling loop
```

### المشكلة: "Bad Request: chat not found"

**تشخيص القناة**:
```python
# اختبر الوصول للقناة
channel_attempts = [
    "@your_channel",
    "your_channel",
    "-1003555110266",  # معرف رقمي إن كان جروب
]

for channel in channel_attempts:
    try:
        info = bot.get_chat(channel)
        print(f"✅ نجح: {channel}")
        print(f"   Type: {info.type}")
        print(f"   ID: {info.id}")
        break
    except Exception as e:
        print(f"❌ فشل {channel}: {e}")
```

**الحل**:
1. استخدم المعرف الرقمي بدل الاسم
2. تأكد من أن البوت لديه permission `get_chat`
3. تحقق من أن القناة عامة (public) إن كنت تريد فحصها

---

## 📊 مؤشرات الصحة (Health Indicators)

| المؤشر | ❌ سيء | ⚠️ تحذير | ✅ جيد |
|--------|--------|---------|--------|
| Polling crashes | > 1 per hour | 1 per day | 0 per day |
| Foreign key errors | > 0 | بعض في البداية | 0 بعد دقيقة |
| Channel check success | < 50% | 50-90% | > 90% |
| User registration time | > 5s | 2-5s | < 2s |
| Subscription check latency | > 3s | 1-3s | < 1s |

---

## 🔧 أوامر مفيدة للتشخيص

### عرض آخر أخطاء في قاعدة البيانات
```bash
# من داخل Supabase studio:
SELECT * FROM bot_users LIMIT 10;
SELECT * FROM channel_subscriptions LIMIT 10;
```

### مراقبة السجلات مباشرة
```bash
# Linux/Mac
tail -f bot_output.log | grep -E "ERROR|✅|❌|⚠️"

# Windows PowerShell
Get-Content bot_output.log -Tail 20 -Wait
```

### اختبار foreign key constraint
```python
import subprocess
result = subprocess.run([
    "python", "-c", """
from supabase import create_client
# ... initialize supabase ...
# حاول عملية تنتهك القيد
supabase.table('channel_subscriptions').insert({
    'chat_id': 999999,  # لا يعني في bot_users
    'is_subscribed': False
}).execute()
"""
])
```

---

## 📋 Pre-Flight Checklist

قبل تشغيل البوت في الـ production:

- [ ] `.env` يحتوي على `CHANNEL_USERNAME` الصحيح
- [ ] `REQUIRE_CHANNEL_SUBSCRIPTION` محدد بشكل صحيح
- [ ] البوت موجود في القناة المذكورة
- [ ] `BOT_TOKEN` و `SUPABASE_KEY` صحيحة
- [ ] قاعدة البيانات Supabase متصلة
- [ ] لا توجد أخطاء في الـ imports
- [ ] جميع المتطلبات في `requirements.txt` مثبتة

---

## 🚨 في حالة الطوارئ

إذا استمرت الأخطاء رغم الإصلاحات:

1. **قم بعرض stack trace كامل**:
```python
import traceback
traceback.print_exc()  # مع كل except
```

2. **استخدم logging بدل print**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.error("Detailed error info", exc_info=True)
```

3. **شغّل اختبارات منفصلة**:
```bash
python -c "from final_bot_with_image import check_channel_subscription; check_channel_subscription(123456)"
```

---

**آخر تحديث**: 2026-03-20
**الحالة**: ✅ جميع الإصلاحات مطبقة
