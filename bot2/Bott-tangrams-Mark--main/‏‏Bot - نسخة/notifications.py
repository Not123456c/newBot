"""
وحدة الإشعارات التلقائية (تم تحديثها للعمل مع السحابة عبر Supabase)
تقوم بفحص قاعدة البيانات دورياً وإرسال تنبيهات في حال صدور نتائج جديدة للطلاب المشتركين
"""

from apscheduler.schedulers.background import BackgroundScheduler
import telebot

# متغير عام للـ supabase client
_supabase_client = None

def set_supabase_client(supabase):
    """تعيين عميل Supabase للاستخدام في الوحدة"""
    global _supabase_client
    _supabase_client = supabase

def migrate_old_json_files(supabase):
    import json
    import os
    # نقل الاشتراكات القديمة
    if os.path.exists("subscriptions.json"):
        try:
            with open("subscriptions.json", "r", encoding="utf-8") as f:
                subs = json.load(f)
                for chat_id, student_id in subs.items():
                    supabase.table("user_subscriptions").upsert({"chat_id": int(chat_id), "student_id": str(student_id)}).execute()
            os.remove("subscriptions.json")
        except Exception as e:
            print("Error migrating old subscriptions:", e)
            
    # نقل النتائج القديمة
    if os.path.exists("known_grades.json"):
        try:
            with open("known_grades.json", "r", encoding="utf-8") as f:
                grades = json.load(f)
                for student_id, grades_data in grades.items():
                    supabase.table("known_grades").upsert({"student_id": str(student_id), "grades_data": grades_data}).execute()
            os.remove("known_grades.json")
        except Exception as e:
            print("Error migrating old known_grades:", e)

def subscribe_user(chat_id, student_id, supabase=None):
    """ربط حساب تليجرام برقم جامعي محدد لتلقي الإشعارات (حفظ في قاعدة البيانات)"""
    global _supabase_client
    
    # استخدام الـ supabase الممرر أو العام
    db = supabase if supabase is not None else _supabase_client
    
    if db is None:
        print("⚠️ Warning: supabase client not available for subscribe_user")
        return
    
    try:
        db.table("user_subscriptions").upsert({
            "chat_id": chat_id,
            "student_id": str(student_id)
        }).execute()
    except Exception as e:
        print(f"Error subscribing user to DB: {e}")

def check_for_new_grades(bot: telebot.TeleBot, supabase):
    """فحص قاعدة البيانات بحثاً عن درجات جديدة"""
    try:
        # جلب جميع الاشتراكات
        subs_res = supabase.table("user_subscriptions").select("*").execute()
        if not subs_res.data:
            return
            
        subscriptions = {str(row['chat_id']): row['student_id'] for row in subs_res.data}
        student_ids = list(set(subscriptions.values()))
        
        # جلب درجات المعرفة مسبقاً
        known_res = supabase.table("known_grades").select("*").in_("student_id", student_ids).execute()
        known_grades = {row['student_id']: row['grades_data'] for row in known_res.data} if known_res.data else {}

    except Exception as e:
        print(f"Error fetching subs/known_grades from DB: {e}")
        return

    for sid in student_ids:
        try:
            # جلب النتيجة الحالية من قاعدة البيانات
            response = supabase.table("all_marks").select("*").eq("student_id", sid).execute()
            current_data = response.data

            if not current_data:
                continue

            # بناء قاموس بالمواد ودرجاتها الحالية (حتى نعرف ما هو الجديد)
            current_marks_dict = {}
            for m in current_data:
                subj_name = m.get('subject_name')
                if subj_name and m.get('total_grade') is not None:
                    current_marks_dict[subj_name] = m.get('total_grade')

            # الدرجات السابقة المعروفة لهذا الطالب
            known = known_grades.get(str(sid), {})

            new_subjects = []

            # مقارنة لمعرفة الدرجات الجديدة
            for subject, grade in current_marks_dict.items():
                if subject not in known:
                    new_subjects.append({'subject': subject, 'grade': grade})

            # إذا كان هناك مواد جديدة
            if new_subjects:
                # تحديث قاعدة البيانات
                supabase.table("known_grades").upsert({
                    "student_id": str(sid),
                    "grades_data": current_marks_dict
                }).execute()

                # البحث عن المشتركين وإرسال رسائل لهم
                for chat_id, sub_sid in subscriptions.items():
                    if sub_sid == sid:
                        for item in new_subjects:
                            msg = (
                                f"🎉 *بشرى سارة: نتيجة جديدة!* 🎓\n\n"
                                f"📌 المادة: `{item['subject']}`\n"
                                f"📊 الدرجة: `{item['grade']}`\n\n"
                                f"يمكنك عرض نتيجتك الكاملة بإرسال رقمك الجامعي أو الضغط على /start"
                            )
                            try:
                                bot.send_message(int(chat_id), msg, parse_mode="Markdown")
                            except Exception as e:
                                print(f"فشل الإرسال إلى {chat_id}: {e}")

        except Exception as e:
            print(f"Error checking grades for {sid}: {e}")

def start_notifications_scheduler(bot, supabase, interval_minutes=60):
    """بدء المشغل الزمني (Job Scheduler)"""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(check_for_new_grades, 'interval', minutes=interval_minutes, args=[bot, supabase])
    scheduler.start()
    print(f"⏱️ تم تشغيل نظام الإشعارات التلقائية (كل {interval_minutes} دقيقة).")
