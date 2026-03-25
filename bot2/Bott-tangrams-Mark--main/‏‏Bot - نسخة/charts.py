"""
وحدة الرسوم البيانية
إنشاء رسوم بيانية للنتائج
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import io
import os

# استخدام خط يدعم العربية
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

def create_grades_chart(marks_data, student_id):
    """رسم بياني للعلامات (شريطي)"""
    try:
        subjects = [m.get('subject_name', 'unknown')[:15] for m in marks_data]
        grades = [m.get('total_grade') or 0 for m in marks_data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#16a34a' if g >= 60 else '#dc2626' for g in grades]
        
        bars = ax.bar(range(len(subjects)), grades, color=colors, alpha=0.7, edgecolor='black')
        
        # إضافة القيم على الأعمدة
        for i, (bar, grade) in enumerate(zip(bars, grades)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{grade}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        ax.set_ylabel('Grade %', fontsize=11, fontweight='bold')
        ax.set_xlabel('Subjects', fontsize=11, fontweight='bold')
        ax.set_title('Subject Grades', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.axhline(y=60, color='red', linestyle='--', linewidth=1.5, alpha=0.5, label='Pass Line')
        ax.set_xticks(range(len(subjects)))
        ax.set_xticklabels(subjects, rotation=45, ha='right', fontsize=9)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        output_path = os.path.join(os.getcwd(), f"chart_grades_{student_id}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    except Exception as e:
        print(f"Error creating grades chart: {e}")
        return None

def create_theoretical_practical_chart(marks_data, student_id):
    """رسم بياني مقارنة بين النظري والعملي"""
    try:
        subjects = [m.get('subject_name', 'unknown')[:15] for m in marks_data]
        theoretical = [m.get('theoretical_grade') or 0 for m in marks_data]
        practical = [m.get('practical_grade') or 0 for m in marks_data]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(subjects))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], theoretical, width, label='Theoretical', 
                       color='#3b82f6', alpha=0.7, edgecolor='black')
        bars2 = ax.bar([i + width/2 for i in x], practical, width, label='Practical', 
                       color='#f59e0b', alpha=0.7, edgecolor='black')
        
        ax.set_ylabel('Grade %', fontsize=11, fontweight='bold')
        ax.set_xlabel('Subjects', fontsize=11, fontweight='bold')
        ax.set_title('Theoretical vs Practical Grades', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.set_xticks(x)
        ax.set_xticklabels(subjects, rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        output_path = os.path.join(os.getcwd(), f"chart_theory_practical_{student_id}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    except Exception as e:
        print(f"Error creating theory/practical chart: {e}")
        return None

def create_performance_pie_chart(stats, student_id):
    """رسم بياني دائري لنسب النجاح والرسوب"""
    try:
        passed = stats.get('passed_subjects', 0)
        failed = stats.get('failed_subjects', 0)
        
        if passed + failed == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(8, 8))
        sizes = [passed, failed]
        labels = [f'Passed ({passed})', f'Failed ({failed})']
        colors = ['#16a34a', '#dc2626']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                          autopct='%1.1f%%', shadow=True, startangle=90,
                                          textprops={'fontsize': 12, 'fontweight': 'bold'})
        
        ax.set_title('Pass/Fail Rate', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        output_path = os.path.join(os.getcwd(), f"chart_pie_{student_id}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    except Exception as e:
        print(f"Error creating pie chart: {e}")
        return None

def create_statistics_summary_image(stats, student_id):
    """إنشاء صورة ملخص الإحصائيات"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        width, height = 600, 400
        img = Image.new('RGB', (width, height), color=(245, 247, 250))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            text_font = ImageFont.truetype("arial.ttf", 16)
            value_font = ImageFont.truetype("arialbd.ttf", 20)
        except:
            title_font = text_font = value_font = ImageFont.load_default()
        
        # Header
        draw.rectangle([0, 0, width, 80], fill=(37, 99, 235))
        draw.text((300, 40), "Statistics", fill=(255, 255, 255), font=title_font, anchor="mm")
        
        # Data
        y_pos = 110
        line_height = 50
        
        stats_data = [
            (f"Total Subjects: {stats.get('total_subjects', 0)}", (100, 116, 139)),
            (f"Success Rate: {stats.get('success_rate', 0)}%", (22, 163, 74)),
            (f"Average: {stats.get('average_grade', 0)}", (37, 99, 235)),
            (f"Highest: {stats.get('highest_grade', 0)}", (34, 197, 94)),
            (f"Lowest: {stats.get('lowest_grade', 0)}", (239, 68, 68))
        ]
        
        for text, color in stats_data:
            draw.text((50, y_pos), text, fill=color, font=text_font)
            y_pos += line_height
        
        output_path = os.path.join(os.getcwd(), f"stats_summary_{student_id}.png")
        img.save(output_path)
        
        return output_path
    except Exception as e:
        print(f"Error creating statistics image: {e}")
        return None


