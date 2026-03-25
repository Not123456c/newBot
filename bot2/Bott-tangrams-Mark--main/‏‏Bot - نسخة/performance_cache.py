# -*- coding: utf-8 -*-
"""
نظام التخزين المؤقت المتقدم
Advanced Cache System with Redis Support
"""

import os
import json
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import wraps
import time


class AdvancedCache:
    """
    نظام تخزين مؤقت متقدم
    يدعم Redis أو الذاكرة المحلية
    """
    
    def __init__(self, redis_url: str = None, default_ttl: int = 300):
        """
        Args:
            redis_url: رابط Redis (اختياري)
            default_ttl: مدة الصلاحية الافتراضية بالثواني
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.local_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }
        self._lock = threading.Lock()
        
        # محاولة الاتصال بـ Redis
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                print("✅ تم الاتصال بـ Redis")
            except Exception as e:
                print(f"⚠️ فشل الاتصال بـ Redis، استخدام الذاكرة المحلية: {e}")
                self.redis_client = None
    
    def _generate_key(self, key: str, prefix: str = "cache") -> str:
        """توليد مفتاح فريد"""
        return f"{prefix}:{hashlib.md5(key.encode()).hexdigest()[:16]}:{key[:50]}"
    
    def get(self, key: str) -> Optional[Any]:
        """الحصول على قيمة من الكاش"""
        cache_key = self._generate_key(key)
        
        try:
            if self.redis_client:
                data = self.redis_client.get(cache_key)
                if data:
                    self.cache_stats['hits'] += 1
                    return json.loads(data)
            else:
                with self._lock:
                    if cache_key in self.local_cache:
                        item = self.local_cache[cache_key]
                        if item['expires_at'] > datetime.now():
                            self.cache_stats['hits'] += 1
                            return item['value']
                        else:
                            del self.local_cache[cache_key]
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """تخزين قيمة في الكاش"""
        cache_key = self._generate_key(key)
        ttl = ttl or self.default_ttl
        
        try:
            if self.redis_client:
                self.redis_client.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(value, ensure_ascii=False, default=str)
                )
            else:
                with self._lock:
                    self.local_cache[cache_key] = {
                        'value': value,
                        'expires_at': datetime.now() + timedelta(seconds=ttl)
                    }
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """حذف من الكاش"""
        cache_key = self._generate_key(key)
        
        try:
            if self.redis_client:
                self.redis_client.delete(cache_key)
            else:
                with self._lock:
                    if cache_key in self.local_cache:
                        del self.local_cache[cache_key]
            return True
        except:
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """حذف مفاتيح تطابق نمط معين"""
        deleted = 0
        
        try:
            if self.redis_client:
                keys = self.redis_client.keys(f"cache:*{pattern}*")
                if keys:
                    deleted = self.redis_client.delete(*keys)
            else:
                with self._lock:
                    keys_to_delete = [
                        k for k in self.local_cache 
                        if pattern in k
                    ]
                    for k in keys_to_delete:
                        del self.local_cache[k]
                    deleted = len(keys_to_delete)
            
            return deleted
        except:
            return 0
    
    def clear_all(self) -> bool:
        """مسح كل الكاش"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                with self._lock:
                    self.local_cache.clear()
            return True
        except:
            return False
    
    def get_stats(self) -> Dict:
        """إحصائيات الكاش"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        
        stats = {
            **self.cache_stats,
            'hit_rate': round(hit_rate, 2),
            'backend': 'redis' if self.redis_client else 'memory'
        }
        
        if not self.redis_client:
            stats['items_count'] = len(self.local_cache)
        
        return stats
    
    def cleanup_expired(self):
        """تنظيف العناصر منتهية الصلاحية (للذاكرة المحلية فقط)"""
        if self.redis_client:
            return  # Redis يتعامل مع هذا تلقائياً
        
        with self._lock:
            now = datetime.now()
            expired = [
                k for k, v in self.local_cache.items() 
                if v['expires_at'] <= now
            ]
            for k in expired:
                del self.local_cache[k]
            
            return len(expired)


def cached(cache: AdvancedCache, ttl: int = 300, key_prefix: str = ""):
    """
    Decorator للتخزين المؤقت
    
    Usage:
        @cached(cache_instance, ttl=600, key_prefix="results")
        def get_student_results(student_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # توليد مفتاح الكاش
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # محاولة الحصول من الكاش
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # تنفيذ الدالة وتخزين النتيجة
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


class ConnectionPool:
    """
    مجمع اتصالات لقاعدة البيانات
    """
    
    def __init__(self, create_connection, max_connections: int = 10):
        self.create_connection = create_connection
        self.max_connections = max_connections
        self._pool = []
        self._in_use = []
        self._lock = threading.Lock()
    
    def get_connection(self):
        """الحصول على اتصال من المجمع"""
        with self._lock:
            # محاولة إعادة استخدام اتصال موجود
            if self._pool:
                conn = self._pool.pop()
                self._in_use.append(conn)
                return conn
            
            # إنشاء اتصال جديد إذا لم نصل للحد الأقصى
            if len(self._in_use) < self.max_connections:
                conn = self.create_connection()
                self._in_use.append(conn)
                return conn
            
            # انتظار اتصال متاح
            raise Exception("No available connections")
    
    def release_connection(self, conn):
        """إعادة الاتصال للمجمع"""
        with self._lock:
            if conn in self._in_use:
                self._in_use.remove(conn)
                self._pool.append(conn)
    
    def close_all(self):
        """إغلاق جميع الاتصالات"""
        with self._lock:
            for conn in self._pool + self._in_use:
                try:
                    conn.close()
                except:
                    pass
            self._pool.clear()
            self._in_use.clear()


class LazyLoader:
    """
    تحميل كسول للبيانات الثقيلة
    """
    
    def __init__(self, loader_func, cache: AdvancedCache = None, cache_ttl: int = 600):
        self.loader_func = loader_func
        self.cache = cache
        self.cache_ttl = cache_ttl
        self._data = None
        self._loaded = False
        self._lock = threading.Lock()
    
    @property
    def data(self):
        """الحصول على البيانات (تحميل عند الحاجة)"""
        if not self._loaded:
            with self._lock:
                if not self._loaded:
                    # محاولة من الكاش
                    if self.cache:
                        cache_key = f"lazy:{self.loader_func.__name__}"
                        cached = self.cache.get(cache_key)
                        if cached is not None:
                            self._data = cached
                            self._loaded = True
                            return self._data
                    
                    # تحميل البيانات
                    self._data = self.loader_func()
                    self._loaded = True
                    
                    # تخزين في الكاش
                    if self.cache:
                        self.cache.set(cache_key, self._data, self.cache_ttl)
        
        return self._data
    
    def reload(self):
        """إعادة تحميل البيانات"""
        with self._lock:
            self._loaded = False
            self._data = None


class RateLimiter:
    """
    محدد معدل الطلبات
    """
    
    def __init__(self, cache: AdvancedCache, max_requests: int = 10, window_seconds: int = 60):
        self.cache = cache
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier: str) -> tuple:
        """
        التحقق من السماح بالطلب
        
        Returns:
            (is_allowed, remaining, reset_time)
        """
        key = f"ratelimit:{identifier}"
        now = time.time()
        
        # الحصول على السجل الحالي
        record = self.cache.get(key) or {'requests': [], 'window_start': now}
        
        # تنظيف الطلبات القديمة
        window_start = now - self.window_seconds
        record['requests'] = [r for r in record['requests'] if r > window_start]
        
        # التحقق من الحد
        if len(record['requests']) >= self.max_requests:
            oldest = min(record['requests'])
            reset_time = oldest + self.window_seconds - now
            return False, 0, reset_time
        
        # إضافة الطلب الحالي
        record['requests'].append(now)
        self.cache.set(key, record, self.window_seconds)
        
        remaining = self.max_requests - len(record['requests'])
        return True, remaining, 0
    
    def reset(self, identifier: str):
        """إعادة تعيين العداد"""
        self.cache.delete(f"ratelimit:{identifier}")


