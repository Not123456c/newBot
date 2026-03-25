"""
وحدة الإدارة والصيانة
أدوات إدارية للمشرفين
"""

from datetime import datetime
import os
import json
import glob
import pandas as pd

def generate_admin_menu_keyboard():
    """توليد لوحة مفاتيح إدارية"""
    keyboard_data = {
        'buttons': [
            ['📊 الإحصائيات العامة', '👥 عدد المستخدمين'],
            ['📈 الأداء', '🧹 تنظيف الملفات'],
            ['📝 السجلات', '⚙️ الإعدادات'],
            ['🔄 إعادة تشغيل', '❌ إيقاف']
        ]
    }
    return keyboard_data

def get_system_stats():
    """الحصول على إحصائيات النظام"""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'bot_status': 'active',
        'uptime': 'يتم الحساب...',
        'total_users': 0,  # يتم تحديثه من قاعدة البيانات
        'total_queries': 0,
        'memory_usage': f'{os.path.getsize(".")} bytes'
    }
    return stats

def cleanup_temp_files():
    """تنظيف الملفات المؤقتة"""
    temp_files = {
        'images': 0,
        'charts': 0,
        'reports': 0
    }
    
    # تنظيف صور النتائج
    for file in os.listdir('.'):
        if file.startswith('result_') and file.endswith('.png'):
            try:
                os.remove(file)
                temp_files['images'] += 1
            except:
                pass
        
        # تنظيف الرسوم البيانية
        if file.startswith('chart_') and file.endswith('.png'):
            try:
                os.remove(file)
                temp_files['charts'] += 1
            except:
                pass
        
        # تنظيف التقارير
        if file.startswith('report_') and (file.endswith('.pdf') or file.endswith('.txt')):
            try:
                os.remove(file)
                temp_files['reports'] += 1
            except:
                pass
    
    return temp_files

def get_log_statistics():
    """الحصول على إحصائيات السجلات"""
    log_stats = {
        'total_messages': 0,
        'total_errors': 0,
        'errors_today': 0
    }
    
    # محاولة قراءة السجلات
    try:
        if os.path.exists('logs'):
            for log_file in os.listdir('logs'):
                log_path = os.path.join('logs', log_file)
                if os.path.isfile(log_path):
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            if 'ERROR' in line:
                                log_stats['total_errors'] += 1
                            log_stats['total_messages'] += 1
    except:
        pass
    
    return log_stats

def get_admin_info():
    """الحصول على معلومات إدارية شاملة"""
    info = {
        'system_stats': get_system_stats(),
        'temp_files': cleanup_temp_files(),
        'log_stats': get_log_statistics(),
        'generated_at': datetime.now().isoformat()
    }
    return info

def export_admin_report():
    """تصدير تقرير إداري"""
    report = {
        'title': 'تقرير إداري - بوت النتائج الجامعية',
        'date': datetime.now().isoformat(),
        'data': get_admin_info()
    }
    
    report_name = f"admin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(report_name, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report_name
    except Exception as e:
        print(f"Error exporting report: {e}")
        return None

def format_admin_message(info):
    """تنسيق رسالة إدارية"""
    sys_stats = info['system_stats']
    temp_files = info['temp_files']
    log_stats = info['log_stats']
    
    message = (
        f"👨‍💼 *لوحة التحكم الإدارية*\n\n"
        f"🤖 *حالة النظام:*\n"
        f"├ الحالة: {sys_stats['bot_status']}\n"
        f"├ الوقت: {sys_stats['timestamp']}\n"
        f"└ استهلاك الذاكرة: {sys_stats['memory_usage']}\n\n"
        
        f"📊 *الإحصائيات:*\n"
        f"├ إجمالي العمليات: {log_stats['total_messages']}\n"
        f"├ عدد الأخطاء: {log_stats['total_errors']}\n"
        f"└ أخطاء اليوم: {log_stats['errors_today']}\n\n"
        
        f"🧹 *الملفات المؤقتة المحذوفة:*\n"
        f"├ صور: {temp_files['images']}\n"
        f"├ رسوم بيانية: {temp_files['charts']}\n"
        f"└ تقارير: {temp_files['reports']}\n"
    )
    
    return message

