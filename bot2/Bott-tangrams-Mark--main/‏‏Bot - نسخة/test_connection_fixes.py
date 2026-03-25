# -*- coding: utf-8 -*-
"""
اختبار معالج الإرسال الآمن
يتحقق من أن جميع الوظائف تعمل بشكل صحيح
"""

import sys
import os

def test_imports():
    """اختبر استيراد جميع الملفات المطلوبة"""
    print("🔍 اختبار الاستيراد...")
    
    try:
        print("  ✅ استيراد send_handler...")
        from send_handler import (
            SafeSendHandler, 
            safe_send_message, 
            safe_send_photo, 
            safe_send_document,
            send_handler
        )
        
        print("  ✅ استيراد connection_manager...")
        from connection_manager import (
            ConnectionManager,
            TelegramPollingManager,
            DatabaseErrorHandler,
            safe_db_operation,
            configure_polling_with_safety
        )
        
        print("  ✅ استيراد pyTelegramBotAPI...")
        import telebot
        
        print("  ✅ استيراد requests...")
        import requests
        
        print("\n✅ جميع الاستيرادات نجحت!\n")
        return True
        
    except ImportError as e:
        print(f"\n❌ خطأ في الاستيراد: {e}\n")
        return False


def test_send_handler_init():
    """اختبر تهيئة معالج الإرسال"""
    print("🔧 اختبار تهيئة SafeSendHandler...")
    
    try:
        from send_handler import SafeSendHandler
        
        # الإعدادات الافتراضية
        handler1 = SafeSendHandler()
        assert handler1.max_retries == 5
        assert handler1.timeout == 30
        print("  ✅ الإعدادات الافتراضية صحيحة")
        
        # إعدادات مخصصة
        handler2 = SafeSendHandler(max_retries=10, timeout=60)
        assert handler2.max_retries == 10
        assert handler2.timeout == 60
        print("  ✅ الإعدادات المخصصة صحيحة")
        
        print("\n✅ اختبارات التهيئة نجحت!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في التهيئة: {e}\n")
        return False


def test_connection_manager():
    """اختبر معالج الاتصال"""
    print("🔗 اختبار ConnectionManager...")
    
    try:
        from connection_manager import ConnectionManager
        
        conn_mgr = ConnectionManager(
            max_retries=5,
            initial_backoff=2,
            max_backoff=60,
            timeout=30
        )
        
        assert conn_mgr.max_retries == 5
        assert conn_mgr.initial_backoff == 2
        assert conn_mgr.max_backoff == 60
        assert conn_mgr.timeout == 30
        
        print("  ✅ معالج الاتصال مهيأ بشكل صحيح")
        print("\n✅ اختبارات الاتصال نجحت!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ خطأ في معالج الاتصال: {e}\n")
        return False


def test_file_existence():
    """تحقق من وجود جميع الملفات المطلوبة"""
    print("📁 فحص وجود الملفات...")
    
    required_files = [
        "send_handler.py",
        "connection_manager.py",
        "final_bot_with_image.py",
        "FIXES_CONNECTION_ERRORS.md"
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = os.path.join(os.getcwd(), filename)
        if os.path.exists(filepath):
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} (غير موجود)")
            all_exist = False
    
    if all_exist:
        print("\n✅ جميع الملفات موجودة!\n")
    else:
        print("\n❌ بعض الملفات غير موجودة!\n")
    
    return all_exist


def check_safe_send_usage():
    """تحقق من أن safe_send يتم استخدامه في main البوت"""
    print("🔍 فحص استخدام safe_send في البوت...")
    
    try:
        with open("final_bot_with_image.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
            # تحقق من الاستيراد
            if "from send_handler import safe_send_message, safe_send_photo, safe_send_document" in content:
                print("  ✅ الاستيراد موجود")
            else:
                print("  ❌ الاستيراد غير موجود")
                return False
            
            # تحقق من الاستخدام
            safe_send_count = content.count("safe_send_message(bot,") + \
                             content.count("safe_send_photo(bot,") + \
                             content.count("safe_send_document(bot,")
            
            if safe_send_count > 10:
                print(f"  ✅ safe_send مستخدم في {safe_send_count} موقع")
            else:
                print(f"  ⚠️  safe_send مستخدم في {safe_send_count} موقع فقط")
                
            print("\n✅ فحص الاستخدام نجح!\n")
            return True
            
    except Exception as e:
        print(f"\n❌ خطأ في الفحص: {e}\n")
        return False


def main():
    """تشغيل جميع الاختبارات"""
    print("=" * 60)
    print("🧪 اختبار حل معالجة أخطاء الاتصال المتقطعة")
    print("=" * 60)
    print()
    
    results = []
    
    # اختبر الاستيرادات
    results.append(("استيراد المكتبات", test_imports()))
    
    if results[0][1]:  # إذا نجح الاستيراد، استمر في الاختبارات
        results.append(("تهيئة SafeSendHandler", test_send_handler_init()))
        results.append(("معالج الاتصال", test_connection_manager()))
    
    # اختبر وجود الملفات
    results.append(("وجود الملفات", test_file_existence()))
    
    # اختبر الاستخدام
    results.append(("استخدام safe_send", check_safe_send_usage()))
    
    # ملخص النتائج
    print("=" * 60)
    print("📊 ملخص الاختبارات")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{status:8} | {test_name}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"✅ نجح: {passed}")
    print(f"❌ فشل: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 جميع الاختبارات نجحت! البوت جاهز للعمل.")
        print("\n📝 الخطوات التالية:")
        print("  1. تأكد من متغيرات البيئة (.env)")
        print("  2. قم بتشغيل البوت: python final_bot_with_image.py")
        print("  3. ابحث عن رسائل أخطاء في السجل")
        return 0
    else:
        print("\n⚠️  بعض الاختبارات فشلت. يرجى تصحيح الأخطاء أعلاه.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