# ══════════════════════════════════════
# إعداد الكاش العام
# ══════════════════════════════════════

def setup_performance_optimizations(supabase, redis_url: str = None):
    """إعداد تحسينات الأداء"""
    
    # إنشاء الكاش
    cache = AdvancedCache(redis_url=redis_url, default_ttl=300)
    
    # محدد المعدل
    rate_limiter = RateLimiter(cache, max_requests=30, window_seconds=60)
    
    # تشغيل مهمة تنظيف الكاش
    def cleanup_task():
        while True:
            time.sleep(300)  # كل 5 دقائق
            cache.cleanup_expired()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    return {
        'cache': cache,
        'rate_limiter': rate_limiter
    }


# ══════════════════════════════════════
# أمثلة الاستخدام
# ══════════════════════════════════════
"""
# إنشاء الكاش
cache = AdvancedCache(redis_url=os.environ.get('REDIS_URL'))

# استخدام الـ decorator
@cached(cache, ttl=600, key_prefix="results")
def get_student_results(student_id):
    # استعلام قاعدة البيانات
    return supabase.table("all_marks").select("*").eq("student_id", student_id).execute()

# استخدام محدد المعدل
rate_limiter = RateLimiter(cache, max_requests=10, window_seconds=60)

def handle_message(message):
    allowed, remaining, reset = rate_limiter.is_allowed(str(message.chat.id))
    
    if not allowed:
        bot.send_message(message.chat.id, f"⏳ انتظر {reset:.0f} ثانية")
        return
    
    # معالجة الرسالة

# التحميل الكسول
top_students = LazyLoader(
    lambda: supabase.table("all_marks").select("*").execute(),
    cache=cache,
    cache_ttl=600
)

# استخدام البيانات (ستُحمّل عند الحاجة فقط)
data = top_students.data
"""
