# -*- coding: utf-8 -*-
"""
نظام الإعلانات المتقدم
Advanced Announcements System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
import json


class AnnouncementsSystem:
    """
    نظام الإعلانات المتقدم مع جدولة وفئات
    """
    
    # فئات الطلاب
    TARGET_GROUPS = {
        'all': {
            'id': 'all',
            'name': 'الجميع',
            'description': 'جميع المستخدمين',
            'filter': lambda user, data: True
        },
        'failing': {
            'id': 'failing',
            'name': 'الراسبين',
            'description': 'الطلاب الذين لديهم مواد راسبين فيها',
            'filter': lambda user, data: data.get('failed_subjects', 0) > 0
        },
        'at_risk': {
            'id': 'at_risk',
            'name': 'المعرضين للخطر',
            'description': 'الطلاب بمعدل أقل من 60%',
            'filter': lambda user, data: data.get('average', 100) < 60
        },
        'top_performers': {
            'id': 'top_performers',
            'name': 'المتفوقين',
            'description': 'الطلاب بمعدل فوق 85%',
            'filter': lambda user, data: data.get('average', 0) >= 85
        },
        'inactive': {
            'id': 'inactive',
            'name': 'غير النشطين',
            'description': 'لم يستخدموا البوت منذ 7 أيام',
            'filter': lambda user, data: data.get('days_inactive', 0) >= 7
        },
        'new_users': {
            'id': 'new_users',
            'name': 'المستخدمين الجدد',
            'description': 'انضموا خلال آخر 7 أيام',
            'filter': lambda user, data: data.get('days_since_join', 999) <= 7
        },
        'subscribed': {
            'id': 'subscribed',
            'name': 'المشتركين بالإشعارات',
            'description': 'المشتركين في نظام الإشعارات',
            'filter': lambda user, data: data.get('is_subscribed', False)
        }
    }
    
    def __init__(self, bot, supabase, admin_ids: List[int]):
        self.bot = bot
        self.supabase = supabase
        self.admin_ids = admin_ids
        self._scheduler_running = False
        self._scheduler_thread = None
    
    def create_announcement(self, admin_id: int, content: str, 
                           target_group: str = 'all',
                           image_url: str = None,
                           scheduled_time: datetime = None,
                           is_recurring: bool = False,
                           recurrence_interval: str = None) -> Dict:
        """إنشاء إعلان جديد"""
        try:
            if admin_id not in self.admin_ids:
                return {'success': False, 'error': 'غير مصرح'}
            
            announcement = {
                'content': content,
                'target_group': target_group,
                'image_url': image_url,
                'created_by': admin_id,
                'created_at': datetime.now().isoformat(),
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                'is_recurring': is_recurring,
                'recurrence_interval': recurrence_interval,  # 'daily', 'weekly', 'monthly'
                'status': 'scheduled' if scheduled_time else 'pending',
                'sent_count': 0,
                'failed_count': 0
            }
            
            response = self.supabase.table("announcements").insert(announcement).execute()
            
            return {
                'success': True,
                'announcement_id': response.data[0]['id'],
                'message': 'تم إنشاء الإعلان بنجاح'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_announcement(self, announcement_id: int) -> Dict:
        """إرسال إعلان"""
        try:
            # جلب الإعلان
            response = self.supabase.table("announcements").select("*").eq(
                "id", announcement_id
            ).execute()
            
            if not response.data:
                return {'success': False, 'error': 'الإعلان غير موجود'}
            
            announcement = response.data[0]
            target_group = announcement['target_group']
            
            # جلب المستخدمين المستهدفين
            users = self._get_target_users(target_group)
            
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    if announcement.get('image_url'):
                        self.bot.send_photo(
                            user['chat_id'],
                            announcement['image_url'],
                            caption=announcement['content'],
                            parse_mode="Markdown"
                        )
                    else:
                        self.bot.send_message(
                            user['chat_id'],
                            f"📢 *إعلان*\n\n{announcement['content']}",
                            parse_mode="Markdown"
                        )
                    sent_count += 1
                    time.sleep(0.05)  # تجنب Rate Limiting
                except Exception as e:
                    failed_count += 1
                    print(f"Failed to send to {user['chat_id']}: {e}")
            
            # تحديث الإحصائيات
            self.supabase.table("announcements").update({
                'status': 'sent',
                'sent_at': datetime.now().isoformat(),
                'sent_count': sent_count,
                'failed_count': failed_count
            }).eq('id', announcement_id).execute()
            
            # جدولة التكرار إذا كان متكرراً
            if announcement.get('is_recurring'):
                self._schedule_next_recurrence(announcement)
            
            return {
                'success': True,
                'sent_count': sent_count,
                'failed_count': failed_count
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_target_users(self, target_group: str) -> List[Dict]:
        """جلب المستخدمين حسب الفئة"""
        try:
            # جلب جميع المستخدمين
            users_response = self.supabase.table("bot_users").select("*").execute()
            users = users_response.data
            
            if target_group == 'all':
                return users
            
            # جلب بيانات الطلاب
            filtered_users = []
            for user in users:
                user_data = self._get_user_academic_data(user['chat_id'])
                
                if target_group in self.TARGET_GROUPS:
                    filter_func = self.TARGET_GROUPS[target_group]['filter']
                    if filter_func(user, user_data):
                        filtered_users.append(user)
            
            return filtered_users
            
        except Exception as e:
            print(f"Error getting target users: {e}")
            return []
    
    def _get_user_academic_data(self, chat_id: int) -> Dict:
        """جلب بيانات الطالب الأكاديمية"""
        try:
            # البحث عن الملف الشخصي
            profile = self.supabase.table("mini_app_profiles").select("student_id").eq(
                "telegram_id", chat_id
            ).execute()
            
            if not profile.data:
                return {}
            
            student_id = profile.data[0]['student_id']
            
            # جلب النتائج
            results = self.supabase.table("all_marks").select("total_grade").eq(
                "student_id", student_id
            ).execute()
            
            if not results.data:
                return {}
            
            grades = [r['total_grade'] for r in results.data if r['total_grade']]
            failed = len([g for g in grades if g < 60])
            
            return {
                'average': sum(grades) / len(grades) if grades else 0,
                'failed_subjects': failed,
                'total_subjects': len(grades)
            }
            
        except Exception as e:
            return {}
    
    def _schedule_next_recurrence(self, announcement: Dict):
        """جدولة التكرار التالي"""
        try:
            interval = announcement.get('recurrence_interval')
            
            if interval == 'daily':
                next_time = datetime.now() + timedelta(days=1)
            elif interval == 'weekly':
                next_time = datetime.now() + timedelta(weeks=1)
            elif interval == 'monthly':
                next_time = datetime.now() + timedelta(days=30)
            else:
                return
            
            # إنشاء إعلان جديد مجدول
            self.create_announcement(
                admin_id=announcement['created_by'],
                content=announcement['content'],
                target_group=announcement['target_group'],
                image_url=announcement.get('image_url'),
                scheduled_time=next_time,
                is_recurring=True,
                recurrence_interval=interval
            )
            
        except Exception as e:
            print(f"Error scheduling recurrence: {e}")
    
    def get_scheduled_announcements(self) -> List[Dict]:
        """جلب الإعلانات المجدولة"""
        try:
            response = self.supabase.table("announcements").select("*").eq(
                "status", "scheduled"
            ).order("scheduled_time").execute()
            
            return response.data
            
        except Exception as e:
            print(f"Error getting scheduled: {e}")
            return []
    
    def cancel_announcement(self, announcement_id: int) -> Dict:
        """إلغاء إعلان مجدول"""
        try:
            self.supabase.table("announcements").update({
                'status': 'cancelled'
            }).eq('id', announcement_id).execute()
            
            return {'success': True, 'message': 'تم إلغاء الإعلان'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_announcement_stats(self) -> Dict:
        """إحصائيات الإعلانات"""
        try:
            all_announcements = self.supabase.table("announcements").select("*").execute()
            
            total = len(all_announcements.data)
            sent = len([a for a in all_announcements.data if a['status'] == 'sent'])
            scheduled = len([a for a in all_announcements.data if a['status'] == 'scheduled'])
            
            total_sent = sum(a.get('sent_count', 0) for a in all_announcements.data)
            total_failed = sum(a.get('failed_count', 0) for a in all_announcements.data)
            
            return {
                'total_announcements': total,
                'sent_announcements': sent,
                'scheduled_announcements': scheduled,
                'total_messages_sent': total_sent,
                'total_messages_failed': total_failed,
                'success_rate': (total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0
            }
            
        except Exception as e:
            return {}
    
    def start_scheduler(self, check_interval: int = 60):
        """بدء مجدول الإعلانات"""
        if self._scheduler_running:
            return
        
        self._scheduler_running = True
        
        def scheduler_loop():
            while self._scheduler_running:
                try:
                    # جلب الإعلانات المجدولة
                    scheduled = self.get_scheduled_announcements()
                    now = datetime.now()
                    
                    for announcement in scheduled:
                        scheduled_time = datetime.fromisoformat(announcement['scheduled_time'])
                        
                        if scheduled_time <= now:
                            print(f"📢 إرسال إعلان مجدول #{announcement['id']}")
                            self.send_announcement(announcement['id'])
                    
                except Exception as e:
                    print(f"Scheduler error: {e}")
                
                time.sleep(check_interval)
        
        self._scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        print("🕐 تم تشغيل مجدول الإعلانات")
    
    def stop_scheduler(self):
        """إيقاف المجدول"""
        self._scheduler_running = False


def setup_announcements_commands(bot, announcements_system, admin_ids):
    """إعداد أوامر الإعلانات"""
    from telebot import types
    
    @bot.message_handler(commands=['announce', 'اعلان'])
    def start_announcement(message):
        """بدء إنشاء إعلان"""
        if message.chat.id not in admin_ids:
            bot.send_message(message.chat.id, "❌ هذا الأمر للمشرفين فقط")
            return
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        for group_id, group_info in AnnouncementsSystem.TARGET_GROUPS.items():
            markup.add(types.InlineKeyboardButton(
                f"{group_info['name']}",
                callback_data=f"ann_target_{group_id}"
            ))
        
        bot.send_message(
            message.chat.id,
            "📢 *إنشاء إعلان جديد*\n\n"
            "اختر الفئة المستهدفة:",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('ann_target_'))
    def select_target(call):
        """اختيار الفئة المستهدفة"""
        target = call.data.replace('ann_target_', '')
        
        bot.answer_callback_query(call.id)
        
        # حفظ الاختيار مؤقتاً
        bot.send_message(
            call.message.chat.id,
            f"✅ الفئة: {AnnouncementsSystem.TARGET_GROUPS[target]['name']}\n\n"
            "📝 الآن أرسل نص الإعلان:",
            parse_mode="Markdown"
        )
        
        bot.register_next_step_handler(
            call.message, 
            lambda m: receive_announcement_text(m, target)
        )
    
    def receive_announcement_text(message, target):
        """استلام نص الإعلان"""
        content = message.text
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📤 إرسال الآن", callback_data=f"ann_send_now_{target}"),
            types.InlineKeyboardButton("🕐 جدولة", callback_data=f"ann_schedule_{target}")
        )
        markup.add(
            types.InlineKeyboardButton("🖼️ إضافة صورة", callback_data=f"ann_add_image_{target}"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="ann_cancel")
        )
        
        # حفظ المحتوى مؤقتاً
        bot.send_message(
            message.chat.id,
            f"📢 *معاينة الإعلان:*\n\n{content}\n\n"
            f"🎯 الفئة: {AnnouncementsSystem.TARGET_GROUPS[target]['name']}\n\n"
            "اختر الإجراء:",
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        # تخزين مؤقت
        if not hasattr(bot, 'pending_announcements'):
            bot.pending_announcements = {}
        bot.pending_announcements[message.chat.id] = {
            'content': content,
            'target': target
        }
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('ann_send_now_'))
    def send_now(call):
        """إرسال الإعلان الآن"""
        if call.message.chat.id not in admin_ids:
            return
        
        pending = getattr(bot, 'pending_announcements', {}).get(call.message.chat.id)
        if not pending:
            bot.answer_callback_query(call.id, "❌ انتهت الجلسة")
            return
        
        bot.answer_callback_query(call.id, "⏳ جاري الإرسال...")
        
        # إنشاء وإرسال الإعلان
        result = announcements_system.create_announcement(
            admin_id=call.message.chat.id,
            content=pending['content'],
            target_group=pending['target']
        )
        
        if result['success']:
            send_result = announcements_system.send_announcement(result['announcement_id'])
            
            bot.edit_message_text(
                f"✅ *تم إرسال الإعلان*\n\n"
                f"📤 أُرسل إلى: {send_result.get('sent_count', 0)} مستخدم\n"
                f"❌ فشل: {send_result.get('failed_count', 0)}",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                f"❌ فشل: {result.get('error')}",
                call.message.chat.id,
                call.message.message_id
            )
    
    @bot.message_handler(commands=['announcement_stats', 'احصائيات_الاعلانات'])
    def show_announcement_stats(message):
        """عرض إحصائيات الإعلانات"""
        if message.chat.id not in admin_ids:
            return
        
        stats = announcements_system.get_announcement_stats()
        
        msg = (
            "📊 *إحصائيات الإعلانات*\n\n"
            f"📢 إجمالي الإعلانات: {stats.get('total_announcements', 0)}\n"
            f"✅ المُرسلة: {stats.get('sent_announcements', 0)}\n"
            f"🕐 المجدولة: {stats.get('scheduled_announcements', 0)}\n\n"
            f"📤 إجمالي الرسائل: {stats.get('total_messages_sent', 0)}\n"
            f"❌ الفاشلة: {stats.get('total_messages_failed', 0)}\n"
            f"📈 نسبة النجاح: {stats.get('success_rate', 0):.1f}%"
        )
        
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
