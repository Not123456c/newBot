"""
وحدة التسجيل والتصحيح
تسجيل جميع عمليات البوت للتصحيح الشامل
"""

import logging
import os
from datetime import datetime

# إعداد التسجيل
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# اسم ملف السجل
log_file = os.path.join(LOG_DIR, f"bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# إعداد المسجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_user_search(user_id, search_type, search_query):
    """تسجيل عملية البحث"""
    logger.info(f"User {user_id} searched by {search_type}: {search_query}")

def log_student_result_sent(user_id, student_id, student_name):
    """تسجيل إرسال النتيجة"""
    logger.info(f"User {user_id} received result for student {student_id} ({student_name})")

def log_error(user_id, error_type, error_message):
    """تسجيل الأخطاء"""
    logger.error(f"User {user_id} - {error_type}: {error_message}")

def log_chart_generated(chart_type, student_id, success=True):
    """تسجيل توليد الرسوم البيانية"""
    status = "✓" if success else "✗"
    logger.info(f"{status} Chart {chart_type} generated for student {student_id}")

def log_pdf_generated(student_id, success=True):
    """تسجيل توليد PDF"""
    status = "✓" if success else "✗"
    logger.info(f"{status} PDF generated for student {student_id}")

def log_db_query(query_type, status, details=""):
    """تسجيل استعلامات قاعدة البيانات"""
    logger.info(f"DB Query - {query_type}: {status} {details}")

def get_log_file():
    """الحصول على ملف السجل الحالي"""
    return log_file
