# -*- coding: utf-8 -*-
import sys
import io
import os
from dotenv import load_dotenv
from datetime import datetime
import datetime as datetime_module
import time
import traceback

# تحميل متغيرات البيئة أولاً (قبل أي استيراد آخر)
load_dotenv()

# حل مشاكل الترميز على Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import telebot
from telebot import types
from supabase import create_client
import re
import os
from image_generator import generate_result_image, generate_top_students_image
from analytics import calculate_statistics, calculate_statistics_fast, analyze_performance, get_top_10_students
from ratings import get_rating, format_grade_display
from recommendations import generate_recommendations, get_motivation_message
from charts import (create_grades_chart, create_theoretical_practical_chart, 
                    create_performance_pie_chart, create_statistics_summary_image,
                    create_grade_distribution_chart, create_subjects_performance_chart)
from alerts_system import generate_alerts, format_alerts_message
from reports import generate_pdf_report, create_simple_text_report
from admin import get_system_stats, get_admin_info, format_admin_message, get_recent_errors, generate_excel_backup, get_top_10_students, get_all_subjects, get_top_10_in_subject, get_top_n_students
from cohort_analytics import (get_cohort_analytics, get_grade_distribution, 
                              get_subjects_performance, get_at_risk_students,
                              get_borderline_students, get_incomplete_students,
                              format_cohort_message, format_grade_distribution_message,
                              format_subjects_performance_message, format_at_risk_message,
                              format_borderline_message, format_incomplete_message)
from ai_service import ai_service
from notifications import subscribe_user, start_notifications_scheduler
from backup_scheduler import initialize_backup_scheduler
from storage_manager import SupabaseStorageManager
from spam_protection import SpamProtection
from connection_manager import configure_polling_with_safety, safe_db_operation
from cache_manager import cache, get_cached_top_students, start_cache_cleanup
from task_manager import task_manager, generate_image_async
from instant_notifications import InstantNotificationSystem, setup_notification_commands
from exam_schedule import ExamScheduleSystem, setup_exam_commands
from usage_analytics import UsageAnalytics, setup_analytics_commands, AnalyticsMiddleware
import json

# ══════════════════════════════════════
#  إعدادات
# ══════════════════════════════════════
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
USERS_FILE   = "users.json"


def parse_admin_ids(raw_admin_ids):
    admin_ids = []
    for value in raw_admin_ids.split(","):
        cleaned = value.strip()
        if not cleaned:
            continue
        try:
            admin_ids.append(int(cleaned))
        except ValueError:
            print(f"Warning: invalid ADMIN_IDS value ignored: {cleaned}")
    return admin_ids


def validate_required_settings():
    missing_vars = []
    if not BOT_TOKEN:
        missing_vars.append("BOT_TOKEN")
    if not SUPABASE_URL:
        missing_vars.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing_vars.append("SUPABASE_KEY")

    if missing_vars:
        missing_text = ", ".join(missing_vars)
        raise RuntimeError(
            f"Missing required environment variables: {missing_text}. "
            "Set them in .env before running the bot."
        )


ADMIN_IDS = parse_admin_ids(os.environ.get("ADMIN_IDS", ""))

# ══════════════════════════════════════
# إعدادات قناة البوت والاشتراك
# ══════════════════════════════════════
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@bot_channel")  # حدد اسم قناة البوت الخاص بك
CHANNEL_LINK = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
REQUIRE_CHANNEL_SUBSCRIPTION = os.environ.get("REQUIRE_CHANNEL_SUBSCRIPTION", "false").lower() == "true"

# ══════════════════════════════════════
validate_required_settings()
bot = telebot.TeleBot(BOT_TOKEN)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# تهيئة نظام الحماية من الطلبات المتتالية
spam_protection = SpamProtection(supabase)

# تهيئة وحدة الإشعارات مع supabase
from notifications import set_supabase_client
set_supabase_client(supabase)

# بدء جدولة النسخ الاحتياطي التلقائي
# ⚠️ تعطيل مؤقتاً - bucket "bot-storage" غير موجود في Supabase
# print("🔄 جاري تشغيل النسخ الاحتياطي التلقائي...")
# backup_scheduler = initialize_backup_scheduler(supabase, backup_interval_hours=24)
backup_scheduler = None

# بدء تنظيف الـ Cache دورياً
start_cache_cleanup(interval_minutes=10)

# ══════════════════════════════════════
# تهيئة الأنظمة الجديدة
# ══════════════════════════════════════

# نظام الإشعارات الفورية (/notify)
instant_notify = InstantNotificationSystem(
    bot=bot,
    supabase=supabase,
    channel_username=CHANNEL_USERNAME
)
instant_notify.start(check_interval=60)  # فحص كل دقيقة

# إعداد أوامر الإشعارات
setup_notification_commands(bot, instant_notify)

# نظام جدول الامتحانات
exam_system = ExamScheduleSystem(
    bot=bot,
    supabase=supabase,
    admin_ids=ADMIN_IDS
)
exam_system.start()  # بدء نظام التذكيرات

# إعداد أوامر الامتحانات
setup_exam_commands(bot, exam_system, ADMIN_IDS)

# نظام إحصائيات الاستخدام
usage_analytics = UsageAnalytics(supabase)
analytics_middleware = AnalyticsMiddleware(usage_analytics)

# إعداد أوامر الإحصائيات
setup_analytics_commands(bot, usage_analytics, ADMIN_IDS)

print("✅ تم تفعيل: الإشعارات الفورية + جدول الامتحانات + إحصائيات الاستخدام")

# ══════════════════════════════════════
# تعيين قائمة أوامر البوت (Bot Menu)
# ══════════════════════════════════════
def setup_bot_commands():
    """تعيين قائمة الأوامر التي تظهر في قائمة البوت"""
    try:
        from telebot.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
        
        # أوامر المستخدمين العاديين
        user_commands = [
            BotCommand("start", "🏠 البدء والقائمة الرئيسية"),
            BotCommand("help", "📖 دليل استخدام البوت"),
            BotCommand("app", "📱 فتح التطبيق المصغر"),
            BotCommand("top", "🏆 عرض أفضل 3 طلاب"),
            BotCommand("notify", "🔔 تفعيل الإشعارات الفورية"),
            BotCommand("notify_status", "📊 حالة اشتراكك في الإشعارات"),
            BotCommand("exams", "📅 عرض جدول الامتحانات"),
            BotCommand("exam_remind", "⏰ تفعيل تذكيرات الامتحانات"),
            BotCommand("exam_unremind", "🔕 إلغاء تذكيرات الامتحانات"),
            BotCommand("analyze", "🔍 تحليل ذكي لنقاط ضعفك"),
            BotCommand("plan", "📚 خطة دراسة مخصصة لك"),
            BotCommand("ask", "🤖 اسأل أي سؤال أكاديمي"),
        ]
        
        # تعيين الأوامر الافتراضية لجميع المستخدمين
        bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
        
        # أوامر إضافية للمشرفين
        admin_commands = user_commands + [
            BotCommand("admin", "👨‍💼 لوحة تحكم الإدارة"),
            BotCommand("backup", "💾 نسخ احتياطي فوري"),
            BotCommand("backup_status", "📊 حالة النسخ الاحتياطي"),
            BotCommand("upload", "📤 رفع ملفات"),
            BotCommand("add_exam", "➕ إضافة امتحان جديد"),
        ]
        
        # تعيين الأوامر للمشرفين
        for admin_id in ADMIN_IDS:
            try:
                bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(admin_id))
            except Exception as e:
                print(f"⚠️ تعذر تعيين أوامر للمشرف {admin_id}: {e}")
        
        print("✅ تم تعيين قائمة أوامر البوت بنجاح")
        
    except Exception as e:
        print(f"⚠️ خطأ في تعيين أوامر البوت: {e}")

# تنفيذ تعيين الأوامر
setup_bot_commands()

# قائمة المستخدمين
bot_users = set()
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, 'r') as f:
            bot_users = set(json.load(f))
    except Exception as e:
        print(f"Error loading users from {USERS_FILE}: {e}")

def save_user(chat_id):
    """تسجيل المستخدم في النظام والقاعدة البيانات"""
    if chat_id not in bot_users:
        bot_users.add(chat_id)
        try:
            with open(USERS_FILE, 'w') as f:
                json.dump(list(bot_users), f)
        except Exception as e:
            print(f"Error saving user: {e}")
    
    # 🔴 أهم خطوة: تسجيل في bot_users قبل أي عملية أخرى
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = supabase.table("bot_users").select("chat_id").eq(
                "chat_id", chat_id
            ).execute()
            
            # إذا لم يكن مسجل، سجله
            if not response.data:
                try:
                    supabase.table("bot_users").insert({
                        "chat_id": chat_id,
                        "created_at": datetime.now().isoformat()
                    }).execute()
                    print(f"✅ تم تسجيل المستخدم {chat_id} في bot_users")
                except Exception as insert_error:
                    # قد يكون المستخدم موجود بالفعل (race condition)
                    if "duplicate" not in str(insert_error).lower():
                        print(f"⚠️ خطأ في إدراج المستخدم: {insert_error}")
                    retry_count += 1
                    if retry_count < max_retries:
                        continue
            break
        except Exception as e:
            print(f"⚠️ خطأ في التحقق من وجود المستخدم: {e}")
            retry_count += 1
            if retry_count < max_retries:
                continue

