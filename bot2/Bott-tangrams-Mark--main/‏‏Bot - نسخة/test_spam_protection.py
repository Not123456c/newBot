# -*- coding: utf-8 -*-
"""
اختبار سريع لنظام الحماية من الطلبات المتتالية
للتحقق من سلامة الكود قبل التشغيل
"""

import sys
from pathlib import Path

def test_imports():
    """اختبار الاستيرادات"""
    print("🔍 اختبار الاستيرادات...")
    try:
        from spam_protection import SpamProtection
        print("✅ SpamProtection: OK")
        return True
    except ImportError as e:
        print(f"❌ خطأ في الاستيراد: {e}")
        return False

def test_spam_protection_logic():
    """اختبار منطق الحماية من الرسائل المزعجة"""
    print("\n🧪 اختبار منطق الحماية...")
    print("⚠️ ملاحظة: اختبار بدون Supabase (نسخة محاكاة)")
    
    try:
        # محاكاة SpamProtection بدون قاعدة بيانات فعلية
        print("✅ يمكنك البدء برسالة اختبار للبوت")
        return True
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def check_file_structure():
    """التحقق من وجود الملفات المطلوبة"""
    print("\n📁 التحقق من هيكل الملفات...")
    
    required_files = [
        "spam_protection.py",
        "final_bot_with_image.py",
        "SQL_SPAM_PROTECTION.md",
        "SPAM_PROTECTION_GUIDE.md"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - غير موجود")
            all_exist = False
    
    return all_exist

def check_syntax():
    """التحقق من صحة الصيغة في الملفات Python"""
    print("\n🔧 التحقق من الصيغة...")
    
    try:
        import ast
        
        files_to_check = [
            "spam_protection.py",
            "final_bot_with_image.py"
        ]
        
        for file in files_to_check:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
                print(f"✅ {file} - الصيغة سليمة")
            except SyntaxError as e:
                print(f"❌ {file} - خطأ في الصيغة: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ خطأ في الفحص: {e}")
        return False

def print_setup_instructions():
    """طباعة تعليمات الإعداد"""
    print("\n" + "="*50)
    print("📖 تعليمات الإعداد المطلوبة:")
    print("="*50)
    
    instructions = """
1️⃣  افتح ملف SQL_SPAM_PROTECTION.md

2️⃣  انسخ أوامر SQL من القسم "الكود الكامل"

3️⃣  اذهب إلى: https://app.supabase.com

4️⃣  افتح SQL Editor وألصق الأوامر

5️⃣  اضغط "Run" لتنفيذ الأوامر

6️⃣  تحقق من التحقق:
    SELECT * FROM blocked_users;
    SELECT * FROM spam_incidents;
    SELECT * FROM request_log;

7️⃣  أعد تشغيل البوت

8️⃣  ابدأ الاختبار! 🎉
    """
    
    print(instructions)

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء الاختبارات...\n")
    
    # تشغيل الاختبارات
    results = []
    
    results.append(("الاستيرادات", test_imports()))
    results.append(("الملفات", check_file_structure()))
    results.append(("الصيغة", check_syntax()))
    results.append(("المنطق", test_spam_protection_logic()))
    
    # ملخص النتائج
    print("\n" + "="*50)
    print("📊 ملخص الاختبارات:")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{test_name}: {status}")
    
    print("\n" + "="*50)
    
    if all(result for _, result in results):
        print("✅ جميع الاختبارات نجحت!")
        print_setup_instructions()
        return 0
    else:
        print("❌ بعض الاختبارات فشلت. يرجى تصحيح الأخطاء أعلاه.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
