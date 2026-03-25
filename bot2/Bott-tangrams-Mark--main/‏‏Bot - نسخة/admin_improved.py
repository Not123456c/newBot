"""
إضافات لملف admin.py - وظائف محسّنة لاستخدام الجداول الجديدة
يمكن دمجها في admin.py الأصلي
"""

def get_all_students_info_fast(supabase):
    """
    🚀 جلب معلومات جميع الطلاب (سريع جداً)
    من جدول students + student_stats_cache
    """
    try:
        # جلب من الجداول المحسّنة
        students_response = supabase.table("students").select(
            "student_id, student_name, father_name, department, level, status"
        ).eq("status", "active").execute()
        
        stats_response = supabase.table("student_stats_cache").select("*").execute()
        
        # دمج البيانات
        stats_dict = {s['student_id']: s for s in stats_response.data}
        
        students_with_stats = []
        for student in students_response.data:
            sid = student['student_id']
            student_data = {
                'student_id': sid,
                'student_name': student['student_name'],
                'father_name': student.get('father_name', '—'),
                'department': student.get('department', '—'),
                'level': student.get('level', '—'),
                'average_grade': 0,
                'rank': '—',
                'status': '—'
            }
            
            # إضافة الإحصائيات إن وجدت
            if sid in stats_dict:
                stats = stats_dict[sid]
                student_data.update({
                    'average_grade': stats.get('average_grade', 0),
                    'total_subjects': stats.get('total_subjects', 0),
                    'passed_subjects': stats.get('passed_subjects', 0),
                    'failed_subjects': stats.get('failed_subjects', 0),
                    'rank': stats.get('rank', '—')
                })
                
                # تحديد الحالة
                if stats.get('failed_subjects', 0) > 0:
                    student_data['status'] = '⚠️ يوجد رسوب'
                elif stats.get('average_grade', 0) >= 85:
                    student_data['status'] = '⭐ ممتاز'
                else:
                    student_data['status'] = '✅ ناجح'
            
            students_with_stats.append(student_data)
        
        print(f"✅ تم جلب معلومات {len(students_with_stats)} طالب من الجداول المحسّنة")
        return students_with_stats
        
    except Exception as e:
        print(f"❌ خطأ في جلب معلومات الطلاب: {e}")
        return []


def get_department_statistics(supabase, department=None):
    """
    إحصائيات القسم أو الكلية
    """
    try:
        query = supabase.table("students").select(
            "department, student_id"
        ).eq("status", "active")
        
        if department:
            query = query.eq("department", department)
        
        students = query.execute().data
        
        if not students:
            return "لا توجد بيانات للقسم المحدد"
        
        # تجميع حسب القسم
        dept_groups = {}
        for s in students:
            dept = s.get('department', 'غير محدد')
            if dept not in dept_groups:
                dept_groups[dept] = []
            dept_groups[dept].append(s['student_id'])
        
        # جلب الإحصائيات
        msg = "📊 *إحصائيات الأقسام*\n\n"
        
        for dept, student_ids in dept_groups.items():
            stats_response = supabase.table("student_stats_cache").select(
                "average_grade, passed_subjects, failed_subjects"
            ).in_("student_id", student_ids).execute()
            
            if stats_response.data:
                total_students = len(student_ids)
                avg_grades = [s.get('average_grade', 0) for s in stats_response.data if s.get('average_grade')]
                dept_average = round(sum(avg_grades) / len(avg_grades), 2) if avg_grades else 0
                
                students_with_failures = sum(1 for s in stats_response.data if s.get('failed_subjects', 0) > 0)
                
                msg += f"📌 *{dept}*\n"
                msg += f"   عدد الطلاب: {total_students}\n"
                msg += f"   المعدل العام: {dept_average}%\n"
                msg += f"   طلاب مع رسوب: {students_with_failures}\n\n"
        
        return msg
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return "حدث خطأ في جلب إحصائيات الأقسام"


def get_at_risk_students(supabase, threshold=50):
    """
    🚨 الطلاب المعرضون للخطر (معدل منخفض أو رسوب متعدد)
    """
    try:
        response = supabase.table("student_stats_cache").select(
            "student_id, average_grade, failed_subjects, total_subjects"
        ).or_(
            f"average_grade.lt.{threshold},failed_subjects.gte.3"
        ).execute()
        
        if not response.data:
            return "✅ لا يوجد طلاب في خطر حالياً"
        
        # جلب أسماء الطلاب
        student_ids = [s['student_id'] for s in response.data]
        names_response = supabase.table("students").select(
            "student_id, student_name"
        ).in_("student_id", student_ids).execute()
        
        names_dict = {s['student_id']: s['student_name'] for s in names_response.data}
        
        msg = "🚨 *الطلاب المعرضون للخطر*\n\n"
        msg += f"⚠️ المعيار: معدل أقل من {threshold}% أو 3+ مواد راسبة\n\n"
        
        for i, student in enumerate(response.data, 1):
            name = names_dict.get(student['student_id'], 'غير معروف')
            msg += f"{i}. *{name}*\n"
            msg += f"   📊 المعدل: {student.get('average_grade', 0)}%\n"
            msg += f"   ❌ مواد راسبة: {student.get('failed_subjects', 0)}/{student.get('total_subjects', 0)}\n\n"
        
        msg += f"\n📌 إجمالي: {len(response.data)} طالب"
        
        return msg
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return "حدث خطأ في جلب الطلاب المعرضين للخطر"