def check_channel_subscription_telegram(chat_id: int) -> bool:
    """
    التحقق من اشتراك المستخدم في القناة مباشرة من Telegram
    البوت يجب أن يكون ADMIN في القناة
    """
    if not REQUIRE_CHANNEL_SUBSCRIPTION:
        return True
    
    try:
        # تجربة طرق مختلفة للوصول للقناة
        channel_attempts = [
            f"@{CHANNEL_USERNAME.lstrip('@')}",  # مع @ (الأساسي)
            CHANNEL_USERNAME,  # بدون @ 
            CHANNEL_USERNAME.lstrip('@'),  # بدون @ نظيف
        ]
        
        member = None
        successful_channel = None
        
        for channel_name in channel_attempts:
            try:
                member = bot.get_chat_member(channel_name, chat_id)
                successful_channel = channel_name
                print(f"✅ نجح الفحص مع: {channel_name}")
                break
            except Exception as e:
                print(f"⚠️ فشل مع {channel_name}: {e}")
                continue
        
        if member is None:
            print(f"❌ لم نتمكن من الوصول للقناة. تحقق من CHANNEL_USERNAME={CHANNEL_USERNAME}")
            return False
        
        # الحالات المقبولة
        status = member.status
        
        if status in ["member", "administrator", "creator"]:
            # المستخدم مشترك ✅
            print(f"✅ {chat_id} مشترك حقاً (status: {status})")
            try:
                # تأكد أن المستخدم موجود في bot_users أولاً
                response = supabase.table("bot_users").select("chat_id").eq(
                    "chat_id", chat_id
                ).execute()
                
                if response.data:
                    # فقط حاول تحديث إذا كان موجود
                    try:
                        supabase.table("channel_subscriptions").update({
                            "chat_id": chat_id,
                            "is_subscribed": True,
                            "subscription_date": datetime.now().isoformat()
                        }).eq("chat_id", chat_id).execute()
                        print(f"✅ تم تحديث قاعدة البيانات: {chat_id} مشترك")
                    except Exception as upsert_error:
                        print(f"⚠️ Database update (non-critical): {upsert_error}")
            except Exception as check_error:
                print(f"⚠️ خطأ في التحقق من وجود المستخدم: {check_error}")
            
            return True
        else:
            # المستخدم غير مشترك ❌
            print(f"❌ {chat_id} غير مشترك (status: {status} - ترك القناة أو لم يشترك)")
            
            # 🔴 أهم خطوة: تحديث قاعدة البيانات بالحالة الحقيقية
            try:
                response = supabase.table("bot_users").select("chat_id").eq(
                    "chat_id", chat_id
                ).execute()
                
                if response.data:
                    # تحديث حالة الاشتراك لتعكس الحقيقة
                    try:
                        supabase.table("channel_subscriptions").update({
                            "chat_id": chat_id,
                            "is_subscribed": False,
                            "subscription_date": None,
                            "last_reminder": datetime.now().isoformat()
                        }).eq("chat_id", chat_id).execute()
                        print(f"✅ تم تحديث قاعدة البيانات: {chat_id} غير مشترك")
                    except Exception as update_error:
                        # إذا كان السجل غير موجود، أنشئه
                        if "duplicate" not in str(update_error).lower():
                            try:
                                supabase.table("channel_subscriptions").insert({
                                    "chat_id": chat_id,
                                    "is_subscribed": False,
                                    "reminder_count": 0,
                                    "last_reminder": datetime.now().isoformat()
                                }).execute()
                                print(f"ℹ️ تم إنشاء سجل جديد: {chat_id} غير مشترك")
                            except Exception as insert_error:
                                print(f"⚠️ خطأ في إنشاء السجل: {insert_error}")
            except Exception as check_error:
                print(f"⚠️ خطأ في التحقق من وجود المستخدم: {check_error}")
            
            return False
            
    except Exception as e:
        print(f"❌ خطأ في فحص عضوية Telegram: {e}")
        return False

def check_channel_subscription(chat_id: int) -> bool:
    """
    التحقق من اشتراك المستخدم في قناة البوت
    الأولوية: Telegram API (الحقيقة المطلقة)
    """
    if not REQUIRE_CHANNEL_SUBSCRIPTION:
        return True
    
    try:
        # 🔴 الخطوة الأولى: تأكد أن المستخدم مسجل في bot_users أولاً
        user_exists = False
        try:
            response = supabase.table("bot_users").select("chat_id").eq(
                "chat_id", chat_id
            ).execute()
            
            if response.data:
                user_exists = True
            else:
                # سجل المستخدم إذا لم يكن موجود
                print(f"ℹ️ تسجيل مستخدم جديد: {chat_id}")
                try:
                    supabase.table("bot_users").insert({
                        "chat_id": chat_id,
                        "created_at": datetime.now().isoformat()
                    }).execute()
                    user_exists = True
                except Exception as insert_error:
                    if "duplicate" in str(insert_error).lower():
                        user_exists = True
                    else:
                        print(f"⚠️ خطأ في تسجيل المستخدم: {insert_error}")
        except Exception as reg_error:
            print(f"⚠️ خطأ في التحقق من وجود المستخدم: {reg_error}")
        
        if not user_exists:
            print(f"❌ لم نتمكن من تسجيل المستخدم {chat_id}")
            return False
        
        # 🟢 الخطوة الثانية: جرب فحص Telegram API أولاً (هذا هو الحقيقة)
        result_telegram = check_channel_subscription_telegram(chat_id)
        
        # ✅ إذا نجح Telegram، لا نحتاج لفحص DB
        if result_telegram:
            print(f"✅ تم التحقق من {chat_id} مباشرة من Telegram: مشترك ✓")
            return True
        
        # ❌ إذا أظهر Telegram أنه غير مشترك، هذه هي الحقيقة
        # لا نستخدم DB كـ backup لأن البيانات قد تكون متقادمة
        print(f"❌ تم التحقق من {chat_id} مباشرة من Telegram: غير مشترك ✗")
        return False
        
    except Exception as e:
        print(f"❌ خطأ في check_channel_subscription: {e}")
        import traceback
        traceback.print_exc()
        return False  # للأمان: لا نسمح عند الشك

def update_channel_reminder(chat_id: int):
    """تحديث عداد التذكيرات"""
    try:
        # تأكد أن المستخدم موجود في bot_users أولاً
        response = supabase.table("bot_users").select("chat_id").eq(
            "chat_id", chat_id
        ).execute()
        
        if not response.data:
            print(f"⚠️ المستخدم {chat_id} غير موجود في bot_users")
            return
        
        # تحقق من وجود سجل الاشتراك
        response = supabase.table("channel_subscriptions").select(
            "reminder_count"
        ).eq("chat_id", chat_id).execute()
        
        if response.data:
            current_count = response.data[0].get("reminder_count", 0)
            try:
                supabase.table("channel_subscriptions").update({
                    "reminder_count": current_count + 1,
                    "last_reminder": datetime.now().isoformat()
                }).eq("chat_id", chat_id).execute()
            except Exception as update_error:
                print(f"⚠️ خطأ في تحديث التذكيرات: {update_error}")
        else:
            # إنشاء سجل جديد إذا لم يكن موجود
            try:
                supabase.table("channel_subscriptions").insert({
                    "chat_id": chat_id,
                    "is_subscribed": False,
                    "reminder_count": 1,
                    "last_reminder": datetime.now().isoformat()
                }).execute()
            except Exception as insert_error:
                print(f"⚠️ خطأ في إنشاء سجل تذكير جديد: {insert_error}")
    except Exception as e:
        print(f"⚠️ خطأ في update_channel_reminder: {e}")

def convert_arabic_digits(text):
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    western_digits = '0123456789'
    table = str.maketrans(arabic_digits, western_digits)
    return str(text).translate(table)

# ══════════════════════════════════════
# Mini App Integration
# ══════════════════════════════════════

MINI_APP_URL = os.environ.get("MINI_APP_URL", "")

