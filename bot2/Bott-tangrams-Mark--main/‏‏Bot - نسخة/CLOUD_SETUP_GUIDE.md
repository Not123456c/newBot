# دليل إعداد نظام التخزين السحابي الكامل 🚀

## المحتويات
1. [الملفات المضافة](#الملفات-المضافة)
2. [خطوات الإعداد](#خطوات-الإعداد)
3. [الهجرة من JSON](#الهجرة-من-json)
4. [تشغيل النظام](#تشغيل-النظام)
5. [اختبار النظام](#اختبار-النظام)

---

## الملفات المضافة

### ملفات التخزين السحابي: 📦

| الملف | الوصف |
|------|--------|
| `cloud_database_manager.py` | مدير قاعدة البيانات الرئيسي - جميع العمليات |
| `bot_cloud_integration.py` | تكامل البوت مع النظام السحابي |
| `data_migration_manager.py` | هجرة البيانات من JSON إلى Supabase |
| `cloud_database_api.py` | API REST للتعامل مع البيانات |
| `CLOUD_DATABASE_GUIDE.md` | دليل شامل مفصل |

---

## خطوات الإعداد

### 1️⃣ تحديث المتطلبات
```bash
pip install -r requirements.txt
```

الملفات الجديدة المطلوبة:
- `flask>=2.3.0` - لـ API REST
- `flask-cors>=4.0.0` - للـ CORS
- `supabase>=2.0.0` - عميل Supabase

### 2️⃣ إنشاء الجداول في Supabase

#### طريقة سريعة: استخدم SQL Editor
في لوحة تحكم Supabase:
1. اذهب إلى `SQL Editor`
2. البدء بـ `New Query`
3. انسخ كود SQL التالي:

```sql
-- 1️⃣ جدول المستخدمين
CREATE TABLE IF NOT EXISTS public.bot_users (
  chat_id bigint NOT NULL,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT bot_users_pkey PRIMARY KEY (chat_id)
);

-- 2️⃣ جدول الاشتراكات
CREATE TABLE IF NOT EXISTS public.user_subscriptions (
  chat_id bigint NOT NULL,
  student_id text NOT NULL,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT user_subscriptions_pkey PRIMARY KEY (chat_id)
);

-- 3️⃣ جدول جميع الدرجات
CREATE TABLE IF NOT EXISTS public.all_marks (
  id bigserial NOT NULL,
  student_id character varying NOT NULL,
  student_name text,
  father_name text,
  subject_name text NOT NULL,
  practical_grade integer,
  theoretical_grade integer,
  total_grade integer,
  grade_in_words text,
  result text,
  rank integer,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT all_marks_pkey PRIMARY KEY (id)
);

-- 4️⃣ جدول الدرجات المعروفة (JSON)
CREATE TABLE IF NOT EXISTS public.known_grades (
  student_id text NOT NULL,
  grades_data jsonb NOT NULL,
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT known_grades_pkey PRIMARY KEY (student_id)
);

-- 5️⃣ جدول درجات اللغة
CREATE TABLE IF NOT EXISTS public.language_grades (
  student_id character varying NOT NULL,
  student_name text,
  father_name text,
  practical_grade integer,
  theoretical_grade integer,
  total_grade integer,
  grade_in_words text,
  result text,
  CONSTRAINT language_grades_pkey PRIMARY KEY (student_id)
);

-- 6️⃣ جدول درجات الطلاب
CREATE TABLE IF NOT EXISTS public.student_grades (
  student_id character varying NOT NULL,
  student_name text,
  father_name text,
  practical_grade integer,
  theoretical_grade integer,
  total_grade integer,
  grade_in_words text,
  result text,
  CONSTRAINT student_grades_pkey PRIMARY KEY (student_id)
);

-- إضافة فهارس للأداء (Indexes)
CREATE INDEX IF NOT EXISTS idx_all_marks_student_id ON all_marks(student_id);
CREATE INDEX IF NOT EXISTS idx_all_marks_subject_name ON all_marks(subject_name);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_student_id ON user_subscriptions(student_id);
```

### 3️⃣ تحديث متغيرات البيئة (.env)

تأكد من وجود هذه المتغيرات:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# API (اختياري)
API_KEY=your-secret-api-key
```

---

## الهجرة من JSON

### خطوة 1: النسخ الاحتياطية التلقائية
```bash
python -c "
from supabase import create_client
from data_migration_manager import DataMigrationManager
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
migrator = DataMigrationManager(supabase)

# إنشاء نسخة احتياطية من JSON
backup = migrator.backup_json_files('backup/')
print('النسخ الاحتياطية:')
for file, result in backup['backups'].items():
    status = '✅' if result['success'] else '❌'
    print(f'  {status} {file}')
"
```

### خطوة 2: الهجرة الكاملة
```bash
python data_migration_manager.py
```

**الناتج المتوقع:**
```
🔐 تشغيل النسخ الاحتياطية...
✅ تم إنشاء نسخ احتياطية

🚀 بدء الهجرة...
============================================================
👥 المستخدمين: 13 مهجر، 0 فشل
🔗 الاشتراكات: 4 مهجر، 0 فشل
============================================================

📋 تقرير الهجرة:
✅ المهجرة: 17
❌ الفاشلة: 0

🔍 التحقق من الهجرة...
✅ تحقق من الهجرة:

👥 المستخدمين في Supabase: 13
🔗 الاشتراكات في Supabase: 4
📚 الدرجات في Supabase: 0
```

### خطوة 3: حذف ملفات JSON (اختياري وآمن)
```bash
# بعد التأكد من نجاح الهجرة، يمكنك حذف الملفات الأصلية
# لا تنساها - أنت محتاج فقط الملفات في Supabase الآن
# rm users.json subscriptions.json
```

---

## تشغيل النظام

### الخيار 1: استخدام البوت الحالي

تحديث `final_bot_with_image.py`:

```python
# استبدل قسم إدارة المستخدمين:

from cloud_database_manager import CloudDatabaseManager
from bot_cloud_integration import BotCloudIntegration

# ══════════════════════════════════════════════════════════════
# إعدادات Supabase
# ══════════════════════════════════════════════════════════════
cloud_db = CloudDatabaseManager(supabase)
bot_integration = BotCloudIntegration(supabase)

# ══════════════════════════════════════════════════════════════
# معالجات البوت الجديدة
# ══════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    response = bot_integration.handle_new_user(chat_id)
    bot.send_message(chat_id, response)

@bot.message_handler(commands=['subscribe'])
def handle_subscribe(message):
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) < 2:
        bot.send_message(chat_id, "❌ الرجاء استخدام: /subscribe رقم_الطالب")
        return
    
    student_id = args[1]
    response = bot_integration.handle_subscription(chat_id, student_id)
    bot.send_message(chat_id, response)

@bot.message_handler(commands=['grades'])
def handle_grades(message):
    chat_id = message.chat.id
    response = bot_integration.format_grades_message(chat_id)
    bot.send_message(chat_id, response)

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    chat_id = message.chat.id
    
    if chat_id not in ADMIN_IDS:
        bot.send_message(chat_id, "❌ ليست لديك صلاحيات")
        return
    
    response = bot_integration.get_database_info()
    bot.send_message(chat_id, response)
```

### الخيار 2: تشغيل API بشكل منفصل
```bash
python cloud_database_api.py
```

**الناتج:**
```
🚀 بدء تشغيل API على http://0.0.0.0:5000
📝 تذكر: استخدم X-API-Key header مع جميع الطلبات
 * Running on http://0.0.0.0:5000
```

---

## اختبار النظام

### اختبار 1: التحقق من الاتصال

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# اختبار الاتصال
try:
    result = supabase.table('bot_users').select('count', count='exact').execute()
    print(f"✅ الاتصال ناجح! عدد المستخدمين: {result.count}")
except Exception as e:
    print(f"❌ خطأ الاتصال: {e}")
```

### اختبار 2: إضافة مستخدم

```python
from cloud_database_manager import CloudDatabaseManager

db = CloudDatabaseManager(supabase)

# إضافة مستخدم جديد
result = db.add_user(123456789)
print(result)

# الحصول على المستخدم
result = db.get_user(123456789)
print(result)
```

### اختبار 3: اختبار API

```bash
# الحصول على جميع المستخدمين
curl -X GET http://localhost:5000/api/users \
  -H "X-API-Key: your-secret-api-key"

# إضافة مستخدم جديد
curl -X POST http://localhost:5000/api/users \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 987654321}'

# الاشتراك برقم طالب
curl -X POST http://localhost:5000/api/subscriptions \
  -H "X-API-Key: your-secret-api-key" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 987654321, "student_id": "220450"}'

# الحصول على درجات طالب
curl -X GET http://localhost:5000/api/grades/student/220450 \
  -H "X-API-Key: your-secret-api-key"
```

---

## هيكل البيانات الجديد

```
📊 Supabase
├── 👥 bot_users
│   ├── chat_id (PK)
│   └── created_at
├── 🔗 user_subscriptions
│   ├── chat_id (PK)
│   ├── student_id
│   └── created_at
├── 📚 all_marks
│   ├── id (PK)
│   ├── student_id, subject_name
│   ├── practical_grade, theoretical_grade
│   ├── total_grade, result, rank
│   └── created_at
├── 📝 known_grades (JSON)
│   ├── student_id (PK)
│   ├── grades_data (JSONB)
│   └── updated_at
├── 🌐 language_grades
│   └── [تفاصيل درجات اللغة]
└── 👨‍🎓 student_grades
    └── [تفاصيل درجات الطالب العام]
```

---

## أوامر مساعدة

### حذف جميع البيانات (احذر!)
```python
from cloud_database_manager import CloudDatabaseManager
db = CloudDatabaseManager(supabase)
result = db.clear_all_data()
print(result)
```

### الحصول على الإحصائيات
```python
stats = db.get_statistics()
print(f"المستخدمين: {stats['total_users']}")
print(f"الاشتراكات: {stats['total_subscriptions']}")
print(f"الدرجات: {stats['total_grades']}")
```

### إضافة درجات من ملف CSV

```python
import pandas as pd

df = pd.read_csv('grades.csv')
for _, row in df.iterrows():
    db.add_grade(
        student_id=row['student_id'],
        student_name=row['student_name'],
        father_name=row['father_name'],
        subject_name=row['subject_name'],
        practical_grade=int(row['practical_grade']),
        theoretical_grade=int(row['theoretical_grade']),
        total_grade=int(row['total_grade']),
        grade_in_words=row['grade_in_words'],
        result=row['result']
    )
print("✅ تم إضافة الدرجات من CSV")
```

---

## استكشاف الأخطاء

### ❌ خطأ: "جدول غير موجود"
**الحل:** تأكد من تشغيل أكواد SQL في Supabase

### ❌ خطأ: "فشل الاتصال"
**الحل:** تحقق من SUPABASE_URL و SUPABASE_KEY

### ❌ خطأ: "البيانات مفقودة"
**الحل:** تحقق من صيغة JSON (يجب أن تكون صحيحة)

### ❌ خطأ: "API 401 Unauthorized"
**الحل:** تأكد من استخدام `X-API-Key` الصحيح

---

## السياق التاريخي

| التاريخ | الحدث |
|--------|-------|
| سابقاً | استخدام JSON محلي (users.json, subscriptions.json) |
| الآن | نظام تخزين سحابي كامل (Supabase) |
| المستقبل | API REST، لوحة تحكم، تقارير متقدمة |

---

## التالي ✅

- [ ] تثبيت المتطلبات: `pip install -r requirements.txt`
- [ ] إنشاء الجداول في Supabase
- [ ] هجرة البيانات: `python data_migration_manager.py`
- [ ] اختبار النظام
- [ ] تحديث البوت الرئيسي
- [ ] تشغيل البوت: `python final_bot_with_image.py`

---

**آخر تحديث**: مارس 2026
**الإصدار**: 1.0.0
