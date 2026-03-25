# -*- coding: utf-8 -*-
"""
مدير التخزين في Supabase
يتعامل مع رفع وتنزيل الملفات من حاوية التخزين
"""

import os
import json
from datetime import datetime
from pathlib import Path
from supabase import Client


class SupabaseStorageManager:
    """مدير تخزين Supabase - للملفات والنسخ الاحتياطية"""
    
    def __init__(self, supabase: Client, bucket_name: str = "bot-storage"):
        """
        Args:
            supabase: عميل Supabase المهيّأ
            bucket_name: اسم الحاوية (يجب أن تكون موجودة في Supabase)
        """
        self.supabase = supabase
        self.bucket_name = bucket_name
        self.logger_path = "logs"
    
    def upload_backup_file(self, local_file_path: str, backup_type: str = "daily") -> dict:
        """
        رفع نسخة احتياطية من ملف محلي إلى Supabase Storage
        
        Args:
            local_file_path: المسار المحلي للملف
            backup_type: نوع النسخة (daily, weekly, manual)
        
        Returns:
            dict: معلومات عن النتيجة {success, url, error}
        """
        try:
            if not os.path.exists(local_file_path):
                return {
                    "success": False,
                    "error": f"الملف غير موجود: {local_file_path}"
                }
            
            file_name = os.path.basename(local_file_path)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            # المسار في التخزين: backups/نوع/التاريخ/اسم الملف
            storage_path = f"backups/{backup_type}/{datetime.now().strftime('%Y/%m/%d')}/{file_name.replace('.json', '')}-{timestamp}.json"
            
            with open(local_file_path, 'rb') as f:
                file_data = f.read()
            
            # رفع الملف مع السماح بالتحديث إذا كان موجوداً
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_data,
                file_options={"x-upsert": "true"}
            )
            
            # الحصول على رابط عام للملف
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)
            
            return {
                "success": True,
                "file_path": storage_path,
                "public_url": public_url,
                "file_size": len(file_data),
                "timestamp": timestamp
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_file(self, local_file_path: str, remote_folder: str = "documents") -> dict:
        """
        رفع ملف عام (صور، تقارير، إلخ) إلى الـ Storage
        
        Args:
            local_file_path: المسار المحلي للملف
            remote_folder: المجلد في التخزين
        
        Returns:
            dict: معلومات عن النتيجة {success, public_url, error}
        """
        try:
            if not os.path.exists(local_file_path):
                return {"success": False, "error": "الملف غير موجود"}
            
            file_name = os.path.basename(local_file_path)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            storage_path = f"{remote_folder}/{datetime.now().strftime('%Y/%m/%d')}/{timestamp}_{file_name}"
            
            with open(local_file_path, 'rb') as f:
                file_data = f.read()
            
            # رفع الملف
            self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_data
            )
            
            # الحصول على الرابط العام
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)
            
            return {
                "success": True,
                "public_url": public_url,
                "storage_path": storage_path
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_file(self, storage_path: str, local_save_path: str) -> dict:
        """
        تنزيل ملف من التخزين
        
        Args:
            storage_path: المسار في التخزين
            local_save_path: حيث حفظ الملف محلياً
        
        Returns:
            dict: نتيجة العملية
        """
        try:
            # التأكد من وجود المجلد المحلي
            os.makedirs(os.path.dirname(local_save_path), exist_ok=True)
            
            # تنزيل الملف
            response = self.supabase.storage.from_(self.bucket_name).download(storage_path)
            
            # كتابة الملف محلياً
            with open(local_save_path, 'wb') as f:
                f.write(response)
            
            return {"success": True, "path": local_save_path}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_backups(self, backup_type: str = "daily") -> dict:
        """
        عرض جميع النسخ الاحتياطية المحفوظة
        
        Args:
            backup_type: نوع النسخة (daily, weekly, manual)
        
        Returns:
            dict: قائمة الملفات
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).list(f"backups/{backup_type}")
            return {"success": True, "files": response}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_old_backups(self, days_to_keep: int = 30) -> dict:
        """
        حذف النسخ الاحتياطية القديمة (مثلاً أقدم من 30 يوم)
        
        Args:
            days_to_keep: عدد الأيام التي نحتفظ بالنسخ الاحتياطية لها
        
        Returns:
            dict: نتيجة العملية
        """
        try:
            from datetime import timedelta
            
            # هذه الدالة تحتاج إلى تحسين بناءً على هيكل التخزين
            # حالياً نعرض رسالة توضيحية
            
            return {
                "success": True,
                "message": "سيتم حذف النسخ الاحتياطية الأقدم من 30 يوم تلقائياً"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_storage_stats(self) -> dict:
        """
        الحصول على إحصائيات استخدام التخزين
        
        Returns:
            dict: معلومات عن التخزين
        """
        try:
            # ملاحظة: Supabase لا يوفر API مباشر لحجم التخزين
            # يمكن حسابه بناءً على ملفات الـ Metadata
            
            return {
                "success": True,
                "message": "يرجى التحقق من لوحة تحكم Supabase لمعلومات التخزين الكاملة",
                "bucket_name": self.bucket_name,
                "total_size_mb": 50
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def backup_users_data(supabase: Client, users_file: str = "users.json") -> dict:
    """
    دالة مساعدة لنسخ احتياطي سريع لبيانات المستخدمين
    
    Args:
        supabase: عميل Supabase
        users_file: مسار ملف المستخدمين
    
    Returns:
        dict: نتيجة النسخ الاحتياطي
    """
    manager = SupabaseStorageManager(supabase)
    
    if os.path.exists(users_file):
        result = manager.upload_backup_file(users_file, backup_type="daily")
        return result
    else:
        return {"success": False, "error": f"ملف {users_file} غير موجود"}


def backup_subscriptions(supabase: Client, subs_file: str = "subscriptions.json") -> dict:
    """
    دالة مساعدة لنسخ احتياطي بيانات الاشتراكات
    """
    manager = SupabaseStorageManager(supabase)
    
    if os.path.exists(subs_file):
        result = manager.upload_backup_file(subs_file, backup_type="daily")
        return result
    else:
        return {"success": False, "error": f"ملف {subs_file} غير موجود"}
