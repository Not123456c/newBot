#!/bin/bash

# ════════════════════════════════════════
# 🚀 سكريبت تشغيل Mini App بسهولة
# ════════════════════════════════════════

echo "════════════════════════════════════════"
echo "🎓 بوت النتائج الجامعية - Mini App"
echo "════════════════════════════════════════"
echo ""

# التحقق من المتطلبات
echo "🔍 التحقق من المتطلبات..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 غير مثبت"
    exit 1
fi

echo "✅ Python 3 موجود"

# الانتقال لمجلد Mini App
cd "$(dirname "$0")"

# التحقق من وجود .env
if [ ! -f ".env" ]; then
    echo "⚠️  ملف .env غير موجود!"
    echo "📝 جاري إنشاء ملف .env من القالب..."
    
    cat > .env << 'EOF'
# ========================================
# 🎓 إعدادات Mini App
# ========================================

# ☁️ بيانات Supabase
SUPABASE_URL=YOUR_SUPABASE_URL
SUPABASE_KEY=YOUR_SUPABASE_KEY

# 📱 توكن البوت
BOT_TOKEN=YOUR_BOT_TOKEN

# 🔧 إعدادات Flask
FLASK_ENV=development
FLASK_DEBUG=False

# 🌐 إعدادات الخادم
HOST=0.0.0.0
PORT=5000
MINI_APP_PORT=5000
EOF
    
    echo "✅ تم إنشاء .env"
    echo "⚠️  يرجى تعديل الملف بمعلوماتك الصحيحة"
    exit 1
fi

echo "✅ ملف .env موجود"

# التحقق من المكتبات
echo ""
echo "📦 التحقق من المكتبات..."

if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask غير مثبت"
    echo "📥 جاري التثبيت..."
    pip3 install -r requirements.txt
fi

echo "✅ جميع المكتبات موجودة"

# التحقق من قاعدة البيانات
echo ""
echo "🔗 التحقق من اتصال قاعدة البيانات..."
python3 << 'PYEOF'
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ بيانات Supabase غير موجودة في .env")
    exit(1)

if "YOUR_" in SUPABASE_URL:
    print("❌ يرجى تحديث .env ببياناتك الصحيحة")
    exit(1)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # محاولة query بسيط
    response = supabase.table("all_marks").select("id").limit(1).execute()
    print("✅ الاتصال بقاعدة البيانات نجح")
except Exception as e:
    print(f"⚠️  تحذير: {str(e)[:100]}")
    print("💡 تأكد من صحة بيانات Supabase")
PYEOF

# عرض المعلومات
echo ""
echo "════════════════════════════════════════"
echo "🚀 جاري تشغيل Mini App..."
echo "════════════════════════════════════════"
echo ""
echo "📱 سيعمل التطبيق على:"
echo "   http://localhost:5000"
echo ""
echo "🌐 للوصول من الخارج، استخدم:"
echo "   ngrok http 5000"
echo ""
echo "⏹️  للإيقاف: اضغط Ctrl+C"
echo ""
echo "════════════════════════════════════════"
echo ""

# تشغيل التطبيق
python3 app.py
