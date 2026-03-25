# جداول حماية البوت من الطلبات المتتالية

> استنسخ وألصق هذه الأوامر في **Supabase SQL Editor** لإنشاء الجداول المطلوبة

## 📋 قائمة الجداول المطلوبة:

### 1️⃣ جدول تسجيل الطلبات (request_log)
```sql
CREATE TABLE IF NOT EXISTS request_log (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
    request_type TEXT DEFAULT 'search',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_request_log_user ON request_log(user_id);
CREATE INDEX IF NOT EXISTS idx_request_log_time ON request_log(request_time);
```

### 2️⃣ جدول المستخدمين المحظورين (blocked_users)
```sql
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
```

### 3️⃣ جدول حوادث الرسائل المزعجة (spam_incidents)
```sql
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

---

## 🚀 خطوات التثبيت:

1. **افتح Supabase Dashboard** 👉 https://app.supabase.com
2. **اذهب إلى SQL Editor** (في الجانب الأيسر)
3. **انسخ العمليات أعلاه واحدة تلو الأخرى** أو استخدم هذا الكود الكامل:

---

## ✅ الكود الكامل (انسخ وألصق مباشرة):

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

---

## 📊 شرح الجداول:

### request_log
- **user_id**: معرف المستخدم
- **request_time**: وقت الطلب
- **request_type**: نوع الطلب (search، etc)

### blocked_users
- **user_id**: معرف المستخدم المحظور
- **reason**: سبب الحظر
- **is_active**: هل الحظر نشط الآن?
- **blocked_at**: وقت الحظر
- **unblock_at**: الوقت المتوقع لفك الحظر

### spam_incidents
- **user_id**: معرف المستخدم
- **request_count**: عدد الطلبات المكتشفة
- **status**: الحالة (pending/blocked/ignored)
- **detected_at**: وقت الكشف

---

## 🔧 التعديلات الممكنة:

إذا أردت تغيير حدود الرسائل المزعجة، عدّل هذه القيم في `spam_protection.py`:

```python
self.MAX_REQUESTS_PER_MINUTE = 5      # أقصى 5 طلبات في دقيقة
self.MAX_REQUESTS_PER_5_MINUTES = 15  # أقصى 15 طلب في 5 دقائق
self.BAN_DURATION_MINUTES = 30        # مدة الحظر (30 دقيقة)
```

---

## ❓ الأسئلة الشائعة:

**س: ماذا يحدث عندما يرسل المستخدم طلبات كثيرة؟**
- يتلقى تحذير
- يتلقى المسؤول إشعار مع زرين: ✅حظر أو ❌تجاهل

**س: كم مدة الحظر؟**
- 30 دقيقة افتراضياً (يمكن تعديلها)

**س: هل يمكن فك الحظر يدوياً؟**
- نعم، من خلال لوحة البيانات أو بـ unblock_user() function

---

