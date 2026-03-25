# -*- coding: utf-8 -*-
"""
مدير المهام الثقيلة (Heavy Task Manager)
لتشغيل العمليات الثقيلة في الخلفية
"""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
import queue
import time
from typing import Callable, Any, Optional


class TaskManager:
    """
    مدير للمهام الثقيلة باستخدام Thread Pool
    - يمنع تجميد البوت أثناء توليد الصور
    - يدعم Timeout للمهام
    - يدعم قائمة انتظار للمهام
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Args:
            max_workers: عدد الـ Workers المتزامنين (افتراضي: 4)
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
        self._active_tasks = 0
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._lock = threading.Lock()
    
    def submit(self, func: Callable, *args, timeout: int = 60, **kwargs) -> Any:
        """
        تنفيذ مهمة في الخلفية والانتظار للنتيجة
        
        Args:
            func: الدالة المراد تنفيذها
            *args: معاملات الدالة
            timeout: الحد الأقصى للانتظار (ثواني)
            **kwargs: معاملات إضافية
        
        Returns:
            نتيجة الدالة
        
        Raises:
            TimeoutError: إذا تجاوز الوقت المحدد
        """
        with self._lock:
            self._active_tasks += 1
        
        try:
            future = self.executor.submit(func, *args, **kwargs)
            result = future.result(timeout=timeout)
            
            with self._lock:
                self._completed_tasks += 1
            
            return result
        
        except TimeoutError:
            with self._lock:
                self._failed_tasks += 1
            raise TimeoutError(f"⏰ المهمة تجاوزت الحد الأقصى ({timeout} ثانية)")
        
        except Exception as e:
            with self._lock:
                self._failed_tasks += 1
            raise e
        
        finally:
            with self._lock:
                self._active_tasks -= 1
    
    def submit_async(self, func: Callable, callback: Callable = None, *args, **kwargs):
        """
        تنفيذ مهمة في الخلفية بدون انتظار
        
        Args:
            func: الدالة المراد تنفيذها
            callback: دالة تُستدعى عند الانتهاء (اختياري)
            *args: معاملات الدالة
        """
        def task_wrapper():
            try:
                result = func(*args, **kwargs)
                if callback:
                    callback(result, None)
            except Exception as e:
                if callback:
                    callback(None, e)
        
        self.executor.submit(task_wrapper)
    
    def get_stats(self) -> dict:
        """الحصول على إحصائيات المهام"""
        with self._lock:
            return {
                'max_workers': self.max_workers,
                'active_tasks': self._active_tasks,
                'completed_tasks': self._completed_tasks,
                'failed_tasks': self._failed_tasks
            }
    
    def shutdown(self, wait: bool = True):
        """إيقاف الـ Task Manager"""
        self.executor.shutdown(wait=wait)


# إنشاء instance عام
task_manager = TaskManager(max_workers=4)


# دوال مساعدة لتوليد الصور
def generate_image_async(generate_func, *args, timeout: int = 30, **kwargs):
    """
    توليد صورة في الخلفية
    
    Args:
        generate_func: دالة توليد الصورة
        *args: معاملات الدالة
        timeout: الحد الأقصى للانتظار
    
    Returns:
        مسار الصورة المولدة
    """
    try:
        return task_manager.submit(generate_func, *args, timeout=timeout, **kwargs)
    except TimeoutError:
        print(f"⚠️ فشل توليد الصورة: تجاوز الوقت المحدد")
        return None
    except Exception as e:
        print(f"⚠️ خطأ في توليد الصورة: {e}")
        return None


# Rate Limiter للاستعلامات
class RateLimiter:
    """
    محدد معدل الطلبات
    - يمنع إغراق قاعدة البيانات بالاستعلامات
    - يحمي من هجمات DoS
    """
    
    def __init__(self, max_requests: int = 10, time_window: int = 1):
        """
        Args:
            max_requests: أقصى عدد طلبات
            time_window: النافذة الزمنية (بالثواني)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests = []
        self._lock = threading.Lock()
    
    def acquire(self) -> bool:
        """
        محاولة الحصول على إذن لتنفيذ طلب
        
        Returns:
            True إذا سُمح بالطلب، False إذا تجاوز الحد
        """
        with self._lock:
            now = time.time()
            
            # إزالة الطلبات القديمة
            self._requests = [
                t for t in self._requests
                if now - t < self.time_window
            ]
            
            # التحقق من الحد
            if len(self._requests) >= self.max_requests:
                return False
            
            self._requests.append(now)
            return True
    
    def wait_and_acquire(self, timeout: float = 5.0) -> bool:
        """
        انتظار حتى يتوفر إذن
        
        Args:
            timeout: الحد الأقصى للانتظار
        
        Returns:
            True إذا حصل على إذن، False إذا انتهى الوقت
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.acquire():
                return True
            time.sleep(0.1)
        
        return False


# Rate limiters للخدمات المختلفة
db_rate_limiter = RateLimiter(max_requests=20, time_window=1)  # 20 استعلام/ثانية
telegram_rate_limiter = RateLimiter(max_requests=30, time_window=1)  # 30 رسالة/ثانية


def rate_limited_db_query(query_func, *args, **kwargs):
    """
    تنفيذ استعلام قاعدة بيانات مع Rate Limiting
    """
    if db_rate_limiter.wait_and_acquire(timeout=5.0):
        return query_func(*args, **kwargs)
    else:
        raise Exception("⚠️ تم تجاوز حد الاستعلامات. يرجى المحاولة لاحقاً.")
