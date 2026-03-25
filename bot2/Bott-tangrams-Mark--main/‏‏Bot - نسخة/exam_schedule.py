# -*- coding: utf-8 -*-
"""
نظام جدول الامتحانات
إدارة وعرض مواعيد الامتحانات مع تذكيرات
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import time


class ExamScheduleSystem:
    """
    نظام إدارة جدول الامتحانات
    - عرض جدول الامتحانات
    - تذكيرات قبل الامتحان
    - إضافة/تعديل مواعيد (للمسؤولين)
    """
    
    def __init__(self, bot, supabase, admin_ids: list = None):
        """
        Args:
            bot: instance من telebot
            supabase: عميل Supabase
            admin_ids: قائمة معرفات المسؤولين
        """
        self.bot = bot
        self.supabase = supabase
        self.admin_ids = admin_ids or []
        
        # المشتركين في التذكيرات: {chat_id: True}
        self.reminder_subscribers = {}
        
        # حالة التشغيل
        self._running = False
        self._reminder_thread = None
        
        # تحميل المشتركين
        self._load_reminder_subscribers()
    
    def _load_reminder_subscribers(self):
        """تحميل المشتركين في التذكيرات"""
        try:
            response = self.supabase.table("exam_reminder_subscribers").select("chat_id").eq("is_active", True).execute()
            for row in response.data:
                self.reminder_subscribers[row['chat_id']] = True
            print(f"✅ تم تحميل {len(self.reminder_subscribers)} مشترك في تذكيرات الامتحانات")
        except Exception as e:
            print(f"⚠️ خطأ في تحميل مشتركي التذكيرات: {e}")
    
    def get_upcoming_exams(self, days: int = 30) -> List[dict]:
        """جلب الامتحانات القادمة"""
        try:
            today = datetime.now().date()
            end_date = today + timedelta(days=days)
            
            response = self.supabase.table("exam_schedule").select("*")\
                .gte("exam_date", today.isoformat())\
                .lte("exam_date", end_date.isoformat())\
                .order("exam_date")\
                .execute()
            
            return response.data
        except Exception as e:
            print(f"❌ خطأ في جلب الامتحانات: {e}")
            return []
    
    def get_exams_by_subject(self, subject_name: str) -> List[dict]:
        """جلب امتحانات مادة معينة"""
        try:
            response = self.supabase.table("exam_schedule").select("*")\
                .ilike("subject_name", f"%{subject_name}%")\
                .order("exam_date")\
                .execute()
            return response.data
        except:
            return []
    
    def format_exam_schedule(self, exams: List[dict], title: str = "📅 جدول الامتحانات") -> str:
        """تنسيق جدول الامتحانات"""
        if not exams:
            return "📭 لا توجد امتحانات قادمة حالياً."
        
        message = f"*{title}*\n"
        message += "═" * 30 + "\n\n"
        
        current_date = None
        for exam in exams:
            exam_date = exam.get('exam_date', '')
            subject = exam.get('subject_name', 'مادة')
            exam_time = exam.get('exam_time', '')
            location = exam.get('location', '')
            duration = exam.get('duration_minutes', '')
            notes = exam.get('notes', '')
            
            # عرض التاريخ إذا تغير
            if exam_date != current_date:
                current_date = exam_date
                try:
                    date_obj = datetime.strptime(exam_date, '%Y-%m-%d')
                    day_name = self._get_arabic_day(date_obj.weekday())
                    formatted_date = date_obj.strftime('%Y/%m/%d')
                    message += f"📆 *{day_name} - {formatted_date}*\n"
                    message += "─" * 25 + "\n"
                except:
                    message += f"📆 *{exam_date}*\n"
            
            # معلومات الامتحان
            message += f"📚 *{subject}*\n"
            if exam_time:
                message += f"   🕐 الساعة: {exam_time}\n"
            if location:
                message += f"   📍 المكان: {location}\n"
            if duration:
                message += f"   ⏱ المدة: {duration} دقيقة\n"
            if notes:
                message += f"   💡 ملاحظة: {notes}\n"
            message += "\n"
        
        message += "─" * 25 + "\n"
        message += "🔔 استخدم /exam\\_remind للاشتراك في التذكيرات"
        
        return message
    
    def _get_arabic_day(self, weekday: int) -> str:
        """تحويل رقم اليوم لاسم عربي"""
        days = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        return days[weekday]
    
    def add_exam(self, exam_data: dict) -> dict:
        """إضافة امتحان جديد (للمسؤولين فقط)"""
        try:
            required_fields = ['subject_name', 'exam_date']
            for field in required_fields:
                if field not in exam_data:
                    return {'success': False, 'message': f'❌ الحقل {field} مطلوب'}
            
            exam_data['created_at'] = datetime.now().isoformat()
            
            response = self.supabase.table("exam_schedule").insert(exam_data).execute()
            
            return {
                'success': True,
                'message': f"✅ تم إضافة امتحان: {exam_data['subject_name']}",
                'exam_id': response.data[0]['id'] if response.data else None
            }
        except Exception as e:
            return {'success': False, 'message': f'❌ خطأ: {e}'}
    
    def update_exam(self, exam_id: int, updates: dict) -> dict:
        """تحديث امتحان"""
        try:
            updates['updated_at'] = datetime.now().isoformat()
            self.supabase.table("exam_schedule").update(updates).eq('id', exam_id).execute()
            return {'success': True, 'message': '✅ تم تحديث الامتحان'}
        except Exception as e:
            return {'success': False, 'message': f'❌ خطأ: {e}'}
    
    def delete_exam(self, exam_id: int) -> dict:
        """حذف امتحان"""
        try:
            self.supabase.table("exam_schedule").delete().eq('id', exam_id).execute()
            return {'success': True, 'message': '✅ تم حذف الامتحان'}
        except Exception as e:
            return {'success': False, 'message': f'❌ خطأ: {e}'}
    
    def subscribe_to_reminders(self, chat_id: int) -> dict:
        """الاشتراك في تذكيرات الامتحانات"""
        try:
            self.supabase.table("exam_reminder_subscribers").upsert({
                'chat_id': chat_id,
                'is_active': True,
                'subscribed_at': datetime.now().isoformat()
            }).execute()
            
            self.reminder_subscribers[chat_id] = True
            
            return {
                'success': True,
                'message': '✅ تم الاشتراك في تذكيرات الامتحانات!\n\n'
                          'سيصلك تذكير قبل كل امتحان بـ:\n'
                          '• 24 ساعة\n'
                          '• 3 ساعات\n\n'
                          'استخدم /exam\\_unremind لإلغاء التذكيرات'
            }
        except Exception as e:
            return {'success': False, 'message': f'❌ خطأ: {e}'}
    
    def unsubscribe_from_reminders(self, chat_id: int) -> dict:
        """إلغاء الاشتراك في التذكيرات"""
        try:
            self.supabase.table("exam_reminder_subscribers").update({
                'is_active': False
            }).eq('chat_id', chat_id).execute()
            
            if chat_id in self.reminder_subscribers:
                del self.reminder_subscribers[chat_id]
            
            return {
                'success': True,
                'message': '✅ تم إلغاء الاشتراك في تذكيرات الامتحانات'
            }
        except Exception as e:
            return {'success': False, 'message': f'❌ خطأ: {e}'}
    
    def _check_and_send_reminders(self):
        """فحص وإرسال التذكيرات"""
        now = datetime.now()
        
        # جلب الامتحانات القادمة خلال 24 ساعة
        tomorrow = now + timedelta(hours=24)
        three_hours = now + timedelta(hours=3)
        
        try:
            # تذكير 24 ساعة
            exams_24h = self.supabase.table("exam_schedule").select("*")\
                .gte("exam_date", now.date().isoformat())\
                .lte("exam_date", tomorrow.date().isoformat())\
                .execute()
            
            for exam in exams_24h.data:
                exam_datetime = self._parse_exam_datetime(exam)
                if exam_datetime:
                    diff = (exam_datetime - now).total_seconds() / 3600  # بالساعات
                    
                    # تذكير 24 ساعة (بين 23-25 ساعة)
                    if 23 <= diff <= 25:
                        self._send_reminder(exam, "24 ساعة")
                    
                    # تذكير 3 ساعات (بين 2.5-3.5 ساعة)
                    elif 2.5 <= diff <= 3.5:
                        self._send_reminder(exam, "3 ساعات")
                        
        except Exception as e:
            print(f"⚠️ خطأ في التذكيرات: {e}")
    
    def _parse_exam_datetime(self, exam: dict) -> Optional[datetime]:
        """تحويل تاريخ ووقت الامتحان لـ datetime"""
        try:
            date_str = exam.get('exam_date', '')
            time_str = exam.get('exam_time', '08:00')
            
            if not date_str:
                return None
            
            datetime_str = f"{date_str} {time_str}"
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
        except:
            return None
    
    def _send_reminder(self, exam: dict, time_until: str):
        """إرسال تذكير للمشتركين"""
        subject = exam.get('subject_name', 'امتحان')
        exam_date = exam.get('exam_date', '')
        exam_time = exam.get('exam_time', '')
        location = exam.get('location', '')
        
        message = f"⏰ *تذكير بامتحان قادم!*\n\n"
        message += f"📚 المادة: *{subject}*\n"
        message += f"📅 التاريخ: {exam_date}\n"
        if exam_time:
            message += f"🕐 الوقت: {exam_time}\n"
        if location:
            message += f"📍 المكان: {location}\n"
        message += f"\n⏳ متبقي: *{time_until}*\n"
        message += "\n🍀 بالتوفيق!"
        
        sent_count = 0
        for chat_id in self.reminder_subscribers:
            try:
                self.bot.send_message(chat_id, message, parse_mode="Markdown")
                sent_count += 1
            except Exception as e:
                print(f"⚠️ فشل إرسال تذكير لـ {chat_id}: {e}")
        
        if sent_count > 0:
            print(f"📤 تم إرسال {sent_count} تذكير لامتحان {subject}")
    
    def _reminder_loop(self):
        """حلقة التذكيرات"""
        while self._running:
            try:
                self._check_and_send_reminders()
            except Exception as e:
                print(f"❌ خطأ في حلقة التذكيرات: {e}")
            
            # فحص كل 30 دقيقة
            time.sleep(1800)
    
    def start(self):
        """بدء نظام التذكيرات"""
        if self._running:
            return
        
        self._running = True
        self._reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self._reminder_thread.start()
        print("🚀 نظام تذكيرات الامتحانات يعمل")
    
    def stop(self):
        """إيقاف نظام التذكيرات"""
        self._running = False
        if self._reminder_thread:
            self._reminder_thread.join(timeout=5)


def setup_exam_commands(bot, exam_system, admin_ids):
    """إعداد أوامر الامتحانات في البوت"""
    from telebot import types
    
    @bot.message_handler(commands=['exams', 'exam', 'schedule'])
    def handle_exams(message):
        """عرض جدول الامتحانات"""
        exams = exam_system.get_upcoming_exams(days=30)
        formatted = exam_system.format_exam_schedule(exams)
        bot.send_message(message.chat.id, formatted, parse_mode="Markdown")
    
    @bot.message_handler(commands=['exam_remind'])
    def handle_exam_remind(message):
        """الاشتراك في التذكيرات"""
        result = exam_system.subscribe_to_reminders(message.chat.id)
        bot.send_message(message.chat.id, result['message'], parse_mode="Markdown")
    
    @bot.message_handler(commands=['exam_unremind'])
    def handle_exam_unremind(message):
        """إلغاء التذكيرات"""
        result = exam_system.unsubscribe_from_reminders(message.chat.id)
        bot.send_message(message.chat.id, result['message'], parse_mode="Markdown")
    
    @bot.message_handler(commands=['add_exam'])
    def handle_add_exam(message):
        """إضافة امتحان (للمسؤولين)"""
        if message.chat.id not in admin_ids:
            bot.send_message(message.chat.id, "❌ هذا الأمر للمسؤولين فقط")
            return
        
        bot.send_message(
            message.chat.id,
            "📝 *إضافة امتحان جديد*\n\n"
            "أرسل البيانات بالتنسيق التالي:\n"
            "`اسم المادة | التاريخ (YYYY-MM-DD) | الوقت (HH:MM) | المكان | المدة (دقائق)`\n\n"
            "مثال:\n"
            "`الرياضيات | 2026-02-01 | 09:00 | قاعة 101 | 120`",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(message, lambda m: process_add_exam(m, exam_system, admin_ids))
    
    def process_add_exam(message, es, admins):
        """معالجة إضافة امتحان"""
        if message.chat.id not in admins:
            return
        
        try:
            parts = [p.strip() for p in message.text.split('|')]
            
            exam_data = {
                'subject_name': parts[0],
                'exam_date': parts[1],
            }
            
            if len(parts) > 2:
                exam_data['exam_time'] = parts[2]
            if len(parts) > 3:
                exam_data['location'] = parts[3]
            if len(parts) > 4:
                exam_data['duration_minutes'] = int(parts[4])
            
            result = es.add_exam(exam_data)
            bot.send_message(message.chat.id, result['message'])
            
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطأ في التنسيق: {e}")