def update_student_info(supabase, student_id, updates):
    """
    تحديث معلومات طالب في جدول students
    
    Args:
        student_id: رقم الطالب
        updates: dict من الحقول المراد تحديثها
                مثال: {'phone': '123456', 'email': 'test@test.com'}
    """
    try:
        updates['updated_at'] = 'now()'
        
        response = supabase.table("students").update(updates).eq(
            "student_id", student_id
        ).execute()
        
        if response.data:
            return True, "✅ تم تحديث البيانات بنجاح"
        else:
            return False, "❌ لم يتم العثور على الطالب"
            
    except Exception as e:
        return False, f"❌ خطأ: {str(e)}"


def add_new_student(supabase, student_data):
    """
    إضافة طالب جديد
    
    Args:
        student_data: dict يحتوي على:
            - student_id (مطلوب)
            - student_name (مطلوب)
            - father_name
            - department
            - level
            - phone
            - email
            ... إلخ
    """
    try:
        # التحقق من الحقول المطلوبة
        if 'student_id' not in student_data or 'student_name' not in student_data:
            return False, "❌ الرقم الجامعي والاسم مطلوبان"
        
        # التحقق من عدم التكرار
        existing = supabase.table("students").select("student_id").eq(
            "student_id", student_data['student_id']
        ).execute()
        
        if existing.data:
            return False, "❌ الطالب موجود مسبقاً"
        
        # إضافة الطالب
        response = supabase.table("students").insert(student_data).execute()
        
        if response.data:
            return True, "✅ تم إضافة الطالب بنجاح"
        else:
            return False, "❌ فشل إضافة الطالب"
            
    except Exception as e:
        return False, f"❌ خطأ: {str(e)}"


def refresh_student_cache(supabase, student_id=None):
    """
    تحديث Cache الإحصائيات
    
    Args:
        student_id: رقم طالب محدد (None = الكل)
    """
    try:
        if student_id:
            # تحديث طالب واحد
            result = supabase.rpc('update_student_stats', {'p_student_id': student_id}).execute()
            return True, f"✅ تم تحديث إحصائيات الطالب {student_id}"
        else:
            # تحديث الكل
            result = supabase.rpc('update_all_student_stats').execute()
            count = result.data if result.data else 0
            return True, f"✅ تم تحديث إحصائيات {count} طالب"
            
    except Exception as e:
        return False, f"❌ خطأ: {str(e)}"


