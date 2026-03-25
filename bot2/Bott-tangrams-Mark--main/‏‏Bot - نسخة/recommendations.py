"""
وحدة النصائح والتوصيات الذكية
توصيات مخصصة بناءً على الأداء
"""

def generate_recommendations(analysis_data):
    """توليد نصائح وتوصيات ذكية"""
    stats = analysis_data.get('statistics', {})
    weak_subjects = analysis_data.get('weak_subjects', [])
    strong_subjects = analysis_data.get('strong_subjects', [])
    avg_grade = stats.get('average_grade', 0)
    
    recommendations = {
        'positive': [],
        'action_needed': [],
        'tips': []
    }
    
    # التوصيات الإيجابية
    if avg_grade >= 85:
        recommendations['positive'].append("🎉 أداؤك ممتاز! استمر على هذا المستوى المرتفع.")
    
    if strong_subjects:
        top_subject = strong_subjects[0]
        recommendations['positive'].append(
            f"⭐ أنت متفوق في مادة '{top_subject['name']}' - "
            f"حاول تطبيق نفس أسلوب الدراسة على المواد الأخرى."
        )
    
    if stats.get('success_rate', 0) == 100:
        recommendations['positive'].append("✅ نجحت في جميع المواد! عمل رائع!")
    
    # التوصيات المطلوبة إجراء
    if weak_subjects:
        weak_count = len(weak_subjects)
        if weak_count == 1:
            w = weak_subjects[0]
            recommendations['action_needed'].append(
                f"⚠️ المادة '{w['name']}' تحتاج اهتمام: {w['grade']}%\n"
                f"   ركز على الأجزاء الضعيفة خصوصاً النظري ({w['theoretical']}%)"
            )
        else:
            grades_list = ", ".join([f"{w['name']} ({w['grade']}%)" for w in weak_subjects[:3]])
            recommendations['action_needed'].append(
                f"📢 هناك {weak_count} مواد تحتاج جهد إضافي:\n"
                f"   {grades_list}"
            )
    
    if stats.get('failure_rate', 0) > 0:
        recommendations['action_needed'].append(
            f"❌ أنت راسب في {stats.get('failed_subjects', 0)} مادة(مواد). "
            f"اطلب مساعدة أكاديمية فوراً!"
        )
    
    if avg_grade < 70:
        recommendations['action_needed'].append(
            f"📊 معدلك الحالي {avg_grade}% - تحتاج لزيادة الجهد لتحسين النتيجة"
        )
    
    # نصائح عملية
    recommendations['tips'].append("💡 درس المواد الصعبة أولاً عندما تكون مركزاً")
    recommendations['tips'].append("📚 استخدم أسلوب الدراسة الجماعية للمواد الضعيفة")
    
    if stats.get('theoretical_weak'):
        recommendations['tips'].append("📖 ركز على الجانب النظري - قد يكون نقطة ضعفك")
    
    if stats.get('practical_weak'):
        recommendations['tips'].append("🔬 مارس التطبيقات العملية بشكل مكثف")
    
    recommendations['tips'].append("🎯 حدد أهدافاً قصيرة المدى لكل مادة ضعيفة")
    recommendations['tips'].append("⏱️ نظم وقتك: خذ فترات راحة منتظمة أثناء الدراسة")
    
    return recommendations

def get_motivation_message(performance_level):
    """رسالة تحفيزية بناءً على الأداء"""
    messages = {
        'ممتاز': "🌟 أنت نجم! استمر في هذا المسار المميز!",
        'جيد جداً': "⭐ أداؤك رائع جداً! بعض الجهد الإضافي سيجعلك نجماً!",
        'جيد': "👍 تقدم ملحوظ! لا تتوقف، يمكنك أفضل من هذا!",
        'مقبول': "📌 تقدم إيجابي، لكن تحتاج لبذل جهد أكبر!",
        'ضعيف': "⚡ هذا الوقت لتغيير استراتيجيتك! اطلب المساعدة الآن!"
    }
    return messages.get(performance_level, "📊 استمر في بذل الجهد!")
