# 📢 دليل الاشتراك في قناة البوت

آخر تحديث: **19 مارس 2026**

---

## 🎯 نظرة عامة

تم إضافة ميزة **الاشتراك الإجباري في قناة البوت** لضمان وجود مجتمع نشط وتفاعلي. هذه الميزة تسمح بـ:

✅ التحكم في الوصول إلى خدمات البوت  
✅ تتبع نسبة الاشتراك في القناة  
✅ إرسال إشعارات وتحديثات مهمة  
✅ بناء مجتمع منظم حول البوت  

---

## 🗄️ البنية التقنية

### جدول قاعدة البيانات: `channel_subscriptions`

```sql
CREATE TABLE public.channel_subscriptions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chat_id BIGINT NOT NULL UNIQUE REFERENCES bot_users(chat_id),
    is_subscribed BOOLEAN DEFAULT FALSE,
    subscription_date TIMESTAMP WITH TIME ZONE,
    unsubscription_date TIMESTAMP WITH TIME ZONE,
    last_reminder TIMESTAMP WITH TIME ZONE,
    reminder_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- الفهارس لتحسين الأداء
CREATE INDEX idx_channel_subscriptions_status ON channel_subscriptions(is_subscribed);
CREATE INDEX idx_channel_subscriptions_chat_id ON channel_subscriptions(chat_id);
```

### الأعمدة

| اسم العمود | نوع البيانات | الوصف |
|-----------|------------|-------|
| `id` | BIGINT | معرف فريد للسجل |
| `chat_id` | BIGINT | معرف المستخدم في Telegram (مفتاح أجنبي) |
| `is_subscribed` | BOOLEAN | حالة الاشتراك (true/false) |
| `subscription_date` | TIMESTAMP | تاريخ ووقت الاشتراك |
| `unsubscription_date` | TIMESTAMP | تاريخ إلغاء الاشتراك (اختياري) |
| `last_reminder` | TIMESTAMP | آخر تذكير تم إرساله |
| `reminder_count` | INTEGER | عدد التذكيرات المرسلة |
| `created_at` | TIMESTAMP | تاريخ إنشاء السجل |
| `updated_at` | TIMESTAMP | آخر تحديث للسجل |

---

## 🔧 الدوال الجديدة في `cloud_database_manager.py`

### 1. `check_channel_subscription(chat_id: int)`
**الوصف:** التحقق من اشتراك المستخدم في قناة البوت

**الإرجاع:**
```python
{
    "success": True,
    "is_subscribed": bool,
    "reminder_count": int
}
```

**مثال الاستخدام:**
```python
result = db.check_channel_subscription(USER_ID)
if result["is_subscribed"]:
    # السماح بالمتابعة
else:
    # عرض رسالة الاشتراك
```

---

### 2. `mark_channel_subscribed(chat_id: int)`
**الوصف:** تسجيل اشتراك المستخدم في قناة البوت

**الإرجاع:**
```python
{
    "success": True,
    "message": "✅ تم تسجيل اشتراكك في القناة"
}
```

**مثال الاستخدام:**
```python
db.mark_channel_subscribed(USER_ID)
```

---

### 3. `update_reminder_count(chat_id: int)`
**الوصف:** تحديث عداد التذكيرات عند محاولة استخدام البوت بدون اشتراك

**الإرجاع:**
```python
{
    "success": True,
    "new_count": int,
    "message": str
}
```

---

### 4. `get_unsubscribed_users()`
**الوصف:** الحصول على قائمة بجميع المستخدمين غير المشتركين

**الإرجاع:**
```python
{
    "success": True,
    "users": [chat_id_1, chat_id_2, ...],
    "count": int
}
```

---

### 5. `get_channel_statistics()`
**الوصف:** الحصول على إحصائيات الاشتراك في القناة

**الإرجاع:**
```python
{
    "success": True,
    "total_tracked_users": int,
    "subscribed_users": int,
    "unsubscribed_users": int,
    "subscription_rate": float  # كنسبة مئوية
}
```

---

## 🔌 التكامل مع البوت الرئيسي

### متغيرات البيئة الجديدة (.env)

```env
# قناة البوت
CHANNEL_USERNAME=@your_bot_channel  # اسم القناة بدون https://t.me/
REQUIRE_CHANNEL_SUBSCRIPTION=true   # تفعيل/تعطيل الميزة (true/false)
```

### الدوال الجديدة في `final_bot_with_image.py`

#### `check_channel_subscription(chat_id: int) -> bool`
فحص اشتراك المستخدم من البوت

```python
if not check_channel_subscription(msg.chat.id):
    bot.send_message(msg.chat.id, f"👉 [اشترك في القناة]({CHANNEL_LINK})")
    return
```

#### `update_channel_reminder(chat_id: int)`
تحديث عداد التذكيرات

```python
update_channel_reminder(msg.chat.id)
```

---

## 📊 سير العمل

