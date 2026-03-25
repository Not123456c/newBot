# -*- coding: utf-8 -*-
"""
صفحة الويب العامة للنتائج
Public Results Web Page
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from supabase import create_client
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# إعداد Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None


# ══════════════════════════════════════
# الصفحات
# ══════════════════════════════════════

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return render_template('public/index.html')


@app.route('/results/<student_id>')
def view_results(student_id):
    """صفحة نتائج طالب"""
    return render_template('public/results.html', student_id=student_id)


@app.route('/top')
def view_top():
    """صفحة الأوائل"""
    return render_template('public/top.html')


@app.route('/search')
def search_page():
    """صفحة البحث"""
    return render_template('public/search.html')


# ══════════════════════════════════════
# API Endpoints
# ══════════════════════════════════════

@app.route('/api/public/results/<student_id>')
def api_get_results(student_id):
    """API لجلب نتائج طالب"""
    try:
        response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
        
        if not response.data:
            return jsonify({'success': False, 'error': 'لا توجد نتائج'})
        
        marks = response.data
        student_name = marks[0].get('student_name', '') if marks else ''
        
        # حساب الإحصائيات
        grades = [m['total_grade'] for m in marks if m.get('total_grade')]
        passed = len([g for g in grades if g >= 60])
        
        stats = {
            'total_subjects': len(marks),
            'passed_subjects': passed,
            'failed_subjects': len(grades) - passed,
            'success_rate': round(passed / len(grades) * 100, 1) if grades else 0,
            'average_grade': round(sum(grades) / len(grades), 2) if grades else 0,
            'highest_grade': max(grades) if grades else 0,
            'lowest_grade': min(grades) if grades else 0
        }
        
        # تحديد التقدير
        avg = stats['average_grade']
        if avg >= 95: rating = {'name': 'A+', 'label': 'امتياز مرتفع', 'color': '#22c55e'}
        elif avg >= 90: rating = {'name': 'A', 'label': 'امتياز', 'color': '#22c55e'}
        elif avg >= 85: rating = {'name': 'B+', 'label': 'جيد جداً مرتفع', 'color': '#3b82f6'}
        elif avg >= 80: rating = {'name': 'B', 'label': 'جيد جداً', 'color': '#3b82f6'}
        elif avg >= 75: rating = {'name': 'C+', 'label': 'جيد مرتفع', 'color': '#f59e0b'}
        elif avg >= 70: rating = {'name': 'C', 'label': 'جيد', 'color': '#f59e0b'}
        elif avg >= 65: rating = {'name': 'D+', 'label': 'مقبول مرتفع', 'color': '#f97316'}
        elif avg >= 60: rating = {'name': 'D', 'label': 'مقبول', 'color': '#f97316'}
        else: rating = {'name': 'F', 'label': 'راسب', 'color': '#ef4444'}
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'student_name': student_name,
            'marks': marks,
            'stats': stats,
            'rating': rating
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/public/top/<int:n>')
def api_get_top(n):
    """API لجلب الأوائل"""
    try:
        n = min(n, 50)
        
        response = supabase.table("all_marks").select("student_id, student_name, total_grade").execute()
        
        students = {}
        for row in response.data:
            sid = row['student_id']
            grade = row.get('total_grade', 0) or 0
            
            if sid not in students:
                students[sid] = {
                    'student_id': sid,
                    'student_name': row.get('student_name', ''),
                    'total': 0,
                    'count': 0
                }
            
            students[sid]['total'] += float(grade)
            students[sid]['count'] += 1
        
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


@app.route('/api/public/search')
def api_search():
    """API للبحث"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query or len(query) < 2:
            return jsonify({'success': False, 'error': 'أدخل حرفين على الأقل'})
        
        response = supabase.table("all_marks").select("student_id, student_name").ilike("student_name", f"%{query}%").execute()
        
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


@app.route('/api/public/stats')
def api_stats():
    """إحصائيات عامة"""
    try:
        response = supabase.table("all_marks").select("total_grade").execute()
        
        grades = [r['total_grade'] for r in response.data if r.get('total_grade')]
        
        return jsonify({
            'success': True,
            'total_students': len(set(r.get('student_id') for r in response.data)),
            'total_grades': len(grades),
            'average_grade': round(sum(grades) / len(grades), 2) if grades else 0,
            'pass_rate': round(len([g for g in grades if g >= 60]) / len(grades) * 100, 1) if grades else 0
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ══════════════════════════════════════
# تشغيل التطبيق
# ══════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('WEB_PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🌐 صفحة النتائج العامة تعمل على المنفذ {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
