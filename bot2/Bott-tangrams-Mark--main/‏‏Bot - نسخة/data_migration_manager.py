# -*- coding: utf-8 -*-
"""
هجرة البيانات من JSON المحلي إلى Supabase
يساعد في نقل البيانات الموجودة من ملفات JSON إلى جداول السحابة
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from supabase import Client
from cloud_database_manager import CloudDatabaseManager


class DataMigrationManager:
    """مدير هجرة البيانات من JSON إلى Supabase"""
    
    def __init__(self, supabase: Client):
        """
        Args:
            supabase: عميل Supabase
        """
        self.supabase = supabase
        self.db = CloudDatabaseManager(supabase)
        self.migration_log = []
    
    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """قراءة ملف JSON"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": f"الملف غير موجود: {file_path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════════
    # هجرة ملف users.json -> جدول bot_users
    # ═══════════════════════════════════════════════════════════════════
    
    def migrate_users_json(self, users_file: str = "users.json") -> Dict[str, Any]:
        """
        هجرة قائمة المستخدمين من users.json إلى جدول bot_users
        
        الملف الأصلي يحتوي على:
        [chat_id1, chat_id2, ...]
        """
        self.migration_log.append(f"🔄 بدء هجرة المستخدمين من {users_file}")
        
        # قراءة ملف JSON
        file_data = self.load_json_file(users_file)
        if not file_data["success"]:
            return file_data
        
        users_list = file_data["data"]
        if not isinstance(users_list, list):
            return {"success": False, "error": "صيغة الملف غير صحيحة. يجب أن يكون قائمة"}
        
        success_count = 0
        error_count = 0
        errors = []
        
        for chat_id in users_list:
            try:
                # تحقق من أن chat_id رقم صحيح
                if not isinstance(chat_id, int):
                    chat_id = int(chat_id)
                
                # أضف المستخدم
                result = self.db.add_user(chat_id)
                if result["success"]:
                    success_count += 1
                else:
                    # قد يكون موجود بالفعل
                    if "موجود" in result.get("message", ""):
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"chat_id {chat_id}: {result.get('error', 'خطأ')}")
                        
            except Exception as e:
                error_count += 1
                errors.append(f"chat_id {chat_id}: {str(e)}")
        
        log_msg = f"✅ تم هجرة {success_count} مستخدم"
        if error_count > 0:
            log_msg += f" | ❌ فشل {error_count}"
        
        self.migration_log.append(log_msg)
        
        return {
            "success": True,
            "migrated": success_count,
            "failed": error_count,
            "errors": errors,
            "log": self.migration_log
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # هجرة ملف subscriptions.json -> جدول user_subscriptions
    # ═══════════════════════════════════════════════════════════════════
    
    def migrate_subscriptions_json(self, subscriptions_file: str = "subscriptions.json") -> Dict[str, Any]:
        """
        هجرة الاشتراكات من subscriptions.json إلى جدول user_subscriptions
        
        الملف الأصلي يحتوي على:
        {
            "chat_id": "student_id",
            ...
        }
        """
        self.migration_log.append(f"🔄 بدء هجرة الاشتراكات من {subscriptions_file}")
        
        # قراءة ملف JSON
        file_data = self.load_json_file(subscriptions_file)
        if not file_data["success"]:
            return file_data
        
        subscriptions_dict = file_data["data"]
        if not isinstance(subscriptions_dict, dict):
            return {"success": False, "error": "صيغة الملف غير صحيحة. يجب أن يكون كائن"}
        
        success_count = 0
        error_count = 0
        errors = []
        
        for chat_id_str, student_id in subscriptions_dict.items():
            try:
                chat_id = int(chat_id_str)
                
                # ربط المستخدم بالطالب
                result = self.db.subscribe_user(chat_id, student_id)
                if result["success"]:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"chat_id {chat_id}: {result.get('error', 'خطأ')}")
                    
            except Exception as e:
                error_count += 1
                errors.append(f"chat_id {chat_id_str}: {str(e)}")
        
        log_msg = f"✅ تم هجرة {success_count} اشتراك"
        if error_count > 0:
            log_msg += f" | ❌ فشل {error_count}"
        
        self.migration_log.append(log_msg)
        
        return {
            "success": True,
            "migrated": success_count,
            "failed": error_count,
            "errors": errors,
            "log": self.migration_log
        }
    
    # ═══════════════════════════════════════════════════════════════════
    # هجرة كاملة من JSON إلى Supabase
    # ═══════════════════════════════════════════════════════════════════
    
    def migrate_all_data(self, users_file: str = "users.json",
                        subscriptions_file: str = "subscriptions.json") -> Dict[str, Any]:
        """هجرة جميع البيانات من JSON إلى Supabase"""
        print("\n🚀 بدء الهجرة الشاملة...")
        print("=" * 60)
        
        self.migration_log = []
        self.migration_log.append(f"🕐 وقت الهجرة: {datetime.now().isoformat()}")
        
        # 1. هجرة المستخدمين
        users_result = self.migrate_users_json(users_file)
        print(f"👥 المستخدمين: {users_result.get('migrated', 0)} مهجر، {users_result.get('failed', 0)} فشل")
        
        # 2. هجرة الاشتراكات
        subs_result = self.migrate_subscriptions_json(subscriptions_file)
        print(f"🔗 الاشتراكات: {subs_result.get('migrated', 0)} مهجر، {subs_result.get('failed', 0)} فشل")
        
        print("=" * 60)
        
        # ملخص الهجرة
        total_migrated = users_result.get('migrated', 0) + subs_result.get('migrated', 0)
        total_failed = users_result.get('failed', 0) + subs_result.get('failed', 0)
        
        self.migration_log.append(f"\n📊 الملخص:")
        self.migration_log.append(f"✅ المهجرة: {total_migrated}")
        self.migration_log.append(f"❌ الفاشلة: {total_failed}")
        
        return {
            "success": True,
            "total_migrated": total_migrated,
            "total_failed": total_failed,
            "users": users_result,
            "subscriptions": subs_result,
            "log": self.migration_log
        }
    
    def backup_json_files(self, backup_dir: str = "backups") -> Dict[str, Any]:
        """
        نسخ احتياطية من ملفات JSON قبل الهجرة
        """
        import shutil
        
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        files_to_backup = ["users.json", "subscriptions.json"]
        backup_results = {}
        
        for file_name in files_to_backup:
            try:
                if os.path.exists(file_name):
                    backup_path = f"{backup_dir}/{file_name}.{timestamp}.backup"
                    shutil.copy2(file_name, backup_path)
                    backup_results[file_name] = {
                        "success": True,
                        "backup_path": backup_path
                    }
                else:
                    backup_results[file_name] = {
                        "success": False,
                        "error": "الملف غير موجود"
                    }
            except Exception as e:
                backup_results[file_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": True,
            "backups": backup_results,
            "timestamp": timestamp
        }
    
    def verify_migration(self) -> Dict[str, Any]:
        """
        التحقق من نجاح الهجرة بمقارنة عدد السجلات
        """
        # الحصول على الإحصائيات من Supabase
        stats = self.db.get_statistics()
        
        if not stats["success"]:
            return {"success": False, "error": stats["error"]}
        
        message = "✅ تحقق من الهجرة:\n\n"
        message += f"👥 المستخدمين في Supabase: {stats['total_users']}\n"
        message += f"🔗 الاشتراكات في Supabase: {stats['total_subscriptions']}\n"
        message += f"📚 الدرجات في Supabase: {stats['total_grades']}\n"
        
        return {
            "success": True,
            "message": message,
            "statistics": stats
        }
    
    def print_migration_log(self) -> str:
        """طباعة تقرير الهجرة"""
        report = "\n📋 تقرير الهجرة:\n"
        report += "=" * 60 + "\n"
        for line in self.migration_log:
            report += line + "\n"
        report += "=" * 60
        return report


# ==============================================================================
# سكريبت الهجرة الرئيسي
# ==============================================================================

def run_migration(supabase_client: Client):
    """
    تشغيل الهجرة الكاملة
    
    مثال الاستخدام:
    ```python
    from supabase import create_client
    from data_migration_manager import run_migration
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    run_migration(supabase)
    ```
    """
    migrator = DataMigrationManager(supabase_client)
    
    print("\n🔐 تشغيل النسخ الاحتياطية...")
    backup_result = migrator.backup_json_files()
    if backup_result["success"]:
        print("✅ تم إنشاء نسخ احتياطية")
    
    print("\n🚀 بدء الهجرة...")
    migration_result = migrator.migrate_all_data()
    
    print(migrator.print_migration_log())
    
    print("\n🔍 التحقق من الهجرة...")
    verification = migrator.verify_migration()
    if verification["success"]:
        print(verification["message"])
    
    return migration_result


if __name__ == "__main__":
    """
    للتشغيل المباشر:
    python data_migration_manager.py
    """
    import os
    from dotenv import load_dotenv
    from supabase import create_client
    
    load_dotenv()
    
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ خطأ: متغيرات البيئة غير محددة")
        exit(1)
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    run_migration(supabase)