```
المستخدم يرسل رسالة
    ↓
فحص الحظر الأساسي
    ↓
فحص الاشتراك في القناة
    ├─ مشترك ✅ → المتابعة
    └─ غير مشترك ❌ → عرض رسالة الاشتراك + تحديث العداد
    ↓
فحص الرسائل العشوائية
    ↓
معالجة الطلب
```

---

## 🎯 حالات الاستخدام

### 1. مستخدم جديد غير مشترك
- يظهر رسالة تطلب الاشتراك
- يتم إنشاء سجل في `channel_subscriptions` مع `is_subscribed = false`
- يتم تحديث `reminder_count` كل مرة يحاول الوصول

### 2. مستخدم اشترك في القناة
- عند النقر على الزر "اشترك"، يتم تحديث `is_subscribed = true`
- يمكنه استخدام جميع خدمات البوت بدون قيود

### 3. مسؤول البوت
- لا يتحقق من الاشتراك في القناة
- يمكنه الوصول إلى جميع الأوامر مباشرة

---

## 📈 الإحصائيات والتقارير

### الحصول على إحصائيات الاشتراك

```python
from cloud_database_manager import CloudDatabaseManager

stats = db.get_channel_statistics()
print(f"نسبة الاشتراك: {stats['subscription_rate']}%")
```

### من لوحة تحكم الإدارة

1. اذهب إلى `/admin`
2. اختر "📊 إحصائيات النظام"
3. سيظهر ملخص إحصائيات الاشتراك

---

## 🛠️ تفعيل/تعطيل الميزة

### تفعيل الميزة

في ملف `.env`:
```env
REQUIRE_CHANNEL_SUBSCRIPTION=true
CHANNEL_USERNAME=@your_channel_name
```

### تعطيل الميزة

```env
REQUIRE_CHANNEL_SUBSCRIPTION=false
```

---

## 🔐 الأمان والخصوصية

- ✅ بيانات الاشتراك محفوظة في قاعدة بيانات آمنة
- ✅ فقط البوت والمسؤولين يمكنهم الوصول للبيانات
- ✅ لا يتم حفظ بيانات شخصية إضافية
- ✅ يمكن حذف بيانات المستخدم في أي وقت

---

## 📝 أمثلة عملية

### مثال 1: فحص طلب المستخدم

```python
from cloud_database_manager import CloudDatabaseManager

db = CloudDatabaseManager(supabase)

def handle_user_request(user_id):
    # فحص الاشتراك
    result = db.check_channel_subscription(user_id)
    
    if not result["is_subscribed"]:
        # تحديث التذكيرات
        db.update_reminder_count(user_id)
        return "❌ يجب الاشتراك في القناة أولاً"
    
    return "✅ تم معالجة طلبك بنجاح"
```

### مثال 2: تسجيل الاشتراك الجديد

```python
# عندما يشترك المستخدم
db.mark_channel_subscribed(user_id)

# التحقق من تحديث البيانات
result = db.check_channel_subscription(user_id)
print(result["is_subscribed"])  # True
```

### مثال 3: إرسال إشعارات للمستخدمين غير المشتركين

```python
# الحصول على المستخدمين غير المشتركين
unsubscribed = db.get_unsubscribed_users()

# إرسال رسائل تذكيرية
for user_id in unsubscribed["users"]:
    bot.send_message(
        user_id,
        f"👉 لم تشترك بعد في قناتنا!\n[اشترك الآن]({CHANNEL_LINK})"
    )
```

---

## 🐛 استكشاف الأخطاء والتحسينات

### المشكلة: الرسالة لا تظهر
**الحل:**
1. تحقق من أن `REQUIRE_CHANNEL_SUBSCRIPTION=true` في `.env`
2. تأكد من أن البيانات موجودة في جدول `channel_subscriptions`

### المشكلة: جدول غير موجود
**الحل:**
1. انسخ استعلام SQL من أعلى الدليل
2. اذهب إلى Supabase SQL Editor
3. نفّذ الاستعلام

### المشكلة: البيانات غير محدثة
**الحل:**
استخدم `updated_at` للتحقق من الوقت الفعلي للتحديث

---

## 📞 الدعم والمساعدة

إذا واجهت مشكلة:

1. ✅ تحقق من ملف `.env`
2. ✅ تأكد من وجود جدول `channel_subscriptions`
3. ✅ راجع سجلات الأخطاء
4. ✅ اتصل بمسؤول النظام

---

## ✅ قائمة التحقق

- [ ] تم إنشاء جدول `channel_subscriptions`
- [ ] تم إضافة متغيرات البيئة الجديدة
- [ ] تم تحديث ملف `cloud_database_manager.py`
- [ ] تم تحديث ملف `final_bot_with_image.py`
- [ ] تم اختبار فحص الاشتراك
- [ ] تم التحقق من عرض الرسائل
- [ ] تم حفظ التغييرات في Git

---

**آخر تحديث:** 19 مارس 2026  
**الإصدار:** 1.0.0  
**الحالة:** ✅ جاهز للإنتاج
