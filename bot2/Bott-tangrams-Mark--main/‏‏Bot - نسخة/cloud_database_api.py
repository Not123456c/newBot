# -*- coding: utf-8 -*-
"""
API Endpoints للتعامل مع البيانات السحابية
يوفر واجهة موحدة للتعامل مع جميع عمليات قاعدة البيانات
"""

from flask import Flask, request, jsonify
from cloud_database_manager import CloudDatabaseManager
from supabase import Client
from typing import Dict, Any
from functools import wraps
import os


class CloudDatabaseAPI:
    """واجهة API للتعامل مع قاعدة البيانات السحابية"""
    
    def __init__(self, supabase: Client):
        """
        Args:
            supabase: عميل Supabase
        """
        self.db = CloudDatabaseManager(supabase)
        self.app = Flask(__name__)
        self.setup_routes()
        
        # المفتاح السري للتحقق من الطلبات
        self.api_key = os.environ.get("API_KEY", "your-secret-key")
    
    def require_api_key(self, f):
        """ديكوريتر للتحقق من مفتاح API"""
        @wraps(f)
        def decorated(*args, **kwargs):
            key = request.headers.get('X-API-Key')
            if key != self.api_key:
                return jsonify({"error": "Unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated
    
    def setup_routes(self):
        """إعداد جميع المسارات"""
        
        # ═══════════════════════════════════════════════════════════
        # المستخدمين
        # ═══════════════════════════════════════════════════════════
        
        @self.app.route('/api/users', methods=['GET'])
        @self.require_api_key
        def get_all_users():
            """الحصول على جميع المستخدمين"""
            result = self.db.get_all_users()
            return jsonify(result)
        
        @self.app.route('/api/users/<int:chat_id>', methods=['GET'])
        @self.require_api_key
        def get_user(chat_id):
            """الحصول على مستخدم محدد"""
            result = self.db.get_user(chat_id)
            return jsonify(result)
        
        @self.app.route('/api/users', methods=['POST'])
        @self.require_api_key
        def add_user():
            """إضافة مستخدم جديد"""
            data = request.get_json()
            chat_id = data.get('chat_id')
            
            if not chat_id:
                return jsonify({"error": "chat_id مطلوب"}), 400
            
            result = self.db.add_user(int(chat_id))
            return jsonify(result), 201
        
        @self.app.route('/api/users/<int:chat_id>', methods=['DELETE'])
        @self.require_api_key
        def delete_user(chat_id):
            """حذف مستخدم"""
            result = self.db.delete_user(chat_id)
            return jsonify(result)
        
        # ═══════════════════════════════════════════════════════════
        # الاشتراكات
        # ═══════════════════════════════════════════════════════════
        
        @self.app.route('/api/subscriptions', methods=['POST'])
        @self.require_api_key
        def subscribe():
            """الاشتراك برقم طالب"""
            data = request.get_json()
            chat_id = data.get('chat_id')
            student_id = data.get('student_id')
            
            if not chat_id or not student_id:
                return jsonify({"error": "chat_id و student_id مطلوبة"}), 400
            
            result = self.db.subscribe_user(int(chat_id), student_id)
            return jsonify(result), 201
        
        @self.app.route('/api/subscriptions/<int:chat_id>', methods=['GET'])
        @self.require_api_key
        def get_subscription(chat_id):
            """الحصول على اشتراك المستخدم"""
            result = self.db.get_subscription(chat_id)
            return jsonify(result)
        
        @self.app.route('/api/subscriptions/student/<student_id>', methods=['GET'])
        @self.require_api_key
        def get_student_subscribers(student_id):
            """الحصول على المشتركين لطالب معين"""
            result = self.db.get_subscriptions_for_student(student_id)
            return jsonify(result)
        
        @self.app.route('/api/subscriptions/<int:chat_id>', methods=['DELETE'])
        @self.require_api_key
        def unsubscribe(chat_id):
            """إلغاء الاشتراك"""
            result = self.db.unsubscribe_user(chat_id)
            return jsonify(result)
        
        # ═══════════════════════════════════════════════════════════
        # الدرجات
        # ═══════════════════════════════════════════════════════════
        
        @self.app.route('/api/grades', methods=['POST'])
        @self.require_api_key
        def add_grade():
            """إضافة درجة جديدة"""
            data = request.get_json()
            
            required_fields = ['student_id', 'student_name', 'father_name',
                             'subject_name', 'practical_grade',
                             'theoretical_grade', 'total_grade',
                             'grade_in_words', 'result']
            
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"{field} مطلوب"}), 400
            
            result = self.db.add_grade(
                student_id=data['student_id'],
                student_name=data['student_name'],
                father_name=data['father_name'],
                subject_name=data['subject_name'],
                practical_grade=int(data['practical_grade']),
                theoretical_grade=int(data['theoretical_grade']),
                total_grade=int(data['total_grade']),
                grade_in_words=data['grade_in_words'],
                result=data['result'],
                rank=data.get('rank')
            )
            
            return jsonify(result), 201
        
        @self.app.route('/api/grades/student/<student_id>', methods=['GET'])
        @self.require_api_key
        def get_student_grades(student_id):
            """الحصول على درجات طالب"""
            result = self.db.get_student_grades(student_id)
            return jsonify(result)
        
        @self.app.route('/api/grades/subject/<subject_name>', methods=['GET'])
        @self.require_api_key
        def get_subject_grades(subject_name):
            """الحصول على درجات مادة معينة"""
            result = self.db.get_subject_grades(subject_name)
            return jsonify(result)
        
        @self.app.route('/api/grades/student/<student_id>/subject/<subject_name>',
                       methods=['PUT'])
        @self.require_api_key
        def update_grade(student_id, subject_name):
            """تحديث درجة"""
            data = request.get_json()
            
            result = self.db.update_grade(
                student_id=student_id,
                subject_name=subject_name,
                practical_grade=int(data.get('practical_grade', 0)),
                theoretical_grade=int(data.get('theoretical_grade', 0)),
                total_grade=int(data.get('total_grade', 0)),
                grade_in_words=data.get('grade_in_words', ''),
                result=data.get('result', '')
            )
            
            return jsonify(result)
        
        # ═══════════════════════════════════════════════════════════
        # درجات اللغة
        # ═══════════════════════════════════════════════════════════
        
        @self.app.route('/api/grades/language', methods=['POST'])
        @self.require_api_key
        def add_language_grade():
            """إضافة درجة لغة"""
            data = request.get_json()
            
            result = self.db.add_language_grade(
                student_id=data['student_id'],
                student_name=data['student_name'],
                father_name=data['father_name'],
                practical_grade=int(data['practical_grade']),
                theoretical_grade=int(data['theoretical_grade']),
                total_grade=int(data['total_grade']),
                grade_in_words=data['grade_in_words'],
                result=data['result']
            )
            
            return jsonify(result), 201
        
        @self.app.route('/api/grades/language/<student_id>', methods=['GET'])
        @self.require_api_key
        def get_language_grade(student_id):
            """الحصول على درجة اللغة"""
            result = self.db.get_language_grade(student_id)
            return jsonify(result)
        
        # ═══════════════════════════════════════════════════════════
        # درجات الطلاب
        # ═══════════════════════════════════════════════════════════
        
        @self.app.route('/api/grades/student-general', methods=['POST'])
        @self.require_api_key
        def add_student_grade():
            """إضافة درجة طالب عام"""
            data = request.get_json()
            
            result = self.db.add_student_grade(
                student_id=data['student_id'],
                student_name=data['student_name'],
                father_name=data['father_name'],
                practical_grade=int(data['practical_grade']),
                theoretical_grade=int(data['theoretical_grade']),
                total_grade=int(data['total_grade']),
                grade_in_words=data['grade_in_words'],
                result=data['result']
            )
            
            return jsonify(result), 201
        
        @self.app.route('/api/grades/student-general/<student_id>', methods=['GET'])
        @self.require_api_key
        def get_student_grade(student_id):
            """الحصول على درجة طالب عام"""
            result = self.db.get_student_grade(student_id)
            return jsonify(result)
        
        # ═══════════════════════════════════════════════════════════
        # الدرجات المعروفة (JSON)
        # ═══════════════════════════════════════════════════════════
        
        @self.app.route('/api/grades/known', methods=['POST'])
        @self.require_api_key
        def save_known_grades():
            """حفظ الدرجات المعروفة"""
            data = request.get_json()
            
            result = self.db.save_known_grades(
                student_id=data['student_id'],
                grades_data=data['grades_data']
            )
            
            return jsonify(result), 201
        
        @self.app.route('/api/grades/known/<student_id>', methods=['GET'])
        @self.require_api_key
        def get_known_grades(student_id):
            """الحصول على الدرجات المعروفة"""
            result = self.db.get_known_grades(student_id)
            return jsonify(result)
        
        # ═══════════════════════════════════════════════════════════
        # عمليات عامة
        # ═══════════════════════════════════════════════════════════
        
        @self.app.route('/api/students', methods=['GET'])
        @self.require_api_key
        def get_all_students():
            """الحصول على جميع الطلاب"""
            result = self.db.get_all_students()
            return jsonify(result)
        
        @self.app.route('/api/statistics', methods=['GET'])
        @self.require_api_key
        def get_statistics():
            """الحصول على إحصائيات النظام"""
            result = self.db.get_statistics()
            return jsonify(result)
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """فحص صحة API"""
            return jsonify({
                "status": "ok",
                "message": "Cloud Database API is running"
            })
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """تشغيل خادم API"""
        self.app.run(host=host, port=port, debug=debug)


# ==============================================================================
# مثال الاستخدام
# ==============================================================================

def create_api(supabase: Client) -> CloudDatabaseAPI:
    """
    إنشاء وتشغيل API
    
    مثال:
    ```python
    from supabase import create_client
    from cloud_database_api import create_api
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    api = create_api(supabase)
    api.run()
    ```
    """
    return CloudDatabaseAPI(supabase)


if __name__ == "__main__":
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
    api = create_api(supabase)
    
    print("🚀 بدء تشغيل API على http://0.0.0.0:5000")
    print("📝 تذكر: استخدم X-API-Key header مع جميع الطلبات")
    
    api.run(debug=True)
