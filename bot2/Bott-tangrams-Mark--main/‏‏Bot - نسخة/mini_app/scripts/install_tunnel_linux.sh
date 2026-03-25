#!/bin/bash
# ══════════════════════════════════════════════════════════════
# سكريبت تثبيت Cloudflare Tunnel - Linux / Raspberry Pi
# ══════════════════════════════════════════════════════════════

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║   🌐 Cloudflare Tunnel Installer for Linux            ║"
echo "║   Mini App - بوت النتائج الجامعية                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# الألوان
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# دالة للطباعة الملونة
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# ══════════════════════════════════════
# الخطوة 1: التحقق من النظام
# ══════════════════════════════════════
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 الخطوة 1: التحقق من النظام"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# التحقق من المعمارية
ARCH=$(uname -m)
print_info "المعمارية: $ARCH"

case $ARCH in
    x86_64)
        CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        print_status "نظام 64-bit x86"
        ;;
    aarch64|arm64)
        CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        print_status "نظام ARM 64-bit (Raspberry Pi 4/5)"
        ;;
    armv7l|armhf)
        CLOUDFLARED_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
        print_status "نظام ARM 32-bit (Raspberry Pi 3)"
        ;;
    *)
        print_error "معمارية غير مدعومة: $ARCH"
        exit 1
        ;;
esac

# ══════════════════════════════════════
# الخطوة 2: تحميل Cloudflared
# ══════════════════════════════════════
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📥 الخطوة 2: تحميل Cloudflared"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# التحقق من وجود cloudflared
if command -v cloudflared &> /dev/null; then
    CURRENT_VERSION=$(cloudflared --version 2>/dev/null | head -1)
    print_warning "Cloudflared مثبت بالفعل: $CURRENT_VERSION"
    read -p "هل تريد إعادة التثبيت؟ (y/n): " REINSTALL
    if [[ $REINSTALL != "y" && $REINSTALL != "Y" ]]; then
        print_info "تم تخطي التثبيت"
    else
        print_info "جاري إعادة التثبيت..."
        sudo rm -f /usr/local/bin/cloudflared
    fi
fi

if ! command -v cloudflared &> /dev/null; then
    print_info "جاري التحميل من: $CLOUDFLARED_URL"
    curl -L "$CLOUDFLARED_URL" -o /tmp/cloudflared
    chmod +x /tmp/cloudflared
    sudo mv /tmp/cloudflared /usr/local/bin/cloudflared
    print_status "تم تثبيت Cloudflared بنجاح"
fi

# التحقق من التثبيت
cloudflared --version
print_status "التحقق من التثبيت: نجح ✓"

# ══════════════════════════════════════
# الخطوة 3: إعداد المجلدات
# ══════════════════════════════════════
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 الخطوة 3: إعداد المجلدات"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

mkdir -p ~/.cloudflared
print_status "تم إنشاء مجلد الإعدادات: ~/.cloudflared"

# ══════════════════════════════════════
# الخطوة 4: اختيار طريقة التشغيل
# ══════════════════════════════════════
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 الخطوة 4: اختيار طريقة التشغيل"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "اختر طريقة التشغيل:"
echo ""
echo "  1) 🚀 سريع (Quick Tunnel) - رابط مؤقت يتغير كل مرة"
echo "  2) 🔒 دائم (Named Tunnel) - رابط ثابت مع دومين خاص"
echo ""
read -p "اختر (1 أو 2): " TUNNEL_TYPE

if [[ $TUNNEL_TYPE == "1" ]]; then
    # ══════════════════════════════════════
    # الطريقة السريعة
    # ══════════════════════════════════════
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 التشغيل السريع (Quick Tunnel)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    read -p "أدخل رقم البورت (افتراضي: 5000): " PORT
    PORT=${PORT:-5000}
    
    echo ""
    print_info "تأكد أن Mini App يعمل على البورت $PORT"
    print_info "جاري إنشاء النفق..."
    echo ""
    echo "═══════════════════════════════════════════════════════"
    echo "  اضغط Ctrl+C لإيقاف النفق"
    echo "═══════════════════════════════════════════════════════"
    echo ""
    
    cloudflared tunnel --url http://localhost:$PORT
    
