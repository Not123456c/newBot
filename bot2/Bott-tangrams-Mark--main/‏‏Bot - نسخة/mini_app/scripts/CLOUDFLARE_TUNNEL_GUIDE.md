# 🌐 دليل تثبيت Cloudflare Tunnel الكامل

## 📋 الفهرس

1. [ما هو Cloudflare Tunnel؟](#ما-هو-cloudflare-tunnel)
2. [المتطلبات](#المتطلبات)
3. [التثبيت على Linux/Raspberry Pi](#التثبيت-على-linux)
4. [التثبيت على Windows](#التثبيت-على-windows)
5. [الإعداد اليدوي](#الإعداد-اليدوي)
6. [ربط مع BotFather](#ربط-مع-botfather)
7. [استكشاف الأخطاء](#استكشاف-الأخطاء)
8. [الأوامر المفيدة](#الأوامر-المفيدة)

---

## ما هو Cloudflare Tunnel؟

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  جهازك     │────▶│  Cloudflare  │◀────│  المستخدم  │
│ localhost  │     │   Tunnel     │     │  Telegram   │
└─────────────┘     └──────────────┘     └─────────────┘
     :5000              HTTPS              يفتح Mini App
```

**الفوائد:**
- ✅ مجاني 100%
- ✅ HTTPS تلقائي
- ✅ رابط ثابت دائم
- ✅ بدون فتح بورتات
- ✅ بدون IP ثابت
- ✅ حماية DDoS

---

## المتطلبات

### لجميع الأنظمة:
- حساب Cloudflare (مجاني): https://dash.cloudflare.com/sign-up
- Mini App يعمل على localhost:5000

### Linux / Raspberry Pi:
- curl أو wget
- صلاحيات sudo

### Windows:
- Windows 10/11
- صلاحيات Administrator
- PowerShell

---

## التثبيت على Linux

### الطريقة 1: استخدام السكريبت التلقائي (موصى به)

```bash
# 1. إعطاء صلاحيات التنفيذ
chmod +x scripts/install_tunnel_linux.sh

# 2. تشغيل السكريبت
./scripts/install_tunnel_linux.sh
```

### الطريقة 2: التثبيت اليدوي

#### الخطوة 1: تحميل Cloudflared

```bash
# Raspberry Pi 4/5 (64-bit)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o cloudflared

# Raspberry Pi 3 (32-bit)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm -o cloudflared

# Ubuntu/Debian (64-bit)
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared

# إعطاء صلاحيات وتثبيت
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# التحقق
cloudflared --version
```

#### الخطوة 2: التشغيل السريع (مؤقت)

```bash
# تشغيل نفق مؤقت
cloudflared tunnel --url http://localhost:5000

# ستحصل على رابط مثل:
# https://random-name-here.trycloudflare.com
```

#### الخطوة 3: إعداد نفق دائم

```bash
# 1. تسجيل الدخول
cloudflared tunnel login

# 2. إنشاء النفق
cloudflared tunnel create miniapp-bot

# 3. ربط الدومين
cloudflared tunnel route dns miniapp-bot miniapp.yourdomain.com

# 4. إنشاء ملف الإعدادات
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

**محتوى config.yml:**
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/YOUR_USER/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: miniapp.yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

```bash
# 5. تشغيل النفق
cloudflared tunnel run miniapp-bot
```

#### الخطوة 4: تشغيل تلقائي (Systemd)

```bash
# إنشاء ملف الخدمة
sudo nano /etc/systemd/system/cloudflared-miniapp.service
```

**محتوى الملف:**
```ini
[Unit]
Description=Cloudflare Tunnel for Mini App
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/cloudflared tunnel run miniapp-bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# تفعيل وتشغيل
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-miniapp
sudo systemctl start cloudflared-miniapp

# التحقق
sudo systemctl status cloudflared-miniapp
```

---

## التثبيت على Windows

### الطريقة 1: استخدام السكريبت التلقائي (موصى به)

```
1. اضغط كليك يمين على: install_tunnel_windows.bat
2. اختر "Run as administrator"
3. اتبع التعليمات
```

### الطريقة 2: التثبيت اليدوي

#### الخطوة 1: تحميل Cloudflared

```powershell
# افتح PowerShell كـ Administrator

# إنشاء مجلد
New-Item -ItemType Directory -Force -Path C:\cloudflared

# تحميل (64-bit)
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "C:\cloudflared\cloudflared.exe"

# إضافة للـ PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\cloudflared", "Machine")

# إعادة تشغيل PowerShell ثم التحقق
cloudflared --version
```

#### الخطوة 2: التشغيل السريع

```cmd
cloudflared tunnel --url http://localhost:5000
```

#### الخطوة 3: إعداد نفق دائم

```cmd
# 1. تسجيل الدخول
cloudflared tunnel login

# 2. إنشاء النفق
cloudflared tunnel create miniapp-bot

# 3. ربط الدومين
cloudflared tunnel route dns miniapp-bot miniapp.yourdomain.com
```

#### الخطوة 4: إنشاء ملف الإعدادات

**المسار:** `C:\Users\YOUR_USER\.cloudflared\config.yml`

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: C:\Users\YOUR_USER\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: miniapp.yourdomain.com
    service: http://localhost:5000
  - service: http_status:404
```

#### الخطوة 5: تثبيت كخدمة Windows

```cmd
# تثبيت الخدمة
cloudflared service install

# تشغيل
net start cloudflared

# إيقاف
net stop cloudflared

# إزالة الخدمة
cloudflared service uninstall
```

---

## ربط مع BotFather

### بعد الحصول على الرابط:

```
1. افتح @BotFather في Telegram
2. أرسل /mybots
3. اختر البوت الخاص بك
4. اضغط "Bot Settings"
5. اضغط "Menu Button"
6. اضغط "Configure menu button"
7. أرسل الرابط:
   https://miniapp.yourdomain.com
8. أرسل اسم الزر:
   📱 التطبيق

✅ تم! الآن سيظهر زر بجانب مربع الكتابة
```

---

## استكشاف الأخطاء

### المشكلة: "tunnel not found"

```bash
# تحقق من قائمة الأنفاق
cloudflared tunnel list

# إذا لم يظهر، أعد إنشاءه
cloudflared tunnel create miniapp-bot
```

### المشكلة: "credentials file not found"

```bash
# تحقق من مسار الملف
ls ~/.cloudflared/

# يجب أن ترى ملف .json
# تأكد من مطابقة الاسم في config.yml
```

### المشكلة: "connection refused"

```bash
# تأكد أن Mini App يعمل
curl http://localhost:5000/api/health

# إذا لم يعمل، شغله:
cd mini_app
python app.py
```

### المشكلة: "DNS not propagated"

```bash
# انتظر 1-5 دقائق
# أو تحقق من DNS:
nslookup miniapp.yourdomain.com
```

### المشكلة: الخدمة لا تعمل (Linux)

```bash
# تحقق من السجلات
journalctl -u cloudflared-miniapp -f

# أعد التشغيل
sudo systemctl restart cloudflared-miniapp
```

### المشكلة: الخدمة لا تعمل (Windows)

```cmd
# تحقق من الحالة
sc query cloudflared

# أعد التشغيل
net stop cloudflared
net start cloudflared

# تحقق من السجلات
eventvwr.msc
```

---

## الأوامر المفيدة

### Linux

```bash
# ═══════════════════════════════════════
# إدارة النفق
# ═══════════════════════════════════════

# قائمة الأنفاق
cloudflared tunnel list

# معلومات النفق
cloudflared tunnel info miniapp-bot

# حذف النفق
cloudflared tunnel delete miniapp-bot

# تشغيل النفق يدوياً
cloudflared tunnel run miniapp-bot

# تشغيل سريع (مؤقت)
cloudflared tunnel --url http://localhost:5000

# ═══════════════════════════════════════
# إدارة الخدمة
# ═══════════════════════════════════════

# تشغيل
sudo systemctl start cloudflared-miniapp

# إيقاف
sudo systemctl stop cloudflared-miniapp

# إعادة تشغيل
sudo systemctl restart cloudflared-miniapp

# الحالة
sudo systemctl status cloudflared-miniapp

# السجلات
journalctl -u cloudflared-miniapp -f

# تفعيل التشغيل التلقائي
sudo systemctl enable cloudflared-miniapp

# إلغاء التشغيل التلقائي
sudo systemctl disable cloudflared-miniapp
```

### Windows

```cmd
:: ═══════════════════════════════════════
:: إدارة النفق
:: ═══════════════════════════════════════

:: قائمة الأنفاق
cloudflared tunnel list

:: تشغيل النفق يدوياً
cloudflared tunnel run miniapp-bot

:: تشغيل سريع (مؤقت)
cloudflared tunnel --url http://localhost:5000

:: ═══════════════════════════════════════
:: إدارة الخدمة
:: ═══════════════════════════════════════

:: تشغيل
net start cloudflared

:: إيقاف
net stop cloudflared

:: الحالة
sc query cloudflared

:: تثبيت الخدمة
cloudflared service install

:: إزالة الخدمة
cloudflared service uninstall
```

---

## 📊 مقارنة الطرق

| الميزة | Quick Tunnel | Named Tunnel |
|--------|--------------|--------------|
| السرعة | فوري | يحتاج إعداد |
| الرابط | مؤقت (يتغير) | **ثابت دائماً** |
| الدومين | عشوائي | **مخصص** |
| التشغيل التلقائي | ❌ | ✅ |
| مناسب لـ | التجربة | **الإنتاج** |

---

## 🎯 الخطوات النهائية

```
1. ✅ تثبيت Cloudflared
2. ✅ إنشاء النفق
3. ✅ إعداد الدومين
4. ✅ تشغيل Mini App: python mini_app/app.py
5. ✅ تشغيل النفق: cloudflared tunnel run miniapp-bot
6. ✅ إضافة الرابط في BotFather
7. 🎉 استمتع!
```

---

## 📞 المساعدة

- [وثائق Cloudflare الرسمية](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [منتدى Cloudflare](https://community.cloudflare.com/)

---

**تم التحديث:** يناير 2026
