"""
وحدة تحليلات الدفعة الشاملة
تحليل شامل لأداء جميع الطلاب والمواد
"""

import pandas as pd
from ratings import get_rating

def fetch_all_records(supabase, table_name="all_marks"):
    """جلب جميع البيانات من قاعدة البيانات مع تجاوز حد الـ 1000 سجل"""
    all_data = []
    limit = 1000
    offset = 0
    try:
        while True:
            response = supabase.table(table_name).select("*").range(offset, offset + limit - 1).execute()
            data = response.data
            if not data:
                break
            all_data.extend(data)
            if len(data) < limit:
                break
            offset += limit
        return all_data
    except Exception as e:
        print(f"Error fetching all records: {e}")
        return all_data

def get_cohort_analytics(supabase):
    """جلب إحصائيات الدفعة الشاملة"""
    try:
        data = fetch_all_records(supabase)
        
        if not data:
            return {
                'total_students': 0,
                'total_records': 0,
                'pass_count': 0,
                'fail_count': 0,
                'pass_rate': 0,
                'fail_rate': 0,
                'overall_average': 0,
                'highest_grade': 0,
                'lowest_grade': 0,
                'error': 'لا توجد بيانات'
            }
        
        df = pd.DataFrame(data)
        
        # إحصاء الطلاب الفريدين
        total_students = df['student_id'].nunique() if 'student_id' in df.columns else 0
        
        # إحصاء النجاح والرسوب
        pass_count = len(df[df['result'] == 'ناجح']) if 'result' in df.columns else 0
        fail_count = len(df[df['result'] == 'راسب']) if 'result' in df.columns else 0
        
        total_records = len(df)
        pass_rate = round((pass_count / total_records * 100), 2) if total_records > 0 else 0
        fail_rate = round((fail_count / total_records * 100), 2) if total_records > 0 else 0
        
        # إحصاء الدرجات
        if 'total_grade' in df.columns:
            df['total_grade'] = pd.to_numeric(df['total_grade'], errors='coerce')
            grades = df['total_grade'].dropna()
            overall_average = round(grades.mean(), 2) if len(grades) > 0 else 0
            highest_grade = grades.max() if len(grades) > 0 else 0
            lowest_grade = grades.min() if len(grades) > 0 else 0
        else:
            overall_average = 0
            highest_grade = 0
            lowest_grade = 0
        
        return {
            'total_students': total_students,
            'total_records': total_records,
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': pass_rate,
            'fail_rate': fail_rate,
            'overall_average': overall_average,
            'highest_grade': highest_grade,
            'lowest_grade': lowest_grade
        }
    except Exception as e:
        print(f"Error in get_cohort_analytics: {e}")
        return {'error': str(e)}


def get_grade_distribution(supabase):
    """حساب توزيع التقديرات (A+, A, B, C, D, F)"""
    try:
        data = fetch_all_records(supabase)
        
        if not data:
            return {}
        
        distribution = {
            'A+': 0,
            'A': 0,
            'B': 0,
            'C': 0,
            'D': 0,
            'F': 0
        }
        
        df = pd.DataFrame(data)
        
        if 'total_grade' in df.columns:
            df['total_grade'] = pd.to_numeric(df['total_grade'], errors='coerce')
            
            for grade in df['total_grade'].dropna():
                rating_info = get_rating(grade)
                rating_letter = rating_info.get('letter', 'F')
                if rating_letter in distribution:
                    distribution[rating_letter] += 1
        
        return distribution
    except Exception as e:
        print(f"Error in get_grade_distribution: {e}")
        return {}