else
    # ══════════════════════════════════════
    # الطريقة الدائمة
    # ══════════════════════════════════════
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔒 إعداد النفق الدائم (Named Tunnel)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # تسجيل الدخول
    echo ""
    print_info "الخطوة 4.1: تسجيل الدخول لـ Cloudflare"
    print_warning "سيفتح المتصفح - سجل دخول واختر الدومين"
    echo ""
    read -p "اضغط Enter للمتابعة..."
    
    cloudflared tunnel login
    print_status "تم تسجيل الدخول بنجاح"
    
    # إنشاء النفق
    echo ""
    print_info "الخطوة 4.2: إنشاء النفق"
    read -p "أدخل اسم النفق (مثال: miniapp-bot): " TUNNEL_NAME
    TUNNEL_NAME=${TUNNEL_NAME:-miniapp-bot}
    
    cloudflared tunnel create $TUNNEL_NAME
    print_status "تم إنشاء النفق: $TUNNEL_NAME"
    
    # الحصول على معرف النفق
    TUNNEL_ID=$(cloudflared tunnel list | grep $TUNNEL_NAME | awk '{print $1}')
    print_info "معرف النفق: $TUNNEL_ID"
    
    # إعداد الدومين
    echo ""
    print_info "الخطوة 4.3: إعداد الدومين"
    read -p "أدخل الدومين الفرعي الكامل (مثال: miniapp.yourdomain.com): " DOMAIN
    
    read -p "أدخل رقم البورت (افتراضي: 5000): " PORT
    PORT=${PORT:-5000}
    
    # إنشاء ملف الإعدادات
    echo ""
    print_info "الخطوة 4.4: إنشاء ملف الإعدادات"
    
    cat > ~/.cloudflared/config.yml << EOF
# Cloudflare Tunnel Configuration
# Mini App - بوت النتائج الجامعية
# Generated: $(date)

tunnel: $TUNNEL_ID
credentials-file: $HOME/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: $DOMAIN
    service: http://localhost:$PORT
  - service: http_status:404
EOF
    
    print_status "تم إنشاء ملف الإعدادات: ~/.cloudflared/config.yml"
    
    # ربط الدومين
    echo ""
    print_info "الخطوة 4.5: ربط الدومين بـ DNS"
    cloudflared tunnel route dns $TUNNEL_NAME $DOMAIN
    print_status "تم ربط الدومين: $DOMAIN"
    
    # إنشاء خدمة systemd
    echo ""
    print_info "الخطوة 4.6: إنشاء خدمة تشغيل تلقائي"
    
    sudo cat > /etc/systemd/system/cloudflared-miniapp.service << EOF
[Unit]
Description=Cloudflare Tunnel for Mini App
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/cloudflared tunnel run $TUNNEL_NAME
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable cloudflared-miniapp
    print_status "تم إنشاء خدمة التشغيل التلقائي"
    
    # تشغيل الخدمة
    echo ""
    read -p "هل تريد تشغيل النفق الآن؟ (y/n): " START_NOW
    
    if [[ $START_NOW == "y" || $START_NOW == "Y" ]]; then
        sudo systemctl start cloudflared-miniapp
        print_status "تم تشغيل النفق"
        
        sleep 3
        sudo systemctl status cloudflared-miniapp --no-pager
    fi
    
    # ملخص
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║                  ✅ تم الإعداد بنجاح!                  ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📋 ملخص الإعدادات:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🏷️  اسم النفق:    $TUNNEL_NAME"
    echo "  🆔 معرف النفق:   $TUNNEL_ID"
    echo "  🌐 الرابط:        https://$DOMAIN"
    echo "  🔌 البورت المحلي: $PORT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📌 أوامر مفيدة:"
    echo "  تشغيل:   sudo systemctl start cloudflared-miniapp"
    echo "  إيقاف:   sudo systemctl stop cloudflared-miniapp"
    echo "  الحالة:  sudo systemctl status cloudflared-miniapp"
    echo "  السجلات: journalctl -u cloudflared-miniapp -f"
    echo ""
    echo "🎯 الخطوة التالية:"
    echo "  1. تأكد أن Mini App يعمل: python mini_app/app.py"
    echo "  2. أضف الرابط في BotFather: https://$DOMAIN"
    echo ""
fi

print_status "انتهى السكريبت بنجاح! 🎉"
