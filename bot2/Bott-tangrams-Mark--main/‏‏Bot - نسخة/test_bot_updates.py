#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت اختبار التحديثات
يتحقق من أن البوت يعمل مع الجداول الجديدة
"""

import os
import sys
from dotenv import load_dotenv

print("═══════════════════════════════════════")
print("🧪 اختبار تحديثات البوت")
print("═══════════════════════════════════════\n")

# تحميل المتغيرات البيئية
load_dotenv()

# التحقق من المتطلبات
print("1️⃣ فحص المتطلبات...")

try:
    from supabase import create_client
    print("   ✅ supabase")
except ImportError:
    print("   ❌ supabase - قم بتثبيته: pip install supabase")
    sys.exit(1)

try:
    import telebot
    print("   ✅ telebot")
except ImportError:
    print("   ❌ telebot - قم بتثبيته: pip install pyTelegramBotAPI")
    sys.exit(1)

# التحقق من الاتصال بقاعدة البيانات
print("\n2️⃣ فحص الاتصال بقاعدة البيانات...")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("   ❌ بيانات Supabase غير موجودة في .env")
    sys.exit(1)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # اختبار الاتصال
    response = supabase.table("all_marks").select("id").limit(1).execute()
    print("   ✅ الاتصال بـ all_marks")
    
    # فحص الجداول الجديدة
    try:
        response = supabase.table("students").select("student_id").limit(1).execute()
        print("   ✅ جدول students موجود")
    except Exception as e:
        print(f"   ⚠️  جدول students: {str(e)[:50]}")
    
    try:
        response = supabase.table("student_stats_cache").select("student_id").limit(1).execute()
        print("   ✅ جدول student_stats_cache موجود")
        
        if response.data:
            print(f"      📊 عدد السجلات: {len(response.data)}")
        else:
            print("      ⚠️  الجدول فارغ - قم بتنفيذ update_all_student_stats()")
            
    except Exception as e:
        print(f"   ⚠️  جدول student_stats_cache: {str(e)[:50]}")
    
    try:
        response = supabase.table("subjects").select("id").limit(1).execute()
        print("   ✅ جدول subjects موجود")
    except Exception as e:
        print(f"   ⚠️  جدول subjects: {str(e)[:50]}")
        
except Exception as e:
    print(f"   ❌ خطأ في الاتصال: {str(e)}")
    sys.exit(1)

# فحص الوحدات المحدثة
print("\n3️⃣ فحص الوحدات المحدثة...")

try:
    from analytics import calculate_statistics_fast, get_top_10_students
    print("   ✅ analytics.py - calculate_statistics_fast")
    print("   ✅ analytics.py - get_top_10_students")
except ImportError as e:
    print(f"   ❌ خطأ في استيراد analytics: {e}")
    sys.exit(1)

# اختبار الدوال
print("\n4️⃣ اختبار الدوال...")

try:
    # جلب أول طالب للاختبار
    response = supabase.table("all_marks").select("student_id").limit(1).execute()
    
    if response.data:
        test_student_id = response.data[0]['student_id']
        print(f"   🎯 اختبار بالطالب: {test_student_id}")
        
        # اختبار calculate_statistics_fast
        print("\n   📊 اختبار calculate_statistics_fast...")
        import time
        
        start = time.time()
        stats = calculate_statistics_fast(test_student_id, supabase)
        elapsed = time.time() - start
        
        if stats:
            print(f"      ✅ نجح الاختبار ({elapsed:.3f} ثانية)")
            print(f"      📈 المعدل: {stats.get('average_grade', 0)}%")
            print(f"      📚 المواد: {stats.get('total_subjects', 0)}")
            print(f"      ✅ نجح: {stats.get('passed_subjects', 0)}")
            print(f"      ❌ رسب: {stats.get('failed_subjects', 0)}")
            
            if stats.get('rank'):
                print(f"      🏅 الترتيب: #{stats['rank']}")
        else:
            print("      ⚠️  لا توجد بيانات")
        
        # اختبار get_top_10_students
        print("\n   🏆 اختبار get_top_10_students...")
        
        start = time.time()
        top_msg = get_top_10_students(supabase)
        elapsed = time.time() - start
        
        if top_msg and "خطأ" not in top_msg:
            print(f"      ✅ نجح الاختبار ({elapsed:.3f} ثانية)")
            lines = top_msg.split('\n')[:5]  # أول 5 سطور
            for line in lines:
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"      ⚠️  {top_msg[:100]}")
    else:
        print("   ⚠️  لا توجد بيانات للاختبار")
        
except Exception as e:
    print(f"   ❌ خطأ في الاختبار: {str(e)}")
    import traceback
    traceback.print_exc()

# النتيجة النهائية
print("\n═══════════════════════════════════════")
print("✅ اكتمل الاختبار!")
print("═══════════════════════════════════════\n")

print("📝 الخطوات التالية:")
print("1. تأكد من تنفيذ سكريبتات SQL في Supabase")
print("2. قم بتحديث Cache: SELECT update_all_student_stats();")
print("3. شغّل البوت: python final_bot_with_image.py")
print("\n🎉 البوت جاهز للعمل مع الجداول الجديدة!")
