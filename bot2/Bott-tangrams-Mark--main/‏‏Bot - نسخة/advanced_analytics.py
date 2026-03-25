# -*- coding: utf-8 -*-
"""
نظام التحليلات المتقدم
Advanced Analytics System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import json


class AdvancedAnalytics:
    """
    نظام التحليلات المتقدم للبوت
    """
    
    def __init__(self, supabase):
        self.supabase = supabase
    
    # ══════════════════════════════════════
    # تحليلات الاستخدام
    # ══════════════════════════════════════
    
    def log_activity(self, telegram_id: int, action: str, details: Dict = None):
        """تسجيل نشاط"""
        try:
            self.supabase.table("activity_log").insert({
                'telegram_id': telegram_id,
                'action': action,
                'details': json.dumps(details) if details else None,
                'created_at': datetime.now().isoformat(),
                'hour_of_day': datetime.now().hour,
                'day_of_week': datetime.now().weekday()
            }).execute()
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_usage_by_hour(self, days: int = 7) -> Dict:
        """أكثر الأوقات استخداماً"""
        try:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table("activity_log").select(
                "hour_of_day"
            ).gte("created_at", since).execute()
            
            hours = defaultdict(int)
            for row in response.data:
                hours[row['hour_of_day']] += 1
            
            # تحويل لقائمة مرتبة
            result = []
            for hour in range(24):
                count = hours.get(hour, 0)
                result.append({
                    'hour': hour,
                    'hour_label': f"{hour:02d}:00",
                    'count': count
                })
            
            # أكثر ساعة نشاطاً
            peak_hour = max(result, key=lambda x: x['count']) if result else None
            
            return {
                'hourly_data': result,
                'peak_hour': peak_hour,
                'total_activities': sum(r['count'] for r in result)
            }
            
        except Exception as e:
            print(f"Error getting usage by hour: {e}")
            return {}
    
    def get_usage_by_day(self, days: int = 30) -> Dict:
        """الاستخدام حسب اليوم"""
        try:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table("activity_log").select(
                "day_of_week"
            ).gte("created_at", since).execute()
            
            days_names = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
            
            day_counts = defaultdict(int)
            for row in response.data:
                day_counts[row['day_of_week']] += 1
            
            result = []
            for i, name in enumerate(days_names):
                result.append({
                    'day': i,
                    'day_name': name,
                    'count': day_counts.get(i, 0)
                })
            
            return {
                'daily_data': result,
                'busiest_day': max(result, key=lambda x: x['count']) if result else None
            }
            
        except Exception as e:
            return {}
    
    def get_most_searched_subjects(self, limit: int = 10) -> List[Dict]:
        """أكثر المواد بحثاً"""
        try:
            response = self.supabase.table("activity_log").select(
                "details"
            ).eq("action", "search_result").execute()
            
            subjects = defaultdict(int)
            
            for row in response.data:
                if row.get('details'):
                    try:
                        details = json.loads(row['details'])
                        for subject in details.get('subjects', []):
                            subjects[subject] += 1
                    except:
                        pass
            
            # ترتيب حسب الأكثر بحثاً
            sorted_subjects = sorted(
                subjects.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:limit]
            
            return [{'subject': s[0], 'count': s[1]} for s in sorted_subjects]
            
        except Exception as e:
            return []
    
    def get_feature_usage(self) -> Dict:
        """استخدام الميزات"""
        try:
            response = self.supabase.table("activity_log").select(
                "action"
            ).execute()
            
            features = defaultdict(int)
            for row in response.data:
                features[row['action']] += 1
            
            # ترتيب
            sorted_features = sorted(
                features.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            feature_names = {
                'search_result': '🔍 بحث عن نتيجة',
                'view_top': '🏆 عرض الأوائل',
                'view_chart': '📊 عرض رسم بياني',
                'ai_analyze': '🤖 تحليل AI',
                'ai_plan': '📚 خطة دراسة',
                'view_exams': '📅 جدول امتحانات',
                'share_result': '📤 مشاركة نتيجة',
                'download_pdf': '📥 تحميل PDF',
                'mini_app': '📱 Mini App'
            }
            
            return {
                'features': [
                    {
                        'action': f[0],
                        'name': feature_names.get(f[0], f[0]),
                        'count': f[1]
                    }
                    for f in sorted_features
                ],
                'total_actions': sum(features.values())
            }
            
        except Exception as e:
            return {}
    
    # ══════════════════════════════════════
    # تحليلات أكاديمية
    # ══════════════════════════════════════
    
    def get_overall_improvement(self) -> Dict:
        """معدل التحسن العام"""
        try:
            # هذا يتطلب بيانات تاريخية للفصول
            response = self.supabase.table("semester_history").select("*").execute()
            
            if not response.data:
                return {'message': 'لا توجد بيانات تاريخية'}
            
            students_improvement = []
            
            # تجميع حسب الطالب
            students = defaultdict(list)
            for row in response.data:
                students[row['student_id']].append({
                    'semester': row['semester'],
                    'average': row['average']
                })
            
            for student_id, semesters in students.items():
                if len(semesters) >= 2:
                    semesters.sort(key=lambda x: x['semester'])
                    improvement = semesters[-1]['average'] - semesters[-2]['average']
                    students_improvement.append(improvement)
            
            if students_improvement:
                avg_improvement = sum(students_improvement) / len(students_improvement)
                improved_count = len([i for i in students_improvement if i > 0])
                declined_count = len([i for i in students_improvement if i < 0])
                
                return {
                    'average_improvement': round(avg_improvement, 2),
                    'students_improved': improved_count,
                    'students_declined': declined_count,
                    'students_stable': len(students_improvement) - improved_count - declined_count,
                    'improvement_rate': round(improved_count / len(students_improvement) * 100, 1)
                }
            
            return {}
            
        except Exception as e:
            return {}
    
    def get_grade_distribution(self) -> Dict:
        """توزيع الدرجات"""
        try:
            response = self.supabase.table("all_marks").select("total_grade").execute()
            
            grades = [r['total_grade'] for r in response.data if r['total_grade']]
            
            distribution = {
                'A+ (95-100)': len([g for g in grades if g >= 95]),
                'A (90-94)': len([g for g in grades if 90 <= g < 95]),
                'B+ (85-89)': len([g for g in grades if 85 <= g < 90]),
                'B (80-84)': len([g for g in grades if 80 <= g < 85]),
                'C+ (75-79)': len([g for g in grades if 75 <= g < 80]),
                'C (70-74)': len([g for g in grades if 70 <= g < 75]),
                'D+ (65-69)': len([g for g in grades if 65 <= g < 70]),
                'D (60-64)': len([g for g in grades if 60 <= g < 65]),
                'F (<60)': len([g for g in grades if g < 60])
            }
            
            total = len(grades)
            
            return {
                'distribution': distribution,
                'total_grades': total,
                'average': round(sum(grades) / total, 2) if total > 0 else 0,
                'pass_rate': round(len([g for g in grades if g >= 60]) / total * 100, 1) if total > 0 else 0
            }
            
        except Exception as e:
            return {}
    
    def predict_at_risk_students(self) -> List[Dict]:
        """توقع الطلاب المعرضين للرسوب"""
        try:
            # جلب جميع النتائج
            response = self.supabase.table("all_marks").select(
                "student_id, student_name, total_grade, subject_name"
            ).execute()
            
            # تجميع حسب الطالب
            students = defaultdict(lambda: {'grades': [], 'name': '', 'subjects': []})
            
            for row in response.data:
                sid = row['student_id']
                students[sid]['grades'].append(row['total_grade'] or 0)
                students[sid]['name'] = row['student_name']
                if row['total_grade'] and row['total_grade'] < 60:
                    students[sid]['subjects'].append(row['subject_name'])
            
            at_risk = []
            
            for sid, data in students.items():
                grades = data['grades']
                if not grades:
                    continue
                
                average = sum(grades) / len(grades)
                failed_count = len([g for g in grades if g < 60])
                
                # معايير الخطر
                risk_score = 0
                risk_factors = []
                
                if average < 50:
                    risk_score += 40
                    risk_factors.append("معدل منخفض جداً")
                elif average < 60:
                    risk_score += 25
                    risk_factors.append("معدل أقل من الحد")
                
                if failed_count >= 3:
                    risk_score += 30
                    risk_factors.append(f"{failed_count} مواد راسب")
                elif failed_count >= 1:
                    risk_score += 15
                    risk_factors.append(f"{failed_count} مادة راسب")
                
                # درجات قريبة من الرسوب
                borderline = len([g for g in grades if 60 <= g < 65])
                if borderline >= 2:
                    risk_score += 10
                    risk_factors.append(f"{borderline} مواد على الحافة")
                
                if risk_score >= 30:
                    at_risk.append({
                        'student_id': sid,
                        'student_name': data['name'],
                        'average': round(average, 1),
                        'failed_subjects': failed_count,
                        'risk_score': risk_score,
                        'risk_level': 'عالي' if risk_score >= 50 else 'متوسط',
                        'risk_factors': risk_factors,
                        'failing_subjects': data['subjects'][:3]
                    })
            
            # ترتيب حسب الخطر
            at_risk.sort(key=lambda x: x['risk_score'], reverse=True)
            
            return at_risk
            
        except Exception as e:
            print(f"Error predicting at-risk: {e}")
            return []
    
    def get_subject_statistics(self) -> List[Dict]:
        """إحصائيات المواد"""
        try:
            response = self.supabase.table("all_marks").select(
                "subject_name, total_grade"
            ).execute()
            
            subjects = defaultdict(list)
            for row in response.data:
                if row['total_grade']:
                    subjects[row['subject_name']].append(row['total_grade'])
            
            stats = []
            for name, grades in subjects.items():
                if not grades:
                    continue
                
                avg = sum(grades) / len(grades)
                passed = len([g for g in grades if g >= 60])
                
                stats.append({
                    'subject_name': name,
                    'students_count': len(grades),
                    'average': round(avg, 1),
                    'highest': max(grades),
                    'lowest': min(grades),
                    'pass_rate': round(passed / len(grades) * 100, 1),
                    'difficulty': 'صعبة' if avg < 65 else 'متوسطة' if avg < 75 else 'سهلة'
                })
            
            # ترتيب حسب المعدل
            stats.sort(key=lambda x: x['average'])
            
            return stats
            
        except Exception as e:
            return []
    
    # ══════════════════════════════════════
    # تحليلات المستخدمين
    # ══════════════════════════════════════
    
    def get_user_growth(self, days: int = 30) -> Dict:
        """نمو المستخدمين"""
        try:
            response = self.supabase.table("bot_users").select(
                "created_at"
            ).execute()
            
            daily_signups = defaultdict(int)
            
            for row in response.data:
                if row.get('created_at'):
                    date = row['created_at'][:10]
                    daily_signups[date] += 1
            
            # آخر n يوم
            dates = []
            today = datetime.now().date()
            
            for i in range(days):
                date = (today - timedelta(days=i)).isoformat()
                dates.append({
                    'date': date,
                    'signups': daily_signups.get(date, 0)
                })
            
            dates.reverse()
            
            total_users = len(response.data)
            new_users_week = sum(d['signups'] for d in dates[-7:])
            
            return {
                'daily_data': dates,
                'total_users': total_users,
                'new_users_week': new_users_week,
                'new_users_month': sum(d['signups'] for d in dates)
            }
            
        except Exception as e:
            return {}
    
    def get_active_users(self, days: int = 7) -> Dict:
        """المستخدمين النشطين"""
        try:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table("activity_log").select(
                "telegram_id"
            ).gte("created_at", since).execute()
            
            unique_users = set(row['telegram_id'] for row in response.data)
            
            # إجمالي المستخدمين
            total_response = self.supabase.table("bot_users").select("id").execute()
            total_users = len(total_response.data)
            
            return {
                'active_users': len(unique_users),
                'total_users': total_users,
                'activity_rate': round(len(unique_users) / total_users * 100, 1) if total_users > 0 else 0
            }
            
        except Exception as e:
            return {}
    
    # ══════════════════════════════════════
    # تقارير شاملة
    # ══════════════════════════════════════
    
    def generate_daily_report(self) -> str:
        """تقرير يومي"""
        usage = self.get_usage_by_hour(1)
        active = self.get_active_users(1)
        features = self.get_feature_usage()
        
        report = (
            "📊 *التقرير اليومي*\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            "👥 *المستخدمون:*\n"
            f"• نشطون اليوم: {active.get('active_users', 0)}\n"
            f"• إجمالي: {active.get('total_users', 0)}\n\n"
            
            "📈 *النشاط:*\n"
            f"• إجمالي الإجراءات: {usage.get('total_activities', 0)}\n"
        )
        
        if usage.get('peak_hour'):
            report += f"• ساعة الذروة: {usage['peak_hour']['hour_label']}\n"
        
        report += "\n🔥 *أكثر الميزات استخداماً:*\n"
        for f in features.get('features', [])[:5]:
            report += f"• {f['name']}: {f['count']}\n"
        
        return report
    
    def generate_weekly_report(self) -> str:
        """تقرير أسبوعي"""
        usage_day = self.get_usage_by_day(7)
        growth = self.get_user_growth(7)
        at_risk = self.predict_at_risk_students()
        subjects = self.get_subject_statistics()
        
        report = (
            "📊 *التقرير الأسبوعي*\n"
            f"📅 الأسبوع المنتهي في {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            "👥 *نمو المستخدمين:*\n"
            f"• مستخدمون جدد: {growth.get('new_users_week', 0)}\n"
            f"• إجمالي: {growth.get('total_users', 0)}\n\n"
        )
        
        if usage_day.get('busiest_day'):
            report += f"📅 أكثر يوم نشاطاً: {usage_day['busiest_day']['day_name']}\n\n"
        
        report += f"⚠️ *طلاب معرضون للخطر:* {len(at_risk)}\n"
        
        if at_risk[:3]:
            for student in at_risk[:3]:
                report += f"• {student['student_name']} ({student['risk_level']})\n"
        
        report += "\n📚 *أصعب المواد:*\n"
        for subj in subjects[:3]:
            report += f"• {subj['subject_name']}: {subj['average']}%\n"
        
        return report
    
    def format_analytics_message(self) -> str:
        """تنسيق رسالة التحليلات"""
        usage = self.get_usage_by_hour()
        active = self.get_active_users()
        features = self.get_feature_usage()
        distribution = self.get_grade_distribution()
        
        msg = "📊 *لوحة التحليلات*\n\n"
        
        # استخدام
        msg += "👥 *المستخدمون:*\n"
        msg += f"  • نشطون (7 أيام): {active.get('active_users', 0)}\n"
        msg += f"  • معدل النشاط: {active.get('activity_rate', 0)}%\n\n"
        
        # ساعات الذروة
        if usage.get('peak_hour'):
            msg += f"⏰ *ساعة الذروة:* {usage['peak_hour']['hour_label']}\n\n"
        
        # الميزات
        msg += "🔥 *أكثر الميزات استخداماً:*\n"
        for f in features.get('features', [])[:5]:
            msg += f"  • {f['name']}: {f['count']}\n"
        
        # توزيع الدرجات
        if distribution:
            msg += f"\n📈 *توزيع الدرجات:*\n"
            msg += f"  • المعدل العام: {distribution.get('average', 0)}%\n"
            msg += f"  • نسبة النجاح: {distribution.get('pass_rate', 0)}%\n"
        
        return msg


def setup_analytics_commands(bot, analytics_system, admin_ids):
    """إعداد أوامر التحليلات"""
    
    @bot.message_handler(commands=['analytics', 'تحليلات'])
    def show_analytics(message):
        """عرض التحليلات"""
        if message.chat.id not in admin_ids:
            bot.send_message(message.chat.id, "❌ هذا الأمر للمشرفين فقط")
            return
        
        msg = analytics_system.format_analytics_message()
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    
    @bot.message_handler(commands=['daily_report', 'تقرير_يومي'])
    def show_daily_report(message):
        """التقرير اليومي"""
        if message.chat.id not in admin_ids:
            return
        
        report = analytics_system.generate_daily_report()
        bot.send_message(message.chat.id, report, parse_mode="Markdown")
    
    @bot.message_handler(commands=['weekly_report', 'تقرير_اسبوعي'])
    def show_weekly_report(message):
        """التقرير الأسبوعي"""
        if message.chat.id not in admin_ids:
            return
        
        report = analytics_system.generate_weekly_report()
        bot.send_message(message.chat.id, report, parse_mode="Markdown")
    
    @bot.message_handler(commands=['at_risk', 'المعرضين_للخطر'])
    def show_at_risk(message):
        """الطلاب المعرضين للخطر"""
        if message.chat.id not in admin_ids:
            return
        
        at_risk = analytics_system.predict_at_risk_students()
        
        if not at_risk:
            bot.send_message(message.chat.id, "✅ لا يوجد طلاب معرضين للخطر")
            return
        
        msg = f"⚠️ *الطلاب المعرضين للخطر ({len(at_risk)})*\n\n"
        
        for i, student in enumerate(at_risk[:15], 1):
            risk_emoji = "🔴" if student['risk_level'] == 'عالي' else "🟡"
            msg += f"{risk_emoji} *{i}. {student['student_name']}*\n"
            msg += f"   معدل: {student['average']}% | راسب: {student['failed_subjects']}\n"
            if student['failing_subjects']:
                msg += f"   المواد: {', '.join(student['failing_subjects'])}\n"
            msg += "\n"
        
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
