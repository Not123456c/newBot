from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
import time
import os

def prepare_text(text):
    if not text: return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def generate_top_students_image(top_data, title="أوائل الدفعة"):
    width, height = 1200, max(600, 300 + len(top_data) * 100)
    bg_color = (245, 247, 250)
    header_bg = (52, 152, 219)
    table_header_bg = (235, 238, 242)
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_medium = ImageFont.truetype("arial.ttf", 40)
        font_small = ImageFont.truetype("arial.ttf", 30)
    except:
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
