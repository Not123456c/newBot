# -*- coding: utf-8 -*-
"""
نظام الإنجازات والشارات
Achievements & Badges System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json


class AchievementsSystem:
    """
    نظام الإنجازات والشارات للطلاب
    """
    
    # تعريف الإنجازات
    ACHIEVEMENTS = {
        # إنجازات الأداء الأكاديمي
        'top_performer': {
            'id': 'top_performer',
            'name': '🥇 المتفوق',
            'name_en': 'Top Performer',
            'description': 'حصلت على معدل فوق 90%',
            'icon': '🥇',
            'category': 'academic',
            'points': 100,
            'condition': lambda data: data.get('average', 0) >= 90
        },
        'excellent': {
            'id': 'excellent',
            'name': '⭐ ممتاز',
            'name_en': 'Excellent',
            'description': 'حصلت على معدل فوق 85%',
            'icon': '⭐',
            'category': 'academic',
            'points': 75,
            'condition': lambda data: data.get('average', 0) >= 85
        },
        'good_student': {
            'id': 'good_student',
            'name': '✨ جيد جداً',
            'name_en': 'Very Good',
            'description': 'حصلت على معدل فوق 75%',
            'icon': '✨',
            'category': 'academic',
            'points': 50,
            'condition': lambda data: data.get('average', 0) >= 75
        },
        'perfect_score': {
            'id': 'perfect_score',
            'name': '💯 الدرجة الكاملة',
            'name_en': 'Perfect Score',
            'description': 'حصلت على 100% في مادة',
            'icon': '💯',
            'category': 'academic',
            'points': 150,
            'condition': lambda data: data.get('highest_grade', 0) == 100
        },
        'subject_star': {
            'id': 'subject_star',
            'name': '🌟 نجم المادة',
            'name_en': 'Subject Star',
            'description': 'حصلت على أعلى درجة في مادة على الدفعة',
            'icon': '🌟',
            'category': 'academic',
            'points': 200,
            'condition': lambda data: data.get('is_top_in_subject', False)
        },
        'all_passed': {
            'id': 'all_passed',
            'name': '✅ ناجح بالكامل',
            'name_en': 'All Passed',
            'description': 'نجحت في جميع المواد',
            'icon': '✅',
            'category': 'academic',
            'points': 100,
            'condition': lambda data: data.get('success_rate', 0) == 100
        },
        
        # إنجازات التحسن
        'improver': {
            'id': 'improver',
            'name': '🔥 متحسن',
            'name_en': 'Improver',
            'description': 'رفعت معدلك 10% عن الفصل السابق',
            'icon': '🔥',
            'category': 'improvement',
            'points': 80,
            'condition': lambda data: data.get('improvement', 0) >= 10
        },
        'rising_star': {
            'id': 'rising_star',
            'name': '📈 نجم صاعد',
            'name_en': 'Rising Star',
            'description': 'رفعت معدلك 5% عن الفصل السابق',
            'icon': '📈',
            'category': 'improvement',
            'points': 50,
            'condition': lambda data: data.get('improvement', 0) >= 5
        },
        'comeback': {
            'id': 'comeback',
            'name': '💪 العودة القوية',
            'name_en': 'Comeback',
            'description': 'نجحت في مادة كنت راسباً فيها',
            'icon': '💪',
            'category': 'improvement',
            'points': 100,
            'condition': lambda data: data.get('recovered_subjects', 0) > 0
        },
        
        # إنجازات الاستخدام
        'persistent': {
            'id': 'persistent',
            'name': '📚 مثابر',
            'name_en': 'Persistent',
            'description': 'استخدمت البوت 30 يوم متتالي',
            'icon': '📚',
            'category': 'usage',
            'points': 50,
            'condition': lambda data: data.get('streak_days', 0) >= 30
        },
        'regular': {
            'id': 'regular',
            'name': '📅 منتظم',
            'name_en': 'Regular',
            'description': 'استخدمت البوت 7 أيام متتالية',
            'icon': '📅',
            'category': 'usage',
            'points': 20,
            'condition': lambda data: data.get('streak_days', 0) >= 7
        },
        'early_bird': {
            'id': 'early_bird',
            'name': '🌅 الطائر المبكر',
            'name_en': 'Early Bird',
            'description': 'أول من بحث عن نتائجه عند صدورها',
            'icon': '🌅',
            'category': 'usage',
            'points': 30,
            'condition': lambda data: data.get('is_early_bird', False)
        },
        'explorer': {
            'id': 'explorer',
            'name': '🔍 مستكشف',
            'name_en': 'Explorer',
            'description': 'استخدمت جميع ميزات البوت',
            'icon': '🔍',
            'category': 'usage',
            'points': 40,
            'condition': lambda data: data.get('features_used', 0) >= 10
        },
        
        # إنجازات اجتماعية
        'sharer': {
            'id': 'sharer',
            'name': '📤 مُشارك',
            'name_en': 'Sharer',
            'description': 'شاركت نتائجك 5 مرات',
            'icon': '📤',
            'category': 'social',
            'points': 25,
            'condition': lambda data: data.get('shares_count', 0) >= 5
        },
        'influencer': {
            'id': 'influencer',
            'name': '👥 مؤثر',
            'name_en': 'Influencer',
            'description': 'دعوت 10 أصدقاء للبوت',
            'icon': '👥',
            'category': 'social',
            'points': 100,
            'condition': lambda data: data.get('referrals', 0) >= 10
        },
        
        # إنجازات خاصة
        'first_place': {
            'id': 'first_place',
            'name': '🏆 الأول',
            'name_en': 'First Place',
            'description': 'حصلت على المركز الأول على الدفعة',
            'icon': '🏆',
            'category': 'special',
            'points': 500,
            'condition': lambda data: data.get('rank', 999) == 1
        },
        'top_three': {
            'id': 'top_three',
            'name': '🥉 من الثلاثة الأوائل',
            'name_en': 'Top Three',
            'description': 'حصلت على مركز من الثلاثة الأوائل',
            'icon': '🥉',
            'category': 'special',
            'points': 300,
            'condition': lambda data: data.get('rank', 999) <= 3
        },
        'top_ten': {
            'id': 'top_ten',
            'name': '🔟 من العشرة الأوائل',
            'name_en': 'Top Ten',
            'description': 'حصلت على مركز من العشرة الأوائل',
            'icon': '🔟',
            'category': 'special',
            'points': 150,
            'condition': lambda data: data.get('rank', 999) <= 10
        }
    }
    
    # المستويات
    LEVELS = [
        {'level': 1, 'name': '🌱 مبتدئ', 'min_points': 0, 'max_points': 99},
        {'level': 2, 'name': '📗 متعلم', 'min_points': 100, 'max_points': 249},
        {'level': 3, 'name': '📘 متقدم', 'min_points': 250, 'max_points': 499},
        {'level': 4, 'name': '📙 خبير', 'min_points': 500, 'max_points': 999},
        {'level': 5, 'name': '📕 محترف', 'min_points': 1000, 'max_points': 1999},
        {'level': 6, 'name': '👑 أسطوري', 'min_points': 2000, 'max_points': float('inf')}
    ]
    
    def __init__(self, supabase):
        self.supabase = supabase
    
    def get_user_achievements(self, telegram_id: int) -> Dict:
        """الحصول على إنجازات المستخدم"""
        try:
            response = self.supabase.table("user_achievements").select("*").eq(
                "telegram_id", telegram_id
            ).execute()
            
            if response.data:
                return response.data[0]
            
            # إنشاء سجل جديد
            new_record = {
                'telegram_id': telegram_id,
                'achievements': [],
                'total_points': 0,
                'level': 1,
                'streak_days': 0,
                'last_active': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            self.supabase.table("user_achievements").insert(new_record).execute()
            return new_record
            
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return {}
    
    def check_and_award_achievements(self, telegram_id: int, student_data: Dict) -> List[Dict]:
        """التحقق من الإنجازات ومنحها"""
        try:
            user_achievements = self.get_user_achievements(telegram_id)
            current_achievements = user_achievements.get('achievements', [])
            new_achievements = []
            
            for ach_id, achievement in self.ACHIEVEMENTS.items():
                # تخطي الإنجازات المكتسبة
                if ach_id in current_achievements:
                    continue
                
                # التحقق من الشرط
                try:
                    if achievement['condition'](student_data):
                        new_achievements.append(achievement)
                        current_achievements.append(ach_id)
                except:
                    continue
            
            if new_achievements:
                # حساب النقاط الجديدة
                new_points = sum(a['points'] for a in new_achievements)
                total_points = user_achievements.get('total_points', 0) + new_points
                new_level = self.calculate_level(total_points)
                
                # تحديث قاعدة البيانات
                self.supabase.table("user_achievements").update({
                    'achievements': current_achievements,
                    'total_points': total_points,
                    'level': new_level,
                    'updated_at': datetime.now().isoformat()
                }).eq('telegram_id', telegram_id).execute()
                
                # تسجيل الإنجازات الجديدة
                for ach in new_achievements:
                    self.supabase.table("achievement_log").insert({
                        'telegram_id': telegram_id,
                        'achievement_id': ach['id'],
                        'points_earned': ach['points'],
                        'earned_at': datetime.now().isoformat()
                    }).execute()
            
            return new_achievements
            
        except Exception as e:
            print(f"Error checking achievements: {e}")
            return []
    
    def calculate_level(self, points: int) -> int:
        """حساب المستوى من النقاط"""
        for level_info in self.LEVELS:
            if level_info['min_points'] <= points <= level_info['max_points']:
                return level_info['level']
        return 1
    
    def get_level_info(self, level: int) -> Dict:
        """الحصول على معلومات المستوى"""
        for level_info in self.LEVELS:
            if level_info['level'] == level:
                return level_info
        return self.LEVELS[0]
    
    def update_streak(self, telegram_id: int) -> int:
        """تحديث سلسلة الأيام المتتالية"""
        try:
            user = self.get_user_achievements(telegram_id)
            last_active = user.get('last_active')
            current_streak = user.get('streak_days', 0)
            
            if last_active:
                last_date = datetime.fromisoformat(last_active).date()
                today = datetime.now().date()
                diff = (today - last_date).days
                
                if diff == 1:
                    # يوم متتالي
                    current_streak += 1
                elif diff > 1:
                    # انقطاع
                    current_streak = 1
                # diff == 0 يعني نفس اليوم، لا تغيير
            else:
                current_streak = 1
            
            self.supabase.table("user_achievements").update({
                'streak_days': current_streak,
                'last_active': datetime.now().isoformat()
            }).eq('telegram_id', telegram_id).execute()
            
            return current_streak
            
        except Exception as e:
            print(f"Error updating streak: {e}")
            return 0
    
    def add_points(self, telegram_id: int, points: int, reason: str) -> Dict:
        """إضافة نقاط للمستخدم"""
        try:
            user = self.get_user_achievements(telegram_id)
            total_points = user.get('total_points', 0) + points
            new_level = self.calculate_level(total_points)
            old_level = user.get('level', 1)
            
            self.supabase.table("user_achievements").update({
                'total_points': total_points,
                'level': new_level,
                'updated_at': datetime.now().isoformat()
            }).eq('telegram_id', telegram_id).execute()
            
            # تسجيل النقاط
            self.supabase.table("points_log").insert({
                'telegram_id': telegram_id,
                'points': points,
                'reason': reason,
                'created_at': datetime.now().isoformat()
            }).execute()
            
            return {
                'total_points': total_points,
                'new_level': new_level,
                'level_up': new_level > old_level
            }
            
        except Exception as e:
            print(f"Error adding points: {e}")
            return {}
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """الحصول على لوحة الصدارة"""
        try:
            response = self.supabase.table("user_achievements").select(
                "telegram_id, total_points, level, achievements"
            ).order("total_points", desc=True).limit(limit).execute()
            
            leaderboard = []
            for i, user in enumerate(response.data, 1):
                level_info = self.get_level_info(user['level'])
                leaderboard.append({
                    'rank': i,
                    'telegram_id': user['telegram_id'],
                    'points': user['total_points'],
                    'level': user['level'],
                    'level_name': level_info['name'],
                    'achievements_count': len(user.get('achievements', []))
                })
            
            return leaderboard
            
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def format_achievements_message(self, telegram_id: int) -> str:
        """تنسيق رسالة الإنجازات"""
        user = self.get_user_achievements(telegram_id)
        level_info = self.get_level_info(user.get('level', 1))
        
        msg = f"🏆 *إنجازاتك*\n\n"
        msg += f"📊 *المستوى:* {level_info['name']}\n"
        msg += f"⭐ *النقاط:* {user.get('total_points', 0)}\n"
        msg += f"🔥 *سلسلة الأيام:* {user.get('streak_days', 0)} يوم\n\n"
        
        earned = user.get('achievements', [])
        
        if earned:
            msg += "✅ *الإنجازات المكتسبة:*\n"
            for ach_id in earned:
                if ach_id in self.ACHIEVEMENTS:
                    ach = self.ACHIEVEMENTS[ach_id]
                    msg += f"  {ach['icon']} {ach['name']} (+{ach['points']})\n"
        
        # الإنجازات غير المكتسبة
        locked = [a for a in self.ACHIEVEMENTS.values() if a['id'] not in earned]
        if locked:
            msg += f"\n🔒 *إنجازات متبقية:* {len(locked)}\n"
            for ach in locked[:5]:
                msg += f"  🔸 {ach['name']}: {ach['description']}\n"
        
        return msg
    
    def format_new_achievement_message(self, achievement: Dict) -> str:
        """تنسيق رسالة إنجاز جديد"""
        return (
            f"🎉 *مبروك! إنجاز جديد!*\n\n"
            f"{achievement['icon']} *{achievement['name']}*\n"
            f"_{achievement['description']}_\n\n"
            f"⭐ +{achievement['points']} نقطة"
        )


# دالة مساعدة للتكامل مع البوت
def setup_achievements_commands(bot, achievements_system, supabase):
    """إعداد أوامر الإنجازات في البوت"""
    
    @bot.message_handler(commands=['achievements', 'badges', 'انجازاتي'])
    def show_achievements(message):
        """عرض الإنجازات"""
        msg = achievements_system.format_achievements_message(message.chat.id)
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    
    @bot.message_handler(commands=['leaderboard', 'top_users', 'الصدارة'])
    def show_leaderboard(message):
        """عرض لوحة الصدارة"""
        leaderboard = achievements_system.get_leaderboard(10)
        
        msg = "🏆 *لوحة الصدارة*\n\n"
        
        medals = ['🥇', '🥈', '🥉']
        for user in leaderboard:
            rank = user['rank']
            medal = medals[rank-1] if rank <= 3 else f"#{rank}"
            msg += f"{medal} {user['level_name']} - {user['points']} نقطة\n"
        
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    
    @bot.message_handler(commands=['points', 'نقاطي'])
    def show_points(message):
        """عرض النقاط"""
        user = achievements_system.get_user_achievements(message.chat.id)
        level_info = achievements_system.get_level_info(user.get('level', 1))
        
        # حساب التقدم للمستوى التالي
        current_points = user.get('total_points', 0)
        next_level = min(user.get('level', 1) + 1, 6)
        next_level_info = achievements_system.get_level_info(next_level)
        
        if next_level_info['min_points'] != float('inf'):
            progress = ((current_points - level_info['min_points']) / 
                       (next_level_info['min_points'] - level_info['min_points'])) * 100
            progress = min(progress, 100)
            progress_bar = '█' * int(progress/10) + '░' * (10 - int(progress/10))
        else:
            progress = 100
            progress_bar = '█' * 10
        
        msg = (
            f"⭐ *نقاطك: {current_points}*\n\n"
            f"📊 المستوى: {level_info['name']}\n"
            f"📈 التقدم: [{progress_bar}] {progress:.0f}%\n\n"
            f"🎯 المستوى التالي: {next_level_info['name']}\n"
            f"💫 تحتاج: {max(0, next_level_info['min_points'] - current_points)} نقطة"
        )
        
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
