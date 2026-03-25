# -*- coding: utf-8 -*-
"""
مثال على استخدام نظام التخزين السحابي الكامل
يوضح كيفية دمج مدير قاعدة البيانات السحابية في البوت
"""

from cloud_database_manager import CloudDatabaseManager
from supabase import Client


class BotCloudIntegration:
    """تكامل البوت مع قاعدة البيانات السحابية"""
    
    def __init__(self, supabase: Client):
        """
        Args:
            supabase: عميل Supabase
        """
        self.db = CloudDatabaseManager(supabase)
    
    # ==================================================================
    # العمليات الأساسية للمستخدمين
    # ==================================================================
    
    def handle_new_user(self, chat_id: int) -> str:
        """معالجة مستخدم جديد"""
        result = self.db.add_user(chat_id)
        if result["success"]:
            return f"✅ مرحباً! تم تسجيلك في النظام. معرفك: {chat_id}"
        else:
            return "ℹ️ أنت مسجل بالفعل في النظام"
    
    def handle_subscription(self, chat_id: int, student_id: str) -> str:
        """معالجة اشتراك المستخدم بطالب"""
        # تحقق من أن المستخدم موجود
        user = self.db.get_user(chat_id)
        if not user["success"] or not user["exists"]:
            # أضف المستخدم إذا لم يكن موجوداً
            self.db.add_user(chat_id)
        
        # ربط الطالب
        result = self.db.subscribe_user(chat_id, student_id)
        if result["success"]:
            return f"✅ {result['message']}"
        else:
            return f"❌ خطأ: {result['error']}"
    
    def get_user_student(self, chat_id: int) -> dict:
        """الحصول على الطالب المرتبط بالمستخدم"""
        result = self.db.get_subscription(chat_id)
        if result["success"] and result["subscription"]:
            return {
                "success": True,
                "student_id": result["student_id"]
            }
        return {"success": False, "student_id": None}
    
    # ==================================================================
    # الحصول على درجات الطالب
    # ==================================================================
    
    def get_user_grades(self, chat_id: int) -> dict:
        """الحصول على درجات الطالب المرتبط بالمستخدم"""
        # احصل على الطالب المرتبط
        subscription = self.db.get_subscription(chat_id)
        if not subscription["success"] or not subscription["subscription"]:
            return {
                "success": False,
                "message": "أنت لم تشترك برقم طالب بعد"
            }
        
        student_id = subscription["student_id"]
        
        # احصل على الدرجات
        result = self.db.get_student_grades(student_id)
        if result["success"]:
            return {
                "success": True,
                "student_id": student_id,
                "grades": result["grades"],
                "count": result["count"]
            }
        else:
            return {
                "success": False,
                "message": f"خطأ: {result['error']}"
            }
    
    # ==================================================================
    # الإخطارات والتنبيهات
    # ==================================================================
    
    def get_users_for_student(self, student_id: str) -> list:
        """الحصول على جميع المستخدمين المشتركين لطالب (للإخطارات)"""
        result = self.db.get_subscriptions_for_student(student_id)
        return result.get("users", []) if result["success"] else []
    
    def notify_grade_update(self, student_id: str) -> dict:
        """إخطار جميع مستخدمي الطالب عند تحديث الدرجات"""
        users = self.get_users_for_student(student_id)
        
        return {
            "success": True,
            "student_id": student_id,
            "affected_users": users,
            "user_count": len(users)
        }
    
    # ==================================================================
    # عمليات المسؤول
    # ==================================================================
    
    def admin_get_statistics(self) -> dict:
        """الحصول على الإحصائيات (للمسؤولين فقط)"""
        return self.db.get_statistics()
    
    def admin_get_top_students(self, limit: int = 10) -> dict:
        """الحصول على أفضل الطلاب (للمسؤولين)"""
        try:
            # استعلام من جدول all_marks مع ترتيب حسب المجموع
            from supabase import Client
            
            response = self.db.supabase.table("all_marks").select(
                "student_id, student_name, total_grade"
            ).order("total_grade", desc=True).limit(limit).execute()
            
            return {
                "success": True,
                "students": response.data,
                "count": len(response.data)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def admin_update_grade(self, student_id: str, subject_name: str,
                          practical_grade: int, theoretical_grade: int,
                          grade_in_words: str, result: str) -> dict:
        """تحديث درجة طالب (للمسؤولين)"""
        total_grade = practical_grade + theoretical_grade
        
        result_obj = self.db.update_grade(
            student_id, subject_name,
            practical_grade, theoretical_grade,
            total_grade, grade_in_words, result
        )
        
        if result_obj["success"]:
            # إخطار المستخدمين
            self.notify_grade_update(student_id)
        
        return result_obj
    
    # ==================================================================
    # خدمات المساعدة
    # ==================================================================
    
    def format_grades_message(self, chat_id: int) -> str:
        """تنسيق رسالة الدرجات للمستخدم"""
        grades_result = self.get_user_grades(chat_id)
        
        if not grades_result["success"]:
            return f"❌ {grades_result['message']}"
        
        grades = grades_result["grades"]
        if not grades:
            return "📊 لا توجد درجات حالياً"
        
        message = f"📊 درجات الطالب {grades_result['student_id']}:\n\n"
        
        total_practical = 0
        total_theoretical = 0
        count = 0
        
        for grade in grades:
            practical = grade.get("practical_grade", 0) or 0
            theoretical = grade.get("theoretical_grade", 0) or 0
            total = grade.get("total_grade", 0) or 0
            subject = grade.get("subject_name", "مادة")
            result = grade.get("result", "")
            
            message += f"📌 {subject}\n"
            message += f"   عملي: {practical} | نظري: {theoretical} | المجموع: {total} {result}\n"
            
            total_practical += practical
            total_theoretical += theoretical
            count += 1
        
        if count > 0:
            message += f"\n📈 المتوسط العام:\n"
            message += f"متوسط العملي: {total_practical/count:.1f}\n"
            message += f"متوسط النظري: {total_theoretical/count:.1f}\n"
        
        return message
    
    def get_database_info(self) -> str:
        """الحصول على معلومات قاعدة البيانات"""
        stats = self.admin_get_statistics()
        
        if not stats["success"]:
            return f"❌ خطأ: {stats['error']}"
        
        message = "📊 إحصائيات النظام:\n\n"
        message += f"👥 المستخدمين: {stats['total_users']}\n"
        message += f"🔗 الاشتراكات: {stats['total_subscriptions']}\n"
        message += f"📚 الدرجات: {stats['total_grades']}\n"
        message += f"👨‍🎓 الطلاب: {stats['total_students']}\n"
        
        return message


# ==============================================================================
# أمثلة الاستخدام في البوت الرئيسي
# ==============================================================================

"""
# في ملف البوت الرئيسي (final_bot_with_image.py)

from cloud_database_manager import CloudDatabaseManager
from bot_cloud_integration import BotCloudIntegration

# الإعدادات
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
cloud_db = CloudDatabaseManager(supabase)
bot_integration = BotCloudIntegration(supabase)

# عند استقبال رسالة /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    response = bot_integration.handle_new_user(chat_id)
    bot.send_message(chat_id, response)

# عند الاشتراك برقم طالب
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

# الحصول على الدرجات
@bot.message_handler(commands=['grades'])
def handle_grades(message):
    chat_id = message.chat.id
    response = bot_integration.format_grades_message(chat_id)
    bot.send_message(chat_id, response)

# إحصائيات النظام (للمسؤولين فقط)
@bot.message_handler(commands=['stats'])
def handle_stats(message):
    chat_id = message.chat.id
    
    if chat_id not in ADMIN_IDS:
        bot.send_message(chat_id, "❌ ليست لديك صلاحيات")
        return
    
    response = bot_integration.get_database_info()
    bot.send_message(chat_id, response)
"""
