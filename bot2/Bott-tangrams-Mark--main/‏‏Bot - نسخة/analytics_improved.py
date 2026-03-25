"""
وحدة الإحصائيات والتحليلات - نسخة محسّنة
استخدام student_stats_cache لأداء أفضل
"""

def calculate_statistics_fast(student_id, supabase):
    """
    حساب الإحصائيات من Cache (سريع جداً) 🚀
    
    Args:
        student_id: رقم الطالب
        supabase: اتصال قاعدة البيانات
    
    Returns:
        dict: الإحصائيات الجاهزة
    """
    try:
        # 🚀 جلب من Cache (سريع جداً - استعلام واحد)
        response = supabase.table("student_stats_cache").select("*").eq("student_id", student_id).execute()
        
        if response.data and len(response.data) > 0:
            cache_data = response.data[0]
            
            # تحويل إلى الصيغة المتوقعة
            stats = {
                'total_subjects': cache_data.get('total_subjects', 0),
                'passed_subjects': cache_data.get('passed_subjects', 0),
                'failed_subjects': cache_data.get('failed_subjects', 0),
                'success_rate': float(cache_data.get('success_rate', 0)),
                'failure_rate': 100 - float(cache_data.get('success_rate', 0)),
                'average_grade': float(cache_data.get('average_grade', 0)),
                'highest_grade': cache_data.get('highest_grade', 0),
                'lowest_grade': cache_data.get('lowest_grade', 0),
                'gpa': cache_data.get('gpa'),
                'rank': cache_data.get('rank'),
                'rank_percentile': cache_data.get('rank_percentile'),
                'last_updated': cache_data.get('last_updated')
            }
            
            print(f"✅ استخدام Cache للطالب {student_id} (سريع)")
            return stats
        else:
            # إذا لم يكن موجود في Cache، احسب واحفظ
            print(f"⚠️ لا يوجد في Cache، جاري الحساب للطالب {student_id}")
            return calculate_statistics_and_cache(student_id, supabase)
            
    except Exception as e:
        print(f"❌ خطأ في جلب من Cache: {e}")
        # Fallback: استخدام الطريقة القديمة
        return calculate_statistics_legacy(student_id, supabase)


def calculate_statistics_and_cache(student_id, supabase):
    """
    حساب الإحصائيات وحفظها في Cache
    يُستخدم فقط إذا لم يكن موجود في Cache
    """
    try:
        # جلب البيانات
        response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
        marks_data = response.data
        
        if not marks_data:
            return {}
        
        # حساب الإحصائيات
        total_grades = [m.get('total_grade', 0) for m in marks_data if m.get('total_grade')]
        passed = sum(1 for m in marks_data if m.get('result') == 'ناجح' or (m.get('total_grade', 0) >= 60))
        failed = sum(1 for m in marks_data if m.get('result') == 'راسب' or (m.get('total_grade', 0) < 60))
        
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
        
        # حفظ في Cache
        try:
            supabase.table("student_stats_cache").upsert({
                'student_id': student_id,
                'total_subjects': stats['total_subjects'],
                'passed_subjects': stats['passed_subjects'],
                'failed_subjects': stats['failed_subjects'],
                'success_rate': stats['success_rate'],
                'average_grade': stats['average_grade'],
                'highest_grade': stats['highest_grade'],
                'lowest_grade': stats['lowest_grade'],
                'last_updated': 'now()'
            }).execute()
            print(f"✅ تم حفظ الإحصائيات في Cache للطالب {student_id}")
        except Exception as cache_error:
            print(f"⚠️ تعذر الحفظ في Cache: {cache_error}")
        
        return stats
        
    except Exception as e:
        print(f"❌ خطأ في حساب الإحصائيات: {e}")
        return {}


def calculate_statistics_legacy(student_id, supabase):
    """
    الطريقة القديمة (Fallback فقط)
    """
    try:
        response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
        marks_data = response.data
        
        if not marks_data:
            return {}
        
        total_grades = [m.get('total_grade', 0) for m in marks_data if m.get('total_grade')]
        passed = sum(1 for m in marks_data if m.get('result') == 'ناجح')
        failed = sum(1 for m in marks_data if m.get('result') == 'راسب')
        
        return {
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
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return {}


def calculate_statistics(marks_data):
    """
    الدالة الأصلية - للتوافق مع الكود القديم
    """
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


def get_top_10_students_fast(supabase):
    """
    🚀 جلب الأوائل من Cache (سريع جداً)
    بدلاً من حساب آلاف السجلات
    """
    try:
        response = supabase.table("student_stats_cache").select(
            "student_id, average_grade, total_subjects, rank"
        ).order("average_grade", desc=True).limit(10).execute()
        
        if not response.data:
            return "لا توجد بيانات كافية لحساب الأوائل."
        
        # جلب أسماء الطلاب
        student_ids = [s['student_id'] for s in response.data]
        students_response = supabase.table("students").select(
            "student_id, student_name"
        ).in_("student_id", student_ids).execute()
        
        # دمج البيانات
        students_dict = {s['student_id']: s['student_name'] for s in students_response.data}
        
        # تنسيق الرسالة
        msg = "🏆 *لوحة الشرف - أوائل الدفعة* 🏆\n\n"
        medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
        
        for i, student in enumerate(response.data):
            medal = medals[i] if i < len(medals) else "🔹"
            name = students_dict.get(student['student_id'], 'غير معروف')
            msg += f"{medal} *المركز {i+1}*\n"
            msg += f"👤 الاسم: `{name}`\n"
            msg += f"📊 المعدل: *{student['average_grade']}%*\n\n"
        
        print("✅ استخدام Cache لجلب الأوائل (سريع جداً)")
        return msg
        
    except Exception as e:
        print(f"❌ خطأ في جلب الأوائل من Cache: {e}")
        # Fallback للطريقة القديمة
        return get_top_10_students_legacy(supabase)


def get_top_10_students_legacy(supabase):
    """الطريقة القديمة (Fallback)"""
    try:
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
            msg += f"{medal} *المركز {i+1}*\n"
            msg += f"👤 الاسم: `{student['name']}`\n"
            msg += f"📊 المعدل: *{student['avg']}%*\n\n"
        
        return msg
        
    except Exception as e:
        print(f"Error calculating top 10: {e}")
        return "حدث خطأ أثناء حساب أوائل الدفعة."


# دالة للتوافق مع الكود القديم
def get_top_10_students(supabase):
    """
    نقطة دخول موحدة - تحاول Cache أولاً
    """
    return get_top_10_students_fast(supabase)
