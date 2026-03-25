# -*- coding: utf-8 -*-
"""
نظام إحصائيات الاستخدام الشامل
تتبع وتحليل استخدام البوت
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import threading
import json


class UsageAnalytics:
    """
    نظام تتبع وتحليل استخدام البوت
    - تسجيل كل طلب
    - إحصائيات المستخدمين
    - أوقات الذروة
    - أكثر الأوامر استخداماً
    """
    
    def __init__(self, supabase):
        """
        Args:
            supabase: عميل Supabase
        """
        self.supabase = supabase
        self._lock = threading.Lock()
        
        # Cache محلي للإحصائيات السريعة
        self._today_stats = defaultdict(int)
        self._hourly_stats = defaultdict(int)
        self._user_stats = defaultdict(int)
        self._command_stats = defaultdict(int)
        
        # تحميل إحصائيات اليوم
        self._load_today_stats()
    
    def _load_today_stats(self):
        """تحميل إحصائيات اليوم من قاعدة البيانات"""
        try:
            today = datetime.now().date().isoformat()
            response = self.supabase.table("usage_analytics").select("*")\
                .gte("created_at", today).execute()
            
            for row in response.data:
                self._user_stats[row['user_id']] += 1
                self._command_stats[row['action_type']] += 1
                hour = datetime.fromisoformat(row['created_at'].replace('Z', '')).hour
                self._hourly_stats[hour] += 1
            
            print(f"✅ تم تحميل {len(response.data)} سجل استخدام لليوم")
        except Exception as e:
            print(f"⚠️ خطأ في تحميل إحصائيات اليوم: {e}")
    
    def log_action(self, user_id: int, action_type: str, details: dict = None, 
                   username: str = None, first_name: str = None):
        """
        تسجيل إجراء المستخدم
        
        Args:
            user_id: معرف المستخدم
            action_type: نوع الإجراء (search, stats, top, notify, exam, etc.)
            details: تفاصيل إضافية
            username: اسم المستخدم
            first_name: الاسم الأول
        """
        try:
            now = datetime.now()
            
            # تحديث الـ Cache المحلي
            with self._lock:
                self._user_stats[user_id] += 1
                self._command_stats[action_type] += 1
                self._hourly_stats[now.hour] += 1
                self._today_stats['total'] += 1
            
            # حفظ في قاعدة البيانات
            record = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'action_type': action_type,
                'action_details': json.dumps(details) if details else None,
                'created_at': now.isoformat(),
                'hour_of_day': now.hour,
                'day_of_week': now.weekday()
            }
            
            self.supabase.table("usage_analytics").insert(record).execute()
            
        except Exception as e:
            print(f"⚠️ خطأ في تسجيل الإجراء: {e}")
    
    def get_today_summary(self) -> dict:
        """ملخص إحصائيات اليوم"""
        try:
            today = datetime.now().date().isoformat()
            
            response = self.supabase.table("usage_analytics").select("*")\
                .gte("created_at", today).execute()
            
            total_requests = len(response.data)
            unique_users = len(set(r['user_id'] for r in response.data))
            
            # أكثر الأوامر استخداماً
            command_counts = defaultdict(int)
            for r in response.data:
                command_counts[r['action_type']] += 1
            
            top_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'date': today,
                'total_requests': total_requests,
                'unique_users': unique_users,
                'avg_per_user': round(total_requests / unique_users, 2) if unique_users > 0 else 0,
                'top_commands': top_commands
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_top_users(self, limit: int = 10, days: int = 7) -> List[dict]:
        """أكثر المستخدمين نشاطاً"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table("usage_analytics").select("user_id, username, first_name")\
                .gte("created_at", start_date).execute()
            
            user_counts = defaultdict(lambda: {'count': 0, 'username': None, 'first_name': None})
            
            for r in response.data:
                uid = r['user_id']
                user_counts[uid]['count'] += 1
                user_counts[uid]['username'] = r.get('username')
                user_counts[uid]['first_name'] = r.get('first_name')
            
            # ترتيب حسب الاستخدام
            sorted_users = sorted(user_counts.items(), key=lambda x: x[1]['count'], reverse=True)[:limit]
            
            result = []
            for i, (user_id, data) in enumerate(sorted_users, 1):
                result.append({
                    'rank': i,
                    'user_id': user_id,
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'request_count': data['count']
                })
            
            return result
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return []
    
    def get_peak_hours(self, days: int = 7) -> List[Tuple[int, int]]:
        """أوقات الذروة"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table("usage_analytics").select("hour_of_day")\
                .gte("created_at", start_date).execute()
            
            hourly_counts = defaultdict(int)
            for r in response.data:
                hourly_counts[r['hour_of_day']] += 1
            
            # ترتيب حسب الاستخدام
            sorted_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_hours
        except Exception as e:
            return []
    
    def get_command_stats(self, days: int = 7) -> dict:
        """إحصائيات الأوامر"""
        try:
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table("usage_analytics").select("action_type")\
                .gte("created_at", start_date).execute()
            
            command_counts = defaultdict(int)
            for r in response.data:
                command_counts[r['action_type']] += 1
            
            total = sum(command_counts.values())
            
            result = {}
            for cmd, count in sorted(command_counts.items(), key=lambda x: x[1], reverse=True):
                result[cmd] = {
                    'count': count,
                    'percentage': round(count / total * 100, 2) if total > 0 else 0
                }
            
            return result
        except Exception as e:
            return {}
    
    def get_weekly_trend(self) -> List[dict]:
        """اتجاه الاستخدام الأسبوعي"""
        try:
            result = []
            
            for i in range(7):
                date = datetime.now().date() - timedelta(days=i)
                start = date.isoformat()
                end = (date + timedelta(days=1)).isoformat()
                
                response = self.supabase.table("usage_analytics").select("user_id", count="exact")\
                    .gte("created_at", start).lt("created_at", end).execute()
                
                result.append({
                    'date': start,
                    'day_name': self._get_arabic_day(date.weekday()),
                    'total_requests': response.count or 0
                })
            
            return list(reversed(result))
        except Exception as e:
            return []
    
    def get_user_history(self, user_id: int, limit: int = 20) -> List[dict]:
        """سجل استخدام مستخدم معين"""
        try:
            response = self.supabase.table("usage_analytics").select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit).execute()
            
            return response.data
        except Exception as e:
            return []
    
    def get_full_report(self, days: int = 7) -> dict:
        """تقرير شامل"""
        return {
            'today': self.get_today_summary(),
            'top_users': self.get_top_users(limit=10, days=days),
            'peak_hours': self.get_peak_hours(days=days)[:5],
            'command_stats': self.get_command_stats(days=days),
            'weekly_trend': self.get_weekly_trend(),
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_arabic_day(self, weekday: int) -> str:
        """تحويل رقم اليوم لاسم عربي"""
        days = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        return days[weekday]
    
    def format_stats_message(self, days: int = 7) -> str:
        """تنسيق رسالة الإحصائيات للإرسال"""
        report = self.get_full_report(days)
        today = report['today']
        
        message = "📊 *إحصائيات استخدام البوت*\n"
        message += "═" * 28 + "\n\n"
        
        # إحصائيات اليوم
        message += "📅 *إحصائيات اليوم:*\n"
        message += f"├ إجمالي الطلبات: `{today.get('total_requests', 0)}`\n"
        message += f"├ المستخدمين الفريدين: `{today.get('unique_users', 0)}`\n"
        message += f"└ متوسط لكل مستخدم: `{today.get('avg_per_user', 0)}`\n\n"
        
        # أكثر المستخدمين نشاطاً
        message += f"🏆 *أكثر المستخدمين نشاطاً (آخر {days} أيام):*\n"
        for user in report['top_users'][:5]:
            name = user.get('first_name') or user.get('username') or f"User {user['user_id']}"
            message += f"  {user['rank']}. {name}: `{user['request_count']}` طلب\n"
        message += "\n"
        
        # أوقات الذروة
        message += "⏰ *أوقات الذروة:*\n"
        for hour, count in report['peak_hours'][:3]:
            message += f"  • الساعة {hour}:00 - `{count}` طلب\n"
        message += "\n"
        
        # أكثر الأوامر استخداماً
        message += "📌 *أكثر الأوامر استخداماً:*\n"
        cmd_stats = report['command_stats']
        for cmd, data in list(cmd_stats.items())[:5]:
            emoji = self._get_command_emoji(cmd)
            message += f"  {emoji} {cmd}: `{data['count']}` ({data['percentage']}%)\n"
        message += "\n"
        
        # الاتجاه الأسبوعي
        message += "📈 *الاتجاه الأسبوعي:*\n"
        for day in report['weekly_trend']:
            bar = "█" * min(int(day['total_requests'] / 10), 10)
            message += f"  {day['day_name']}: {bar} `{day['total_requests']}`\n"
        
        message += "\n" + "─" * 28
        message += f"\n🕐 آخر تحديث: {datetime.now().strftime('%H:%M')}"
        
        return message
    
    def _get_command_emoji(self, cmd: str) -> str:
        """إيموجي لكل أمر"""
        emojis = {
            'search': '🔍',
            'start': '▶️',
            'stats': '📊',
            'top': '🏆',
            'notify': '🔔',
            'exams': '📅',
            'help': '❓',
            'admin': '👨‍💼',
            'chart': '📈',
            'pdf': '📄'
        }
        return emojis.get(cmd, '•')


def setup_analytics_commands(bot, analytics: UsageAnalytics, admin_ids: list):
    """إعداد أوامر الإحصائيات"""
    
    @bot.message_handler(commands=['usage', 'analytics', 'stats_usage'])
    def handle_usage_stats(message):
        """عرض إحصائيات الاستخدام (للمسؤولين)"""
        if message.chat.id not in admin_ids:
            bot.send_message(message.chat.id, "❌ هذا الأمر للمسؤولين فقط")
            return
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        stats_message = analytics.format_stats_message(days=7)
        bot.send_message(message.chat.id, stats_message, parse_mode="Markdown")
    
    @bot.message_handler(commands=['top_users'])
    def handle_top_users(message):
        """عرض أكثر المستخدمين نشاطاً"""
        if message.chat.id not in admin_ids:
            bot.send_message(message.chat.id, "❌ هذا الأمر للمسؤولين فقط")
            return
        
        top_users = analytics.get_top_users(limit=15, days=7)
        
        msg = "🏆 *أكثر 15 مستخدم نشاطاً (آخر 7 أيام):*\n\n"
        
        for user in top_users:
            medal = "🥇" if user['rank'] == 1 else "🥈" if user['rank'] == 2 else "🥉" if user['rank'] == 3 else f"{user['rank']}."
            name = user.get('first_name') or user.get('username') or f"ID: {user['user_id']}"
            msg += f"{medal} *{name}*\n"
            msg += f"    └ `{user['request_count']}` طلب\n"
        
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    
    @bot.message_handler(commands=['my_usage'])
    def handle_my_usage(message):
        """عرض سجل استخدام المستخدم الحالي"""
        history = analytics.get_user_history(message.chat.id, limit=10)
        
        if not history:
            bot.send_message(message.chat.id, "📭 لا يوجد سجل استخدام لك بعد.")
            return
        
        msg = "📊 *سجل استخدامك الأخير:*\n\n"
        
        for i, record in enumerate(history, 1):
            action = record.get('action_type', 'unknown')
            time = record.get('created_at', '')[:16].replace('T', ' ')
            emoji = analytics._get_command_emoji(action)
            msg += f"{i}. {emoji} `{action}` - {time}\n"
        
        msg += f"\n📈 إجمالي طلباتك: `{len(analytics.get_user_history(message.chat.id, limit=1000))}`"
        
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")


# Middleware لتسجيل جميع الطلبات
class AnalyticsMiddleware:
    """Middleware لتسجيل الطلبات تلقائياً"""
    
    def __init__(self, analytics: UsageAnalytics):
        self.analytics = analytics
    
    def log_message(self, message):
        """تسجيل رسالة"""
        action_type = 'message'
        details = None
        
        # تحديد نوع الإجراء
        if message.text:
            text = message.text.strip()
            
            if text.startswith('/'):
                # أمر
                cmd = text.split()[0].replace('/', '').replace('@', '')
                action_type = cmd
            elif text.isdigit():
                # بحث برقم
                action_type = 'search_by_id'
                details = {'query_length': len(text)}
            else:
                # بحث بالاسم
                action_type = 'search_by_name'
                details = {'query_length': len(text)}
        
        self.analytics.log_action(
            user_id=message.chat.id,
            action_type=action_type,
            details=details,
            username=message.from_user.username if message.from_user else None,
            first_name=message.from_user.first_name if message.from_user else None
        )
    
    def log_callback(self, call):
        """تسجيل callback"""
        action_type = f"callback_{call.data.split('_')[0]}"
        
        self.analytics.log_action(
            user_id=call.message.chat.id,
            action_type=action_type,
            details={'callback_data': call.data},
            username=call.from_user.username if call.from_user else None,
            first_name=call.from_user.first_name if call.from_user else None
        )
