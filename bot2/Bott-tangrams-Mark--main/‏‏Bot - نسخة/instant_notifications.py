# -*- coding: utf-8 -*-
"""
نظام الإشعارات الفورية المحسن
يرسل إشعار فوري للطالب عند صدور نتائج جديدة
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Set, Optional, List
import hashlib
import json


class InstantNotificationSystem:
    """
    نظام الإشعارات الفورية
    - يراقب قاعدة البيانات للنتائج الجديدة
    - يرسل إشعار فوري للطلاب المشتركين
    - يتطلب اشتراك في قناة المطور
    """
    
    def __init__(self, bot, supabase, channel_username: str = None):
        """
        Args:
            bot: instance من telebot
            supabase: عميل Supabase
            channel_username: اسم قناة المطور (للتحقق من الاشتراك)
        """
        self.bot = bot
        self.supabase = supabase
        self.channel_username = channel_username
        
        # قاموس المشتركين: {chat_id: student_id}
        self.subscribers: Dict[int, str] = {}
        
        # آخر hash للنتائج لكل طالب (لكشف التغييرات)
        self.last_results_hash: Dict[str, str] = {}
        
        # حالة التشغيل
        self._running = False
        self._check_interval = 60  # فحص كل دقيقة
        self._monitor_thread = None
        
        # إحصائيات
        self.stats = {
            'notifications_sent': 0,
            'last_check': None,
            'active_subscribers': 0
        }
        
        # تحميل المشتركين من قاعدة البيانات
        self._load_subscribers()
    
    def _load_subscribers(self):
        """تحميل المشتركين من قاعدة البيانات"""
        try:
            response = self.supabase.table("notification_subscribers").select("*").eq("is_active", True).execute()
            for row in response.data:
                self.subscribers[row['chat_id']] = row['student_id']
                if row.get('last_results_hash'):
                    self.last_results_hash[row['student_id']] = row['last_results_hash']
            
            self.stats['active_subscribers'] = len(self.subscribers)
            print(f"✅ تم تحميل {len(self.subscribers)} مشترك في الإشعارات")
        except Exception as e:
            print(f"⚠️ خطأ في تحميل المشتركين: {e}")
    
    def subscribe(self, chat_id: int, student_id: str) -> dict:
        """
        تسجيل طالب في نظام الإشعارات
        
        Args:
            chat_id: معرف المحادثة
            student_id: الرقم الامتحاني
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # التحقق من الاشتراك في القناة
        if not self._check_channel_subscription(chat_id):
            return {
                'success': False,
                'message': '❌ يجب الاشتراك في قناة المطور أولاً للحصول على الإشعارات الفورية!\n\n'
                          f'👇 اشترك في القناة ثم حاول مرة أخرى:\n{self.channel_username}'
            }
        
        # التحقق من وجود الطالب في قاعدة البيانات
        if not self._verify_student_exists(student_id):
            return {
                'success': False,
                'message': f'❌ الرقم الامتحاني {student_id} غير موجود في قاعدة البيانات.'
            }
        
        try:
            # حفظ في قاعدة البيانات
            self.supabase.table("notification_subscribers").upsert({
                'chat_id': chat_id,
                'student_id': student_id,
                'is_active': True,
                'subscribed_at': datetime.now().isoformat(),
                'last_results_hash': self._get_results_hash(student_id)
            }).execute()
            
            # إضافة للقاموس المحلي
            self.subscribers[chat_id] = student_id
            self.last_results_hash[student_id] = self._get_results_hash(student_id)
            self.stats['active_subscribers'] = len(self.subscribers)
            
            return {
                'success': True,
                'message': f'✅ تم تفعيل الإشعارات الفورية للرقم: {student_id}\n\n'
                          '🔔 سيصلك إشعار فوري عند صدور أي نتيجة جديدة!\n\n'
                          '⚠️ ملاحظة: مغادرة قناة المطور ستوقف الإشعارات.'
            }
            
        except Exception as e:
            print(f"❌ خطأ في التسجيل: {e}")
            return {
                'success': False,
                'message': '❌ حدث خطأ أثناء التسجيل. يرجى المحاولة لاحقاً.'
            }
    
    def unsubscribe(self, chat_id: int) -> dict:
        """إلغاء الاشتراك في الإشعارات"""
        try:
            self.supabase.table("notification_subscribers").update({
                'is_active': False,
                'unsubscribed_at': datetime.now().isoformat()
            }).eq('chat_id', chat_id).execute()
            
            if chat_id in self.subscribers:
                del self.subscribers[chat_id]
            
            self.stats['active_subscribers'] = len(self.subscribers)
            
            return {
                'success': True,
                'message': '✅ تم إلغاء الاشتراك في الإشعارات الفورية.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'❌ حدث خطأ: {e}'
            }
    
    def get_subscription_status(self, chat_id: int) -> dict:
        """الحصول على حالة الاشتراك"""
        if chat_id in self.subscribers:
            student_id = self.subscribers[chat_id]
            return {
                'is_subscribed': True,
                'student_id': student_id,
                'message': f'✅ أنت مشترك في الإشعارات للرقم: {student_id}'
            }
        return {
            'is_subscribed': False,
            'student_id': None,
            'message': '❌ أنت غير مشترك في الإشعارات.\nاستخدم /notify للاشتراك.'
        }
    
    def _check_channel_subscription(self, chat_id: int) -> bool:
        """التحقق من اشتراك المستخدم في القناة"""
        if not self.channel_username:
            return True  # إذا لم تُحدد قناة، اسمح للجميع
        
        try:
            member = self.bot.get_chat_member(self.channel_username, chat_id)
            return member.status in ['member', 'administrator', 'creator']
        except Exception as e:
            print(f"⚠️ خطأ في التحقق من الاشتراك: {e}")
            return False
    
    def _verify_student_exists(self, student_id: str) -> bool:
        """التحقق من وجود الطالب في قاعدة البيانات"""
        try:
            response = self.supabase.table("all_marks").select("student_id").eq("student_id", student_id).limit(1).execute()
            return len(response.data) > 0
        except:
            return False
    
    def _get_results_hash(self, student_id: str) -> str:
        """حساب hash لنتائج الطالب لكشف التغييرات"""
        try:
            response = self.supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
            if response.data:
                # ترتيب البيانات وتحويلها لـ hash
                sorted_data = sorted(response.data, key=lambda x: x.get('subject_name', ''))
                data_str = json.dumps(sorted_data, sort_keys=True, ensure_ascii=False)
                return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            print(f"⚠️ خطأ في حساب hash: {e}")
        return ""
    
    def _get_new_results(self, student_id: str, old_hash: str) -> List[dict]:
        """جلب النتائج الجديدة"""
        try:
            response = self.supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
            return response.data
        except:
            return []
    
    def _format_notification(self, student_id: str, results: List[dict]) -> str:
        """تنسيق رسالة الإشعار"""
        if not results:
            return ""
        
        student_name = results[0].get('student_name', 'طالب')
        
        message = f"🔔 *إشعار نتائج جديدة!*\n\n"
        message += f"👤 الطالب: `{student_name}`\n"
        message += f"🔢 الرقم: `{student_id}`\n"
        message += f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        message += "📚 *النتائج:*\n"
        message += "─" * 25 + "\n"
        
        total = 0
        count = 0
        for r in results:
            subject = r.get('subject_name', 'مادة')
            grade = r.get('total_grade', 0)
            result_status = "✅" if grade and float(grade) >= 60 else "❌"
            message += f"{result_status} {subject}: *{grade}*\n"
            if grade:
                total += float(grade)
                count += 1
        
        if count > 0:
            avg = total / count
            message += "─" * 25 + "\n"
            message += f"📊 المعدل: *{avg:.2f}*\n"
        
        message += "\n💡 أرسل رقمك للحصول على التفاصيل الكاملة."
        
        return message
    
    def _check_for_updates(self):
        """فحص التحديثات لجميع المشتركين"""
        print(f"🔍 فحص التحديثات لـ {len(self.subscribers)} مشترك...")
        
        notifications_sent = 0
        subscribers_to_remove = []
        
        for chat_id, student_id in list(self.subscribers.items()):
            try:
                # التحقق من الاشتراك في القناة
                if not self._check_channel_subscription(chat_id):
                    # إرسال تحذير وإلغاء الاشتراك
                    try:
                        self.bot.send_message(
                            chat_id,
                            "⚠️ *تم إيقاف الإشعارات الفورية*\n\n"
                            "لقد غادرت قناة المطور، لذلك تم إيقاف الإشعارات.\n\n"
                            f"👇 للاستمرار في تلقي الإشعارات، اشترك في:\n{self.channel_username}\n\n"
                            "ثم استخدم /notify للاشتراك مجدداً.",
                            parse_mode="Markdown"
                        )
                    except:
                        pass
                    subscribers_to_remove.append(chat_id)
                    continue
                
                # حساب hash جديد
                new_hash = self._get_results_hash(student_id)
                old_hash = self.last_results_hash.get(student_id, "")
                
                # إذا تغيرت النتائج
                if new_hash and new_hash != old_hash:
                    results = self._get_new_results(student_id, old_hash)
                    notification_msg = self._format_notification(student_id, results)
                    
                    if notification_msg:
                        try:
                            self.bot.send_message(chat_id, notification_msg, parse_mode="Markdown")
                            notifications_sent += 1
                            print(f"✅ إشعار مُرسل لـ {chat_id} (طالب: {student_id})")
                        except Exception as e:
                            print(f"⚠️ فشل إرسال إشعار لـ {chat_id}: {e}")
                    
                    # تحديث الـ hash
                    self.last_results_hash[student_id] = new_hash
                    
                    # حفظ في قاعدة البيانات
                    try:
                        self.supabase.table("notification_subscribers").update({
                            'last_results_hash': new_hash,
                            'last_notification': datetime.now().isoformat()
                        }).eq('chat_id', chat_id).execute()
                    except:
                        pass
                        
            except Exception as e:
                print(f"⚠️ خطأ في فحص {chat_id}: {e}")
        
        # إزالة المشتركين الذين غادروا القناة
        for chat_id in subscribers_to_remove:
            self.unsubscribe(chat_id)
        
        self.stats['notifications_sent'] += notifications_sent
        self.stats['last_check'] = datetime.now().isoformat()
        
        if notifications_sent > 0:
            print(f"📤 تم إرسال {notifications_sent} إشعار")
    
    def _monitor_loop(self):
        """حلقة المراقبة"""
        while self._running:
            try:
                self._check_for_updates()
            except Exception as e:
                print(f"❌ خطأ في حلقة المراقبة: {e}")
            
            time.sleep(self._check_interval)
    
    def start(self, check_interval: int = 60):
        """بدء نظام الإشعارات"""
        if self._running:
            print("⚠️ النظام يعمل بالفعل")
            return
        
        self._check_interval = check_interval
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print(f"🚀 نظام الإشعارات الفورية يعمل (فحص كل {check_interval} ثانية)")
    
    def stop(self):
        """إيقاف نظام الإشعارات"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("🛑 تم إيقاف نظام الإشعارات")
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات النظام"""
        return {
            **self.stats,
            'is_running': self._running,
            'check_interval': self._check_interval
        }


