# -*- coding: utf-8 -*-
"""
اختبار سريع لنظام Supabase Storage والنسخ الاحتياطية
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client
from storage_manager import SupabaseStorageManager
from backup_scheduler import BackupScheduler

def test_storage_connection():
    """اختبار الاتصال بـ Supabase Storage"""
    print("🔍 اختبار الاتصال بـ Supabase Storage...\n")
    
    load_dotenv()
    
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("❌ خطأ: بيانات Supabase غير موجودة في .env")
            return False
        
        print(f"✅ تم قراءة بيانات Supabase")
        print(f"   URL: {url[:30]}...")
        
        # إنشاء عميل Supabase
        supabase = create_client(url, key)
        print("✅ تم الاتصال بـ Supabase بنجاح\n")
        
        # اختبار مدير التخزين
        manager = SupabaseStorageManager(supabase, bucket_name="bot-storage")
        print("✅ تم إنشاء مدير التخزين\n")
        
        # اختبار وجود ملف users.json
        if os.path.exists("users.json"):
            print("📄 ملف users.json موجود - جاหز للنسخ الاحتياطي")
            print(f"   الحجم: {os.path.getsize('users.json')} بايت\n")
        else:
            print("⚠️  ملف users.json غير موجود (سيتم إنشاؤه عند أول استخدام للبوت)\n")
        
        return True, supabase
        
    except Exception as e:
        print(f"❌ خطأ في الاختبار: {str(e)}\n")
        return False, None

def test_manual_backup(supabase):
    """اختبار النسخ الاحتياطي اليدوي"""
    print("🔍 اختبار النسخ الاحتياطي اليدوي...\n")
    
    try:
        # إنشاء ملف اختبار
        test_file = "test_backup.json"
        test_data = {"test": "data", "timestamp": "2026-03-19"}
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
        
        print(f"✅ تم إنشاء ملف اختبار: {test_file}")
        
        # محاولة رفع الملف
        manager = SupabaseStorageManager(supabase)
        result = manager.upload_backup_file(test_file, backup_type="test")
        
        if result.get("success"):
            print(f"✅ تم رفع الملف بنجاح!")
            print(f"   • المسار: {result.get('file_path')}")
            print(f"   • الحجم: {result.get('file_size')} بايت")
            print(f"   • الطابع الزمني: {result.get('timestamp')}\n")
            
            # حذف ملف الاختبار
            if os.path.exists(test_file):
                os.remove(test_file)
            
            return True
        else:
            print(f"❌ فشل الرفع:")
            print(f"   {result.get('error')}\n")
            
            # حذف ملف الاختبار
            if os.path.exists(test_file):
                os.remove(test_file)
            
            return False
            
    except Exception as e:
        print(f"❌ خطأ في اختبار النسخ الاحتياطي: {str(e)}\n")
        return False

def test_backup_scheduler(supabase):
    """اختبار جدولة النسخ الاحتياطي"""
    print("🔍 اختبار جدولة النسخ الاحتياطي...\n")
    
    try:
        # إنشاء جدولة النسخ الاحتياطي بفترة دقيقة واحدة للاختبار
        scheduler = BackupScheduler(supabase, backup_interval_hours=1/60)  # 1 دقيقة
        
        print("✅ تم إنشاء مدير الجدولة")
        print("   • الفترة الزمنية: 1/60 ساعة (دقيقة واحدة)")
        print("   • سيبدأ النسخ الاحتياطي في الخلفية\n")
        
        # عرض الحالة
        status = scheduler.get_backup_status()
        print(f"✅ حالة الجدولة:")
        print(f"   • النشاط: {'نشط' if status['is_running'] else 'متوقف'}")
        print(f"   • الفترة الزمنية: {status['backup_interval_hours']} ساعة\n")
        
        # إيقاف الجدولة
        scheduler.stop()
        print("✅ تم إيقاف الجدولة بنجاح\n")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في اختبار الجدولة: {str(e)}\n")
        return False

def print_summary(results):
    """طباعة ملخص نتائج الاختبارات"""
    print("\n" + "="*50)
    print("📊 ملخص نتائج الاختبارات:")
    print("="*50 + "\n")
    
    if all(results.values()):
        print("✅ جميع الاختبارات نجحت!")
        print("\n🎉 النظام جاهز للاستخدام!")
        print("\nالخطوات التالية:")
        print("1. تأكد من أن ملف .env يحتوي على بيانات Supabase الصحيحة")
        print("2. شغّل البوت باستخدام: python final_bot_with_image.py")
        print("3. استخدم /backup_status للتحقق من حالة النسخ الاحتياطي")
    else:
        print("❌ بعض الاختبارات فشلت. يرجى التحقق من الأخطاء أعلاه.")
        print("\nللمزيد من المساعدة:")
        print("• تحقق من ملف .env والبيانات الموجودة فيه")
        print("• تأكد من اتصالك بالإنترنت")
        print("• تحقق من صلاحيات Supabase Storage")

def main():
    """الدالة الرئيسية"""
    print("\n" + "="*50)
    print("🧪 برنامج فحص نظام Supabase Storage")
    print("="*50 + "\n")
    
    results = {}
    
    # اختبار 1: الاتصال
    connection_result = test_storage_connection()
    if connection_result[0]:
        supabase = connection_result[1]
        results["الاتصال"] = True
        
        # اختبار 2: النسخ الاحتياطي اليدوي
        results["النسخ_الاحتياطي_اليدوي"] = test_manual_backup(supabase)
        
        # اختبار 3: الجدولة
        results["الجدولة"] = test_backup_scheduler(supabase)
    else:
        results["الاتصال"] = False
        print("⛔ تم إيقاف بقية الاختبارات لأن الاتصال فشل\n")
    
    # طباعة الملخص
    print_summary(results)

if __name__ == "__main__":
    main()
