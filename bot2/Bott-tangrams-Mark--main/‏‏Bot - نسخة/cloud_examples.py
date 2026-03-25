# -*- coding: utf-8 -*-
"""
مثال سريع: نظام التخزين السحابي في البوت
This is a quick start example for integrating the cloud database system
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# استيراد مديري قاعدة البيانات والتكامل
from cloud_database_manager import CloudDatabaseManager
from bot_cloud_integration import BotCloudIntegration

# ═══════════════════════════════════════════════════════════════════
# الإعدادات
# ═══════════════════════════════════════════════════════════════════

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# ═══════════════════════════════════════════════════════════════════
# التهيئة
# ═══════════════════════════════════════════════════════════════════

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
cloud_db = CloudDatabaseManager(supabase)
bot_integration = BotCloudIntegration(supabase)


# ═══════════════════════════════════════════════════════════════════
# أمثلة الاستخدام الأساسية
# ═══════════════════════════════════════════════════════════════════

def example_1_add_user():
    """مثال 1: إضافة مستخدم جديد"""
    print("\n📌 مثال 1: إضافة مستخدم جديد")
    print("=" * 60)
    
    chat_id = 123456789
    result = cloud_db.add_user(chat_id)
    
    print(f"الإجراء: إضافة مستخدم {chat_id}")
    print(f"النتيجة: {result}")
    
    if result["success"]:
        print("✅ تم إضافة المستخدم بنجاح")
    else:
        print(f"ℹ️ {result['message']}")


def example_2_subscribe_user():
    """مثال 2: ربط مستخدم برقم طالب"""
    print("\n📌 مثال 2: الاشتراك برقم طالب")
    print("=" * 60)
    
    chat_id = 123456789
    student_id = "220450"
    
    result = cloud_db.subscribe_user(chat_id, student_id)
    
    print(f"الإجراء: ربط المستخدم {chat_id} بالطالب {student_id}")
    print(f"النتيجة: {result}")
    
    if result["success"]:
        print("✅ تم الاشتراك بنجاح")


def example_3_get_subscription():
    """مثال 3: الحصول على اشتراك المستخدم"""
    print("\n📌 مثال 3: الحصول على اشتراك المستخدم")
    print("=" * 60)
    
    chat_id = 123456789
    result = cloud_db.get_subscription(chat_id)
    
    print(f"الإجراء: البحث عن اشتراك المستخدم {chat_id}")
    
    if result["success"] and result["subscription"]:
        print(f"✅ المستخدم مشترك برقم الطالب: {result['student_id']}")
    else:
        print("❌ المستخدم غير مشترك")


def example_4_add_grade():
    """مثال 4: إضافة درجة طالب"""
    print("\n📌 مثال 4: إضافة درجة طالب")
    print("=" * 60)
    
    result = cloud_db.add_grade(
        student_id="220450",
        student_name="محمد أحمد",
        father_name="أحمد علي",
        subject_name="الرياضيات",
        practical_grade=45,
        theoretical_grade=85,
        total_grade=130,
        grade_in_words="جيد جداً",
        result="نجح"
    )
    
    print(f"الإجراء: إضافة درجة الرياضيات للطالب 220450")
    print(f"النتيجة: {result}")
    
    if result["success"]:
        print("✅ تم إضافة الدرجة بنجاح")


def example_5_get_grades():
    """مثال 5: الحصول على درجات طالب"""
    print("\n📌 مثال 5: الحصول على درجات طالب")
    print("=" * 60)
    
    student_id = "220450"
    result = cloud_db.get_student_grades(student_id)
    
    print(f"الإجراء: البحث عن درجات الطالب {student_id}")
    
    if result["success"] and result["grades"]:
        print(f"✅ وجدنا {result['count']} درجة:")
        for grade in result["grades"]:
            subject = grade.get("subject_name", "مادة")
            total = grade.get("total_grade", 0)
            result_text = grade.get("result", "")
            print(f"   - {subject}: {total} ({result_text})")
    else:
        print("❌ لا توجد درجات للطالب")


def example_6_get_statistics():
    """مثال 6: الحصول على إحصائيات النظام"""
    print("\n📌 مثال 6: إحصائيات النظام")
    print("=" * 60)
    
    result = cloud_db.get_statistics()
    
    if result["success"]:
        print(f"👥 المستخدمين: {result['total_users']}")
        print(f"🔗 الاشتراكات: {result['total_subscriptions']}")
        print(f"📚 الدرجات: {result['total_grades']}")
        print(f"👨‍🎓 الطلاب: {result['total_students']}")
    else:
        print(f"❌ خطأ: {result['error']}")


def example_7_bot_integration():
    """مثال 7: استخدام تكامل البوت"""
    print("\n📌 مثال 7: استخدام تكامل البوت")
    print("=" * 60)
    
    chat_id = 123456789
    
    # مرحبة بمستخدم جديد
    response = bot_integration.handle_new_user(chat_id)
    print(f"رسالة الترحيب: {response}")
    
    # الاشتراك
    response = bot_integration.handle_subscription(chat_id, "220450")
    print(f"رسالة الاشتراك: {response}")
    
    # رسالة الدرجات
    response = bot_integration.format_grades_message(chat_id)
    print(f"رسالة الدرجات:\n{response}")


def example_8_known_grades():
    """مثال 8: حفظ الدرجات المعروفة (JSON)"""
    print("\n📌 مثال 8: حفظ الدرجات المعروفة")
    print("=" * 60)
    
    student_id = "220450"
    grades_data = {
        "الرياضيات": {"عملي": 45, "نظري": 85, "مجموع": 130},
        "العلوم": {"عملي": 50, "نظري": 90, "مجموع": 140},
        "اللغة الإنجليزية": {"عملي": 40, "نظري": 80, "مجموع": 120}
    }
    
    result = cloud_db.save_known_grades(student_id, grades_data)
    print(f"الإجراء: حفظ درجات معروفة للطالب {student_id}")
    
    if result["success"]:
        print("✅ تم حفظ الدرجات بنجاح")
        
        # الحصول على الدرجات المحفوظة
        retrieved = cloud_db.get_known_grades(student_id)
        if retrieved["success"]:
            print(f"الدرجات المحفوظة: {retrieved['grades_data']}")


def example_9_all_students():
    """مثال 9: الحصول على جميع الطلاب"""
    print("\n📌 مثال 9: الحصول على جميع الطلاب")
    print("=" * 60)
    
    result = cloud_db.get_all_students()
    
    if result["success"] and result["students"]:
        print(f"✅ وجدنا {result['count']} طالب:")
        for student_id, student_name in list(result["students"].items())[:5]:
            print(f"   - {student_id}: {student_name}")
        
        if result['count'] > 5:
            print(f"   ... و {result['count'] - 5} طالب آخر")
    else:
        print("❌ لا توجد بيانات طلاب")


def example_10_update_grade():
    """مثال 10: تحديث درجة موجودة"""
    print("\n📌 مثال 10: تحديث درجة موجودة")
    print("=" * 60)
    
    result = cloud_db.update_grade(
        student_id="220450",
        subject_name="الرياضيات",
        practical_grade=50,
        theoretical_grade=90,
        total_grade=140,
        grade_in_words="ممتاز",
        result="نجح"
    )
    
    print(f"الإجراء: تحديث درجة الرياضيات")
    print(f"النتيجة: {result}")


# ═══════════════════════════════════════════════════════════════════
# تشغيل الأمثلة
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 أمثلة نظام التخزين السحابي")
    print("=" * 60)
    
    try:
        # اختبر الاتصال أولاً
        print("\n🔍 اختبار الاتصال بـ Supabase...")
        stats = cloud_db.get_statistics()
        if stats["success"]:
            print("✅ الاتصال ناجح!")
        else:
            print("❌ فشل الاتصال!")
            exit(1)
        
        # تشغيل الأمثلة
        example_1_add_user()
        example_2_subscribe_user()
        example_3_get_subscription()
        example_4_add_grade()
        example_5_get_grades()
        example_6_get_statistics()
        example_7_bot_integration()
        example_8_known_grades()
        example_9_all_students()
        example_10_update_grade()
        
        print("\n" + "=" * 60)
        print("✅ تم تنفيذ جميع الأمثلة بنجاح!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
