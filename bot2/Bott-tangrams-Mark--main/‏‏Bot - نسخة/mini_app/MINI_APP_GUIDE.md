# 📱 دليل إعداد Telegram Mini App

## 🎯 نظرة عامة

**Mini App** هو تطبيق ويب يعمل داخل Telegram مباشرة، يوفر واجهة جميلة وتفاعلية لعرض النتائج.

---

## 📂 هيكل الملفات

```
mini_app/
├── app.py                 # الخادم الرئيسي (Flask)
├── requirements.txt       # المتطلبات
├── SQL_MINI_APP.sql      # أوامر قاعدة البيانات
├── templates/
│   └── index.html        # الواجهة الرئيسية
└── static/
    ├── css/
    │   └── style.css     # الأنماط
    └── js/
        └── app.js        # JavaScript
```

---

## 🚀 خطوات التشغيل

### 1️⃣ إعداد قاعدة البيانات

```bash
# انسخ محتوى SQL_MINI_APP.sql
# الصقه في Supabase SQL Editor
# اضغط Run
```

### 2️⃣ إضافة المتغيرات للـ .env

```env
# أضف هذه المتغيرات لملف .env الموجود
MINI_APP_PORT=5000
MINI_APP_URL=https://your-domain.com  # أو IP الراسبيري
```

### 3️⃣ تثبيت المتطلبات

```bash
cd mini_app
pip install -r requirements.txt
```

### 4️⃣ تشغيل Mini App

```bash
# تشغيل مباشر
python app.py

# أو مع gunicorn (للإنتاج)
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

---

## 🔧 إعداد البوت للعمل مع Mini App

### إضافة زر Mini App للبوت

أضف هذا الكود في `final_bot_with_image.py`:

```python
# في معالج /start أو أي مكان مناسب
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

MINI_APP_URL = os.environ.get("MINI_APP_URL", "http://localhost:5000")

@bot.message_handler(commands=['app', 'webapp'])
def open_mini_app(message):
    """فتح Mini App"""
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="📱 فتح التطبيق",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )
    )
    bot.send_message(
        message.chat.id,
        "🎓 *افتح تطبيق النتائج*\n\n"
        "اضغط الزر أدناه لفتح التطبيق المصغر:",
        parse_mode="Markdown",
        reply_markup=markup
    )
```

### إضافة زر Menu Button (اختياري)

```python
# تعيين زر القائمة للبوت
bot.set_chat_menu_button(
    menu_button=types.MenuButtonWebApp(
        text="📱 التطبيق",
        web_app=WebAppInfo(url=MINI_APP_URL)
    )
)
```

---

## 🌐 إعداد HTTPS (مطلوب للإنتاج)

Telegram يتطلب HTTPS للـ Mini Apps.

### الخيار 1: استخدام Cloudflare Tunnel (مجاني)

```bash
# تثبيت cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm -o cloudflared
chmod +x cloudflared

# تشغيل النفق
./cloudflared tunnel --url http://localhost:5000
```

### الخيار 2: استخدام ngrok

```bash
# تثبيت ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# تشغيل
ngrok http 5000
```

### الخيار 3: Let's Encrypt (للدومين الخاص)

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# ثم عدل app.py لاستخدام SSL
app.run(
    host='0.0.0.0',
    port=443,
    ssl_context=('/etc/letsencrypt/live/your-domain.com/fullchain.pem',
                 '/etc/letsencrypt/live/your-domain.com/privkey.pem')
)
```

---

## 🖥️ تشغيل كخدمة (Systemd)

### إنشاء ملف الخدمة

```bash
sudo nano /etc/systemd/system/mini-app.service
```

```ini
[Unit]
Description=Telegram Mini App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/bot/mini_app
Environment=PATH=/home/pi/bot/venv/bin
ExecStart=/home/pi/bot/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### تفعيل الخدمة

```bash
sudo systemctl daemon-reload
sudo systemctl enable mini-app
sudo systemctl start mini-app

# التحقق من الحالة
sudo systemctl status mini-app
```

---

## 📊 الميزات المتاحة

| الميزة | الحالة | الوصف |
|--------|--------|-------|
| عرض النتائج | ✅ | قائمة بجميع المواد والدرجات |
| الإحصائيات | ✅ | المعدل، نسبة النجاح، أعلى/أقل درجة |
| الرسوم البيانية | ✅ | 3 أنواع من الرسوم |
| الأوائل | ✅ | أفضل 3/5/10 طلاب |
| جدول الامتحانات | ✅ | الامتحانات القادمة |
| ربط الحساب | ✅ | ربط مرة واحدة |
| المشاركة | ✅ | مشاركة النتائج |
| تحميل PDF | 🔄 | قيد التطوير |

---

## 🎨 تخصيص الواجهة

### تغيير الألوان

عدل ملف `static/css/style.css`:

```css
:root {
    --success-color: #16a34a;  /* لون النجاح */
    --danger-color: #dc2626;   /* لون الرسوب */
    --warning-color: #f59e0b;  /* لون التحذير */
    --info-color: #3b82f6;     /* لون المعلومات */
}
```

### إضافة شعار

```html
<!-- في index.html -->
<div class="header">
    <img src="/static/images/logo.png" alt="Logo" style="width:60px;">
    <h1>🎓 بوت النتائج</h1>
</div>
```

---

## 🐛 استكشاف الأخطاء

### المشكلة: الصفحة لا تفتح

```bash
# تحقق من تشغيل الخادم
curl http://localhost:5000/api/health

# تحقق من السجلات
journalctl -u mini-app -f
```

### المشكلة: خطأ في قاعدة البيانات

```bash
# تحقق من المتغيرات
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

### المشكلة: HTTPS مطلوب

```
# استخدم أحد خيارات HTTPS المذكورة أعلاه
```

---

## 📱 اختبار Mini App

### في المتصفح

```
http://localhost:5000
```

### في Telegram

1. أرسل `/app` للبوت
2. اضغط زر "فتح التطبيق"
3. سيفتح Mini App داخل Telegram

---

## 🔒 الأمان

- ✅ التحقق من بيانات Telegram
- ✅ CORS محدود
- ✅ لا كلمات مرور مخزنة
- ✅ RLS في Supabase

---

## 📈 التحديثات المستقبلية

- [ ] تحميل PDF
- [ ] وضع Offline
- [ ] إشعارات Push
- [ ] Dark/Light mode toggle
- [ ] لغات متعددة

---

**تم التطوير:** يناير 2026 ✅
