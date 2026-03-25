# -*- coding: utf-8 -*-
"""
معالج إرسال الرسائل والصور بأمان مع retry logic محسّن
يتعامل مع جميع أنواع أخطاء الاتصال والتوقيتات
"""

import time
import traceback
from typing import Optional, Any
from functools import wraps
import requests
from requests.exceptions import ConnectionError, Timeout, ReadTimeout, ChunkedEncodingError


class SafeSendHandler:
    """معالج إرسال آمن للرسائل والصور مع إعادة محاولة ذكية"""
    
    def __init__(self, max_retries: int = 5, timeout: int = 30):
        """
        Args:
            max_retries: عدد محاولات الإعادة القصوى
            timeout: timeout الاتصال بالثواني
        """
        self.max_retries = max_retries
        self.timeout = timeout
    
    def safe_send_message(self, bot, chat_id: int, text: str, **kwargs) -> bool:
        """
        إرسال رسالة نصية بأمان مع إعادة محاولة
        
        Args:
            bot: instance من telebot.TeleBot
            chat_id: معرف الدردشة
            text: نص الرسالة
            **kwargs: معاملات إضافية (parse_mode, reply_markup, إلخ)
        
        Returns:
            True إذا نجح الإرسال، False إذا فشل
        """
        backoff = 1
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # تعيين timeout للاتصال
                bot.send_message(
                    chat_id, 
                    text, 
                    timeout=self.timeout,
                    **kwargs
                )
                
                if attempt > 0:
                    print(f"✅ نجحت الرسالة بعد {attempt} محاولة(ات) إعادة")
                
                return True
                
            except (ConnectionError, Timeout, ReadTimeout, ChunkedEncodingError) as e:
                last_error = e
                
                if attempt < self.max_retries:
                    wait_time = min(backoff, 60)
                    print(
                        f"⚠️  محاولة إرسال رسالة ({attempt + 1}/{self.max_retries + 1}) فشلت"
                        f"\n   🔴 الخطأ: {type(e).__name__}"
                        f"\n   💤 إعادة المحاولة في {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    backoff = min(backoff * 2, 60)  # exponential backoff حتى 60 ثانية
                else:
                    print(
                        f"❌ فشل إرسال الرسالة بعد {self.max_retries + 1} محاولات"
                        f"\n   🔴 آخر خطأ: {type(last_error).__name__}: {str(last_error)[:80]}"
                    )
                    return False
                    
            except Exception as e:
                print(
                    f"❌ خطأ غير متوقع في إرسال الرسالة:"
                    f"\n   {type(e).__name__}: {str(e)[:100]}"
                )
                return False
        
        return False
    
    def safe_send_photo(self, bot, chat_id: int, photo, caption: str = "", **kwargs) -> bool:
        """
        إرسال صورة بأمان مع إعادة محاولة
        
        Args:
            bot: instance من telebot.TeleBot
            chat_id: معرف الدردشة
            photo: الصورة (URL أو bytes أو file path)
            caption: تعليق الصورة
            **kwargs: معاملات إضافية (parse_mode, reply_markup, إلخ)
        
        Returns:
            True إذا نجح الإرسال، False إذا فشل
        """
        backoff = 1
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                bot.send_photo(
                    chat_id,
                    photo,
                    caption=caption,
                    timeout=self.timeout,
                    **kwargs
                )
                
                if attempt > 0:
                    print(f"✅ نجحت الصورة بعد {attempt} محاولة(ات) إعادة")
                
                return True
                
            except (ConnectionError, Timeout, ReadTimeout, ChunkedEncodingError) as e:
                last_error = e
                
                if attempt < self.max_retries:
                    wait_time = min(backoff, 60)
                    print(
                        f"⚠️  محاولة إرسال صورة ({attempt + 1}/{self.max_retries + 1}) فشلت"
                        f"\n   🔴 الخطأ: {type(e).__name__}"
                        f"\n   💤 إعادة المحاولة في {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    backoff = min(backoff * 2, 60)
                else:
                    print(
                        f"❌ فشل إرسال الصورة بعد {self.max_retries + 1} محاولات"
                        f"\n   🔴 آخر خطأ: {type(last_error).__name__}: {str(last_error)[:80]}"
                    )
                    return False
                    
            except Exception as e:
                print(
                    f"❌ خطأ غير متوقع في إرسال الصورة:"
                    f"\n   {type(e).__name__}: {str(e)[:100]}"
                )
                return False
        
        return False
    
    def safe_send_document(self, bot, chat_id: int, document, caption: str = "", **kwargs) -> bool:
        """
        إرسال ملف/وثيقة بأمان مع إعادة محاولة
        """
        backoff = 1
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                bot.send_document(
                    chat_id,
                    document,
                    caption=caption,
                    timeout=self.timeout,
                    **kwargs
                )
                
                if attempt > 0:
                    print(f"✅ نجحت الوثيقة بعد {attempt} محاولة(ات) إعادة")
                
                return True
                
            except (ConnectionError, Timeout, ReadTimeout, ChunkedEncodingError) as e:
                last_error = e
                
                if attempt < self.max_retries:
                    wait_time = min(backoff, 60)
                    print(
                        f"⚠️  محاولة إرسال وثيقة ({attempt + 1}/{self.max_retries + 1}) فشلت"
                        f"\n   🔴 الخطأ: {type(e).__name__}"
                        f"\n   💤 إعادة المحاولة في {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    backoff = min(backoff * 2, 60)
                else:
                    print(
                        f"❌ فشل إرسال الوثيقة بعد {self.max_retries + 1} محاولات"
                    )
                    return False
                    
            except Exception as e:
                print(
                    f"❌ خطأ غير متوقع في إرسال الوثيقة:"
                    f"\n   {type(e).__name__}: {str(e)[:100]}"
                )
                return False
        
        return False


# إنشاء instance واحد للاستخدام العام
send_handler = SafeSendHandler(max_retries=5, timeout=60)


def safe_send_message(bot, chat_id: int, text: str, **kwargs) -> bool:
    """Wrapper function سهل الاستخدام"""
    return send_handler.safe_send_message(bot, chat_id, text, **kwargs)


def safe_send_photo(bot, chat_id: int, photo, caption: str = "", **kwargs) -> bool:
    """Wrapper function سهل الاستخدام"""
    return send_handler.safe_send_photo(bot, chat_id, photo, caption, **kwargs)


def safe_send_document(bot, chat_id: int, document, caption: str = "", **kwargs) -> bool:
    """Wrapper function سهل الاستخدام"""
    return send_handler.safe_send_document(bot, chat_id, document, caption, **kwargs)
