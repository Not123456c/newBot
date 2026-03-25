# -*- coding: utf-8 -*-
"""
Telegram Mini App - Backend API
تطبيق Flask للتواصل مع قاعدة البيانات وتقديم الواجهة
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from supabase import create_client
import os
import json
import hashlib
from datetime import datetime
from functools import wraps

# تحميل متغيرات البيئة
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# إعداد Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("⚠️ تحذير: Supabase غير متصل!")

# ══════════════════════════════════════
# التحقق من Telegram Web App
# ══════════════════════════════════════

def verify_telegram_data(init_data):
    """التحقق من صحة بيانات Telegram"""
    try:
        if not init_data or not BOT_TOKEN:
            return None
        
        # فك تشفير البيانات
        import urllib.parse
        import hmac
        
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        
        if 'hash' not in parsed_data:
            return None
        
        received_hash = parsed_data.pop('hash')
        
        # ترتيب البيانات
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        # حساب المفتاح السري
        secret_key = hmac.new(
            b"WebAppData",
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # حساب الـ hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if calculated_hash == received_hash:
            # استخراج بيانات المستخدم
            if 'user' in parsed_data:
                return json.loads(parsed_data['user'])
        
        return None
    except Exception as e:
        print(f"خطأ في التحقق: {e}")
        return None

def get_user_from_request():
    """استخراج بيانات المستخدم من الطلب"""
    init_data = request.headers.get('X-Telegram-Init-Data', '')
    return verify_telegram_data(init_data)

# ══════════════════════════════════════
# الصفحات
# ══════════════════════════════════════

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

# ══════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════

@app.route('/api/health')
def health_check():
    """فحص صحة الخدمة"""
    return jsonify({
        'status': 'ok',
        'database': 'connected' if supabase else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """الحصول على الملف الشخصي المحفوظ"""
    try:
        telegram_id = request.args.get('telegram_id')
        
        if not telegram_id:
            return jsonify({'success': False, 'error': 'telegram_id مطلوب'})
        
        # البحث عن الملف الشخصي
        response = supabase.table("mini_app_profiles").select("*").eq("telegram_id", int(telegram_id)).execute()
        
        if response.data and len(response.data) > 0:
            profile = response.data[0]
            return jsonify({
                'success': True,
                'has_profile': True,
                'profile': {
                    'telegram_id': profile['telegram_id'],
                    'student_id': profile['student_id'],
                    'student_name': profile.get('student_name', ''),
                    'linked_at': profile.get('linked_at', '')
                }
            })
        
        return jsonify({
            'success': True,
            'has_profile': False
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user/link', methods=['POST'])
def link_student():
    """ربط الرقم الامتحاني بحساب Telegram"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        student_id = data.get('student_id')
        telegram_name = data.get('telegram_name', '')
        
        if not telegram_id or not student_id:
            return jsonify({'success': False, 'error': 'البيانات ناقصة'})
        
        # التحقق من وجود الطالب
        student_response = supabase.table("all_marks").select("student_name").eq("student_id", student_id).limit(1).execute()
        
        if not student_response.data:
            return jsonify({'success': False, 'error': 'الرقم الامتحاني غير موجود في قاعدة البيانات'})
        
        student_name = student_response.data[0].get('student_name', '')
        
        # حفظ أو تحديث الربط
        supabase.table("mini_app_profiles").upsert({
            'telegram_id': int(telegram_id),
            'student_id': student_id,
            'student_name': student_name,
            'telegram_name': telegram_name,
            'linked_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }).execute()
        
        return jsonify({
            'success': True,
            'message': 'تم ربط الحساب بنجاح',
            'student_name': student_name
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user/unlink', methods=['POST'])
def unlink_student():
    """إلغاء ربط الحساب"""
    try:
        data = request.json
        telegram_id = data.get('telegram_id')
        
        if not telegram_id:
            return jsonify({'success': False, 'error': 'telegram_id مطلوب'})
        
        supabase.table("mini_app_profiles").delete().eq("telegram_id", int(telegram_id)).execute()
        
        return jsonify({'success': True, 'message': 'تم إلغاء الربط'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/results/<student_id>')
def get_results(student_id):
    """الحصول على نتائج طالب"""
    try:
        response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
        
        if not response.data:
            return jsonify({'success': False, 'error': 'لا توجد نتائج'})
        
        marks = response.data
        student_name = marks[0].get('student_name', '') if marks else ''
        father_name = marks[0].get('father_name', '') if marks else ''
        
        # حساب الإحصائيات
        total_grades = []
        passed = 0
        failed = 0
        
        for m in marks:
            grade = m.get('total_grade')
            if grade is not None:
                total_grades.append(float(grade))
                if float(grade) >= 60:
                    passed += 1
                else:
                    failed += 1
        
        avg = sum(total_grades) / len(total_grades) if total_grades else 0
        
        stats = {
            'total_subjects': len(marks),
            'passed_subjects': passed,
            'failed_subjects': failed,
            'success_rate': round((passed / len(marks) * 100) if marks else 0, 1),
            'average_grade': round(avg, 2),
            'highest_grade': max(total_grades) if total_grades else 0,
            'lowest_grade': min(total_grades) if total_grades else 0
        }
        
        # ترتيب المواد
        weak_subjects = []
        strong_subjects = []
        
        for m in marks:
            grade = m.get('total_grade', 0) or 0
            subject_info = {
                'name': m.get('subject_name', ''),
                'grade': grade,
                'result': m.get('result', '')
            }
            if float(grade) < 60:
                weak_subjects.append(subject_info)
            elif float(grade) >= 80:
                strong_subjects.append(subject_info)
        
        weak_subjects.sort(key=lambda x: x['grade'])
        strong_subjects.sort(key=lambda x: x['grade'], reverse=True)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'student_name': student_name,
            'father_name': father_name,
            'marks': marks,
            'stats': stats,
            'weak_subjects': weak_subjects[:5],
            'strong_subjects': strong_subjects[:5]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/search')
def search_students():
    """البحث عن طلاب بالاسم"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'success': False, 'error': 'أدخل حرفين على الأقل'})
        
        response = supabase.table("all_marks").select("student_id, student_name").ilike("student_name", f"%{query}%").execute()
        
        # إزالة التكرارات
        seen = set()
        results = []
        for r in response.data:
            sid = r['student_id']
            if sid not in seen:
                seen.add(sid)
                results.append({
                    'student_id': sid,
                    'student_name': r.get('student_name', '')
                })
        
        return jsonify({
            'success': True,
            'results': results[:20]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/top/<int:n>')
def get_top_students(n):
    """الحصول على أفضل n طلاب"""
    try:
        n = min(n, 50)  # حد أقصى 50
        
        response = supabase.table("all_marks").select("student_id, student_name, total_grade").execute()
        
        if not response.data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات'})
        
        # تجميع الدرجات لكل طالب
        students = {}
        for row in response.data:
            sid = row['student_id']
            grade = row.get('total_grade', 0) or 0
            
            if sid not in students:
                students[sid] = {
                    'student_id': sid,
                    'student_name': row.get('student_name', ''),
                    'grades': [],
                    'total': 0,
                    'count': 0
                }
            
            students[sid]['grades'].append(float(grade))
            students[sid]['total'] += float(grade)
            students[sid]['count'] += 1
        
        # حساب المتوسط وترتيب
        top_list = []
        for sid, data in students.items():
            if data['count'] > 0:
                avg = data['total'] / data['count']
                top_list.append({
                    'student_id': sid,
                    'student_name': data['student_name'],
                    'average': round(avg, 2),
                    'subjects_count': data['count']
                })
        
        top_list.sort(key=lambda x: x['average'], reverse=True)
        
        return jsonify({
            'success': True,
            'top_students': top_list[:n]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/exams')
def get_exams():
    """الحصول على جدول الامتحانات"""
    try:
        response = supabase.table("exam_schedule").select("*").gte("exam_date", datetime.now().date().isoformat()).order("exam_date").execute()
        
        exams = []
        for exam in response.data:
            exams.append({
                'id': exam.get('id'),
                'subject_name': exam.get('subject_name', ''),
                'exam_date': exam.get('exam_date', ''),
                'exam_time': exam.get('exam_time', ''),
                'location': exam.get('location', ''),
                'notes': exam.get('notes', '')
            })
        
        return jsonify({
            'success': True,
            'exams': exams
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'exams': []})

@app.route('/api/chart/grades/<student_id>')
def get_chart_data(student_id):
    """الحصول على بيانات الرسم البياني"""
    try:
        response = supabase.table("all_marks").select("subject_name, total_grade, theoretical_grade, practical_grade, result").eq("student_id", student_id).execute()
        
        if not response.data:
            return jsonify({'success': False, 'error': 'لا توجد بيانات'})
        
        chart_data = {
            'labels': [],
            'grades': [],
            'theoretical': [],
            'practical': [],
            'colors': []
        }
        
        for m in response.data:
            chart_data['labels'].append(m.get('subject_name', '')[:15])
            chart_data['grades'].append(m.get('total_grade', 0) or 0)
            chart_data['theoretical'].append(m.get('theoretical_grade', 0) or 0)
            chart_data['practical'].append(m.get('practical_grade', 0) or 0)
            
            grade = m.get('total_grade', 0) or 0
            if float(grade) >= 60:
                chart_data['colors'].append('#16a34a')
            else:
                chart_data['colors'].append('#dc2626')
        
        return jsonify({
            'success': True,
            'chart_data': chart_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ══════════════════════════════════════
# تشغيل التطبيق
# ══════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('MINI_APP_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Mini App يعمل على المنفذ {port}")
    print(f"📱 رابط التطبيق: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
