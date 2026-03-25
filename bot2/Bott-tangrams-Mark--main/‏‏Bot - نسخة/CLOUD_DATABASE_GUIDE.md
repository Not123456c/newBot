# نظام التخزين السحابي الكامل للبوت 🚀

## نظرة عامة
تم تطوير نظام تخزين **سحابي كامل** يعتمد على **Supabase** بدلاً من ملفات JSON المحلية. هذا يوفر:
- ✅ تخزين آمن ومركزي
- ✅ سهولة الوصول من أي مكان
- ✅ قابلية التوسع
- ✅ نسخ احتياطية تلقائية
- ✅ دعم عدة مستخدمين والتزامن

---

## الملفات الجديدة المضافة

### 1. **cloud_database_manager.py**
مدير قاعدة البيانات السحابية الرئيسي
```python
from cloud_database_manager import CloudDatabaseManager
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
db = CloudDatabaseManager(supabase)
```

**الوظائف الرئيسية:**
- إدارة المستخدمين: `add_user()`, `get_user()`, `get_all_users()`
- إدارة الاشتراكات: `subscribe_user()`, `get_subscription()`
- إدارة الدرجات: `add_grade()`, `get_student_grades()`, `update_grade()`
- إدارة درجات خاصة: `add_language_grade()`, `add_student_grade()`

### 2. **bot_cloud_integration.py**
تكامل البوت مع النظام السحابي
```python
from bot_cloud_integration import BotCloudIntegration

bot_integration = BotCloudIntegration(supabase)
```

**الوظائف الرئيسية:**
- معالجة مستخدمين جدد
- إدارة الاشتراكات
- الحصول على درجات الطالب
- الإخطارات والتنبيهات
- عمليات المسؤول

### 3. **data_migration_manager.py**
مدير هجرة البيانات من JSON إلى Supabase
```python
from data_migration_manager import DataMigrationManager

migrator = DataMigrationManager(supabase)
result = migrator.migrate_all_data()
```

---

## جداول Supabase المستخدمة

### 1. **bot_users** - المستخدمين
```sql
{
  chat_id BIGINT PRIMARY KEY,
  created_at TIMESTAMP (تاريخ الانضمام)
}
```

### 2. **user_subscriptions** - الاشتراكات
```sql
{
  chat_id BIGINT PRIMARY KEY,
  student_id TEXT,
  created_at TIMESTAMP
}
```

### 3. **all_marks** - جميع الدرجات
```sql
{
  id SERIAL PRIMARY KEY,
  student_id VARCHAR,
  student_name TEXT,
  father_name TEXT,
  subject_name TEXT,
  practical_grade INT,
  theoretical_grade INT,
  total_grade INT,
  grade_in_words TEXT,
  result TEXT,
  rank INT
}
```

### 4. **known_grades** - الدرجات المعروفة (JSON)
```sql
{
  student_id TEXT PRIMARY KEY,
  grades_data JSONB,
  updated_at TIMESTAMP
}
```

### 5. **language_grades** - درجات اللغة
```sql
{
  student_id VARCHAR PRIMARY KEY,
  student_name TEXT,
  father_name TEXT,
  practical_grade INT,
  theoretical_grade INT,
  total_grade INT,
  grade_in_words TEXT,
  result TEXT
}
```

### 6. **student_grades** - درجات الطلاب
```sql
{
  student_id VARCHAR PRIMARY KEY,
  student_name TEXT,
  father_name TEXT,
  practical_grade INT,
  theoretical_grade INT,
  total_grade INT,
  grade_in_words TEXT,
  result TEXT
}
```

---

## خطوات التشغيل

### الخطوة 1: تثبيت المتطلبات
```bash
pip install supabase python-dotenv
```

### الخطوة 2: إعداد متغيرات البيئة
تأكد من وجود `.env` يحتوي على:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
BOT_TOKEN=your_bot_token
```

### الخطوة 3: إنشاء الجداول في Supabase
في لوحة تحكم Supabase، أنسخ والصق الأمر SQL التالي:

```sql
-- جدول المستخدمين
CREATE TABLE public.bot_users (
  chat_id bigint NOT NULL,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT bot_users_pkey PRIMARY KEY (chat_id)
);

-- جدول الاشتراكات
CREATE TABLE public.user_subscriptions (
  chat_id bigint NOT NULL,
  student_id text NOT NULL,
  created_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT user_subscriptions_pkey PRIMARY KEY (chat_id)
);

-- جدول جميع الدرجات
CREATE TABLE public.all_marks (
  id integer NOT NULL DEFAULT nextval('all_marks_id_seq'::regclass),
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
  CONSTRAINT all_marks_pkey PRIMARY KEY (id)
);

