# استخدام نسخة بايثون خفيفة وسريعة
FROM python:3.10-slim

# ضبط مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف متطلبات المكتبات أولاً
COPY requirements.txt .

# تثبيت المكتبات المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# نسخ جميع ملفات وعناصر البوت إلى داخل الحاوية
COPY . .

# الأمر الذي سيقوم الخادم بتنفيذه لتشغيل البوت
CMD ["python", "final_bot_with_image.py"]