# دالة مساعدة للتكامل مع البوت
def setup_notification_commands(bot, notification_system):
    """إعداد أوامر الإشعارات في البوت"""
    
    @bot.message_handler(commands=['notify'])
    def handle_notify(message):
        """معالج أمر /notify"""
        chat_id = message.chat.id
        
        # التحقق من حالة الاشتراك الحالية
        status = notification_system.get_subscription_status(chat_id)
        
        if status['is_subscribed']:
            # المستخدم مشترك بالفعل - عرض خيارات
            from telebot import types
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("❌ إلغاء الاشتراك", callback_data="notify_unsub"),
                types.InlineKeyboardButton("🔄 تغيير الرقم", callback_data="notify_change")
            )
            bot.send_message(
                chat_id,
                f"🔔 *حالة الإشعارات*\n\n"
                f"✅ أنت مشترك في الإشعارات الفورية\n"
                f"📝 الرقم الامتحاني: `{status['student_id']}`\n\n"
                f"اختر أحد الخيارات:",
                parse_mode="Markdown",
                reply_markup=markup
            )
        else:
            # المستخدم غير مشترك - طلب الرقم
            bot.send_message(
                chat_id,
                "🔔 *نظام الإشعارات الفورية*\n\n"
                "سيصلك إشعار فوري عند صدور أي نتيجة جديدة!\n\n"
                "📝 أرسل رقمك الامتحاني للاشتراك:",
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(message, lambda m: process_notify_subscription(m, notification_system))
    
    @bot.message_handler(commands=['notify_status'])
    def handle_notify_status(message):
        """عرض حالة الاشتراك"""
        status = notification_system.get_subscription_status(message.chat.id)
        bot.send_message(message.chat.id, status['message'], parse_mode="Markdown")
    
    def process_notify_subscription(message, ns):
        """معالجة طلب الاشتراك"""
        student_id = message.text.strip()
        result = ns.subscribe(message.chat.id, student_id)
        bot.send_message(message.chat.id, result['message'], parse_mode="Markdown")
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('notify_'))
    def handle_notify_callback(call):
        """معالج callbacks الإشعارات"""
        chat_id = call.message.chat.id
        
        if call.data == "notify_unsub":
            result = notification_system.unsubscribe(chat_id)
            bot.answer_callback_query(call.id, result['message'])
            bot.edit_message_text(result['message'], chat_id, call.message.message_id)
        
        elif call.data == "notify_change":
            bot.answer_callback_query(call.id)
            bot.send_message(chat_id, "📝 أرسل الرقم الامتحاني الجديد:")
            bot.register_next_step_handler(call.message, lambda m: process_notify_subscription(m, notification_system))