def get_subjects_performance(supabase):
    """حساب أداء كل مادة"""
    try:
        data = fetch_all_records(supabase)
        
        if not data:
            return []
        
        df = pd.DataFrame(data)
        
        if not {'subject_name', 'total_grade', 'result'}.issubset(df.columns):
            return []
        
        df['total_grade'] = pd.to_numeric(df['total_grade'], errors='coerce')
        
        subject_stats = df.groupby('subject_name').agg({
            'total_grade': ['mean', 'max', 'min', 'count'],
            'result': lambda x: (x == 'ناجح').sum()
        }).round(2)
        
        subject_stats.columns = ['average', 'highest', 'lowest', 'total_records', 'passed']
        subject_stats = subject_stats.reset_index()
        subject_stats['pass_rate'] = (subject_stats['passed'] / subject_stats['total_records'] * 100).round(2)
        
        return subject_stats.sort_values('average', ascending=False).to_dict('records')
    except Exception as e:
        print(f"Error in get_subjects_performance: {e}")
        return []


def get_at_risk_students(supabase, risk_threshold=40):
    """الحصول على الطلاب في خطر"""
    try:
        data = fetch_all_records(supabase)
        
        if not data:
            return []
        
        df = pd.DataFrame(data)
        
        if 'total_grade' not in df.columns or 'student_id' not in df.columns:
            return []
        
        df['total_grade'] = pd.to_numeric(df['total_grade'], errors='coerce')
        
        student_avg = df.groupby(['student_id', 'student_name'])['total_grade'].mean().reset_index()
        student_avg.columns = ['student_id', 'student_name', 'average']
        
        at_risk = student_avg[student_avg['average'] < risk_threshold].sort_values('average')
        
        return at_risk.to_dict('records')
    except Exception as e:
        print(f"Error in get_at_risk_students: {e}")
        return []


def get_borderline_students(supabase, lower=40, upper=50):
    """الحصول على الطلاب على حافة الرسوب"""
    try:
        data = fetch_all_records(supabase)
        
        if not data:
            return []
        
        df = pd.DataFrame(data)
        
        if 'total_grade' not in df.columns or 'student_id' not in df.columns:
            return []
        
        df['total_grade'] = pd.to_numeric(df['total_grade'], errors='coerce')
        
        student_avg = df.groupby(['student_id', 'student_name'])['total_grade'].mean().reset_index()
        student_avg.columns = ['student_id', 'student_name', 'average']
        
        borderline = student_avg[(student_avg['average'] >= lower) & (student_avg['average'] < upper)]
        
        return borderline.sort_values('average').to_dict('records')
    except Exception as e:
        print(f"Error in get_borderline_students: {e}")
        return []


def get_incomplete_students(supabase):
    """الحصول على الطلاب الذين لم يكملوا جميع المواد"""
    try:
        data = fetch_all_records(supabase)
        
        if not data:
            return []
        
        df = pd.DataFrame(data)
        
        if 'student_id' not in df.columns:
            return []
        
        # الحصول على عدد المواد لكل طالب
        student_subject_count = df.groupby('student_id')['subject_name'].nunique().reset_index()
        student_subject_count.columns = ['student_id', 'subject_count']
        
        # الحصول على الحد الأقصى للمواد
        max_subjects = student_subject_count['subject_count'].max()
        
        # الطلاب الذين لم يكملوا جميع المواد
        incomplete = student_subject_count[student_subject_count['subject_count'] < max_subjects]
        
        # دمج مع بيانات الطلاب
        if not incomplete.empty:
            incomplete_data = df[df['student_id'].isin(incomplete['student_id'])][['student_id', 'student_name']].drop_duplicates()
            result = incomplete_data.merge(incomplete, on='student_id')
            return result.to_dict('records')
        
        return []
    except Exception as e:
        print(f"Error in get_incomplete_students: {e}")
        return []


