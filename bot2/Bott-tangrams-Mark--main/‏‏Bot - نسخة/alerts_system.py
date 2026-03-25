"""
وحدة نظام التنبيهات الذكية
تنبيهات وتحذيرات بناءً على الأداء
"""

def generate_alerts(stats, weak_subjects, passed_count, failed_count):
    """توليد التنبيهات والتحذيرات"""
    alerts = {
        'critical': [],      # تحذيرات حرجة
        'warning': [],       # تحذيرات عادية
        'info': []           # معلومات
    }
    
    avg_grade = stats.get('average_grade', 0)
    success_rate = stats.get('success_rate', 0)
    
    # تحذيرات حرجة
    if failed_count > 0:
        alerts['critical'].append({
            'icon': '🚨',
            'title': 'حالة حرجة',
            'message': f'أنت راسب في {failed_count} مادة(مواد)! تحتاج إجراء فوري!'
        })
    
    if avg_grade < 50:
        alerts['critical'].append({
            'icon': '❌',
            'title': 'أداء ضعيف جداً',
            'message': f'معدلك {avg_grade}% - أقل من المستوى المقبول!'
        })
    
    # تحذيرات عادية
    if weak_subjects:
        weak_count = len([s for s in weak_subjects if s['grade'] < 60])
        if weak_count > 0:
            alerts['warning'].append({
                'icon': '⚠️',
                'title': 'مواد ضعيفة',
                'message': f'لديك {weak_count} مادة بعلامات منخفضة جداً (<60%)'
            })
    
    if success_rate < 50:
        alerts['warning'].append({
            'icon': '📊',
            'title': 'معدل النجاح منخفض',
            'message': f'نسبة نجاحك {success_rate}% - قم بمراجعة استراتيجيتك'
        })
    
    if 50 <= avg_grade < 65:
        alerts['warning'].append({
            'icon': '⚡',
            'title': 'أداء دون المتوقع',
            'message': 'معدلك متوسط - بذل جهد إضافي سيحسن نتيجتك'
        })
    
    # معلومات إيجابية
    if failed_count == 0 and avg_grade >= 60:
        alerts['info'].append({
            'icon': '✅',
            'title': 'نجاح كامل',
            'message': 'نجحت في جميع المواد! احتفل بهذا الإنجاز!'
        })
    
    if avg_grade >= 85:
        alerts['info'].append({
            'icon': '🌟',
            'title': 'أداء ممتاز',
            'message': 'معدلك ممتاز - استمر على هذا النمط!'
        })
    
    return alerts

def format_alerts_message(alerts):
    """تنسيق الرسالة النهائية للتنبيهات"""
    message = ""
    
    # التحذيرات الحرجة
    if alerts['critical']:
        message += "🚨 *التنبيهات الحرجة:*\n"
        for alert in alerts['critical']:
            message += f"{alert['icon']} *{alert['title']}*\n{alert['message']}\n\n"
    
    # التحذيرات العادية
    if alerts['warning']:
        message += "⚠️ *تحذيرات:*\n"
        for alert in alerts['warning']:
            message += f"{alert['icon']} *{alert['title']}*\n{alert['message']}\n\n"
    
    # المعلومات الإيجابية
    if alerts['info']:
        message += "✨ *معلومات إيجابية:*\n"
        for alert in alerts['info']:
            message += f"{alert['icon']} *{alert['title']}*\n{alert['message']}\n\n"
    
    return message if message else "لا توجد تنبيهات حالياً ✅"

def should_notify_about_exam_prep(weak_subjects, days_to_exam=30):
    """تحديد إذا كان يجب إرسال تنبيه بالتحضير للامتحانات"""
    if not weak_subjects:
        return False, ""
    
    if len(weak_subjects) > 0:
        return True, f"📚 يتبقى {days_to_exam} يوم للامتحانات! ركز على المواد: {', '.join([s['name'] for s in weak_subjects[:3]])}"
    
    return False, ""