-- جدول الدرجات المعروفة
CREATE TABLE public.known_grades (
  student_id text NOT NULL,
  grades_data jsonb NOT NULL,
  updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()),
  CONSTRAINT known_grades_pkey PRIMARY KEY (student_id)
);

-- جدول درجات اللغة
CREATE TABLE public.language_grades (
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

-- جدول درجات الطلاب
CREATE TABLE public.student_grades (
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
```

### الخطوة 4: هجرة البيانات من JSON
```python
from supabase import create_client
from data_migration_manager import run_migration
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
run_migration(supabase)
```

أو من سطر الأوامر:
```bash
python data_migration_manager.py
```

---

## أمثلة الاستخدام في البوت

### إضافة مستخدم جديد
```python
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    result = bot_integration.handle_new_user(chat_id)
    bot.send_message(chat_id, result)
```

### الاشتراك برقم طالب
```python
@bot.message_handler(commands=['subscribe'])
def handle_subscribe(message):
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) < 2:
        bot.send_message(chat_id, "❌ الاستخدام: /subscribe رقم_الطالب")
        return
    
    student_id = args[1]
    result = bot_integration.handle_subscription(chat_id, student_id)
    bot.send_message(chat_id, result)
```

### الحصول على درجات الطالب
```python
@bot.message_handler(commands=['grades'])
def handle_grades(message):
    chat_id = message.chat.id
    result = bot_integration.format_grades_message(chat_id)
    bot.send_message(chat_id, result)
```

### إحصائيات النظام (للمسؤولين)
```python
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    chat_id = message.chat.id
    
    if chat_id not in ADMIN_IDS:
        bot.send_message(chat_id, "❌ ليست لديك صلاحيات")
        return
    
    result = bot_integration.get_database_info()
    bot.send_message(chat_id, result)
```

---

## العمليات الإدارية

### الحصول على إحصائيات النظام
```python
stats = db.get_statistics()
# {
#     'total_users': 10,
#     'total_subscriptions': 8,
#     'total_grades': 120,
#     'total_students': 15
# }
```

### الحصول على جميع الطلاب
```python
students = db.get_all_students()
# {
#     '220450': 'محمد أحمد',
#     '220166': 'علي محمود',
#     ...
# }
```

### تحديث درجة طالب
```python
db.update_grade(
    student_id='220450',
    subject_name='الرياضيات',
    practical_grade=80,
    theoretical_grade=90,
    total_grade=170,
    grade_in_words='ممتاز',
    result='نجح'
)
```

### إخطار المستخدمين عند تحديث درجات
```python
users_to_notify = db.get_subscriptions_for_student('220450')
for chat_id in users_to_notify['users']:
    bot.send_message(chat_id, "📊 تم تحديث درجاتك!")
```

---

## المميزات الأمان

- ✅ **مفاتيح آمنة**: استخدام متغيرات البيئة للمفاتيح السرية
- ✅ **التشفير**: Supabase يوفر تشفير على مستوى قاعدة البيانات
- ✅ **التحكم بالدخول**: يمكن تحديد الصلاحيات على مستوى الجدول والصف
- ✅ **تدقيق**: تسجيل جميع التغييرات (اختياري)
- ✅ **النسخ الاحتياطية**: تلقائية يومياً من Supabase

---

## استكشاف الأخطاء

### خطأ: "جدول غير موجود"
```
حل: تأكد من إنشاء الجداول في Supabase أولاً
```

### خطأ: "فشل الاتصال"
```
حل: تحقق من SUPABASE_URL و SUPABASE_KEY في .env
```

### خطأ: "البيانات مفقودة بعد الهجرة"
```
حل: تحقق من صيغة ملفات JSON (يجب أن تكون صيغة صحيحة)
```

---

## الترقيات المستقبلية

- [ ] تشفير البيانات الحساسة قبل التخزين
- [ ] نظام تقارير متقدم من السحابة
- [ ] واجهة ويب لإدارة البيانات
- [ ] البحث المتقدم والفلترة
- [ ] API RESTful عام

---

## الدعم والمساعدة

للمزيد من المعلومات:
- 📚 [توثيق Supabase](https://supabase.com/docs)
- 🤖 [توثيق TeleBot](https://pypi.org/project/pyTelegramBotAPI/)
- 🖥️ مدير قاعدة البيانات: `cloud_database_manager.py`
- 🔄 مدير الهجرة: `data_migration_manager.py`

---

**تاريخ الإنشاء**: مارس 2026
**الإصدار**: 1.0.0
**النوع**: نظام تخزين سحابي كامل
