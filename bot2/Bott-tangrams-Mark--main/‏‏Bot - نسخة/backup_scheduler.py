# -*- coding: utf-8 -*-
"""
مدير جدولة النسخ الاحتياطية التلقائية
يتعامل مع النسخ الاحتياطي الدوري للملفات المهمة
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta
from storage_manager import SupabaseStorageManager


class BackupScheduler:
    """جدولة النسخ الاحتياطي التلقائي"""
    
    def __init__(self, supabase, backup_interval_hours: int = 24):
        """
        Args:
            supabase: عميل Supabase
            backup_interval_hours: عدد الساعات بين كل نسخة احتياطية (افتراضي: 24 ساعة)
        """
        self.supabase = supabase
        self.storage_manager = SupabaseStorageManager(supabase)
        self.backup_interval = backup_interval_hours * 3600  # تحويل إلى ثواني
        self.is_running = False
        self.thread = None
        self.last_backup_time = {}
    
    def start(self, files_to_backup: list = None):
        """
        بدء عملية الجدولة
        
        Args:
            files_to_backup: قائمة الملفات المراد نسخها احتياطياً
                            مثل: ["users.json", "subscriptions.json"]
        """
        if not files_to_backup:
            files_to_backup = ["users.json", "subscriptions.json"]
        
        if self.is_running:
            print("❌ الجدولة قيد التشغيل بالفعل")
            return
        
        self.files_to_backup = files_to_backup
        self.is_running = True
        
        # بدء الخيط على خلفية التطبيق
        self.thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.thread.start()
        
        print(f"✅ تم بدء جدولة النسخ الاحتياطي (كل {self.backup_interval // 3600} ساعة)")
    
    def stop(self):
        """إيقاف الجدولة"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⛔ تم إيقاف الجدولة")
    
    def _backup_loop(self):
        """حلقة النسخ الاحتياطي التلقائي"""
        while self.is_running:
            try:
                self._perform_backups()
                # انتظر المدة المحددة قبل النسخة التالية
                for _ in range(self.backup_interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"❌ خطأ في حلقة النسخ الاحتياطي: {e}")
                time.sleep(60)  # انتظر دقيقة قبل المحاولة مرة أخرى
    
    def _perform_backups(self):
        """تنفيذ النسخ الاحتياطية للملفات"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for file_path in self.files_to_backup:
            if not os.path.exists(file_path):
                print(f"⚠️  [{timestamp}] الملف غير موجود: {file_path}")
                continue
            
            try:
                result = self.storage_manager.upload_backup_file(
                    file_path,
                    backup_type="daily"
                )
                
                if result.get("success"):
                    file_size_kb = result.get("file_size", 0) / 1024
                    print(f"✅ [{timestamp}] تم عمل نسخة احتياطية: {file_path} ({file_size_kb:.2f} KB)")
                    self.last_backup_time[file_path] = datetime.now()
                else:
                    print(f"❌ [{timestamp}] فشل النسخ الاحتياطي: {file_path}")
                    print(f"   الخطأ: {result.get('error', 'خطأ غير معروف')}")
            
            except Exception as e:
                print(f"❌ [{timestamp}] استثناء في النسخ الاحتياطي: {e}")
    
    def get_backup_status(self) -> dict:
        """الحصول على حالة آخر النسخ الاحتياطية"""
        status = {
            "is_running": self.is_running,
            "backup_interval_hours": self.backup_interval // 3600,
            "last_backups": {}
        }
        
        for file_path, timestamp in self.last_backup_time.items():
            status["last_backups"][file_path] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        return status
    
    def force_backup_now(self, file_path: str = None) -> dict:
        """
        فرض نسخ احتياطي فوري لملف معين أو جميع الملفات
        
        Args:
            file_path: مسار الملف (None = جميع الملفات)
        
        Returns:
            dict: نتيجة النسخ الاحتياطي
        """
        if file_path:
            result = self.storage_manager.upload_backup_file(file_path, backup_type="manual")
            if result.get("success"):
                self.last_backup_time[file_path] = datetime.now()
            return result
        else:
            results = {}
            for file in self.files_to_backup:
                if os.path.exists(file):
                    result = self.storage_manager.upload_backup_file(file, backup_type="manual")
                    results[file] = result
                    if result.get("success"):
                        self.last_backup_time[file] = datetime.now()
            
            return {
                "success": all(r.get("success") for r in results.values()),
                "results": results
            }


# دالة مساعدة للاستخدام في البوت
def initialize_backup_scheduler(supabase, backup_interval_hours: int = 24) -> BackupScheduler:
    """
    إنشاء وتشغيل مدير جدولة النسخ الاحتياطي
    
    Args:
        supabase: عميل Supabase
        backup_interval_hours: عدد الساعات بين النسخ الاحتياطية
    
    Returns:
        BackupScheduler: مثيل من مدير الجدولة
    """
    scheduler = BackupScheduler(supabase, backup_interval_hours)
    scheduler.start(files_to_backup=["users.json", "subscriptions.json"])
    return scheduler