@bot.message_handler(commands=['app', 'webapp', 'miniapp'])
def open_mini_app(message):
    """فتح Mini App داخل Telegram"""
    if not MINI_APP_URL:
        bot.send_message(
            message.chat.id,
            "⚠️ تطبيق Mini App غير مُعد حالياً.\n"
            "تواصل مع المسؤول لتفعيله.",
            parse_mode="Markdown"
        )
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="📱 فتح التطبيق",
            web_app=types.WebAppInfo(url=MINI_APP_URL)
        )
    )
    markup.add(
        types.InlineKeyboardButton(
            text="❓ ما هو Mini App؟",
            callback_data="miniapp_info"
        )
    )
    
    bot.send_message(
        message.chat.id,
        "🎓 *تطبيق النتائج الجامعية*\n\n"
        "📱 واجهة جميلة وسهلة لعرض نتائجك!\n\n"
        "✨ *المميزات:*\n"
        "• عرض جميع النتائج والدرجات\n"
        "• إحصائيات شاملة ورسوم بيانية\n"
        "• قائمة الأوائل\n"
        "• جدول الامتحانات\n"
        "• مشاركة النتائج\n\n"
        "👇 اضغط الزر لفتح التطبيق:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "miniapp_info")
def miniapp_info_callback(call):
    """معلومات عن Mini App"""
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📱 *ما هو Mini App؟*\n\n"
        "هو تطبيق ويب صغير يعمل داخل Telegram مباشرة!\n\n"
        "🎯 *لماذا استخدمه؟*\n"
        "• واجهة أجمل وأسهل\n"
        "• رسوم بيانية تفاعلية\n"
        "• تجربة مستخدم أفضل\n"
        "• ربط حسابك مرة واحدة فقط\n\n"
        "💡 جرّب الآن! أرسل /app",
        parse_mode="Markdown"
    )

def send_student_result(chat_id, student_id):
    try:
        response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
        if not response.data:
            bot.send_message(chat_id, "⚠️ لا توجد نتائج مسجلة لهذا الرقم حالياً.")
            return

        data = response.data
        name = data[0].get('student_name', 'غير معروف')
        father = data[0].get('father_name', '')
        
        # حساب المعدل والإحصائيات
        total_sum = 0
        subjects_count = 0
        marks_summary = ""
        
        for m in data:
            if m.get('total_grade'):
                total_sum += m['total_grade']
                subjects_count += 1
            
            subj = m.get('subject_name', 'غير محدد')
            grade = m.get('total_grade', '—')
            marks_summary += f"▫️ {subj}: *{grade}*\n"
            
        average = round(total_sum / subjects_count, 1) if subjects_count > 0 else 0

        # 🚀 استخدام Cache للإحصائيات (أسرع)
        stats = calculate_statistics_fast(student_id, supabase)
        analysis = analyze_performance(data)
        
        # إنشاء نص الكابشن
        caption_text = (
            f"✅ *نتيجة الطالب:* {name} {father}\n"
            f"📍 *الرقم الامتحاني:* `{student_id}`\n"
            f"📊 *المعدل العام:* `{average}`\n"
            f"📈 *المستوى:* {analysis['performance_level']}\n"
            f"✔️ *نسبة النجاح:* {stats.get('success_rate', 0)}%\n"
            f"─────────────────\n"
            f"{marks_summary}\n"
            f"🤖 تم التوليد بواسطة بوت النتائج"
        )

        # توليد الصورة
        bot.send_chat_action(chat_id, "upload_photo")
        image_path = generate_result_image(student_id, name, father, data, average)
        
        # إرسال الصورة مع النص التفصيلي
        with open(image_path, 'rb') as photo:
            bot.send_photo(
                chat_id, 
                photo, 
                caption=caption_text,
                parse_mode="Markdown"
            )
        
        # حذف الصورة
        if os.path.exists(image_path):
            os.remove(image_path)
        # تسجيل الطالب في نظام الإشعارات
        subscribe_user(chat_id, student_id, supabase)
        
        # إنشاء لوحة المفاتيح مع الخيارات الإضافية
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📊 إحصائيات", callback_data=f"stats_{student_id}"),
            types.InlineKeyboardButton("📈 رسوم بيانية", callback_data=f"charts_{student_id}")
        )
        markup.row(
            types.InlineKeyboardButton("⭐ تقديرات", callback_data=f"ratings_{student_id}"),
            types.InlineKeyboardButton("💡 نصائح", callback_data=f"tips_{student_id}")
        )
        markup.row(
            types.InlineKeyboardButton("🚨 التنبيهات", callback_data=f"alerts_{student_id}"),
            types.InlineKeyboardButton("📥 PDF", callback_data=f"pdf_{student_id}")
        )
        
        bot.send_message(chat_id, "🎯 اختر ما تريد:", reply_markup=markup)

    except Exception as e:
        print(f"Error in send_result: {e}")
        bot.send_message(chat_id, "❌ حدث خطأ أثناء معالجة النتيجة.")

def search_by_name(name_query: str):
    try:
        response = supabase.table("all_marks").select("student_id, student_name, father_name").ilike("student_name", f"%{name_query}%").execute()
        if not response.data: return []
        unique_students = {}
        for s in response.data:
            sid = s['student_id']
            if sid not in unique_students:
                unique_students[sid] = f"{s['student_name']} {s.get('father_name', '')}".strip()
        return unique_students
    except Exception as e:
        print(f"Search Error: {e}")
        return []

def get_student_data(student_id):
    """جلب بيانات الطالب من الـ ID"""
    try:
        response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
        return response.data if response.data else None
    except Exception as e:
        print(f"Error getting student data: {e}")
        return None

# ══════════════════════════════════════
@bot.message_handler(commands=["start"])
def start(msg):
    save_user(msg.chat.id)
    welcome_msg = (
        "👋 *أهلاً بك في بوت النتائج الجامعية المطور*\n\n"
        "✨ مميزات جديدة:\n"
        "📊 إحصائيات شاملة\n"
        "📈 رسوم بيانية متقدمة\n"
        "⭐ نظام تقديرات\n"
        "💡 نصائح ذكية\n"
        "🚨 تنبيهات وتحذيرات\n"
        "📥 تصدير PDF\n"
        "🏆 نظام الأوائل\n\n"
        "أرسل *الرقم الامتحاني* أو *اسم الطالب* للبدء.\n"
        "أو أرسل 3 لرؤية أفضل 3 طلاب 🥇"
    )
    bot.send_message(msg.chat.id, welcome_msg, parse_mode="Markdown")

@bot.message_handler(commands=["help"])
def help_command(msg):
    help_text = (
        "📖 دليل استخدام البوت\n\n"
        "═══════════════════════════════════\n"
        "🔷 الأوامر العامة:\n"
        "═══════════════════════════════════\n"
        "/start - البدء والقائمة الرئيسية\n"
        "/top - أفضل 3 طلاب 🏆\n"
        "/help - هذه الرسالة 📖\n\n"
        "═══════════════════════════════════\n"
        "🤖 الأوامر الذكية (AI):\n"
        "═══════════════════════════════════\n"
        "/analyze - تحليل أسباب الضعف 📊\n"
        "  💡 يعطيك تحليل ذكي عن نقاط ضعفك\n\n"
        "/plan - خطة دراسة ذكية 📚\n"
        "  💡 يولد لك خطة مذاكرة مخصصة\n\n"
        "/ask - أسئلة وإجابات ذكية\n"
        "  💡 اطرح أي سؤال أكاديمي والبوت يجيب\n\n"
        "═══════════════════════════════════\n"
        "👨‍💼 أوامر المشرفين فقط:\n"
        "═══════════════════════════════════\n"
        "/admin - لوحة تحكم الإدارة 🎛️\n"
        "  📊 إحصائيات النظام\n"
        "  👥 عدد المستخدمين\n"
        "  📈 تحليلات الدفعة\n"
        "  📝 سجل الأخطاء\n"
        "  📥 استخراج Excel\n"
        "  📢 إرسال تعميم\n"
        "  🏆 الـ 10 الأوائل\n"
        "  📚 الأوائل بالمادة\n"
        "  🚫 إدارة المحظورين\n"
        "  🚨 حوادث مزعجة معلقة\n\n"
        "/backup - نسخ احتياطي يدوي 💾\n"
        "  💡 إنشاء نسخة احتياطية فورية\n\n"
        "/backup_status - حالة النسخ الاحتياطي 📊\n"
        "  💡 معلومات عن آخر نسخة احتياطية\n\n"
        "/upload - رفع الملفات 📁\n"
        "  💡 رفع صور أو مستندات للبوت\n\n"
        "═══════════════════════════════════\n"
        "📝 طريقة الاستخدام الأساسية:\n"
        "═══════════════════════════════════\n"
        "• ابحث برقم الطالب: ارسل الرقم\n"
        "• ابحث بالاسم: ارسل الاسم\n"
        "• للأوائل: ارسل رقم (مثل 10)\n\n"
        "═══════════════════════════════════\n"
        "💬 للمساعدة أو الإبلاغ عن مشكلة:\n"
        "رسالة خاصة للمشرف"
    )
    bot.send_message(msg.chat.id, help_text)

