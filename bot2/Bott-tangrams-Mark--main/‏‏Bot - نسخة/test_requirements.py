#!/usr/bin/env python3
"""
برنامج اختبار المكتبات والإعدادات
تحقق من أن كل شيء جاهز للتشغيل
"""

import sys
import importlib

def test_import(module_name):
    """اختبار استيراد مكتبة"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {module_name} - OK")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - FAILED: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 اختبار البيئة والمكتبات")
    print("=" * 60)
    print()
    
    # المكتبات الأساسية
    required_modules = [
        ('telebot', 'pyTelegramBotAPI'),
        ('supabase', 'supabase-py'),
        ('PIL', 'Pillow'),
        ('matplotlib', 'matplotlib'),
        ('reportlab', 'reportlab'),
        ('arabic_reshaper', 'arabic-reshaper'),
        ('bidi', 'python-bidi')
    ]
    
    print("📦 اختبار المكتبات المطلوبة:")
    print("-" * 60)
    
    all_passed = True
    for module_import, module_display in required_modules:
        if not test_import(module_import):
            all_passed = False
    
    print()
    print("-" * 60)
    
    # اختبار الملفات المحلية
    print()
    print("📁 اختبار الملفات المحلية:")
    print("-" * 60)
    
    local_modules = [
        'image_generator',
        'analytics',
        'ratings',
        'recommendations',
        'charts',
        'alerts_system',
        'reports'
    ]
    
    for module in local_modules:
        if not test_import(module):
            all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ جميع المكتبات والملفات موجودة وجاهزة!")
        print("🚀 يمكنك البدء بتشغيل: python final_bot_with_image.py")
        return 0
    else:
        print("❌ هناك مشاكل في المكتبات")
        print("💡 الحل:")
        print("   pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
