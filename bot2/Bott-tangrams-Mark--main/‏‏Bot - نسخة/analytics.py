"""
وحدة الإحصائيات والتحليلات - نسخة محسّنة
التحليل الشامل لنتائج الطالب مع استخدام Cache
"""

def calculate_statistics_fast(student_id, supabase):
    """
    🚀 حساب الإحصائيات من Cache (سريع جداً)
    يستخدم جدول student_stats_cache للأداء الأفضل
    
    Args:
        student_id: رقم الطالب
        supabase: اتصال قاعدة البيانات
    
    Returns:
        dict: الإحصائيات الجاهزة
    """
    try:
        # محاولة جلب من Cache أولاً
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
                'rank_percentile': cache_data.get('rank_percentile')
            }
            
            # جلب بيانات المواد
            marks_response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
            stats['subjects_data'] = marks_response.data if marks_response.data else []
            
            print(f"✅ استخدام Cache للطالب {student_id}")
            return stats
        else:
            # إذا لم يكن في Cache، احسب وحفظ
            print(f"⚠️ لا يوجد في Cache، جاري الحساب للطالب {student_id}")
            return calculate_and_cache_statistics(student_id, supabase)
            
    except Exception as e:
        print(f"❌ خطأ في جلب من Cache: {e}")
        # Fallback للطريقة القديمة
        try:
            marks_response = supabase.table("all_marks").select("*").eq("student_id", student_id).execute()
            return calculate_statistics(marks_response.data if marks_response.data else [])
        except:
            return {}


def calculate_and_cache_statistics(student_id, supabase):
    """حساب الإحصائيات وحفظها في Cache"""
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
        
        # محاولة حفظ في Cache
        try:
            supabase.table("student_stats_cache").upsert({
                'student_id': student_id,
                'total_subjects': stats['total_subjects'],
                'passed_subjects': stats['passed_subjects'],
                'failed_subjects': stats['failed_subjects'],
                'success_rate': stats['success_rate'],
                'average_grade': stats['average_grade'],
                'highest_grade': stats['highest_grade'],
                'lowest_grade': stats['lowest_grade']
            }).execute()
            print(f"✅ تم حفظ الإحصائيات في Cache")
        except Exception as cache_error:
            print(f"⚠️ تعذر الحفظ في Cache: {cache_error}")
        
        return stats
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return {}


def calculate_statistics(marks_data):
    """حساب إحصائيات شاملة للنتائج (الطريقة القديمة - للتوافق)"""
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
    """
    🚀 جلب قائمة بأوائل الدفعة من Cache (سريع جداً)
    يستخدم جدول student_stats_cache بدلاً من حساب الكل
    """
    try:
        # محاولة جلب من Cache
        response = supabase.table("student_stats_cache").select(
            "student_id, average_grade, rank"
        ).order("average_grade", desc=True).limit(10).execute()
        
        if response.data and len(response.data) > 0:
            # جلب أسماء الطلاب من جدول students أو all_marks
            student_ids = [s['student_id'] for s in response.data]
            
            # محاولة جلب من جدول students أولاً
            try:
                students_response = supabase.table("students").select(
                    "student_id, student_name"
                ).in_("student_id", student_ids).execute()
                
                if students_response.data:
                    names_dict = {s['student_id']: s['student_name'] for s in students_response.data}
                else:
                    raise Exception("No data from students table")
                    
            except:
                # Fallback: جلب من all_marks
                marks_response = supabase.table("all_marks").select(
                    "student_id, student_name"
                ).in_("student_id", student_ids).execute()
                
                names_dict = {}
                for m in marks_response.data:
                    if m['student_id'] not in names_dict:
                        names_dict[m['student_id']] = m.get('student_name', 'طالب غير معروف')
            
            # تنسيق الرسالة
            msg = "🏆 *لوحة الشرف - أوائل الدفعة* 🏆\n\n"
            medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
            
            for i, student in enumerate(response.data):
                medal = medals[i] if i < len(medals) else "🔹"
                name = names_dict.get(student['student_id'], 'طالب غير معروف')
                
                msg += f"{medal} *المركز {i+1}*\n"
                msg += f"👤 الاسم: `{name}`\n"
                msg += f"📊 المعدل: *{student['average_grade']}%*\n"
                
                if student.get('rank'):
                    msg += f"🏅 الترتيب العام: #{student['rank']}\n"
                    
                msg += "\n"
            
            print("✅ استخدام Cache لجلب الأوائل (سريع)")
            return msg
        else:
            # إذا لم يكن هناك بيانات في Cache، استخدم الطريقة القديمة
            print("⚠️ Cache فارغ، استخدام الطريقة القديمة")
            return get_top_10_students_legacy(supabase)
        
    except Exception as e:
        print(f"❌ خطأ في جلب من Cache: {e}")
        return get_top_10_students_legacy(supabase)


def get_top_10_students_legacy(supabase):
    """جلب قائمة بأوائل الدفعة (الطريقة القديمة - Fallback)"""
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
            msg += f"{medal} *المركز {i+1}*\n"
            msg += f"👤 الاسم: `{student['name']}`\n"
            msg += f"📊 المعدل: *{student['avg']}%*\n\n"
            
        return msg
        
    except Exception as e:
        print(f"Error calculating top 10: {e}")
        return "حدث خطأ أثناء حساب أوائل الدفعة."
