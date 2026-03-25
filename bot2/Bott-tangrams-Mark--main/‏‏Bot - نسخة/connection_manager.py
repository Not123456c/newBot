# -*- coding: utf-8 -*-
"""
معالج الأخطاء والاتصال المحسّن للبوت
يوفر retry logic، timeout محسّن، ومعالجة أخطاء ذكية
"""

import time
import traceback
from typing import Optional, Callable, Any
from functools import wraps
import requests
from requests.exceptions import ConnectionError, Timeout, ReadTimeout


class ConnectionManager:
    """مدير الاتصال بـ Telegram مع retry logic محسّن"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff: float = 2,
        max_backoff: float = 60,
        timeout: int = 30
    ):
        """
        Args:
            max_retries: عدد محاولات الإعادة القصوى
            initial_backoff: التأخير الأولي بالثواني
            max_backoff: التأخير الأقصى بالثواني
            timeout: timeout قراءة الاتصال بالثواني
        """
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.timeout = timeout
        
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        تنفيذ دالة مع إعادة محاولة وتأخير أسي
        """
        backoff = self.initial_backoff
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (ConnectionError, Timeout, ReadTimeout) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    wait_time = min(backoff, self.max_backoff)
                    print(
                        f"⚠️ محاولة {attempt + 1}/{self.max_retries + 1} فشلت"
                        f"\n💤 أنتظر {wait_time:g} ثانية..."
                        f"\n🔴 الخطأ: {str(e)[:100]}"
                    )
                    time.sleep(wait_time)
                    backoff *= 2  # exponential backoff
                else:
                    print(
                        f"❌ فشلت جميع المحاولات ({self.max_retries + 1})"
                        f"\n🔴 آخر خطأ: {str(e)}"
                    )
                    raise
            except Exception as e:
                # أخطاء غير متعلقة بالاتصال - رمها مباشرة
                print(f"❌ خطأ غير متوقع: {str(e)}")
                raise
        
        raise last_exception


class TelegramPollingManager:
    """مدير polling مع معالجة أخطاء محسّنة"""
    
    def __init__(self, bot, max_restart_attempts: int = 5, restart_delay: int = 10):
        """
        Args:
            bot: instance من telebot
            max_restart_attempts: عدد محاولات إعادة التشغيل
            restart_delay: التأخير بين محاولات الإعادة (ثانية)
        """
        self.bot = bot
        self.max_restart_attempts = max_restart_attempts
        self.restart_delay = restart_delay
        self.conn_manager = ConnectionManager(
            max_retries=5,  # زيادة من 3 إلى 5
            timeout=60  # زيادة من 25 إلى 60 ثانية
        )
    
    def start_polling(self) -> None:
        """
        بدء polling مع معالجة أخطاء محسّنة
        """
        restart_count = 0
        
        while True:
            try:
                print("🟢 الاتصال بـ Telegram API جاري...")
                
                # استدعاء polling مع timeout محسّن
                self.bot.infinity_polling(
                    timeout=15,
                    long_polling_timeout=45  # زيادة من 25 إلى 45 ثانية
                )
                
                # إذا نجح polling، أعد العداد
                restart_count = 0
                
            except (ConnectionError, Timeout, ReadTimeout) as e:
                restart_count += 1
                
                if restart_count <= self.max_restart_attempts:
                    wait_time = self.restart_delay * restart_count
                    print(
                        f"❌ فقدان الاتصال بـ Telegram (محاولة {restart_count}/{self.max_restart_attempts})"
                        f"\n🔄 إعادة الاتصال في {wait_time} ثانية..."
                        f"\n📝 الخطأ: {str(e)[:80]}"
                    )
                    time.sleep(wait_time)
                else:
                    print(
                        f"❌ فشلت جميع محاولات الاتصال ({self.max_restart_attempts})"
                        f"\n🛑 يتوقف البوت..."
                    )
                    raise
                    
            except Exception as e:
                print(f"❌ خطأ غير متوقع في polling:")
                print(traceback.format_exc())
                
                restart_count += 1
                if restart_count <= self.max_restart_attempts:
                    wait_time = self.restart_delay * 2
                    print(f"🔄 إعادة المحاولة في {wait_time} ثانية...")
                    time.sleep(wait_time)
                else:
                    raise


class DatabaseErrorHandler:
    """معالج أخطاء قاعدة البيانات"""
    
    @staticmethod
    def handle_supabase_error(error: Exception) -> dict:
        """
        تحليل خطأ Supabase وإرجاع معلومات مفيدة
        """
        error_str = str(error)
        
        # أخطاء شائعة
        if "Could not find" in error_str and "column" in error_str:
            return {
                "type": "missing_column",
                "message": "❌ عمود غير موجود في قاعدة البيانات",
                "severity": "critical",
                "action": "تحقق من تعريف الجدول والعمود"
            }
        elif "duplicate" in error_str.lower():
            return {
                "type": "duplicate_entry",
                "message": "⚠️ السجل موجود بالفعل",
                "severity": "warning"
            }
        elif "connection" in error_str.lower():
            return {
                "type": "connection_error",
                "message": "❌ فشل الاتصال بقاعدة البيانات",
                "severity": "critical"
            }
        else:
            return {
                "type": "unknown",
                "message": f"❌ خطأ: {error_str[:100]}",
                "severity": "high"
            }


def safe_db_operation(func: Callable) -> Callable:
    """
    Decorator لتنفيذ آمن لعمليات قاعدة البيانات مع معالجة أخطاء
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = DatabaseErrorHandler.handle_supabase_error(e)
            print(f"{error_info['message']} (نوع: {error_info['type']})")
            return {
                "success": False,
                "error": str(e),
                "error_type": error_info['type']
            }
    return wrapper


def configure_polling_with_safety(bot) -> TelegramPollingManager:
    """
    تكوين polling آمن للبوت
    """
    return TelegramPollingManager(
        bot=bot,
        max_restart_attempts=5,
        restart_delay=10
    )
