# -*- coding: utf-8 -*-
"""
مدير قاعدة البيانات السحابية (Supabase) - نظام تخزين كامل بدون JSON محلي
تدير جميع البيانات في السحابة: المستخدمين، الاشتراكات، الدرجات، وما إلى ذلك
"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from supabase import Client


class CloudDatabaseManager:
    """مدير قاعدة البيانات السحابية - تخزين سحابي كامل"""
    
    def __init__(self, supabase: Client):
        """
        Args:
            supabase: عميل Supabase المهيّأ
        """
        self.supabase = supabase
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة المستخدمين (bot_users)
    # ═══════════════════════════════════════════════════════════════
    
    def add_user(self, chat_id: int) -> Dict[str, Any]:
        """إضافة مستخدم جديد إلى البوت"""
        try:
            # التحقق من وجود المستخدم أولاً
            existing = self.get_user(chat_id)
            if existing['success'] and existing['user']:
                return {"success": False, "message": "المستخدم موجود بالفعل"}
            
            response = self.supabase.table("bot_users").insert({
                "chat_id": chat_id,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            return {
                "success": True,
                "message": f"تم إضافة المستخدم {chat_id}",
                "data": response.data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_user(self, chat_id: int) -> Dict[str, Any]:
        """الحصول على بيانات مستخدم"""
        try:
            response = self.supabase.table("bot_users").select("*").eq(
                "chat_id", chat_id
            ).execute()
            
            user = response.data[0] if response.data else None
            return {
                "success": True,
                "user": user,
                "exists": bool(user)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "exists": False}
    
    def get_all_users(self) -> Dict[str, Any]:
        """الحصول على جميع المستخدمين"""
        try:
            response = self.supabase.table("bot_users").select("chat_id").execute()
            users = [row["chat_id"] for row in response.data]
            return {
                "success": True,
                "users": users,
                "count": len(users)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "users": []}
    
    def delete_user(self, chat_id: int) -> Dict[str, Any]:
        """حذف مستخدم"""
        try:
            self.supabase.table("bot_users").delete().eq(
                "chat_id", chat_id
            ).execute()
            
            return {"success": True, "message": f"تم حذف المستخدم {chat_id}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة الاشتراكات (user_subscriptions)
    # ═══════════════════════════════════════════════════════════════
    
    def subscribe_user(self, chat_id: int, student_id: str) -> Dict[str, Any]:
        """ربط مستخدم بطالب"""
        try:
            # التحقق من عدم وجود اشتراك سابق
            existing = self.get_subscription(chat_id)
            if existing['success'] and existing['subscription']:
                # تحديث الاشتراك
                self.supabase.table("user_subscriptions").update({
                    "student_id": student_id,
                    "created_at": datetime.now().isoformat()
                }).eq("chat_id", chat_id).execute()
                
                return {
                    "success": True,
                    "message": f"تم تحديث الاشتراك - الطالب: {student_id}"
                }
            
            # إضافة اشتراك جديد
            response = self.supabase.table("user_subscriptions").insert({
                "chat_id": chat_id,
                "student_id": student_id,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            return {
                "success": True,
                "message": f"تم الاشتراك - الطالب: {student_id}",
                "data": response.data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_subscription(self, chat_id: int) -> Dict[str, Any]:
        """الحصول على بيانات اشتراك المستخدم"""
        try:
            response = self.supabase.table("user_subscriptions").select("*").eq(
                "chat_id", chat_id
            ).execute()
            
            subscription = response.data[0] if response.data else None
            return {
                "success": True,
                "subscription": subscription,
                "student_id": subscription["student_id"] if subscription else None
            }
        except Exception as e:
            return {"success": False, "error": str(e), "subscription": None}
    
    def get_subscriptions_for_student(self, student_id: str) -> Dict[str, Any]:
        """الحصول على جميع المستخدمين المشتركين لطالب معين"""
        try:
            response = self.supabase.table("user_subscriptions").select("chat_id").eq(
                "student_id", student_id
            ).execute()
            
            users = [row["chat_id"] for row in response.data]
            return {
                "success": True,
                "users": users,
                "count": len(users)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "users": []}
    
    def unsubscribe_user(self, chat_id: int) -> Dict[str, Any]:
        """إلغاء اشتراك المستخدم"""
        try:
            self.supabase.table("user_subscriptions").delete().eq(
                "chat_id", chat_id
            ).execute()
            
            return {"success": True, "message": "تم إلغاء الاشتراك"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة الدرجات (all_marks)
    # ═══════════════════════════════════════════════════════════════
    
    def add_grade(self, student_id: str, student_name: str, father_name: str,
                  subject_name: str, practical_grade: int, theoretical_grade: int,
                  total_grade: int, grade_in_words: str, result: str,
                  rank: Optional[int] = None) -> Dict[str, Any]:
        """إضافة درجة جديدة"""
        try:
            response = self.supabase.table("all_marks").insert({
                "student_id": student_id,
                "student_name": student_name,
                "father_name": father_name,
                "subject_name": subject_name,
                "practical_grade": practical_grade,
                "theoretical_grade": theoretical_grade,
                "total_grade": total_grade,
                "grade_in_words": grade_in_words,
                "result": result,
                "rank": rank
            }).execute()
            
            return {
                "success": True,
                "message": f"تم إضافة درجة {subject_name} للطالب {student_id}",
                "data": response.data
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_student_grades(self, student_id: str) -> Dict[str, Any]:
        """الحصول على جميع درجات طالب"""
        try:
            response = self.supabase.table("all_marks").select("*").eq(
                "student_id", student_id
            ).execute()
            
            return {
                "success": True,
                "grades": response.data,
                "count": len(response.data)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "grades": []}
    
    def get_subject_grades(self, subject_name: str) -> Dict[str, Any]:
        """الحصول على درجات مادة معينة"""
        try:
            response = self.supabase.table("all_marks").select("*").eq(
                "subject_name", subject_name
            ).order("total_grade", desc=True).execute()
            
            return {
                "success": True,
                "grades": response.data,
                "count": len(response.data)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "grades": []}
    
    def update_grade(self, student_id: str, subject_name: str,
                     practical_grade: int, theoretical_grade: int,
                     total_grade: int, grade_in_words: str,
                     result: str) -> Dict[str, Any]:
        """تحديث درجة موجودة"""
        try:
            self.supabase.table("all_marks").update({
                "practical_grade": practical_grade,
                "theoretical_grade": theoretical_grade,
                "total_grade": total_grade,
                "grade_in_words": grade_in_words,
                "result": result
            }).eq("student_id", student_id).eq(
                "subject_name", subject_name
            ).execute()
            
            return {
                "success": True,
                "message": f"تم تحديث درجة {subject_name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة الدرجات المعروفة (known_grades) - JSONB
    # ═══════════════════════════════════════════════════════════════
    
    def save_known_grades(self, student_id: str, grades_data: Dict) -> Dict[str, Any]:
        """حفظ درجات معروفة للطالب (مخزن JSON)"""
        try:
            # التحقق من وجود السجل
            existing = self.supabase.table("known_grades").select("*").eq(
                "student_id", student_id
            ).execute()
            
            if existing.data:
                # تحديث
                self.supabase.table("known_grades").update({
                    "grades_data": grades_data,
                    "updated_at": datetime.now().isoformat()
                }).eq("student_id", student_id).execute()
                
                return {
                    "success": True,
                    "message": "تم تحديث الدرجات المعروفة"
                }
            else:
                # إدراج جديد
                response = self.supabase.table("known_grades").insert({
                    "student_id": student_id,
                    "grades_data": grades_data,
                    "updated_at": datetime.now().isoformat()
                }).execute()
                
                return {
                    "success": True,
                    "message": "تم حفظ الدرجات المعروفة",
                    "data": response.data
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_known_grades(self, student_id: str) -> Dict[str, Any]:
        """الحصول على الدرجات المعروفة للطالب"""
        try:
            response = self.supabase.table("known_grades").select("*").eq(
                "student_id", student_id
            ).execute()
            
            if response.data:
                return {
                    "success": True,
                    "grades_data": response.data[0]["grades_data"],
                    "updated_at": response.data[0]["updated_at"]
                }
            else:
                return {
                    "success": True,
                    "grades_data": None,
                    "message": "لا توجد درجات معروفة"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة درجات اللغة (language_grades)
    # ═══════════════════════════════════════════════════════════════
    
    def add_language_grade(self, student_id: str, student_name: str,
                          father_name: str, practical_grade: int,
                          theoretical_grade: int, total_grade: int,
                          grade_in_words: str, result: str) -> Dict[str, Any]:
        """إضافة درجة اللغة"""
        try:
            # التحقق من الوجود أولاً
            existing = self.supabase.table("language_grades").select("*").eq(
                "student_id", student_id
            ).execute()
            
            if existing.data:
                # تحديث
                self.supabase.table("language_grades").update({
                    "practical_grade": practical_grade,
                    "theoretical_grade": theoretical_grade,
                    "total_grade": total_grade,
                    "grade_in_words": grade_in_words,
                    "result": result
                }).eq("student_id", student_id).execute()
                
                return {
                    "success": True,
                    "message": "تم تحديث درجة اللغة"
                }
            else:
                # إدراج
                response = self.supabase.table("language_grades").insert({
                    "student_id": student_id,
                    "student_name": student_name,
                    "father_name": father_name,
                    "practical_grade": practical_grade,
                    "theoretical_grade": theoretical_grade,
                    "total_grade": total_grade,
                    "grade_in_words": grade_in_words,
                    "result": result
                }).execute()
                
                return {
                    "success": True,
                    "message": "تم إضافة درجة اللغة",
                    "data": response.data
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_language_grade(self, student_id: str) -> Dict[str, Any]:
        """الحصول على درجة اللغة"""
        try:
            response = self.supabase.table("language_grades").select("*").eq(
                "student_id", student_id
            ).execute()
            
            if response.data:
                return {
                    "success": True,
                    "grade": response.data[0]
                }
            else:
                return {
                    "success": True,
                    "grade": None,
                    "message": "لا توجد درجة لغة"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة درجات الطلاب (student_grades)
    # ═══════════════════════════════════════════════════════════════
    
    def add_student_grade(self, student_id: str, student_name: str,
                         father_name: str, practical_grade: int,
                         theoretical_grade: int, total_grade: int,
                         grade_in_words: str, result: str) -> Dict[str, Any]:
        """إضافة درجة طالب عام"""
        try:
            existing = self.supabase.table("student_grades").select("*").eq(
                "student_id", student_id
            ).execute()
            
            if existing.data:
                # تحديث
                self.supabase.table("student_grades").update({
                    "practical_grade": practical_grade,
                    "theoretical_grade": theoretical_grade,
                    "total_grade": total_grade,
                    "grade_in_words": grade_in_words,
                    "result": result
                }).eq("student_id", student_id).execute()
                
                return {
                    "success": True,
                    "message": "تم تحديث درجة الطالب"
                }
            else:
                response = self.supabase.table("student_grades").insert({
                    "student_id": student_id,
                    "student_name": student_name,
                    "father_name": father_name,
                    "practical_grade": practical_grade,
                    "theoretical_grade": theoretical_grade,
                    "total_grade": total_grade,
                    "grade_in_words": grade_in_words,
                    "result": result
                }).execute()
                
                return {
                    "success": True,
                    "message": "تم إضافة درجة الطالب",
                    "data": response.data
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_student_grade(self, student_id: str) -> Dict[str, Any]:
        """الحصول على درجة طالب عام"""
        try:
            response = self.supabase.table("student_grades").select("*").eq(
                "student_id", student_id
            ).execute()
            
            if response.data:
                return {
                    "success": True,
                    "grade": response.data[0]
                }
            else:
                return {
                    "success": True,
                    "grade": None,
                    "message": "لا توجد درجة للطالب"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # عمليات مساعدة
    # ═══════════════════════════════════════════════════════════════
    
    def get_all_students(self) -> Dict[str, Any]:
        """الحصول على جميع الطلاب من جدول all_marks"""
        try:
            response = self.supabase.table("all_marks").select(
                "student_id, student_name"
            ).execute()
            
            # إزالة التكرارات
            students = {row["student_id"]: row["student_name"] 
                       for row in response.data}
            
            return {
                "success": True,
                "students": students,
                "count": len(students)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "students": {}}
    
    def get_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات البيانات"""
        try:
            # عدد المستخدمين
            users_response = self.supabase.table("bot_users").select(
                "count", count="exact"
            ).execute()
            user_count = users_response.count or 0
            
            # عدد الاشتراكات
            subs_response = self.supabase.table("user_subscriptions").select(
                "count", count="exact"
            ).execute()
            subs_count = subs_response.count or 0
            
            # عدد الدرجات
            grades_response = self.supabase.table("all_marks").select(
                "count", count="exact"
            ).execute()
            grades_count = grades_response.count or 0
            
            # عدد الطلاب unique
            students = self.get_all_students()
            
            return {
                "success": True,
                "total_users": user_count,
                "total_subscriptions": subs_count,
                "total_grades": grades_count,
                "total_students": students.get("count", 0)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def clear_all_data(self) -> Dict[str, Any]:
        """حذف جميع البيانات (احذر! عملية لا يمكن عكسها)"""
        try:
            tables = ["bot_users", "user_subscriptions", "all_marks",
                     "known_grades", "language_grades", "student_grades"]
            
            for table in tables:
                self.supabase.table(table).delete().neq("id", 0).execute()
            
            return {
                "success": True,
                "message": "تم حذف جميع البيانات"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ═══════════════════════════════════════════════════════════════
    # إدارة اشتراك القناة (channel_subscriptions)
    # ═══════════════════════════════════════════════════════════════
    
    def check_channel_subscription(self, chat_id: int) -> Dict[str, Any]:
        """التحقق من اشتراك المستخدم في قناة البوت"""
        try:
            response = self.supabase.table("channel_subscriptions").select(
                "is_subscribed, reminder_count"
            ).eq("chat_id", chat_id).execute()
            
            if response.data:
                subscription = response.data[0]
                return {
                    "success": True,
                    "is_subscribed": subscription.get("is_subscribed", False),
                    "reminder_count": subscription.get("reminder_count", 0)
                }
            
            # المستخدم غير موجود في جدول الاشتراك
            return {"success": True, "is_subscribed": False, "reminder_count": 0}
        except Exception as e:
            return {"success": False, "error": str(e), "is_subscribed": False}
    
    def mark_channel_subscribed(self, chat_id: int) -> Dict[str, Any]:
        """تسجيل اشتراك المستخدم في قناة البوت"""
        try:
            # التحقق من وجود السجل أولاً
            existing = self.supabase.table("channel_subscriptions").select(
                "id"
            ).eq("chat_id", chat_id).execute()
            
            if existing.data:
                # تحديث السجل الموجود
                self.supabase.table("channel_subscriptions").update({
                    "is_subscribed": True,
                    "subscription_date": datetime.now().isoformat(),
                    "reminder_count": 0,
                    "updated_at": datetime.now().isoformat()
                }).eq("chat_id", chat_id).execute()
            else:
                # إنشاء سجل جديد
                self.supabase.table("channel_subscriptions").insert({
                    "chat_id": chat_id,
                    "is_subscribed": True,
                    "subscription_date": datetime.now().isoformat(),
                    "reminder_count": 0
                }).execute()
            
            return {"success": True, "message": "✅ تم تسجيل اشتراكك في القناة"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_reminder_count(self, chat_id: int) -> Dict[str, Any]:
        """تحديث عداد التذكيرات عند محاولة استخدام بدون اشتراك"""
        try:
            # الحصول على العداد الحالي
            response = self.supabase.table("channel_subscriptions").select(
                "reminder_count"
            ).eq("chat_id", chat_id).execute()
            
            if response.data:
                current_count = response.data[0].get("reminder_count", 0)
                new_count = current_count + 1
                
                # تحديث العداد
                self.supabase.table("channel_subscriptions").update({
                    "reminder_count": new_count,
                    "last_reminder": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }).eq("chat_id", chat_id).execute()
                
                return {
                    "success": True,
                    "new_count": new_count,
                    "message": f"تم تحديث التذكير (المحاولة #{new_count})"
                }
            else:
                # إنشاء سجل جديد للمستخدم
                self.supabase.table("channel_subscriptions").insert({
                    "chat_id": chat_id,
                    "is_subscribed": False,
                    "reminder_count": 1,
                    "last_reminder": datetime.now().isoformat()
                }).execute()
                
                return {
                    "success": True,
                    "new_count": 1,
                    "message": "تم إنشاء سجل تذكير جديد"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_unsubscribed_users(self) -> Dict[str, Any]:
        """الحصول على جميع المستخدمين غير المشتركين في القناة"""
        try:
            response = self.supabase.table("channel_subscriptions").select(
                "chat_id, reminder_count"
            ).eq("is_subscribed", False).execute()
            
            users = [row["chat_id"] for row in response.data]
            return {
                "success": True,
                "users": users,
                "count": len(users)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "users": []}
    
    def get_channel_statistics(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الاشتراك في القناة"""
        try:
            all_response = self.supabase.table("channel_subscriptions").select(
                "count", count="exact"
            ).execute()
            total_tracked = all_response.count or 0
            
            subscribed_response = self.supabase.table("channel_subscriptions").select(
                "count", count="exact"
            ).eq("is_subscribed", True).execute()
            subscribed_count = subscribed_response.count or 0
            
            unsubscribed_count = total_tracked - subscribed_count
            subscription_rate = (subscribed_count / total_tracked * 100) if total_tracked > 0 else 0
            
            return {
                "success": True,
                "total_tracked_users": total_tracked,
                "subscribed_users": subscribed_count,
                "unsubscribed_users": unsubscribed_count,
                "subscription_rate": round(subscription_rate, 2)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
