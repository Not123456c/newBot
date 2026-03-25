# -*- coding: utf-8 -*-
"""
مدير التخزين المؤقت (Cache Manager)
لتحسين أداء البوت مع آلاف المستخدمين
"""

from datetime import datetime, timedelta
from collections import OrderedDict
import threading


class CacheManager:
    """
    نظام تخزين مؤقت بسيط وفعال
    - يدعم TTL (Time To Live)
    - يدعم LRU (Least Recently Used)
    - Thread-safe
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Args:
            max_size: الحد الأقصى لعدد العناصر في الـ Cache
        """
        self._cache = OrderedDict()
        self._expiry = {}
        self._max_size = max_size
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str):
        """
        جلب قيمة من الـ Cache
        
        Args:
            key: مفتاح القيمة
        
        Returns:
            القيمة إذا وُجدت ولم تنتهي صلاحيتها، وإلا None
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # التحقق من انتهاء الصلاحية
            if key in self._expiry and datetime.now() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                self._misses += 1
                return None
            
            # نقل العنصر للنهاية (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def set(self, key: str, value, ttl_seconds: int = 300):
        """
        تخزين قيمة في الـ Cache
        
        Args:
            key: مفتاح القيمة
            value: القيمة المراد تخزينها
            ttl_seconds: مدة الصلاحية بالثواني (افتراضي: 5 دقائق)
        """
        with self._lock:
            # إزالة العناصر القديمة إذا وصلنا للحد الأقصى
            while len(self._cache) >= self._max_size:
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                if oldest_key in self._expiry:
                    del self._expiry[oldest_key]
            
            self._cache[key] = value
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def delete(self, key: str):
        """حذف قيمة من الـ Cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
    
    def clear(self):
        """مسح كل الـ Cache"""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()
    
    def clear_expired(self):
        """مسح العناصر منتهية الصلاحية فقط"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, exp_time in self._expiry.items()
                if now > exp_time
            ]
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                del self._expiry[key]
            return len(expired_keys)
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات الـ Cache"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self._max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': f"{hit_rate:.2f}%"
            }
    
    def exists(self, key: str) -> bool:
        """التحقق من وجود مفتاح"""
        return self.get(key) is not None


# إنشاء instance عام للاستخدام في البوت
cache = CacheManager(max_size=500)


# دوال مساعدة للاستخدام السريع
def cached(ttl_seconds: int = 300):
    """
    Decorator لتخزين نتائج الدوال تلقائياً
    
    استخدام:
    @cached(ttl_seconds=600)
    def get_expensive_data():
        ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح فريد من اسم الدالة والمعاملات
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # محاولة جلب من الـ Cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # تنفيذ الدالة وتخزين النتيجة
            result = func(*args, **kwargs)
            cache.set(key, result, ttl_seconds)
            return result
        
        return wrapper
    return decorator


# دوال محددة للبوت
def get_cached_top_students(supabase, n: int, fetch_func):
    """
    جلب الأوائل مع تخزين مؤقت
    
    Args:
        supabase: عميل Supabase
        n: عدد الطلاب
        fetch_func: دالة جلب البيانات الأصلية
    
    Returns:
        نتيجة الاستعلام (من الـ Cache أو جديدة)
    """
    cache_key = f"top_students_{n}"
    
    # محاولة جلب من الـ Cache
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        print(f"✅ Cache HIT: {cache_key}")
        return cached_result
    
    print(f"⏳ Cache MISS: {cache_key} - جاري الجلب...")
    
    # جلب البيانات
    result = fetch_func(supabase, n)
    
    # تخزين في الـ Cache لمدة 10 دقائق
    cache.set(cache_key, result, ttl_seconds=600)
    
    return result


def get_cached_cohort_analytics(supabase, fetch_func):
    """جلب تحليلات الدفعة مع تخزين مؤقت"""
    cache_key = "cohort_analytics"
    
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    result = fetch_func(supabase)
    cache.set(cache_key, result, ttl_seconds=600)  # 10 دقائق
    
    return result


def invalidate_student_cache(student_id: str = None):
    """إبطال Cache متعلق بطالب معين أو كل الطلاب"""
    if student_id:
        cache.delete(f"student_{student_id}")
    else:
        # مسح كل cache الطلاب
        cache.clear()


# تنظيف دوري للـ Cache
def start_cache_cleanup(interval_minutes: int = 10):
    """بدء تنظيف دوري للعناصر منتهية الصلاحية"""
    import threading
    import time
    
    def cleanup_loop():
        while True:
            time.sleep(interval_minutes * 60)
            cleared = cache.clear_expired()
            if cleared > 0:
                print(f"🧹 تم مسح {cleared} عنصر منتهي الصلاحية من الـ Cache")
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    print(f"🔄 بدء تنظيف Cache كل {interval_minutes} دقيقة")