def get_recent_errors(limit=15):
    """جلب أحدث الأخطاء من ملفات السجلات"""
    try:
        if not os.path.exists('logs'):
            return "لا يوجد مجلد للسجلات حتى الآن."
            
        # العثور على أحدث ملف سجل
        log_files = glob.glob(os.path.join('logs', '*.log'))
        if not log_files:
            return "لا توجد ملفات سجلات."
            
        latest_log = max(log_files, key=os.path.getctime)
        errors = []
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # البحث عن الأخطاء من الأحدث للأقدم
            for line in reversed(lines):
                if 'ERROR' in line or 'Exception' in line:
                    errors.append(line.strip())
                    if len(errors) >= limit:
                        break
        
        if not errors:
            return "✅ لا توجد أخطاء مسجلة في السجل الأخير بفضل الله."
            
        formatted_errors = "⚠️ *أحدث الأخطاء المسجلة:*\n\n"
        for i, err in enumerate(errors, 1):
            # تبسيط الرسالة قليلاً للتلجرام
            err_parts = err.split(' - ', 3)
            short_err = err_parts[-1] if len(err_parts) > 3 else err
            formatted_errors += f"{i}. `{short_err}`\n"
            
        return formatted_errors
    except Exception as e:
        return f"حدث خطأ أثناء قراءة السجلات: {str(e)}"

def generate_excel_backup(supabase):
    """توليد ملف Excel يحتوي على بيانات جميع الطلاب"""
    try:
        response = supabase.table("all_marks").select("*").execute()
        data = response.data
        if not data:
            return None
            
        df = pd.DataFrame(data)
        
        # ترتيب الأعمدة وتسميتها لتكون أجمل
        if not df.empty:
            columns_mapping = {
                'student_id': 'الرقم الامتحاني',
                'student_name': 'اسم الطالب',
                'subject_name': 'المادة',
                'theoretical_grade': 'النظري',
                'practical_grade': 'العملي',
                'total_grade': 'المجموع',
                'result': 'النتيجة'
            }
            # إبقاء فقط الأعمدة المعروفة وإعادة تسميتها
            existing_cols = [col for col in columns_mapping.keys() if col in df.columns]
            df = df[existing_cols]
            df = df.rename(columns=columns_mapping)
            
            # فرز حسب الرقم الامتحاني
            df = df.sort_values(by='الرقم الامتحاني')
        
        output_path = f"students_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(output_path, index=False, engine='openpyxl')
        return output_path
    except Exception as e:
        print(f"Error generating Excel: {str(e)}")
        return None

def get_top_10_students(supabase):
    """جلب قائمة بأفضل 10 طلاب بناءً على المعدل العام"""
    return get_top_n_students(supabase, n=10)

def get_all_subjects(supabase):
    """جلب قائمة بجميع المواد الموجودة في قاعدة البيانات"""
    try:
        all_data = []
        start = 0
        limit = 1000
        while True:
            response = supabase.table("all_marks").select("subject_name").range(start, start + limit - 1).execute()
            data = response.data
            if not data:
                break
            all_data.extend(data)
            if len(data) < limit:
                break
            start += limit
            
        if not all_data:
            return []
        
        # إزالة التكرارات والفارغة
        subjects = list(set([item.get('subject_name') for item in all_data if item.get('subject_name')]))
        return sorted(subjects)
    except Exception as e:
        print(f"Error getting subjects: {str(e)}")
        return []

def get_top_10_in_subject(supabase, subject_name):
    """جلب أفضل 10 طلاب في مادة معينة"""
    try:
        all_data = []
        start = 0
        limit = 1000
        while True:
            response = supabase.table("all_marks").select("student_id, student_name, total_grade").eq("subject_name", subject_name).range(start, start + limit - 1).execute()
            data = response.data
            if not data:
                break
            all_data.extend(data)
            if len(data) < limit:
                break
            start += limit
            
        if not all_data:
            return f"❌ لا توجد بيانات للمادة '{subject_name}'."
        
        df = pd.DataFrame(all_data)
        
        # تحويل الدرجات إلى أرقام
        df["total_grade"] = pd.to_numeric(df["total_grade"], errors="coerce")
        df = df.dropna(subset=["total_grade"])
        
        # إزالة التكرارات (في حالة وجود نفس الطالب مع نفس الدرجة)
        df = df.drop_duplicates(subset=["student_id"], keep="first")
        
        # ترتيب الطلاب حسب الدرجة تنازلياً
        top_10 = df.sort_values(by="total_grade", ascending=False).head(10)
        
        if top_10.empty:
            return f"❌ لا توجد بيانات كافية للمادة '{subject_name}'."
        
        message = f"🏆 *قائمة الـ 10 الأوائل في مادة: {subject_name}* 🏆\n\n"
        medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
        
        for i, (_, row) in enumerate(top_10.iterrows()):
            medal = medals[i] if i < len(medals) else "🏅"
            message += f"{medal} *المركز {i+1}*\n"
            message += f"👤 الاسم: `{row['student_name']}`\n"
            message += f"🔢 الرقم الامتحاني: `{row['student_id']}`\n"
            message += f"📊 الدرجة: *{row['total_grade']:.1f}* ⭐\n"
            message += "ـ" * 25 + "\n"
        
        return message
    
    except Exception as e:
        return f"❌ حدث خطأ أثناء الحساب: {str(e)}"

