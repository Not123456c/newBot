"""
وحدة نظام التقديرات
تحويل الدرجات إلى تقديرات حرفية
"""

def get_rating(grade):
    """تحويل الدرجة إلى تقدير حرفي"""
    grade = float(grade) if grade else 0
    
    if grade >= 95:
        return {'letter': 'A+', 'rating': 'A+', 'emoji': '⭐', 'description': 'ممتاز جداً'}
    elif grade >= 90:
        return {'letter': 'A', 'rating': 'A', 'emoji': '⭐', 'description': 'ممتاز'}
    elif grade >= 85:
        return {'letter': 'B+', 'rating': 'B+', 'emoji': '👍', 'description': 'جيد جداً'}
    elif grade >= 80:
        return {'letter': 'B', 'rating': 'B', 'emoji': '👍', 'description': 'جيد'}
    elif grade >= 75:
        return {'letter': 'C+', 'rating': 'C+', 'emoji': '📌', 'description': 'فوق الوسط'}
    elif grade >= 70:
        return {'letter': 'C', 'rating': 'C', 'emoji': '📌', 'description': 'وسط'}
    elif grade >= 65:
        return {'letter': 'D+', 'rating': 'D+', 'emoji': '⚡', 'description': 'مقبول'}
    elif grade >= 60:
        return {'letter': 'D', 'rating': 'D', 'emoji': '⚡', 'description': 'ضعيف'}
    else:
        return {'letter': 'F', 'rating': 'F', 'emoji': '❌', 'description': 'راسب'}

def grade_to_percentage(grade):
    """تحويل الدرجة إلى نسبة مئوية"""
    return round(float(grade), 1)

def get_color_code(grade):
    """الحصول على رمز اللون بناءً على الدرجة"""
    grade = float(grade) if grade else 0
    
    if grade >= 85:
        return "🟢"  # أخضر (ممتاز)
    elif grade >= 75:
        return "🟡"  # أصفر (جيد)
    elif grade >= 60:
        return "🟠"  # برتقالي (مقبول)
    else:
        return "🔴"  # أحمر (ضعيف)

def format_grade_display(grade):
    """تنسيق عرض الدرجة مع التقدير والإيموجي"""
    rating_info = get_rating(grade)
    color = get_color_code(grade)
    percentage = grade_to_percentage(grade)
    
    return f"{color} {percentage}% - {rating_info['rating']} {rating_info['emoji']}"