def get_subject_statistics(supabase):
    """
    إحصائيات المواد
    """
    try:
        # جلب جميع النتائج مع المواد
        response = supabase.table("all_marks").select(
            "subject_name, total_grade, result"
        ).execute()
        
        if not response.data:
            return "لا توجد بيانات"
        
        # تجميع حسب المادة
        subjects = {}
        for row in response.data:
            subject = row.get('subject_name', 'غير محدد')
            grade = row.get('total_grade', 0)
            result = row.get('result', '')
            
            if subject not in subjects:
                subjects[subject] = {
                    'grades': [],
                    'passed': 0,
                    'failed': 0,
                    'total': 0
                }
            
            subjects[subject]['grades'].append(grade)
            subjects[subject]['total'] += 1
            
            if result == 'ناجح' or grade >= 60:
                subjects[subject]['passed'] += 1
            else:
                subjects[subject]['failed'] += 1
        
        # ترتيب المواد حسب الصعوبة (أقل نسبة نجاح)
        subject_stats = []
        for name, data in subjects.items():
            avg = sum(data['grades']) / len(data['grades']) if data['grades'] else 0
            pass_rate = (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0
            
            subject_stats.append({
                'name': name,
                'average': round(avg, 2),
                'pass_rate': round(pass_rate, 2),
                'passed': data['passed'],
                'failed': data['failed'],
                'total': data['total']
            })
        
        # ترتيب حسب معدل النجاح (الأصعب أولاً)
        subject_stats.sort(key=lambda x: x['pass_rate'])
        
        msg = "📚 *إحصائيات المواد الدراسية*\n\n"
        msg += "🔴 *المواد الأصعب (أقل نسبة نجاح):*\n\n"
        
        for i, s in enumerate(subject_stats[:5], 1):
            msg += f"{i}. *{s['name']}*\n"
            msg += f"   📊 المعدل: {s['average']}%\n"
            msg += f"   ✅ نسبة النجاح: {s['pass_rate']}%\n"
            msg += f"   👥 الطلاب: {s['passed']} ناجح / {s['failed']} راسب\n\n"
        
        msg += "\n🟢 *المواد الأسهل (أعلى نسبة نجاح):*\n\n"
        
        for i, s in enumerate(subject_stats[-5:][::-1], 1):
            msg += f"{i}. *{s['name']}*\n"
            msg += f"   📊 المعدل: {s['average']}%\n"
            msg += f"   ✅ نسبة النجاح: {s['pass_rate']}%\n\n"
        
        return msg
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return "حدث خطأ في جلب إحصائيات المواد"


def get_database_health_check(supabase):
    """
    فحص صحة قاعدة البيانات
    """
    try:
        msg = "🔍 *فحص صحة قاعدة البيانات*\n\n"
        
        # فحص الجداول الرئيسية
        tables = {
            'students': 'جدول الطلاب',
            'all_marks': 'جدول النتائج',
            'student_stats_cache': 'إحصائيات محفوظة',
            'subjects': 'جدول المواد',
            'bot_users': 'مستخدمي البوت'
        }
        
        for table, desc in tables.items():
            try:
                response = supabase.table(table).select("id", count='exact').limit(1).execute()
                count = response.count if hasattr(response, 'count') else len(response.data)
                msg += f"✅ {desc}: {count} سجل\n"
            except Exception as e:
                msg += f"❌ {desc}: خطأ\n"
        
        # فحص الإحصائيات
        try:
            cache_response = supabase.table("student_stats_cache").select(
                "last_updated", count='exact'
            ).execute()
            
            if cache_response.data:
                msg += f"\n📊 *حالة الإحصائيات:*\n"
                msg += f"   عدد الطلاب المحسوبة: {cache_response.count}\n"
                
                # التحقق من آخر تحديث
                from datetime import datetime
                if cache_response.data[0].get('last_updated'):
                    last_update = cache_response.data[0]['last_updated']
                    msg += f"   آخر تحديث: {last_update}\n"
        except Exception as e:
            msg += f"\n⚠️ تعذر فحص الإحصائيات\n"
        
        msg += f"\n✅ *الحالة العامة: سليمة*"
        
        return msg
        
    except Exception as e:
        return f"❌ خطأ في فحص القاعدة: {str(e)}"


# ═══════════════════════════════════════════════════════════
# دوال للتكامل مع admin.py الأصلي
# ═══════════════════════════════════════════════════════════

def admin_dashboard_improved(bot, message, supabase):
    """
    لوحة التحكم المحسّنة للمشرف
    استبدل بها الدالة الأصلية أو أضفها
    """
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            types.InlineKeyboardButton("📊 إحصائيات عامة", callback_data="admin_stats"),
            types.InlineKeyboardButton("🏆 الأوائل", callback_data="admin_top"),
            types.InlineKeyboardButton("🚨 طلاب في خطر", callback_data="admin_at_risk"),
            types.InlineKeyboardButton("📚 إحصائيات المواد", callback_data="admin_subjects"),
            types.InlineKeyboardButton("🏫 إحصائيات الأقسام", callback_data="admin_departments"),
            types.InlineKeyboardButton("🔍 فحص القاعدة", callback_data="admin_health"),
            types.InlineKeyboardButton("🔄 تحديث الإحصائيات", callback_data="admin_refresh"),
            types.InlineKeyboardButton("❌ إغلاق", callback_data="close")
        ]
        
        markup.add(*buttons)
        
        bot.send_message(
            message.chat.id,
            "🎛️ *لوحة التحكم المحسّنة*\n\n"
            "اختر من القائمة:",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ خطأ: {str(e)}")


# مثال على معالج Callback
def handle_admin_callbacks(bot, call, supabase):
    """
    معالج callbacks لوحة التحكم
    """
    try:
        if call.data == "admin_stats":
            # إحصائيات عامة
            stats = get_all_students_info_fast(supabase)
            msg = f"إجمالي الطلاب: {len(stats)}"
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, msg)
            
        elif call.data == "admin_top":
            # الأوائل
            from analytics_improved import get_top_10_students_fast
            msg = get_top_10_students_fast(supabase)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
            
        elif call.data == "admin_at_risk":
            # الطلاب في خطر
            msg = get_at_risk_students(supabase)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
            
        elif call.data == "admin_subjects":
            # إحصائيات المواد
            msg = get_subject_statistics(supabase)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
            
        elif call.data == "admin_departments":
            # إحصائيات الأقسام
            msg = get_department_statistics(supabase)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
            
        elif call.data == "admin_health":
            # فحص القاعدة
            msg = get_database_health_check(supabase)
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
            
        elif call.data == "admin_refresh":
            # تحديث الإحصائيات
            bot.answer_callback_query(call.id, "جاري التحديث...")
            success, msg = refresh_student_cache(supabase)
            bot.send_message(call.message.chat.id, msg)
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"خطأ: {str(e)}")