def get_top_n_students(supabase, n=5, return_data=False, use_cache=True):
    """جلب أفضل N طلاب على الدفعة بناءً على المعدل العام
    
    Args:
        supabase: اتصال قاعدة البيانات
        n: عدد الأوائل المطلوب (افتراضي 5)
        return_data: إذا كان True، ترجع (text, data)، وإلا ترجع text فقط
        use_cache: استخدام التخزين المؤقت (افتراضي True)
    
    Returns:
        رسالة منسقة بأفضل N طالب
        إذا كان return_data=True: (text, top_n_dataframe)
        وإلا: text فقط
    """
    # محاولة جلب من الـ Cache
    if use_cache:
        try:
            from cache_manager import cache
            cache_key = f"top_students_{n}_{return_data}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"✅ Cache HIT: top_students_{n}")
                return cached_result
        except ImportError:
            pass  # استمر بدون cache
    
    try:
        all_data = []
        start = 0
        limit = 1000
        while True:
            response = supabase.table("all_marks").select("student_id, student_name, total_grade").range(start, start + limit - 1).execute()
            data = response.data
            if not data:
                break
            all_data.extend(data)
            if len(data) < limit:
                break
            start += limit

        if not all_data:
            if return_data:
                return f"❌ لا توجد بيانات للطلاب حالياً.", None
            return f"❌ لا توجد بيانات للطلاب حالياً."

        df = pd.DataFrame(all_data)

        # تحويل الدرجات إلى أرقام وتجاهل القيم غير الصالحة
        df["total_grade"] = pd.to_numeric(df["total_grade"], errors="coerce")
        df = df.dropna(subset=["total_grade"])

        # تجميع العلامات لكل طالب على حدة وحساب المعدل وعدد المواد
        student_stats = df.groupby(["student_id", "student_name"]).agg(
            average_grade=("total_grade", "mean"),
            total_subjects=("total_grade", "count")
        ).reset_index()

        # للحصول على أوائل الدفعة الحقيقيين، نعتمد فقط على من قدموا جميع المواد المتاحة (الحد الأقصى للمواد في النظام)
        if not student_stats.empty:
            max_subjects = student_stats["total_subjects"].max()
            student_stats = student_stats[student_stats["total_subjects"] == max_subjects]

        # ترتيب الطلاب حسب المعدل تنازلياً 
        top_n = student_stats.sort_values(by="average_grade", ascending=False).head(n)

        if top_n.empty:
            if return_data:
                return f"❌ لا توجد بيانات كافية لحساب الأوائل.", None
            return f"❌ لا توجد بيانات كافية لحساب الأوائل."

        # اختيار الميداليات بناءً على عدد الأوائل
        medals = {
            1: ["🥇"],
            2: ["🥇", "🥈"],
            3: ["🥇", "🥈", "🥉"],
            4: ["🥇", "🥈", "🥉", "🏅"],
            5: ["🥇", "🥈", "🥉", "🏅", "🏅"],
        }
        
        default_medals = ["🥇", "🥈", "🥉"] + ["🏅"] * (n - 3)
        selected_medals = medals.get(n, default_medals[:n])

        message = f"🏆 *قائمة أفضل {n} طلاب على الدفعة* 🏆\n\n"

        # حلقة لطباعة النتيجة وتنسيقها بشكل جميل
        for i, (_, row) in enumerate(top_n.iterrows()):
            medal = selected_medals[i] if i < len(selected_medals) else "🏅"
            message += f"{medal} *المركز {i+1}*\n"
            message += f"👤 الاسم: `{row['student_name']}`\n"
            message += f"🔢 الرقم الامتحاني: `{row['student_id']}`\n"
            message += f"📊 المعدل: *{row['average_grade']:.2f}* (من {int(row['total_subjects'])} مواد)\n"
            message += "ـ" * 30 + "\n"

        result = (message, top_n) if return_data else message
        
        # حفظ في الـ Cache
        if use_cache:
            try:
                from cache_manager import cache
                cache.set(cache_key, result, ttl_seconds=600)  # 10 دقائق
                print(f"✅ Cache SET: top_students_{n}")
            except:
                pass
        
        return result

    except Exception as e:
        error_msg = f"❌ حدث خطأ أثناء الحساب: {str(e)}"
        if return_data:
            return error_msg, None
        return error_msg

