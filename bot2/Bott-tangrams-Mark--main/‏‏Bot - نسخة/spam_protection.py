# -*- coding: utf-8 -*-
"""
نظام حماية البوت من الطلبات المتتالية والمستخدمين المزعجين
يراقب سلوك المستخدمين ويرسل إشعارات للمسؤول
"""

from datetime import datetime, timedelta
from collections import defaultdict
import json
from supabase import Client

class SpamProtection:
    """فئة لحماية البوت من الطلبات المتتالية"""
    
    def __init__(self, supabase: Client):
        """
        Args:
            supabase: عميل Supabase
        """
        self.supabase = supabase
        # تخزين مؤقت لعدد الطلبات في الذاكرة
        self.request_counts = defaultdict(list)  # {user_id: [timestamps]}
        self.blocked_users = set()
        
        # إعدادات الحد الزمني (قابلة للتعديل)
        self.MAX_REQUESTS_PER_MINUTE = 5  # أقصى 5 طلبات في دقيقة
        self.MAX_REQUESTS_PER_5_MINUTES = 15  # أقصى 15 طلب في 5 دقائق
        self.BAN_DURATION_MINUTES = 30  # مدة الحظر (30 دقيقة)
        
        # تحميل المستخدمين المحظورين من قاعدة البيانات
        self.load_blocked_users()
    
    def load_blocked_users(self):
        """تحميل قائمة المستخدمين المحظورين من قاعدة البيانات"""
        try:
            response = self.supabase.table("blocked_users").select("*").execute()
            self.blocked_users = {row['user_id'] for row in response.data if row.get('is_active')}
        except Exception as e:
            print(f"⚠️ خطأ في تحميل المستخدمين المحظورين: {e}")
            self.blocked_users = set()
    
    def create_tables_if_not_exist(self):
        """إنشاء الجداول المطلوبة إذا لم تكن موجودة"""
        try:
            # هذه الدالة يجب تنفيذها مرة واحدة فقط عند البدء
            # سيتم عرض أوامر SQL في أسفل الملف
            pass
        except Exception as e:
            print(f"⚠️ خطأ: {e}")
    
    def is_user_blocked(self, user_id: int) -> bool:
        """
        التحقق مما إذا كان المستخدم محظوراً
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            bool: True إذا كان المستخدم محظوراً
        """
        return user_id in self.blocked_users
    
    def check_request(self, user_id: int) -> dict:
        """
        التحقق من طلب المستخدم وتسجيله
        
        Args:
            user_id: معرف المستخدم
        
        Returns:
            dict: {
                'is_spam': bool,
                'is_blocked': bool,
                'request_count': int,
                'time_until_unblock': int (بالدقائق)
            }
        """
        current_time = datetime.now()
        
        # إزالة الطلبات القديمة (أكثر من 5 دقائق)
        if user_id in self.request_counts:
            self.request_counts[user_id] = [
                t for t in self.request_counts[user_id]
                if (current_time - t).total_seconds() < 300
            ]
        
        # تسجيل الطلب الجديد
        self.request_counts[user_id].append(current_time)
        
        recent_requests = self.request_counts[user_id]
        
        # فحص الحد الأول: 5 طلبات في دقيقة
        requests_in_minute = [t for t in recent_requests 
                            if (current_time - t).total_seconds() < 60]
        
        # فحص الحد الثاني: 15 طلب في 5 دقائق
        requests_in_5_minutes = len(recent_requests)
        
        is_spam = (len(requests_in_minute) > self.MAX_REQUESTS_PER_MINUTE or 
                   requests_in_5_minutes > self.MAX_REQUESTS_PER_5_MINUTES)
        
        result = {
            'is_spam': is_spam,
            'is_blocked': user_id in self.blocked_users,
            'request_count': requests_in_5_minutes,
            'max_allowed': self.MAX_REQUESTS_PER_5_MINUTES
        }
        
        return result
    
    def block_user(self, user_id: int, reason: str = "طلبات متتالية"):
        """
        حظر المستخدم
        
        Args:
            user_id: معرف المستخدم
            reason: سبب الحظر
        """
        try:
            # استخدام upsert لتجنب مشكلة UNIQUE constraint
            self.supabase.table("blocked_users").upsert({
                "user_id": user_id,
                "reason": reason,
                "blocked_at": datetime.now().isoformat(),
                "is_active": True,
                "unblock_at": (datetime.now() + timedelta(minutes=self.BAN_DURATION_MINUTES)).isoformat()
            }).execute()
            
            self.blocked_users.add(user_id)
            print(f"✅ تم حظر المستخدم {user_id} بنجاح - السبب: {reason}")
            return True
        except Exception as e:
            print(f"❌ خطأ في حظر المستخدم {user_id}: {e}")
            return False
    
    def unblock_user(self, user_id: int):
        """
        فك الحظر عن المستخدم
        
        Args:
            user_id: معرف المستخدم
        """
        try:
            self.supabase.table("blocked_users").update({
                "is_active": False,
                "unblocked_at": datetime.now().isoformat()
            }).eq("user_id", user_id).execute()
            
            self.blocked_users.discard(user_id)
            return True
        except Exception as e:
            print(f"❌ خطأ في فك الحظر: {e}")
            return False
    
    def log_spam_incident(self, user_id: int, request_count: int):
        """
        تسجيل حادثة الرسائل المزعجة
        
        Args:
            user_id: معرف المستخدم
            request_count: عدد الطلبات
        """
        try:
            self.supabase.table("spam_incidents").insert({
                "user_id": user_id,
                "request_count": request_count,
                "detected_at": datetime.now().isoformat(),
                "status": "pending"  # في انتظار قرار المسؤول
            }).execute()
        except Exception as e:
            print(f"❌ خطأ في تسجيل الحادثة: {e}")
    
    def get_pending_incidents(self) -> list:
        """الحصول على قائمة الحوادث في انتظار القرار"""
        try:
            response = self.supabase.table("spam_incidents").select("*").eq("status", "pending").execute()
            return response.data
        except Exception as e:
            print(f"❌ خطأ في جلب الحوادث: {e}")
            return []
    
    def resolve_incident(self, incident_id: int, action: str, user_name: str = ""):
        """
        حل حادثة الرسائل المزعجة
        
        Args:
            incident_id: معرف الحادثة
            action: "block" أو "ignore"
            user_name: اسم المستخدم
        """
        try:
            self.supabase.table("spam_incidents").update({
                "status": action,
                "resolved_at": datetime.now().isoformat()
            }).eq("id", incident_id).execute()
            return True
        except Exception as e:
            print(f"❌ خطأ في حل الحادثة: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> dict:
        """الحصول على إحصائيات المستخدم"""
        return {
            'user_id': user_id,
            'request_count': len(self.request_counts.get(user_id, [])),
            'is_blocked': user_id in self.blocked_users,
            'total_requests': self._get_total_requests(user_id)
        }
    
    def _get_total_requests(self, user_id: int) -> int:
        """إجمالي الطلبات من قاعدة البيانات"""
        try:
            response = self.supabase.table("request_log").select("*").eq("user_id", user_id).execute()
            return len(response.data)
        except:
            return 0


# ════════════════════════════════════════════════════════════
# أوامر SQL المطلوبة (نسخها وألصقها في SQL Editor الخاص بـ Supabase)
# ════════════════════════════════════════════════════════════

"""
-- جدول تسجيل الطلبات
CREATE TABLE IF NOT EXISTS request_log (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
    request_type TEXT DEFAULT 'search',
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول المستخدمين المحظورين
CREATE TABLE IF NOT EXISTS blocked_users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT UNIQUE NOT NULL,
    reason TEXT DEFAULT 'طلبات متتالية',
    blocked_at TIMESTAMP DEFAULT NOW(),
    unblock_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    unblocked_at TIMESTAMP,
    admin_decision TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول حوادث الرسائل المزعجة (بدون FOREIGN KEY لتجنب مشاكل الإدراج)
CREATE TABLE IF NOT EXISTS spam_incidents (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    request_count INT NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending',
    admin_decision TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول اشتراكات المستخدمين
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    student_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول الدرجات المعروفة (للإشعارات)
CREATE TABLE IF NOT EXISTS known_grades (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    student_id TEXT UNIQUE NOT NULL,
    grades_data JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- جدول مستخدمي البوت
CREATE TABLE IF NOT EXISTS bot_users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول اشتراكات القناة
CREATE TABLE IF NOT EXISTS channel_subscriptions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    is_subscribed BOOLEAN DEFAULT FALSE,
    subscription_date TIMESTAMP,
    reminder_count INT DEFAULT 0,
    last_reminder TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- إضافة فهارس للأداء الأفضل
CREATE INDEX IF NOT EXISTS idx_blocked_users_active ON blocked_users(is_active);
CREATE INDEX IF NOT EXISTS idx_spam_incidents_status ON spam_incidents(status);
CREATE INDEX IF NOT EXISTS idx_request_log_user ON request_log(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_student ON user_subscriptions(student_id);
CREATE INDEX IF NOT EXISTS idx_bot_users_chat ON bot_users(chat_id);
"""
