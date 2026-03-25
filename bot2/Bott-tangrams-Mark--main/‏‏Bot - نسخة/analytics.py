"""
وحدة الإحصائيات والتحليلات
التحليل الشامل لنتائج الطالب
"""

def calculate_statistics(marks_data):
    """حساب إحصائيات شاملة للنتائج"""
    if not marks_data:
        return {}
    
    total_grades = [m.get('total_grade', 0) for m in marks_data if m.get('total_grade')]
    passed = sum(1 for m in marks_data if m.get('result') == 'ناجح')
    failed = sum(1 for m in marks_data if m.get('result') == 'راسب')
    
    stats = {
        'total_subjects': len(marks_data),
        'passed_subjects': passed,
        'failed_subjects': failed,
        'success_rate': round((passed / len(marks_data) * 100), 1) if marks_data else 0,
        'failure_rate': round((failed / len(marks_data) * 100), 1) if marks_data else 0,
        'highest_grade': max(total_grades) if total_grades else 0,
        'lowest_grade': min(total_grades) if total_grades else 0,
        'average_grade': round(sum(total_grades) / len(total_grades), 2) if total_grades else 0,
        'subjects_data': marks_data
    }
    
    return stats

def get_weak_subjects(marks_data, threshold=60):
    """الحصول على المواد الضعيفة"""
    weak = []
    for m in marks_data:
        grade = m.get('total_grade', 0)
        if grade < threshold:
            weak.append({
                'name': m.get('subject_name', 'غير محدد'),
                'grade': grade,
                'theoretical': m.get('theoretical_grade', 0),
                'practical': m.get('practical_grade', 0),
                'result': m.get('result', '—')
            })
    return sorted(weak, key=lambda x: x['grade'])

def get_strong_subjects(marks_data, threshold=80):
    """الحصول على المواد القوية"""
    strong = []
    for m in marks_data:
        grade = m.get('total_grade', 0)
        if grade >= threshold:
            strong.append({
                'name': m.get('subject_name', 'غير محدد'),
                'grade': grade,
                'theoretical': m.get('theoretical_grade', 0),
                'practical': m.get('practical_grade', 0),
            })
    return sorted(strong, key=lambda x: x['grade'], reverse=True)

def analyze_performance(marks_data):
    """تحليل شامل للأداء"""
    stats = calculate_statistics(marks_data)
    weak_subjects = get_weak_subjects(marks_data)
    strong_subjects = get_strong_subjects(marks_data)
    
    # تحديد مستوى الأداء
    avg = stats.get('average_grade', 0)
    if avg >= 85:
        performance_level = "ممتاز"
        emoji = "🌟"
    elif avg >= 75:
        performance_level = "جيد جداً"
        emoji = "⭐"
    elif avg >= 65:
        performance_level = "جيد"
        emoji = "👍"
    elif avg >= 50:
        performance_level = "مقبول"
        emoji = "📌"
    else:
        performance_level = "ضعيف"
        emoji = "⚠️"
    
    return {
        'statistics': stats,
        'weak_subjects': weak_subjects,
        'strong_subjects': strong_subjects,
        'performance_level': performance_level,
        'performance_emoji': emoji
    }

def get_top_10_students(supabase):
    """جلب قائمة بأوائل الدفعة (أعلى 10 طلاب بناءً على معدل الدرجات)"""
    try:
        # جلب جميع العلامات
        response = supabase.table("all_marks").select("*").execute()
        data = response.data
        if not data:
            return "لا توجد بيانات كافية لحساب الأوائل."
            
        # تجميع درجات كل طالب
        students_grades = {}
        for row in data:
            sid = row.get('student_id')
            name = row.get('student_name', 'طالب غير معروف')
            grade = row.get('total_grade')
            if sid and grade is not None:
                if sid not in students_grades:
                    students_grades[sid] = {'name': name, 'total': 0, 'count': 0}
                students_grades[sid]['total'] += grade
                students_grades[sid]['count'] += 1
                
        # حساب المعدل لكل طالب
        averages = []
        for sid, info in students_grades.items():
            if info['count'] > 0:
                avg = round(info['total'] / info['count'], 2)
                averages.append({
                    'id': sid,
                    'name': info['name'],
                    'avg': avg
                })
                
        # ترتيب الطلاب تنازلياً وأخذ أول 10
        averages.sort(key=lambda x: x['avg'], reverse=True)
        top_10 = averages[:10]
        
        if not top_10:
            return "لا توجد بيانات كافية لتوليد لوحة الشرف."
            
        # تنسيق الرسالة
        msg = "🏆 *لوحة الشرف - أوائل الدفعة* 🏆\n\n"
        medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
        
        for i, student in enumerate(top_10):
            medal = medals[i] if i < len(medals) else "🔹"
            # إخفاء جزء من الاسم للخصوصية إذا أردنا، أو عرضه كامل
            # هنا نعرضه كامل كلوحة شرف عامة
            msg += f"{medal} *المركز {i+1}*\n"
            msg += f"👤 الاسم: `{student['name']}`\n"
            msg += f"📊 المعدل: *{student['avg']}%*\n\n"
            
        return msg
        
    except Exception as e:
        print(f"Error calculating top 10: {e}")
        return "حدث خطأ أثناء حساب أوائل الدفعة."