@bot.message_handler(commands=["top"])
def top_students_command(msg):
    bot.send_chat_action(msg.chat.id, "typing")
    text, top_data = get_top_n_students(supabase, n=3, return_data=True)
    
    if top_data is not None and len(top_data) > 0:
        try:
            bot.send_chat_action(msg.chat.id, "upload_photo")
            # تحويل البيانات إلى الصيغة المتوقعة
            formatted_data = []
            for _, row in top_data.iterrows():
                formatted_data.append({
                    "الرقم الامتحاني": row['student_id'],
                    "الاسم": row['student_name'],
                    "المعدل": row['average_grade']
                })
            
            img_path = generate_top_students_image(formatted_data, title="أوائل الدفعة")
            with open(img_path, 'rb') as photo:
                bot.send_photo(msg.chat.id, photo, caption=text, parse_mode="Markdown")
            os.remove(img_path)
            return
        except Exception as e:
            print(f"⚠️ خطأ في توليد الصورة: {e}")
            pass # Fallback to text if image generation fails
            
    bot.send_message(msg.chat.id, text, parse_mode="Markdown")

# ══════════════════════════════════════
# Admin 
# ══════════════════════════════════════
@bot.message_handler(commands=["admin"])
def admin_panel(msg):
    if msg.chat.id not in ADMIN_IDS:
        bot.send_message(msg.chat.id, "⛔️ عذراً، هذا الأمر للمدراء فقط.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 عدد المستخدمين", callback_data="admin_users")
    )
    markup.row(
        types.InlineKeyboardButton("� تحليلات الدفعة", callback_data="admin_cohort_analytics"),
        types.InlineKeyboardButton("📝 سجل الأخطاء", callback_data="admin_logs")
    )
    markup.row(
        types.InlineKeyboardButton("📥 استخراج Excel", callback_data="admin_excel"),
        types.InlineKeyboardButton("📢 إرسال تعميم", callback_data="admin_broadcast")
    )
    markup.row(
        types.InlineKeyboardButton("🏆 الـ 10 الأوائل", callback_data="admin_top10"),
        types.InlineKeyboardButton("📚 الأوائل بالمادة", callback_data="admin_top_subject")
    )
    markup.row(
        types.InlineKeyboardButton("🚫 إدارة المحظورين", callback_data="admin_blocked_users"),
        types.InlineKeyboardButton("🚨 حوادث مزعجة معلقة", callback_data="admin_pending_spam")
    )
    
    bot.send_message(
        msg.chat.id, 
        "👨‍💼 *مرحباً بك في لوحة تحكم الإدارة*\n\nيرجى اختيار الإجراء المطلوب:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ══════════════════════════════════════
# معالجات Callbacks
# ══════════════════════════════════════

@bot.callback_query_handler(func=lambda call: call.data.startswith("sid_"))
def callback_student_id(call):
    save_user(call.message.chat.id)
    student_id = call.data.replace("sid_", "")
    bot.answer_callback_query(call.id)
    send_student_result(call.message.chat.id, student_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("stats_"))
def callback_stats(call):
    student_id = call.data.replace("stats_", "")
    bot.answer_callback_query(call.id)
    
    try:
        data = get_student_data(student_id)
        if not data:
            bot.send_message(call.message.chat.id, "❌ لم يتم العثور على النتائج")
            return
        
        # 🚀 استخدام Cache للإحصائيات
        stats = calculate_statistics_fast(student_id, supabase)
        analysis = analyze_performance(data)
        
        stats_msg = (
            f"📊 *الإحصائيات الشاملة*\n\n"
            f"📚 عدد المواد: {stats.get('total_subjects', 0)}\n"
            f"✅ المواد الناجحة: {stats.get('passed_subjects', 0)}\n"
            f"❌ المواد الراسبة: {stats.get('failed_subjects', 0)}\n"
            f"📈 نسبة النجاح: {stats.get('success_rate', 0)}%\n"
            f"📊 المعدل العام: {stats.get('average_grade', 0)}%\n"
            f"🏆 أعلى درجة: {stats.get('highest_grade', 0)}%\n"
            f"📉 أقل درجة: {stats.get('lowest_grade', 0)}%\n"
            f"🎯 المستوى: {analysis['performance_emoji']} {analysis['performance_level']}"
        )
        bot.send_message(call.message.chat.id, stats_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in stats callback: {e}")
        bot.send_message(call.message.chat.id, "❌ حدث خطأ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("charts_"))
def callback_charts(call):
    student_id = call.data.replace("charts_", "")
    bot.answer_callback_query(call.id)
    
    try:
        data = get_student_data(student_id)
        if not data:
            bot.send_message(call.message.chat.id, "❌ لم يتم العثور على النتائج")
            return
        
        # 🚀 استخدام Cache للإحصائيات
        stats = calculate_statistics_fast(student_id, supabase)
        bot.send_chat_action(call.message.chat.id, "upload_photo")
        
        # الرسم البياني الأول - العلامات
        chart1 = create_grades_chart(data, student_id)
        if chart1:
            with open(chart1, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo, caption="📊 الرسم البياني للعلامات")
            os.remove(chart1)
        
        # الرسم البياني الثاني - النظري والعملي
        chart2 = create_theoretical_practical_chart(data, student_id)
        if chart2:
            with open(chart2, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo, caption="📈 مقارنة النظري والعملي")
            os.remove(chart2)
        
        # الرسم البياني الثالث - نسب النجاح
        chart3 = create_performance_pie_chart(stats, student_id)
        if chart3:
            with open(chart3, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo, caption="🎯 نسبة النجاح والرسوب")
            os.remove(chart3)
    except Exception as e:
        print(f"Error in charts callback: {e}")
        bot.send_message(call.message.chat.id, "❌ حدث خطأ في الرسوم البيانية")

@bot.callback_query_handler(func=lambda call: call.data.startswith("ratings_"))
def callback_ratings(call):
    student_id = call.data.replace("ratings_", "")
    bot.answer_callback_query(call.id)
    
    try:
        data = get_student_data(student_id)
        if not data:
            bot.send_message(call.message.chat.id, "❌ لم يتم العثور على النتائج")
            return
        
        ratings_msg = "⭐ *التقديرات*\n\n"
        for m in data:
            subject = m.get('subject_name', 'غير محدد')
            grade = m.get('total_grade', 0)
            rating_info = get_rating(grade)
            ratings_msg += f"📌 {subject}\n"
            ratings_msg += f"   {format_grade_display(grade)}\n"
            ratings_msg += f"   التقدير: *{rating_info['description']}*\n\n"
        
        bot.send_message(call.message.chat.id, ratings_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in ratings callback: {e}")
        bot.send_message(call.message.chat.id, "❌ حدث خطأ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("tips_"))
def callback_tips(call):
    student_id = call.data.replace("tips_", "")
    bot.answer_callback_query(call.id)
    
    try:
        data = get_student_data(student_id)
        if not data:
            bot.send_message(call.message.chat.id, "❌ لم يتم العثور على النتائج")
            return
        
        student_name = data[0].get('student_name', 'الطالب')
        analysis = analyze_performance(data)
        motivation = get_motivation_message(analysis['performance_level'])
        
        # محاولة استخدام AI للنصائح الذكية
        ai_recommendations = ai_service.generate_smart_recommendations(student_name, analysis)
        
        tips_msg = f"💡 *استشارات وتوصيات ذكية لـ {student_name}*\n\n{motivation}\n\n"
        tips_msg += f"🤖 *نصائح مخصصة من نظام ذكي:*\n{ai_recommendations}\n"
        
        bot.send_message(call.message.chat.id, tips_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in tips callback: {e}")
        bot.send_message(call.message.chat.id, "❌ حدث خطأ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("alerts_"))
def callback_alerts(call):
    student_id = call.data.replace("alerts_", "")
    bot.answer_callback_query(call.id)
    
    try:
        data = get_student_data(student_id)
        if not data:
            bot.send_message(call.message.chat.id, "❌ لم يتم العثور على النتائج")
            return
        
        analysis = analyze_performance(data)
        stats = analysis['statistics']
        weak_subjects = analysis['weak_subjects']
        
        alerts = generate_alerts(stats, weak_subjects, 
                                stats.get('passed_subjects', 0),
                                stats.get('failed_subjects', 0))
        alerts_msg = format_alerts_message(alerts)
        
        bot.send_message(call.message.chat.id, alerts_msg, parse_mode="Markdown")
    except Exception as e:
        print(f"Error in alerts callback: {e}")
        bot.send_message(call.message.chat.id, "❌ حدث خطأ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pdf_"))
def callback_pdf(call):
    student_id = call.data.replace("pdf_", "")
    bot.answer_callback_query(call.id)
    
    try:
        data = get_student_data(student_id)
        if not data:
            bot.send_message(call.message.chat.id, "❌ لم يتم العثور على النتائج")
            return
        
        name = data[0].get('student_name', 'unknown')
        father = data[0].get('father_name', '')
        analysis = analyze_performance(data)
        stats = analysis['statistics']
        weak_subjects = analysis['weak_subjects']
        strong_subjects = analysis['strong_subjects']
        recommendations = generate_recommendations(analysis)
        
        bot.send_chat_action(call.message.chat.id, "upload_document")
        
        # محاولة توليد PDF
        pdf_path = generate_pdf_report(student_id, name, father, stats, weak_subjects,
                                       strong_subjects, recommendations, data)
        
        if pdf_path:
            with open(pdf_path, 'rb') as document:
                bot.send_document(call.message.chat.id, document, caption="📄 تقرير النتائج الشامل (PDF)")
            os.remove(pdf_path)
        else:
            # النسخة النصية البديلة
            txt_path = create_simple_text_report(student_id, name, stats, weak_subjects, strong_subjects)
            if txt_path:
                with open(txt_path, 'rb') as document:
                    bot.send_document(call.message.chat.id, document, caption="📄 تقرير النتائج (نص)")
                os.remove(txt_path)
            else:
                bot.send_message(call.message.chat.id, "❌ فشل توليد التقرير")
    except Exception as e:
        print(f"Error in pdf callback: {e}")
        bot.send_message(call.message.chat.id, "❌ حدث خطأ في توليد التقرير")

# ══════════════════════════════════════
# Admin Callbacks
# ══════════════════════════════════════
@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def callback_admin(call):
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔️ غير مصرح لك")
        return
        
    action = call.data.replace("admin_", "")
    bot.answer_callback_query(call.id)
    
    if action == "stats":
        info = get_admin_info()
        msg = format_admin_message(info)
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        
    elif action == "users":
        count = len(bot_users)
        bot.send_message(call.message.chat.id, f"👥 *عدد المستخدمين المسجلين في البوت:* `{count}` مستخدم", parse_mode="Markdown")
        
    elif action == "logs":
        logs_msg = get_recent_errors(limit=15)
        bot.send_message(call.message.chat.id, logs_msg, parse_mode="Markdown")
        
    elif action == "top10":
        bot.send_message(call.message.chat.id, "⏳ جاري حساب قائمة الأوائل... يرجى الانتظار.")
        top_10_msg = get_top_n_students(supabase, n=10) # 10 students for admin
        bot.send_message(call.message.chat.id, top_10_msg, parse_mode="Markdown")

    elif action == "excel":
        bot.send_message(call.message.chat.id, "⏳ جاري استخراج البيانات وبناء ملف Excel... يرجى الانتظار.")
        bot.send_chat_action(call.message.chat.id, "upload_document")
        file_path = generate_excel_backup(supabase)
        
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as doc:
                bot.send_document(call.message.chat.id, doc, caption="📥 تفضل، هذا ملف متكامل لجميع النتائج.")
            os.remove(file_path)
        else:
            bot.send_message(call.message.chat.id, "❌ حدث خطأ أثناء محاولة استخراج الملف أو لا توجد بيانات كافية.")
        
    elif action == "broadcast":
        msg = bot.send_message(call.message.chat.id, "📢 *إرسال تعميم:*\n\nأرسل الرسالة التي تريد إرسالها لجميع المستخدمين الآن، أو أرسل /cancel للإلغاء.", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_broadcast_message)

    elif action == "top_subject":
        subjects = get_all_subjects(supabase)
        if not subjects:
            bot.send_message(call.message.chat.id, "❌ لا توجد مواد في قاعدة البيانات.")
            return
        
        markup = types.InlineKeyboardMarkup()
        for subject in subjects:
            markup.add(types.InlineKeyboardButton(subject, callback_data=f"top_subject_{subject}"))
        
        bot.send_message(call.message.chat.id, "📚 اختر المادة لعرض أفضل 10 طلاب فيها:", reply_markup=markup)

    elif action == "cohort_analytics":
        # عرض منطقة فرعية لتحليلات الدفعة
        cohort_markup = types.InlineKeyboardMarkup()
        cohort_markup.row(
            types.InlineKeyboardButton("📊 إحصائيات عامة", callback_data="cohort_general_stats"),
            types.InlineKeyboardButton("⭐ توزيع التقديرات", callback_data="cohort_grade_dist")
        )
        cohort_markup.row(
            types.InlineKeyboardButton("📚 أداء المواد", callback_data="cohort_subject_perf"),
            types.InlineKeyboardButton("🚨 طلاب في خطر", callback_data="cohort_at_risk")
        )
        cohort_markup.row(
            types.InlineKeyboardButton("⚠️ طلاب حافة رسوب", callback_data="cohort_borderline"),
            types.InlineKeyboardButton("📋 مواد ناقصة", callback_data="cohort_incomplete")
        )
        
        bot.send_message(
            call.message.chat.id,
            "📈 *اختر نوع التحليل:*",
            reply_markup=cohort_markup,
            parse_mode="Markdown"
        )
    
    elif action == "blocked_users":
        # عرض المستخدمين المحظورين
        try:
            response = supabase.table("blocked_users").select("*").eq("is_active", True).execute()
            blocked_list = response.data
            
            if not blocked_list:
                bot.send_message(call.message.chat.id, "✅ لا توجد مستخدمين محظورين حالياً")
                return
            
            message_text = f"🚫 *المستخدمين المحظورين:* ({len(blocked_list)})\n\n"
            
            markup = types.InlineKeyboardMarkup()
            for user in blocked_list:
                user_id = user['user_id']
                reason = user['reason']
                blocked_time = user['blocked_at']
                
                message_text += f"👤 ID: `{user_id}`\n   📌 السبب: {reason}\n   ⏰ الوقت: {blocked_time[:10]}\n\n"
                
                markup.add(
                    types.InlineKeyboardButton(
                        f"🔓 فك الحظر #{user_id}",
                        callback_data=f"unblock_user_{user_id}"
                    )
                )
            
            bot.send_message(call.message.chat.id, message_text, reply_markup=markup, parse_mode="Markdown")
        
        except Exception as e:
            print(f"❌ خطأ في عرض المحظورين: {e}")
            bot.send_message(call.message.chat.id, "❌ حدث خطأ في الوصول للمستخدمين المحظورين")
    
    elif action == "pending_spam":
        # عرض الحوادث المعلقة
        try:
            pending = spam_protection.get_pending_incidents()
            
            if not pending:
                bot.send_message(call.message.chat.id, "✅ لا توجد حوادث معلقة")
                return
            
            message_text = f"🚨 *حوادث مزعجة معلقة:* ({len(pending)})\n\n"
            
            for incident in pending:
                user_id = incident['user_id']
                count = incident['request_count']
                detected = incident['detected_at']
                
                message_text += (
                    f"👤 المستخدم: `{user_id}`\n"
                    f"📊 عدد الطلبات: `{count}`\n"
                    f"⏰ الوقت: {detected[:16]}\n\n"
                )
            
            bot.send_message(call.message.chat.id, message_text, parse_mode="Markdown")
        
        except Exception as e:
            print(f"❌ خطأ في عرض الحوادث: {e}")
            bot.send_message(call.message.chat.id, "❌ حدث خطأ في الوصول للحوادث")

@bot.callback_query_handler(func=lambda call: call.data.startswith("cohort_"))
def callback_cohort_analytics(call):
    """معالجات تحليلات الدفعة"""
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔️ غير مصرح لك")
        return
    
    action = call.data.replace("cohort_", "")
    bot.answer_callback_query(call.id)
    
    try:
        if action == "general_stats":
            bot.send_chat_action(call.message.chat.id, "typing")
            analytics = get_cohort_analytics(supabase)
            message = format_cohort_message(analytics)
            bot.send_message(call.message.chat.id, message, parse_mode="Markdown")
            
        elif action == "grade_dist":
            bot.send_chat_action(call.message.chat.id, "upload_photo")
            distribution = get_grade_distribution(supabase)
            
            # إرسال النص أولاً
            msg_text = format_grade_distribution_message(distribution)
            bot.send_message(call.message.chat.id, msg_text, parse_mode="Markdown")
            
            # ثم الصورة
            chart_path = create_grade_distribution_chart(distribution)
            if chart_path:
                with open(chart_path, 'rb') as photo:
                    bot.send_photo(call.message.chat.id, photo, caption="📊 رسم بياني لتوزيع التقديرات")
                os.remove(chart_path)
            
        elif action == "subject_perf":
            bot.send_chat_action(call.message.chat.id, "typing")
            subjects = get_subjects_performance(supabase)
            if not subjects:
                bot.send_message(call.message.chat.id, "❌ لا توجد بيانات عن المواد")
                return
            
            # Create keyboard
            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            markup = InlineKeyboardMarkup(row_width=2)
            
            # Button for all subjects
            markup.add(InlineKeyboardButton("📊 عرض أداء جميع المواد", callback_data="cohort_all_subjects_perf"))
            
            # Sort subjects alphabetically to ensure stable index
            subjects.sort(key=lambda x: x['subject_name'])
            
            buttons = []
            for i, sub in enumerate(subjects):
                pass_rate = sub['pass_rate']
                emoji = "🟢" if pass_rate >= 80 else ("🟡" if pass_rate >= 60 else "🔴")
                btn_text = f"{emoji} {sub['subject_name']}"
                buttons.append(InlineKeyboardButton(btn_text, callback_data=f"csub_{i}"))
            
            # Add buttons in rows of 2
            markup.add(*buttons)
            
            bot.send_message(call.message.chat.id, "📚 *الرجاء اختيار المادة التي تريد تحليلها:*", reply_markup=markup, parse_mode="Markdown")

        elif action == "all_subjects_perf":
            bot.send_chat_action(call.message.chat.id, "typing")
            subjects = get_subjects_performance(supabase)
            msg_text = format_subjects_performance_message(subjects)
            
            # إرسال الرسالة المقسمة لتجنب تجاوز الحد الأقصى للنصوص في تليجرام
            max_length = 4000
            for i in range(0, len(msg_text), max_length):
                bot.send_message(call.message.chat.id, msg_text[i:i+max_length], parse_mode="Markdown")
            
            # إرسال الصورة للمواد
            bot.send_chat_action(call.message.chat.id, "upload_photo")
            chart_path = create_subjects_performance_chart(subjects)
            if chart_path:
                with open(chart_path, 'rb') as photo:
                    bot.send_photo(call.message.chat.id, photo, caption="📚 أداء جميع المواد")
                os.remove(chart_path)
            
        elif action == "at_risk":
            bot.send_chat_action(call.message.chat.id, "typing")
            at_risk = get_at_risk_students(supabase)
            message = format_at_risk_message(at_risk)
            bot.send_message(call.message.chat.id, message, parse_mode="Markdown")
            
        elif action == "borderline":
            bot.send_chat_action(call.message.chat.id, "typing")
            borderline = get_borderline_students(supabase)
            message = format_borderline_message(borderline)
            bot.send_message(call.message.chat.id, message, parse_mode="Markdown")
            
        elif action == "incomplete":
            bot.send_chat_action(call.message.chat.id, "typing")
            incomplete = get_incomplete_students(supabase)
            message = format_incomplete_message(incomplete)
            bot.send_message(call.message.chat.id, message, parse_mode="Markdown")
    
    except Exception as e:
        print(f"Error in cohort analytics: {e}")
        bot.send_message(call.message.chat.id, f"❌ حدث خطأ: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("csub_"))
def callback_single_subject_perf(call):
    """معالجة النقر على مادة معينة لتحليلها"""
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔️ غير مصرح لك")
        return
        
    bot.answer_callback_query(call.id)
    bot.send_chat_action(call.message.chat.id, "typing")
    
    try:
        idx = int(call.data.replace("csub_", ""))
        subjects = get_subjects_performance(supabase)
        subjects.sort(key=lambda x: x['subject_name'])
        
        if idx >= len(subjects):
            bot.send_message(call.message.chat.id, "❌ حدث خطأ، يرجى المحاولة مرة أخرى.")
            return
            
        subject = subjects[idx]
        pass_rate = subject['pass_rate']
        emoji = "🟢" if pass_rate >= 80 else ("🟡" if pass_rate >= 60 else "🔴")
        
        message = f"📊 *تحليل الأداء لمادة:* `{subject['subject_name']}`\n\n"
        message += f"👥 إجمالي الطلاب: `{int(subject['total_records'])}`\n"
        message += f"✅ عدد الناجحين: `{int(subject['passed'])}`\n"
        message += f"❌ عدد الراسبين: `{int(subject['total_records'] - subject['passed'])}`\n"
        message += f"📈 نسبة النجاح: `{pass_rate}%` {emoji}\n\n"
        message += f"📊 *الإحصائيات للمادة:*\n"
        message += f"   ├ المتوسط: `{subject['average']}`\n"
        message += f"   ├ أعلى درجة: `{subject['highest']}`\n"
        message += f"   └ أقل درجة: `{subject['lowest']}`\n"
        
        bot.send_message(call.message.chat.id, message, parse_mode="Markdown")
        
        # رسم دائري لنسبة النجاح والرسوب للمادة
        bot.send_chat_action(call.message.chat.id, "upload_photo")
        stats = {
            'passed_subjects': int(subject['passed']),
            'failed_subjects': int(subject['total_records'] - subject['passed'])
        }
        
        chart_path = create_performance_pie_chart(stats, f"sub_{idx}")
        if chart_path:
            with open(chart_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo, caption=f"📈 نسبة النجاح: {subject['subject_name']}")
            os.remove(chart_path)
            
    except Exception as e:
        print(f"Error in single subject analytic: {e}")
        bot.send_message(call.message.chat.id, "❌ حدث خطأ أثناء جلب بيانات المادة")


@bot.callback_query_handler(func=lambda call: call.data.startswith("top_subject_"))
def callback_top_subject(call):
    """معالج اختيار المادة لعرض الأوائل فيها"""
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔️ غير مصرح لك")
        return
    
    subject_name = call.data.replace("top_subject_", "")
    bot.answer_callback_query(call.id)
    
    bot.send_message(call.message.chat.id, f"⏳ جاري حساب قائمة الأوائل في مادة: {subject_name}... يرجى الانتظار.")
    result = get_top_10_in_subject(supabase, subject_name)
    bot.send_message(call.message.chat.id, result, parse_mode="Markdown")

def process_broadcast_message(msg):
    if msg.text == "/cancel":
        bot.send_message(msg.chat.id, "تم إلغاء الإرسال.")
        return
        
    success = 0
    failed = 0
    bot.send_message(msg.chat.id, "🔄 جاري الإرسال، يرجى الانتظار...")
    
    for user_id in bot_users:
        try:
            bot.send_message(user_id, f"📢 *إعلان هام من الإدارة:*\n\n{msg.text}", parse_mode="Markdown")
            success += 1
        except Exception:
            failed += 1
            
    bot.send_message(
        msg.chat.id, 
        f"✅ *اكتمل الإرسال!*\n\n"
        f"✔️ نجح: {success}\n"
        f"❌ فشل: {failed} (قد يكون المستخدم حظر البوت)",
        parse_mode="Markdown"
    )


# ══════════════════════════════════════
# معالجات الحماية من الطلبات المتتالية
# ══════════════════════════════════════

def notify_admin_about_spam(user_id: int, incident_id: int, request_count: int):
    """
    إرسال إشعار للمسؤول عن حادثة رسائل مزعجة
    """
    try:
        # معلومات المستخدم
        user_link = f"<a href='tg://user?id={user_id}'>المستخدم #{user_id}</a>"
        
        message_text = (
            f"🚨 *تنبيه أمان: طلبات متتالية مريبة*\n\n"
            f"👤 المستخدم: #{user_id}\n"
            f"📊 عدد الطلبات: `{request_count}` طلب في فترة قصيرة\n"
            f"⏰ الوقت: `{datetime.now().strftime('%H:%M:%S')}`\n"
            f"📅 التاريخ: `{datetime.now().strftime('%Y-%m-%d')}`\n\n"
            f"ماذا تريد أن تفعل؟"
        )
        
        # إنشاء الأزرار
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(
                "✅ حظر المستخدم",
                callback_data=f"spam_block_{user_id}_{incident_id}"
            ),
            types.InlineKeyboardButton(
                "❌ تجاهل التنبيه",
                callback_data=f"spam_ignore_{user_id}_{incident_id}"
            )
        )
        
        # إرسال الإشعار لكل مسؤول
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(
                    admin_id,
                    message_text,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"⚠️ خطأ في إرسال إشعار للمسؤول {admin_id}: {e}")
    
    except Exception as e:
        print(f"❌ خطأ في notify_admin_about_spam: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("unblock_user_"))
def callback_unblock_user(call):
    """معالج فك الحظر عن المستخدم"""
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔️ غير مصرح لك")
        return
    
    try:
        user_id = int(call.data.replace("unblock_user_", ""))
        
        success = spam_protection.unblock_user(user_id)
        
        if success:
            response_text = f"✅ تم فك الحظر عن المستخدم #{user_id} بنجاح"
            # محاولة إرسال رسالة للمستخدم
            try:
                bot.send_message(
                    user_id,
                    "✅ تم فك الحظر عنك! يمكنك الآن استخدام البوت مجدداً.",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            response_text = f"❌ فشل فك الحظر عن المستخدم #{user_id}"
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=call.message.text + f"\n\n✔️ {response_text}",
            parse_mode="Markdown"
        )
        
        bot.answer_callback_query(call.id, response_text)
    
    except Exception as e:
        print(f"❌ خطأ في فك الحظر: {e}")
        bot.answer_callback_query(call.id, "❌ حدث خطأ")


@bot.callback_query_handler(func=lambda call: call.data.startswith("spam_"))

def callback_spam_decision(call):
    """معالج قرار المسؤول بخصوص المستخدم المزعج"""
    if call.message.chat.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "⛔️ أنت لست مسؤولاً")
        return
    
    try:
        parts = call.data.split("_")
        action = parts[1]  # "block" أو "ignore"
        user_id = int(parts[2])
        incident_id = int(parts[3])
        
        if action == "block":
            # حظر المستخدم
            success = spam_protection.block_user(user_id, "حظر بقرار إداري")
            spam_protection.resolve_incident(incident_id, "blocked")
            
            if success:
                response_text = f"✅ تم حظر المستخدم #{user_id} بنجاح"
                # إرسال رسالة للمستخدم المحظور
                try:
                    bot.send_message(
                        user_id,
                        "⛔️ تم حظرك من البوت بسبب إساءة الاستخدام.\n"
                        "إذا كنت تعتقد أن هذا خطأ، اتصل بالإدارة.",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            else:
                response_text = f"❌ فشل حظر المستخدم #{user_id}"
        
        elif action == "ignore":
            # تجاهل التنبيه
            spam_protection.resolve_incident(incident_id, "ignored")
            response_text = f"✅ تم تجاهل التنبيه بشأن المستخدم #{user_id}"
        
        else:
            response_text = "❌ إجراء غير معروف"
        
        # تحديث الرسالة الأصلية
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=call.message.text + f"\n\n✔️ *القرار:* {response_text}",
            parse_mode="Markdown"
        )
        
        bot.answer_callback_query(call.id, "✅ تم تنفيذ الإجراء")
    
    except Exception as e:
        print(f"❌ خطأ في معالج قرار الرسائل المزعجة: {e}")
        bot.answer_callback_query(call.id, "❌ حدث خطأ")


# ══════════════════════════════════════
# AI-Powered Features
# ══════════════════════════════════════

@bot.message_handler(commands=["analyze"])
def analyze_weak_subjects(msg):
    """أمر لتحليل أسباب الضعف في المواد"""
    sent = bot.send_message(msg.chat.id, "📝 أرسل رقمك الجامعي أو اسمك للتحليل الذكي:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, process_analyze_request)

def process_analyze_request(msg):
    """معالجة طلب التحليل الذكي"""
    text = msg.text.strip()
    clean_text = convert_arabic_digits(text)
    
    try:
        data = None
        if clean_text.isdigit():
            # بحث برقم جامعي
            response = supabase.table("all_marks").select("*").eq("student_id", clean_text).execute()
            data = response.data
            student_name = data[0].get('student_name', 'الطالب') if data else 'الطالب'
        else:
            # بحث باسم
            results = search_by_name(text)
            if len(results) == 1:
                student_id = list(results.keys())[0]
                response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
                data = response.data
                student_name = results[student_id]
        
        if not data:
            bot.send_message(msg.chat.id, "❌ لم يتم العثور على النتائج.")
            return
        
        # الحصول على المواد الضعيفة
        analysis = analyze_performance(data)
        weak_subjects = analysis.get('weak_subjects', [])
        
        if not weak_subjects:
            bot.send_message(msg.chat.id, "✅ ممتاز! لا توجد مواد ضعيفة.")
            return
        
        bot.send_chat_action(msg.chat.id, "typing")
        analysis_result = ai_service.analyze_weak_subjects(student_name, weak_subjects)
        
        result_msg = f"🔍 *تحليل أسباب الضعف:*\n\n{analysis_result}"
        bot.send_message(msg.chat.id, result_msg, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error in analyze: {e}")
        bot.send_message(msg.chat.id, f"❌ حدث خطأ: {str(e)}")


@bot.message_handler(commands=["plan"])
def generate_study_plan(msg):
    """أمر لتوليد خطة دراسة ذكية"""
    sent = bot.send_message(msg.chat.id, "📚 أرسل رقمك الجامعي أو اسمك لتوليد خطة دراسية ذكية:", parse_mode="Markdown")
    bot.register_next_step_handler(sent, process_plan_request)

def process_plan_request(msg):
    """معالجة طلب خطة الدراسة"""
    text = msg.text.strip()
    clean_text = convert_arabic_digits(text)
    
    try:
        data = None
        student_name = 'الطالب'
        
        if clean_text.isdigit():
            response = supabase.table("all_marks").select("*").eq("student_id", clean_text).execute()
            data = response.data
            student_name = data[0].get('student_name', 'الطالب') if data else 'الطالب'
        else:
            results = search_by_name(text)
            if len(results) == 1:
                student_id = list(results.keys())[0]
                response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
                data = response.data
                student_name = results[student_id]
        
        if not data:
            bot.send_message(msg.chat.id, "❌ لم يتم العثور على النتائج.")
            return
        
        analysis = analyze_performance(data)
        weak_subjects = analysis.get('weak_subjects', [])
        
        bot.send_chat_action(msg.chat.id, "typing")
        plan = ai_service.generate_study_plan(student_name, weak_subjects, available_days=7)
        
        plan_msg = f"📖 *خطة دراسية ذكية لـ {student_name}:*\n\n{plan}"
        bot.send_message(msg.chat.id, plan_msg, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error in plan generation: {e}")
        bot.send_message(msg.chat.id, f"❌ حدث خطأ: {str(e)}")


@bot.message_handler(commands=["ask"])
def ask_question(msg):
    """أمر لطرح أسئلة والحصول على إجابات ذكية"""
    sent = bot.send_message(msg.chat.id, "❓ اكتب سؤالك (أي موضوع أكاديمي):", parse_mode="Markdown")
    bot.register_next_step_handler(sent, process_question)

def process_question(msg):
    """معالجة السؤال والرد الذكي"""
    question = msg.text.strip()
    
    if len(question) < 5:
        bot.send_message(msg.chat.id, "❌ السؤال قصير جداً. يرجى توضيح أكثر.")
        return
    
    try:
        bot.send_chat_action(msg.chat.id, "typing")
        answer = ai_service.answer_student_question(question)
        
        answer_msg = f"🤖 *الإجابة:*\n\n{answer}"
        bot.send_message(msg.chat.id, answer_msg, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Error in question answering: {e}")
        bot.send_message(msg.chat.id, f"خطأ: {str(e)}")

# ══════════════════════════════════════
# Storage & Backup Management Commands
# ══════════════════════════════════════

@bot.message_handler(commands=["backup"])
def manual_backup_command(msg):
    """أمر النسخ الاحتياطي اليدوي للمشرفين"""
    if msg.chat.id not in ADMIN_IDS:
        bot.send_message(msg.chat.id, "⛔️ عذراً، هذا الأمر للمدراء فقط.")
        return
    
    if backup_scheduler is None:
        bot.send_message(msg.chat.id, "⚠️ النسخ الاحتياطية معطلة حالياً. يرجى إنشاء bucket 'bot-storage' في Supabase أولاً.")
        return
    
    try:
        bot.send_message(msg.chat.id, "⏳ جاري إنشاء نسخة احتياطية... يرجى الانتظار.")
        result = backup_scheduler.force_backup_now()
        
        if result.get("success"):
            msg_text = "✅ *تم النسخ الاحتياطي بنجاح!*\n\n"
            for file, res in result.get("results", {}).items():
                if res.get("success"):
                    msg_text += f"✔️ {file}: تم رفعها\n"
                else:
                    msg_text += f"❌ {file}: فشل الرفع\n"
            bot.send_message(msg.chat.id, msg_text, parse_mode="Markdown")
        else:
            bot.send_message(msg.chat.id, f"❌ فشلت النسخة الاحتياطية: {result.get('error')}", parse_mode="Markdown")
    
    except Exception as e:
        print(f"Error in manual backup: {e}")
        bot.send_message(msg.chat.id, f"❌ خطأ: {str(e)}")

@bot.message_handler(commands=["backup_status"])
def backup_status_command(msg):
    """عرض حالة النسخ الاحتياطي"""
    if msg.chat.id not in ADMIN_IDS:
        bot.send_message(msg.chat.id, "⛔️ عذراً، هذا الأمر للمدراء فقط.")
        return
    
    if backup_scheduler is None:
        bot.send_message(msg.chat.id, "⚠️ النسخ الاحتياطية معطلة حالياً. يرجى إنشاء bucket 'bot-storage' في Supabase أولاً.")
        return
    
    try:
        status = backup_scheduler.get_backup_status()
        
        status_msg = f"📊 *حالة النسخ الاحتياطي:*\n\n"
        status_msg += f"🔄 الحالة: {'🟢 نشط' if status['is_running'] else '🔴 متوقف'}\n"
        status_msg += f"⏱️ الفترة الزمنية: كل {status['backup_interval_hours']} ساعة\n\n"
        status_msg += f"📅 *آخر النسخ الاحتياطية:*\n"
        
        if status['last_backups']:
            for file, timestamp in status['last_backups'].items():
                status_msg += f"• {file}: {timestamp}\n"
        else:
            status_msg += "لم يتم إجراء نسخة احتياطية بعد\n"
        
        # معلومات التخزين
        status_msg += f"\n💾 *معلومات التخزين:*\n"
        status_msg += f"الحد الأقصى: 50 MB\n"
        status_msg += f"يرجى التحقق من لوحة تحكم Supabase للتفاصيل"
        
        bot.send_message(msg.chat.id, status_msg, parse_mode="Markdown")
    
    except Exception as e:
        print(f"Error in backup status: {e}")
        bot.send_message(msg.chat.id, f"❌ خطأ: {str(e)}")

@bot.message_handler(commands=["upload"])
def upload_file_command(msg):
    """أمر رفع ملف محدد إلى التخزين"""
    if msg.chat.id not in ADMIN_IDS:
        bot.send_message(msg.chat.id, "⛔️ عذراً، هذا الأمر للمدراء فقط.")
        return
    
    sent = bot.send_message(
        msg.chat.id,
        "📤 *رفع ملف إلى التخزين*\n\n"
        "أرسل أحد الخيارات:\n"
        "1️⃣ users.json\n"
        "2️⃣ subscriptions.json\n"
        "3️⃣ أو أرسل اسم الملف مباشرة\n\n"
        "أو ارسل /cancel للإلغاء",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent, process_upload_file)

def process_upload_file(msg):
    """معالجة رفع الملف"""
    if msg.text == "/cancel":
        bot.send_message(msg.chat.id, "تم الإلغاء.")
        return
    
    file_name = msg.text.strip()
    file_path = file_name if os.path.exists(file_name) else None
    
    if not file_path or not os.path.exists(file_path):
        bot.send_message(msg.chat.id, f"❌ الملف '{file_name}' غير موجود.")
        return
    
    try:
        bot.send_message(msg.chat.id, "⏳ جاري رفع الملف... يرجى الانتظار.")
        manager = SupabaseStorageManager(supabase)
        result = manager.upload_backup_file(file_path, backup_type="manual")
        
        if result.get("success"):
            upload_msg = (
                f"✅ *تم رفع الملف بنجاح!*\n\n"
                f"📄 الملف: {os.path.basename(file_path)}\n"
                f"💾 الحجم: {result.get('file_size', 0) / 1024:.2f} KB\n"
                f"📍 المسار: `{result.get('file_path')}`\n"
                f"🔗 الرابط: `{result.get('public_url')}`"
            )
            bot.send_message(msg.chat.id, upload_msg, parse_mode="Markdown")
        else:
            bot.send_message(msg.chat.id, f"❌ فشل الرفع: {result.get('error')}", parse_mode="Markdown")
    
    except Exception as e:
        print(f"Error uploading file: {e}")
        bot.send_message(msg.chat.id, f"❌ خطأ: {str(e)}")

# ══════════════════════════════════════
# معالجات الرسائل العامة (يجب أن تكون في النهاية!)
# ══════════════════════════════════════

@bot.message_handler(func=lambda m: True)
def handle_all(msg):
    save_user(msg.chat.id)
    
    # ═══════════════════════════════════════
    # تسجيل الاستخدام في الإحصائيات
    # ═══════════════════════════════════════
    try:
        analytics_middleware.log_message(msg)
    except Exception as e:
        print(f"⚠️ خطأ في تسجيل الإحصائيات: {e}")
    
    # ═══════════════════════════════════════
    # التحقق من الطلبات المتتالية (Spam Protection)
    # ═══════════════════════════════════════
    if spam_protection.is_user_blocked(msg.chat.id):
        bot.send_message(
            msg.chat.id, 
            "🚫 عذراً، لقد تم حظرك مؤقتاً بسبب إرسال طلبات كثيرة متتالية.\n"
            "يرجى الانتظار 30 دقيقة قبل المحاولة مرة أخرى.",
            parse_mode="Markdown"
        )
        return
    
    # ═══════════════════════════════════════
    # فحص الاشتراك في قناة البوت
    # ═══════════════════════════════════════
    is_subscribed = check_channel_subscription(msg.chat.id)
    
    if not is_subscribed and msg.chat.id not in ADMIN_IDS:
        # عداد التذكيرات
        update_channel_reminder(msg.chat.id)
        
        reminder_text = (
            f"❌ *عذراً، يجب الاشتراك في قناة البوت أولاً*\n\n"
            f"👇 *اضغط للاشتراك:*\n"
            f"[📢 اشترك في القناة]({CHANNEL_LINK})\n\n"
            f"بعد الاشتراك، أرسل /start لبدء استخدام البوت."
        )
        
        bot.send_message(msg.chat.id, reminder_text, parse_mode="Markdown")
        return
    
    # فحص الطلب
    spam_check = spam_protection.check_request(msg.chat.id)
    
    if spam_check['is_spam']:
        # تسجيل الحادثة
        spam_protection.log_spam_incident(msg.chat.id, spam_check['request_count'])
        
        # إرسال إشعار للمسؤول
        try:
            pending_incidents = spam_protection.get_pending_incidents()
            for incident in pending_incidents:
                if incident['user_id'] == msg.chat.id:
                    notify_admin_about_spam(msg.chat.id, incident['id'], spam_check['request_count'])
                    break
        except Exception as e:
            print(f"⚠️ خطأ في الإشعار: {e}")
        
        bot.send_message(
            msg.chat.id,
            f"⚠️ تحذير: لقد أرسلت {spam_check['request_count']} طلب في وقت قصير.\n"
            f"الحد المسموح: {spam_check['max_allowed']} طلبات فقط.\n"
            f"يرجى الانتظار قليلاً قبل الطلب التالي.",
            parse_mode="Markdown"
        )
        return
    
    # المتابعة مع معالجة الطلب العادي
    text = msg.text.strip()
    clean_text = convert_arabic_digits(text)

    if clean_text.isdigit():
        # التحقق إذا كان رقم قصير (طلب أوائل) أم رقم جامعي طويل
        if len(clean_text) <= 2:  # أرقام 1-9 فقط (3، 5، 10 إلخ)
            try:
                n = int(clean_text)
                
                # تقييد المستخدمين العاديين برقم أقصى وهو 3 
                if msg.chat.id not in ADMIN_IDS:
                    if n > 3:
                        bot.send_message(msg.chat.id, "⛔️ عذراً، لا يُسمح للطلاب بمعرفة أكثر من أفضل 3 طلاب. تفضل هذه قائمة بأفضل 3 طلاب:")
                        n = 3
                
                if 1 <= n <= 50:  # حد أقصى 50 طالب
                    bot.send_chat_action(msg.chat.id, "typing")
                    bot.send_message(msg.chat.id, f"⏳ جاري حساب أفضل {n} طلاب... يرجى الانتظار.")
                    result = get_top_n_students(supabase, n)
                    bot.send_message(msg.chat.id, result, parse_mode="Markdown")
                else:
                    bot.send_message(msg.chat.id, f"❌ الرقم يجب أن يكون بين 1 و 50. أرسل رقماً صحيحاً.")
            except ValueError:
                send_student_result(msg.chat.id, clean_text)
        else:
            # رقم جامعي عادي
            send_student_result(msg.chat.id, clean_text)
    else:
        bot.send_chat_action(msg.chat.id, "typing")
        results = search_by_name(text)
        if not results:
            bot.send_message(msg.chat.id, f"🔍 لم أجد أي طالب يحتوي اسمه على: '{text}'")
        elif len(results) == 1:
            sid = list(results.keys())[0]
            send_student_result(msg.chat.id, sid)
        else:
            markup = types.InlineKeyboardMarkup()
            for sid, full_name in list(results.items())[:15]:
                markup.add(types.InlineKeyboardButton(text=full_name, callback_data=f"sid_{sid}"))
            bot.send_message(msg.chat.id, f"🔍 وجدت {len(results)} طلاب، اختر اسمك من القائمة:", reply_markup=markup)

if __name__ == "__main__":
    print("جاري تفعيل نظام الإشعارات التلقائية...")
    start_notifications_scheduler(bot, supabase, interval_minutes=60)
    print("البوت المطور يعمل الآن!")
    
    # تشغيل البوت مع معالجة الأخطاء المحسّنة
    polling_manager = configure_polling_with_safety(bot)
    try:
        polling_manager.start_polling()
    except KeyboardInterrupt:
        print("❌ تم إيقاف البوت بواسطة المستخدم")
    except Exception as e:
        print(f"❌ فشل البوت: {str(e)}")
        traceback.print_exc()
