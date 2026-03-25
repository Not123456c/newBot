from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import os

def prepare_text(text):
    if not text: return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def generate_result_image(student_id, student_name, father_name, marks, average):
    # إعدادات الأبعاد والألوان (تمت مضاعفة الدقة للوضوح)
    width, height = 2000, 1400
    if len(marks) > 3: height += (len(marks) - 3) * 160
    
    bg_color = (245, 247, 250)
    header_bg = (255, 255, 255)
    table_header_bg = (235, 238, 242)
    row_even_bg = (255, 255, 255)
    row_odd_bg = (250, 252, 254)
    text_color = (30, 41, 59)
    success_color = (22, 163, 74)
    fail_color = (220, 38, 38)
    blue_accent = (37, 99, 235)
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # تحميل الخطوط - محاولة البحث عن خطوط تدعم العربية
    font_paths = [
        "arial.ttf",
        "arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf"
    ]
    
    selected_font = None
    selected_bold_font = None

    for path in font_paths:
        if os.path.exists(path):
            if "bd" in path or "Bold" in path:
                if not selected_bold_font: selected_bold_font = path
            else:
                if not selected_font: selected_font = path

    # إذا لم يتم العثور على خط، استخدم الافتراضي
    if not selected_font: selected_font = font_paths[0] # Try default even if not exists, PIL might handle generic names
    if not selected_bold_font: selected_bold_font = selected_font

    try:
        f_header = ImageFont.truetype(selected_bold_font, 90)
        f_sub = ImageFont.truetype(selected_font, 50)
        f_table_h = ImageFont.truetype(selected_bold_font, 44)
        f_table_r = ImageFont.truetype(selected_font, 44)
        f_avg = ImageFont.truetype(selected_bold_font, 60)
    except:
        f_header = f_sub = f_table_h = f_table_r = f_avg = ImageFont.load_default()

    # رسم الهيدر
    draw.rectangle([0, 0, width, 300], fill=header_bg)
    name_text = f"الاسم: {student_name} {father_name}"
    id_text = f"الرقم الامتحاني: {student_id}"
    
    draw.text((1900, 80), prepare_text(name_text), fill=text_color, font=f_header, anchor="ra")
    draw.text((1900, 200), prepare_text(id_text), fill=(100, 116, 139), font=f_sub, anchor="ra")

    # رسم الجدول
    start_y = 360
    col_widths = [400, 300, 300, 300, 300, 400]
    headers = ["الترتيب", "النتيجة", "المجموع", "نظري", "أعمال", "المادة"]
    
    # رأس الجدول
    draw.rectangle([100, start_y, 1900, start_y + 120], fill=table_header_bg)
    curr_x = 1900
    for i, h in enumerate(reversed(headers)):
        draw.text((curr_x - 200, start_y + 30), prepare_text(h), fill=(71, 85, 105), font=f_table_h, anchor="ma")
        curr_x -= 300 if i < 5 else 400

    # الصفوف
    curr_y = start_y + 120
    for i, m in enumerate(marks):
        bg = row_even_bg if i % 2 == 0 else row_odd_bg
        draw.rectangle([100, curr_y, 1900, curr_y + 140], fill=bg)
        
        # البيانات
        row_data = [
            str(m.get('rank') or '—'),
            m.get('result') or '—',
            str(m.get('total_grade') or 0),
            str(m.get('theoretical_grade') or 0),
            str(m.get('practical_grade') or 0),
            m.get('subject_name') or '—'
        ]
        
        curr_x = 1900
        for j, val in enumerate(reversed(row_data)):
            color = text_color
            if j == 4: # عمود النتيجة
                color = success_color if val == "ناجح" else fail_color
            
            draw.text((curr_x - 200, curr_y + 40), prepare_text(val), fill=color, font=f_table_r, anchor="ma")
            curr_x -= 300 if j < 5 else 400
        
        curr_y += 140

    # المعدل العام
    avg_y = curr_y + 80
    draw.rectangle([100, avg_y, 1900, avg_y + 160], fill=(219, 234, 254), outline=blue_accent, width=4)
    avg_text = f"المعدل العام: {average}"
    draw.text((1000, avg_y + 40), prepare_text(avg_text), fill=blue_accent, font=f_avg, anchor="ma")

    # تذييل
    footer_text = "@Mark_damacuse_bot"
    draw.text((1900, height - 80), prepare_text(footer_text), fill=(148, 163, 184), font=f_sub, anchor="ra")
    
    output_path = os.path.join(os.getcwd(), f"result_{student_id}.png")
    img.save(output_path)
    return output_path

import time

def generate_top_students_image(top_data, title="أوائل الدفعة"):
    width, height = 1200, max(600, 300 + len(top_data) * 100)
    bg_color = (245, 247, 250)
    header_bg = (52, 152, 219)
    table_header_bg = (235, 238, 242)
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # تحميل الخطوط مع دعم Linux
    font_paths = [
        "arial.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf"
    ]
    
    font_large = font_medium = font_small = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                font_large = ImageFont.truetype(path, 60)
                font_medium = ImageFont.truetype(path, 40)
                font_small = ImageFont.truetype(path, 30)
                break
            except:
                continue
    
    if font_large is None:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.rectangle([(0, 0), (width, 150)], fill=header_bg)
    title_text = prepare_text(title)
    draw.text((width//2 - 100, 75), title_text, font=font_large, fill=(255,255,255))

    cols = [
        {"name": "الترتيب", "x": 1050},
        {"name": "الرقم الامتحاني", "x": 750},
        {"name": "الاسم", "x": 300},
        {"name": "المعدل", "x": 50},
    ]

    y_offset = 200
    draw.rectangle([(0, y_offset), (width, y_offset+60)], fill=table_header_bg)
    for col in cols:
        draw.text((col["x"], y_offset + 10), prepare_text(col["name"]), font=font_medium, fill=(50,50,50))
        
    y_offset += 100
    for idx, student in enumerate(top_data):
        row_bg = (255, 255, 255) if idx % 2 == 0 else (250, 252, 254)
        draw.rectangle([(0, y_offset), (width, y_offset+80)], fill=row_bg)
        
        draw.text((1050, y_offset + 20), prepare_text(f"#{idx+1}"), font=font_medium, fill=(231, 76, 60) if idx<3 else (50,50,50))
        
        student_id = student.get("الرقم الامتحاني", student.get("الرقم الجامعي", ""))
        student_name = student.get("الاسم", student.get("الاسم والنسبة", ""))
        avg = student.get("المعدل", student.get("المتوسط", ""))
        
        draw.text((750, y_offset + 25), prepare_text(str(student_id)), font=font_small, fill=(50,50,50))
        draw.text((300, y_offset + 25), prepare_text(str(student_name)), font=font_small, fill=(50,50,50))
        avg_val = f"{avg:.2f}" if isinstance(avg, float) else str(avg)
        draw.text((50, y_offset + 20), prepare_text(avg_val), font=font_medium, fill=(46, 204, 113))
        
        y_offset += 100

    output_path = f"top_students_{int(time.time())}.png"
    img.save(output_path)
    return output_path