def create_grade_distribution_chart(distribution):
    """رسم بياني لتوزيع التقديرات (A+, A, B, C, D, F)"""
    try:
        grades = list(distribution.keys())
        counts = list(distribution.values())
        
        if not counts or sum(counts) == 0:
            return None
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # تحديد الألوان حسب التقدير
        colors = {
            'A+': '#059669',
            'A': '#10b981',
            'B': '#3b82f6',
            'C': '#f59e0b',
            'D': '#ef4444',
            'F': '#991b1b'
        }
        bar_colors = [colors.get(g, '#6b7280') for g in grades]
        
        bars = ax.bar(grades, counts, color=bar_colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        # إضافة القيم على الأعمدة
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            percentage = (count / sum(counts) * 100) if sum(counts) > 0 else 0
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(count)}\n({percentage:.1f}%)', 
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_ylabel('Number of Students', fontsize=12, fontweight='bold')
        ax.set_xlabel('Grade', fontsize=12, fontweight='bold')
        ax.set_title('Grade Distribution Across All Students', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        output_path = os.path.join(os.getcwd(), f"chart_grade_distribution.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    except Exception as e:
        print(f"Error creating grade distribution chart: {e}")
        return None


def create_subjects_performance_chart(subjects):
    """رسم بياني لأداء المواد"""
    try:
        if not subjects:
            return None
        
        # أخذ جميع المواد
        subject_names = [s['subject_name'] for s in subjects]
        averages = [s['average'] for s in subjects]
        pass_rates = [s['pass_rate'] for s in subjects]
        
        # ضبط حجم الرسم البياني ليتناسب مع عدد المواد
        width = max(14, len(subjects) * 0.8)
        fig, ax1 = plt.subplots(figsize=(width, 6))
        
        # رسم المتوسطات
        bars = ax1.bar(range(len(subject_names)), averages, color='#3b82f6', alpha=0.7, 
                       edgecolor='black', linewidth=1.5, label='Average Grade')
        ax1.set_ylabel('Average Grade', fontsize=12, fontweight='bold', color='#3b82f6')
        ax1.tick_params(axis='y', labelcolor='#3b82f6')
        ax1.set_ylim(0, 105)
        
        # إضافة القيم على الأعمدة
        for bar, avg in zip(bars, averages):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{avg:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # رسم نسب النجاح
        ax2 = ax1.twinx()
        line = ax2.plot(range(len(subject_names)), pass_rates, color='#10b981', 
                       marker='o', linewidth=2.5, markersize=8, label='Pass Rate (%)')
        ax2.set_ylabel('Pass Rate (%)', fontsize=12, fontweight='bold', color='#10b981')
        ax2.tick_params(axis='y', labelcolor='#10b981')
        ax2.set_ylim(0, 105)
        
        # تحديد التسميات والعنوان
        ax1.set_xticks(range(len(subject_names)))
        ax1.set_xticklabels(subject_names, rotation=45, ha='right', fontsize=10)
        ax1.set_title('Subject Performance Summary', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # الأساطير
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)
        
        plt.tight_layout()
        
        output_path = os.path.join(os.getcwd(), f"chart_subjects_performance.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    except Exception as e:
        print(f"Error creating subjects performance chart: {e}")
        return None
