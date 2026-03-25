"""
وحدة تصدير PDF
تصدير النتائج والتقارير كملف PDF
"""

from datetime import datetime
import os

def generate_pdf_report(student_id, student_name, father_name, stats, weak_subjects, 
                       strong_subjects, recommendations, marks_data):
    """توليد تقرير PDF شامل"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import arabic_reshaper
        from bidi.algorithm import get_display

        def format_arabic(text):
            """تنسيق النص العربي بشكل صحيح"""
            try:
                reshaped_text = arabic_reshaper.reshape(str(text))
                return get_display(reshaped_text)
            except:
                return str(text)

        # تسجيل خط عربي - دعم Windows و Linux
        font_paths = [
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\tahoma.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]
        
        font_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_path = path
                break

        if font_path and os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
            main_font = 'ArabicFont'
        else:
            main_font = 'Helvetica'

        # إعداد الملف
        output_path = os.path.join(os.getcwd(), f"report_{student_id}.pdf")
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # إنشاء أنماط مخصصة
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=main_font
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_RIGHT,
            fontName=main_font
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_RIGHT,
            fontName=main_font
        )
        
        # العنوان الرئيسي
        story.append(Paragraph(format_arabic("تقرير الأداء الأكاديمي الشامل"), title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # معلومات الطالب
        story.append(Paragraph(format_arabic("معلومات الطالب"), heading_style))
        student_data = [
            [format_arabic(student_id), format_arabic("الرقم الامتحاني:")],
            [format_arabic(f'{student_name} {father_name}'), format_arabic("الاسم:")],
            [format_arabic(datetime.now().strftime('%Y-%m-%d %H:%M')), format_arabic("تاريخ التقرير:")]
        ]
        t = Table(student_data, colWidths=[4*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (-1, 0), (-1, -1), colors.HexColor('#e0f2fe')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), main_font),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # الإحصائيات
        story.append(Paragraph(format_arabic("ملخص الإحصائيات"), heading_style))
        stats_data = [
            [format_arabic(str(stats.get('total_subjects', 0))), format_arabic("إجمالي المواد")],
            [format_arabic(f"{stats.get('success_rate', 0)}%"), format_arabic("نسبة النجاح")],
            [format_arabic(f"{stats.get('average_grade', 0)}%"), format_arabic("المعدل العام")],
            [format_arabic(f"{stats.get('highest_grade', 0)}%"), format_arabic("أعلى درجة")],
            [format_arabic(f"{stats.get('lowest_grade', 0)}%"), format_arabic("أقل درجة")]
        ]
        t = Table(stats_data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), main_font),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # تفاصيل المواد
        story.append(Paragraph(format_arabic("تفاصيل العلامات"), heading_style))
        subjects_data = [[
            format_arabic('النتيجة'), 
            format_arabic('العملي'), 
            format_arabic('النظري'), 
            format_arabic('الدرجة'), 
            format_arabic('المادة')
        ]]
        for m in marks_data:
            subjects_data.append([
                format_arabic(m.get('result', '—')),
                format_arabic(str(m.get('practical_grade', 0))),
                format_arabic(str(m.get('theoretical_grade', 0))),
                format_arabic(str(m.get('total_grade', 0))),
                format_arabic(m.get('subject_name', '—'))
            ])
        
        t = Table(subjects_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 2.8*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), main_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')])
        ]))
        story.append(t)
        
        if weak_subjects:
            story.append(PageBreak())
            story.append(Paragraph(format_arabic("المواد الضعيفة (تتطلب انتباهاً)"), heading_style))
            weak_data = [[format_arabic('الحالة'), format_arabic('الدرجة'), format_arabic('المادة')]]
            for w in weak_subjects[:5]:
                weak_data.append([
                    format_arabic(w.get('result', '—')), 
                    format_arabic(str(w.get('grade', 0))), 
                    format_arabic(w.get('name', '—'))
                ])
            
            t = Table(weak_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), main_font),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(t)
        
        if strong_subjects:
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(format_arabic("نقاط القوة (أفضل المواد)"), heading_style))
            strong_data = [[format_arabic('الدرجة'), format_arabic('المادة')]]
            for s in strong_subjects[:5]:
                strong_data.append([
                    format_arabic(str(s.get('grade', 0))),
                    format_arabic(s.get('name', '—'))
                ])
            
            t = Table(strong_data, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16a34a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), main_font),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            story.append(t)
        
        # التوصيات
        if recommendations.get('action_needed'):
            story.append(PageBreak())
            story.append(Paragraph(format_arabic("توصيات هامة جداً"), heading_style))
            
            for rec in recommendations.get('action_needed', []):
                p = Paragraph(format_arabic(f"• {rec}"), normal_style)
                story.append(p)
                story.append(Spacer(1, 0.1*inch))
        
        # بناء المستند
        doc.build(story)
        
        return output_path
    
    except Exception as e:
        print(f"Error in generated PDF: {e}")
        return None

def create_simple_text_report(student_id, student_name, stats, weak_subjects, strong_subjects):
    """إنشاء تقرير نصي بسيط (backup إذا لم تكن reportlab متاحة)"""
    try:
        output_path = os.path.join(os.getcwd(), f"report_{student_id}.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("تقـرير الأداء الأكاديمي الشامـل\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"الرقم الامتحاني: {student_id}\n")
            f.write(f"الاسم: {student_name}\n")
            f.write(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            f.write("-" * 60 + "\n")
            f.write("ملخص الإحصائيات\n")
            f.write("-" * 60 + "\n")
            f.write(f"إجمالي المواد: {stats.get('total_subjects', 0)}\n")
            f.write(f"نسبة النجاح: {stats.get('success_rate', 0)}%\n")
            f.write(f"المعدل العام: {stats.get('average_grade', 0)}%\n")
            f.write(f"أعلى درجة: {stats.get('highest_grade', 0)}%\n")
            f.write(f"أقل درجة: {stats.get('lowest_grade', 0)}%\n\n")
            
            if weak_subjects:
                f.write("-" * 60 + "\n")
                f.write("المواد الضعيفة\n")
                f.write("-" * 60 + "\n")
                for w in weak_subjects:
                    f.write(f"• {w['name']}: {w['grade']}% ({w['result']})\n")
                f.write("\n")
            
            if strong_subjects:
                f.write("-" * 60 + "\n")
                f.write("المواد الممتازة\n")
                f.write("-" * 60 + "\n")
                for s in strong_subjects:
                    f.write(f"• {s['name']}: {s['grade']}%\n")
                f.write("\n")
        
        return output_path
    except Exception as e:
        print(f"Error creating text report: {e}")
        return None
