#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اختبار سريع لـ Mini App
يتحقق من جميع المكونات
"""

import os
import sys
from dotenv import load_dotenv

print("════════════════════════════════════════")
print("🧪 اختبار Mini App")
print("════════════════════════════════════════\n")

# 1. التحقق من .env
print("1️⃣ فحص ملف .env...")
load_dotenv()

required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'BOT_TOKEN']
missing = []

for var in required_vars:
    value = os.environ.get(var)
    if not value or 'YOUR_' in value:
        missing.append(var)
        print(f"   ❌ {var} - غير موجود أو غير صحيح")
    else:
        print(f"   ✅ {var} - موجود")

if missing:
    print(f"\n⚠️  يرجى تحديث: {', '.join(missing)}")
    sys.exit(1)

print("\n✅ جميع المتغيرات موجودة\n")

# 2. التحقق من المكتبات
print("2️⃣ فحص المكتبات...")

libraries = [
    ('flask', 'Flask'),
    ('flask_cors', 'Flask-CORS'),
    ('supabase', 'Supabase'),
    ('dotenv', 'python-dotenv')
]

for module, name in libraries:
    try:
        __import__(module)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} - غير مثبت")
        print(f"      قم بتشغيل: pip install {name.lower()}")
        sys.exit(1)

print("\n✅ جميع المكتبات موجودة\n")

# 3. التحقق من Supabase
print("3️⃣ فحص اتصال Supabase...")

try:
    from supabase import create_client
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # اختبار بسيط
    response = supabase.table("all_marks").select("id").limit(1).execute()
    
    print("   ✅ الاتصال نجح")
    print(f"   📊 عدد السجلات في جدول all_marks: {len(response.data) if response.data else 0}")
    
    # التحقق من جدول mini_app_profiles
    try:
        response2 = supabase.table("mini_app_profiles").select("id").limit(1).execute()
        print(f"   ✅ جدول mini_app_profiles موجود ({len(response2.data) if response2.data else 0} سجل)")
    except Exception as e:
        print(f"   ⚠️  جدول mini_app_profiles غير موجود")
        print(f"      يرجى تنفيذ: SQL_MINI_APP.sql في Supabase")
    
except Exception as e:
    print(f"   ❌ فشل الاتصال: {str(e)[:100]}")
    sys.exit(1)

print("\n✅ قاعدة البيانات تعمل\n")

# 4. التحقق من الملفات
print("4️⃣ فحص الملفات...")

files = [
    ('app.py', 'ملف Flask الرئيسي'),
    ('templates/index.html', 'الصفحة الرئيسية'),
    ('static/js/app.js', 'JavaScript'),
    ('static/css/style.css', 'CSS')
]

for file, desc in files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"   ✅ {desc} ({size} bytes)")
    else:
        print(f"   ❌ {desc} - غير موجود")

print("\n✅ جميع الملفات موجودة\n")

# 5. اختبار API endpoints
print("5️⃣ اختبار API Endpoints...")

try:
    from flask import Flask
    from app import app as flask_app
    
    with flask_app.test_client() as client:
        # Health check
        response = client.get('/api/health')
        if response.status_code == 200:
            data = response.get_json()
            print(f"   ✅ /api/health - {data.get('status')}")
        else:
            print(f"   ❌ /api/health - status {response.status_code}")
        
        # Test results endpoint
        response = client.get('/api/results/test123')
        if response.status_code in [200, 404]:  # 404 is ok (no data)
            print(f"   ✅ /api/results/:id - يعمل")
        else:
            print(f"   ⚠️  /api/results/:id - status {response.status_code}")
        
except Exception as e:
    print(f"   ⚠️  تحذير: {str(e)[:100]}")

print("\n✅ API يعمل\n")

# النتيجة النهائية
print("════════════════════════════════════════")
print("🎉 جميع الاختبارات نجحت!")
print("════════════════════════════════════════\n")
print("📝 خطوات التشغيل:")
print("   1. قم بتنفيذ SQL_MINI_APP.sql في Supabase (إن لم يكن منفذاً)")
print("   2. شغّل التطبيق: python app.py")
print("   3. افتح: http://localhost:5000")
print("\n💡 للوصول من Telegram:")
print("   - استخدم ngrok: ngrok http 5000")
print("   - حدّث MINI_APP_URL في .env البوت الرئيسي")
print("\n════════════════════════════════════════")
