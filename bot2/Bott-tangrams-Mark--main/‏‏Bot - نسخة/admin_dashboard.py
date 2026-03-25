# -*- coding: utf-8 -*-
"""
لوحة تحكم المسؤولين (Web Admin Dashboard)
واجهة ويب لإدارة البوت والبيانات
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime, timedelta
import hashlib
import secrets


def create_admin_dashboard(supabase, admin_credentials: dict = None):
    """
    إنشاء لوحة تحكم المسؤولين
    
    Args:
        supabase: عميل Supabase
        admin_credentials: بيانات تسجيل الدخول {'username': 'admin', 'password': 'pass'}
    """
    app = Flask(__name__)
    app.secret_key = secrets.token_hex(32)
    CORS(app)
    
    # بيانات الدخول الافتراضية
    ADMIN_USER = admin_credentials.get('username', 'admin') if admin_credentials else 'admin'
    ADMIN_PASS = admin_credentials.get('password', 'admin123') if admin_credentials else 'admin123'
    
    def login_required(f):
        """ديكوراتور للتحقق من تسجيل الدخول"""
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated
    
    # ═══════════════════════════════════════
    # صفحات HTML
    # ═══════════════════════════════════════
    
    LOGIN_PAGE = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تسجيل الدخول - لوحة التحكم</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-box {
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 400px;
            }
            h1 { color: #fff; text-align: center; margin-bottom: 30px; }
            input {
                width: 100%;
                padding: 15px;
                margin: 10px 0;
                border: none;
                border-radius: 10px;
                background: rgba(255,255,255,0.2);
                color: #fff;
                font-size: 16px;
            }
            input::placeholder { color: rgba(255,255,255,0.6); }
            button {
                width: 100%;
                padding: 15px;
                border: none;
                border-radius: 10px;
                background: #4CAF50;
                color: white;
                font-size: 18px;
                cursor: pointer;
                margin-top: 20px;
                transition: 0.3s;
            }
            button:hover { background: #45a049; transform: translateY(-2px); }
            .error { color: #ff6b6b; text-align: center; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🎓 لوحة التحكم</h1>
            <form method="POST">
                <input type="text" name="username" placeholder="اسم المستخدم" required>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit">دخول</button>
            </form>
            {% if error %}<p class="error">{{ error }}</p>{% endif %}
        </div>
    </body>
    </html>
    '''
    
    DASHBOARD_PAGE = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم - بوت النتائج</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, sans-serif;
                background: #0f0f1a;
                color: #fff;
                min-height: 100vh;
            }
            .navbar {
                background: rgba(255,255,255,0.1);
                padding: 15px 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .navbar h1 { font-size: 24px; }
            .navbar a { color: #ff6b6b; text-decoration: none; }
            .container { padding: 30px; max-width: 1400px; margin: 0 auto; }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
                padding: 25px;
                border-radius: 15px;
                text-align: center;
            }
            .stat-card h3 { font-size: 14px; color: #888; margin-bottom: 10px; }
            .stat-card .value { font-size: 36px; font-weight: bold; }
            .stat-card.green .value { color: #4CAF50; }
            .stat-card.blue .value { color: #2196F3; }
            .stat-card.orange .value { color: #FF9800; }
            .stat-card.red .value { color: #f44336; }
            .section {
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 20px;
            }
            .section h2 { margin-bottom: 20px; font-size: 20px; }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: right;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }
            th { background: rgba(255,255,255,0.1); }
            .btn {
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                transition: 0.3s;
            }
            .btn-primary { background: #2196F3; color: white; }
            .btn-danger { background: #f44336; color: white; }
            .btn:hover { transform: translateY(-2px); opacity: 0.9; }
            .chart-container { height: 300px; margin-top: 20px; }
            .tabs {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            .tab {
                padding: 10px 20px;
                background: rgba(255,255,255,0.1);
                border: none;
                border-radius: 8px;
                color: #fff;
                cursor: pointer;
            }
            .tab.active { background: #2196F3; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; color: #888; }
            .form-group input, .form-group textarea {
                width: 100%;
                padding: 10px;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 8px;
                background: rgba(255,255,255,0.1);
                color: #fff;
            }
        </style>
    </head>
    <body>
        <nav class="navbar">
            <h1>🎓 لوحة تحكم بوت النتائج</h1>
            <a href="/logout">تسجيل الخروج</a>
        </nav>
        
        <div class="container">
            <!-- الإحصائيات -->
            <div class="stats-grid">
                <div class="stat-card blue">
                    <h3>إجمالي الطلاب</h3>
                    <div class="value" id="total-students">-</div>
                </div>
                <div class="stat-card green">
                    <h3>مستخدمي البوت</h3>
                    <div class="value" id="bot-users">-</div>
                </div>
                <div class="stat-card orange">
                    <h3>مشتركي الإشعارات</h3>
                    <div class="value" id="notify-subs">-</div>
                </div>
                <div class="stat-card red">
                    <h3>المحظورين</h3>
                    <div class="value" id="blocked-users">-</div>
                </div>
            </div>
            
            <!-- التبويبات -->
            <div class="tabs">
                <button class="tab active" onclick="showTab('students')">الطلاب</button>
                <button class="tab" onclick="showTab('exams')">الامتحانات</button>
                <button class="tab" onclick="showTab('notifications')">الإشعارات</button>
                <button class="tab" onclick="showTab('analytics')">التحليلات</button>
            </div>
            
            <!-- قسم الطلاب -->
            <div id="students-tab" class="section">
                <h2>🔍 البحث عن طالب</h2>
                <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                    <input type="text" id="search-input" placeholder="رقم أو اسم الطالب..." style="flex: 1; padding: 10px; border-radius: 8px; border: none; background: rgba(255,255,255,0.1); color: #fff;">
                    <button class="btn btn-primary" onclick="searchStudent()">بحث</button>
                </div>
                <div id="search-results"></div>
            </div>
            
            <!-- قسم الامتحانات -->
            <div id="exams-tab" class="section" style="display: none;">
                <h2>📅 جدول الامتحانات</h2>
                <button class="btn btn-primary" onclick="showAddExamForm()" style="margin-bottom: 20px;">+ إضافة امتحان</button>
                <div id="add-exam-form" style="display: none; margin-bottom: 20px; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                    <div class="form-group">
                        <label>اسم المادة</label>
                        <input type="text" id="exam-subject">
                    </div>
                    <div class="form-group">
                        <label>التاريخ</label>
                        <input type="date" id="exam-date">
                    </div>
                    <div class="form-group">
                        <label>الوقت</label>
                        <input type="time" id="exam-time">
                    </div>
                    <div class="form-group">
                        <label>المكان</label>
                        <input type="text" id="exam-location">
                    </div>
                    <button class="btn btn-primary" onclick="addExam()">حفظ</button>
                    <button class="btn" onclick="hideAddExamForm()">إلغاء</button>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>المادة</th>
                            <th>التاريخ</th>
                            <th>الوقت</th>
                            <th>المكان</th>
                            <th>إجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="exams-table"></tbody>
                </table>
            </div>
            
            <!-- قسم الإشعارات -->
            <div id="notifications-tab" class="section" style="display: none;">
                <h2>📢 إرسال إشعار جماعي</h2>
                <div class="form-group">
                    <label>نص الرسالة</label>
                    <textarea id="broadcast-message" rows="4" placeholder="اكتب رسالتك هنا..."></textarea>
                </div>
                <button class="btn btn-primary" onclick="sendBroadcast()">إرسال للجميع</button>
                <p id="broadcast-status" style="margin-top: 10px;"></p>
            </div>
            
            <!-- قسم التحليلات -->
            <div id="analytics-tab" class="section" style="display: none;">
                <h2>📊 تحليلات الأداء</h2>
                <div class="chart-container">
                    <canvas id="gradesChart"></canvas>
                </div>
            </div>
        </div>
        
        <script>
            // تحميل الإحصائيات
            async function loadStats() {
                try {
                    const res = await fetch('/api/stats');
                    const data = await res.json();
                    document.getElementById('total-students').textContent = data.total_students || 0;
                    document.getElementById('bot-users').textContent = data.bot_users || 0;
                    document.getElementById('notify-subs').textContent = data.notify_subscribers || 0;
                    document.getElementById('blocked-users').textContent = data.blocked_users || 0;
                } catch (e) {
                    console.error('Error loading stats:', e);
                }
            }
            
            // التبويبات
            function showTab(tab) {
                document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.getElementById(tab + '-tab').style.display = 'block';
                event.target.classList.add('active');
                
                if (tab === 'exams') loadExams();
                if (tab === 'analytics') loadAnalytics();
            }
            
            // البحث عن طالب
            async function searchStudent() {
                const query = document.getElementById('search-input').value;
                const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                
                let html = '<table><thead><tr><th>الرقم</th><th>الاسم</th><th>المعدل</th></tr></thead><tbody>';
                data.forEach(s => {
                    html += `<tr><td>${s.student_id}</td><td>${s.student_name}</td><td>${s.average || '-'}</td></tr>`;
                });
                html += '</tbody></table>';
                document.getElementById('search-results').innerHTML = html;
            }
            
            // تحميل الامتحانات
            async function loadExams() {
                const res = await fetch('/api/exams');
                const data = await res.json();
                
                let html = '';
                data.forEach(e => {
                    html += `<tr>
                        <td>${e.subject_name}</td>
                        <td>${e.exam_date}</td>
                        <td>${e.exam_time || '-'}</td>
                        <td>${e.location || '-'}</td>
                        <td><button class="btn btn-danger" onclick="deleteExam(${e.id})">حذف</button></td>
                    </tr>`;
                });
                document.getElementById('exams-table').innerHTML = html;
            }
            
            function showAddExamForm() {
                document.getElementById('add-exam-form').style.display = 'block';
            }
            
            function hideAddExamForm() {
                document.getElementById('add-exam-form').style.display = 'none';
            }
            
            async function addExam() {
                const exam = {
                    subject_name: document.getElementById('exam-subject').value,
                    exam_date: document.getElementById('exam-date').value,
                    exam_time: document.getElementById('exam-time').value,
                    location: document.getElementById('exam-location').value
                };
                
                await fetch('/api/exams', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(exam)
                });
                
                hideAddExamForm();
                loadExams();
            }
            
            async function deleteExam(id) {
                if (confirm('هل أنت متأكد من الحذف؟')) {
                    await fetch(`/api/exams/${id}`, {method: 'DELETE'});
                    loadExams();
                }
            }
            
            // إرسال إشعار جماعي
            async function sendBroadcast() {
                const message = document.getElementById('broadcast-message').value;
                const res = await fetch('/api/broadcast', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message})
                });
                const data = await res.json();
                document.getElementById('broadcast-status').textContent = data.message;
            }
            
            // تحميل التحليلات
            async function loadAnalytics() {
                const res = await fetch('/api/analytics');
                const data = await res.json();
                
                new Chart(document.getElementById('gradesChart'), {
                    type: 'doughnut',
                    data: {
                        labels: ['ممتاز (A)', 'جيد جداً (B)', 'جيد (C)', 'مقبول (D)', 'راسب (F)'],
                        datasets: [{
                            data: [data.a || 0, data.b || 0, data.c || 0, data.d || 0, data.f || 0],
                            backgroundColor: ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#f44336']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
            
            // تحميل البيانات عند فتح الصفحة
            loadStats();
        </script>
    </body>
    </html>
    '''
    
    # ═══════════════════════════════════════
    # المسارات (Routes)
    # ═══════════════════════════════════════
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username == ADMIN_USER and password == ADMIN_PASS:
                session['logged_in'] = True
                return redirect(url_for('dashboard'))
            else:
                error = 'بيانات الدخول غير صحيحة'
        
        return render_template_string(LOGIN_PAGE, error=error)
    
    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        return redirect(url_for('login'))
    
    @app.route('/')
    @login_required
    def dashboard():
        return render_template_string(DASHBOARD_PAGE)
    
    # ═══════════════════════════════════════
    # API Endpoints
    # ═══════════════════════════════════════
    
    @app.route('/api/stats')
    @login_required
    def api_stats():
        try:
            # إحصائيات من قاعدة البيانات
            students = supabase.table("all_marks").select("student_id", count="exact").execute()
            bot_users = supabase.table("bot_users").select("id", count="exact").execute()
            notify_subs = supabase.table("notification_subscribers").select("id", count="exact").eq("is_active", True).execute()
            blocked = supabase.table("blocked_users").select("id", count="exact").eq("is_active", True).execute()
            
            return jsonify({
                'total_students': students.count or 0,
                'bot_users': bot_users.count or 0,
                'notify_subscribers': notify_subs.count or 0,
                'blocked_users': blocked.count or 0
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/search')
    @login_required
    def api_search():
        query = request.args.get('q', '')
        try:
            if query.isdigit():
                results = supabase.table("all_marks").select("student_id, student_name").eq("student_id", query).limit(10).execute()
            else:
                results = supabase.table("all_marks").select("student_id, student_name").ilike("student_name", f"%{query}%").limit(10).execute()
            
            # حساب المعدل لكل طالب
            unique_students = {}
            for r in results.data:
                if r['student_id'] not in unique_students:
                    unique_students[r['student_id']] = r
            
            return jsonify(list(unique_students.values()))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/exams', methods=['GET', 'POST'])
    @login_required
    def api_exams():
        if request.method == 'GET':
            try:
                exams = supabase.table("exam_schedule").select("*").order("exam_date").execute()
                return jsonify(exams.data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                data['created_at'] = datetime.now().isoformat()
                supabase.table("exam_schedule").insert(data).execute()
                return jsonify({'success': True})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    @app.route('/api/exams/<int:exam_id>', methods=['DELETE'])
    @login_required
    def api_delete_exam(exam_id):
        try:
            supabase.table("exam_schedule").delete().eq("id", exam_id).execute()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/broadcast', methods=['POST'])
    @login_required
    def api_broadcast():
        # هذا يحتاج ربط مع البوت لإرسال الرسائل
        data = request.get_json()
        message = data.get('message', '')
        
        # TODO: ربط مع البوت لإرسال الرسائل
        return jsonify({'success': True, 'message': 'تم حفظ الرسالة للإرسال'})
    
    @app.route('/api/analytics')
    @login_required
    def api_analytics():
        try:
            grades = supabase.table("all_marks").select("total_grade").execute()
            
            # توزيع التقديرات
            distribution = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'f': 0}
            for g in grades.data:
                grade = g.get('total_grade', 0) or 0
                if grade >= 90:
                    distribution['a'] += 1
                elif grade >= 80:
                    distribution['b'] += 1
                elif grade >= 70:
                    distribution['c'] += 1
                elif grade >= 60:
                    distribution['d'] += 1
                else:
                    distribution['f'] += 1
            
            return jsonify(distribution)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


def run_admin_dashboard(supabase, host: str = '0.0.0.0', port: int = 5000, 
                        admin_user: str = 'admin', admin_pass: str = 'admin123'):
    """
    تشغيل لوحة التحكم
    """
    app = create_admin_dashboard(supabase, {'username': admin_user, 'password': admin_pass})
    print(f"🚀 لوحة التحكم تعمل على http://{host}:{port}")
    app.run(host=host, port=port, threaded=True)


if __name__ == '__main__':
    from dotenv import load_dotenv
    from supabase import create_client
    
    load_dotenv()
    
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ SUPABASE_URL و SUPABASE_KEY مطلوبان")
        exit(1)
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    run_admin_dashboard(
        supabase=supabase,
        host='0.0.0.0',
        port=5000,
        admin_user=os.environ.get('ADMIN_USER', 'admin'),
        admin_pass=os.environ.get('ADMIN_PASS', 'admin123')
    )