def format_cohort_message(analytics):
    """تنسيق رسالة إحصائيات الدفعة"""
    if 'error' in analytics:
        return f"❌ خطأ: {analytics['error']}"
    
    message = (
        f"📊 *تحليلات الدفعة الشاملة*\n\n"
        f"👥 *إحصائيات عامة:*\n"
        f"├ عدد الطلاب: `{analytics['total_students']}`\n"
        f"├ إجمالي التسجيلات: `{analytics['total_records']}`\n"
        f"└ متوسط الدفعة: `{analytics['overall_average']}`\n\n"
        
        f"✅ *النجاح والرسوب:*\n"
        f"├ ناجح: `{analytics['pass_count']}` ({analytics['pass_rate']}%)\n"
        f"├ راسب: `{analytics['fail_count']}` ({analytics['fail_rate']}%)\n"
        f"└ نسبة النجاح الكلية: `{analytics['pass_rate']}%`\n\n"
        
        f"📈 *إحصائيات الدرجات:*\n"
        f"├ أعلى درجة: `{analytics['highest_grade']}`\n"
        f"├ أقل درجة: `{analytics['lowest_grade']}`\n"
        f"└ متوسط الدفعة: `{analytics['overall_average']}`\n"
    )
    
    return message


def format_grade_distribution_message(distribution):
    """تنسيق رسالة توزيع التقديرات"""
    total = sum(distribution.values())
    
    message = "⭐ *توزيع التقديرات:*\n\n"
    
    grades_order = ['A+', 'A', 'B', 'C', 'D', 'F']
    for grade in grades_order:
        count = distribution.get(grade, 0)
        percentage = round((count / total * 100), 1) if total > 0 else 0
        bar_length = int(count / max(distribution.values()) * 10) if max(distribution.values()) > 0 else 0
        bar = '█' * bar_length + '░' * (10 - bar_length)
        
        message += f"{grade}: {count:3d} {bar} ({percentage}%)\n"
    
    return message


def format_subjects_performance_message(subjects):
    """تنسيق رسالة أداء المواد"""
    if not subjects:
        return "❌ لا توجد بيانات عن المواد"
    
    message = "📚 *أداء جميع المواد:*\n\n"
    
    for i, subject in enumerate(subjects, 1):
        sub_name = subject['subject_name']
        avg = subject['average']
        pass_rate = subject['pass_rate']
        
        if pass_rate >= 80:
            emoji = "🟢"
        elif pass_rate >= 60:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        message += f"{emoji} {i}. `{sub_name}`\n"
        message += f"   ├ المتوسط: {avg}\n"
        message += f"   ├ نسبة النجاح: {pass_rate}%\n"
        message += f"   └ الحد الأقصى: {subject['highest']}\n\n"
    
    return message


def format_at_risk_message(at_risk_students):
    """تنسيق رسالة الطلاب في خطر"""
    if not at_risk_students:
        return "✅ لا يوجد طلاب في خطر حالياً"
    
    message = f"🚨 *طلاب في خطر حقيقي (متوسط < 40%):*\n\n"
    
    for student in at_risk_students[:15]:
        message += f"⚠️ {student['student_name']}\n"
        message += f"   └ الرقم: `{student['student_id']}` | المتوسط: `{student['average']:.2f}`\n\n"
    
    return message


def format_borderline_message(borderline_students):
    """تنسيق رسالة الطلاب على حافة الرسوب"""
    if not borderline_students:
        return "✅ لا يوجد طلاب على حافة الرسوب حالياً"
    
    message = f"⚠️ *طلاب على حافة الرسوب (40-50%):*\n\n"
    
    for student in borderline_students[:15]:
        message += f"📌 {student['student_name']}\n"
        message += f"   └ الرقم: `{student['student_id']}` | المتوسط: `{student['average']:.2f}`\n\n"
    
    return message


def format_incomplete_message(incomplete_students):
    """تنسيق رسالة الطلاب الذين لم يكملوا المواد"""
    if not incomplete_students:
        return "✅ جميع الطلاب أكملوا المواد المطلوبة"
    
    message = f"📋 *طلاب لم يكملوا جميع المواد:*\n\n"
    
    for student in incomplete_students[:15]:
        subjects_count = student['subject_count']
        message += f"❌ {student['student_name']}\n"
        message += f"   └ الرقم: `{student['student_id']}` | المواد المكتملة: `{int(subjects_count)}`\n\n"
    
    return message
