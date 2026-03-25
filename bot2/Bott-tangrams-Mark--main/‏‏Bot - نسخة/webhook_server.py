# -*- coding: utf-8 -*-
"""
خادم Webhook للبوت
أداء أفضل من Polling للإنتاج
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import telebot
import os
import threading
import time
from datetime import datetime


def create_webhook_server(bot, secret_token: str = None):
    """
    إنشاء خادم Webhook
    
    Args:
        bot: instance من telebot
        secret_token: رمز سري للتحقق من الطلبات (اختياري)
    
    Returns:
        Flask app
    """
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/', methods=['GET'])
    def index():
        """صفحة رئيسية"""
        return jsonify({
            'status': 'running',
            'service': 'Telegram Bot Webhook',
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/health', methods=['GET'])
    def health():
        """فحص صحة الخادم"""
        return jsonify({
            'status': 'healthy',
            'uptime': time.time(),
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """استقبال تحديثات Telegram"""
        # التحقق من الرمز السري
        if secret_token:
            header_token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
            if header_token != secret_token:
                return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            json_data = request.get_json()
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            print(f"❌ خطأ في معالجة Webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/set_webhook', methods=['POST'])
    def set_webhook():
        """تسجيل Webhook URL"""
        data = request.get_json() or {}
        webhook_url = data.get('url')
        
        if not webhook_url:
            return jsonify({'error': 'URL مطلوب'}), 400
        
        try:
            # إزالة Webhook القديم
            bot.remove_webhook()
            time.sleep(0.5)
            
            # تسجيل الجديد
            result = bot.set_webhook(
                url=webhook_url,
                secret_token=secret_token,
                drop_pending_updates=True
            )
            
            return jsonify({
                'success': result,
                'webhook_url': webhook_url
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/remove_webhook', methods=['POST'])
    def remove_webhook():
        """إزالة Webhook"""
        try:
            bot.remove_webhook()
            return jsonify({'success': True, 'message': 'تم إزالة Webhook'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/webhook_info', methods=['GET'])
    def webhook_info():
        """معلومات Webhook الحالي"""
        try:
            info = bot.get_webhook_info()
            return jsonify({
                'url': info.url,
                'has_custom_certificate': info.has_custom_certificate,
                'pending_update_count': info.pending_update_count,
                'last_error_date': info.last_error_date,
                'last_error_message': info.last_error_message
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


def run_webhook_server(bot, host: str = '0.0.0.0', port: int = 8443, 
                       webhook_url: str = None, secret_token: str = None):
    """
    تشغيل خادم Webhook
    
    Args:
        bot: instance من telebot
        host: عنوان الاستماع
        port: منفذ الاستماع
        webhook_url: رابط Webhook الكامل
        secret_token: رمز سري
    """
    app = create_webhook_server(bot, secret_token)
    
    # تسجيل Webhook إذا تم توفير الرابط
    if webhook_url:
        try:
            bot.remove_webhook()
            time.sleep(1)
            bot.set_webhook(
                url=webhook_url,
                secret_token=secret_token,
                drop_pending_updates=True
            )
            print(f"✅ تم تسجيل Webhook: {webhook_url}")
        except Exception as e:
            print(f"⚠️ خطأ في تسجيل Webhook: {e}")
    
    print(f"🚀 خادم Webhook يعمل على {host}:{port}")
    app.run(host=host, port=port, threaded=True)


# للاستخدام المستقل
if __name__ == '__main__':
    import sys
    sys.path.insert(0, '.')
    
    from dotenv import load_dotenv
    load_dotenv()
    
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL')  # مثال: https://yourdomain.com/webhook
    SECRET_TOKEN = os.environ.get('WEBHOOK_SECRET', 'your-secret-token')
    
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN مطلوب")
        exit(1)
    
    bot = telebot.TeleBot(BOT_TOKEN)
    
    # استيراد معالجات البوت
    # from final_bot_with_image import *  # أضف هذا لتحميل جميع المعالجات
    
    run_webhook_server(
        bot=bot,
        host='0.0.0.0',
        port=8443,
        webhook_url=WEBHOOK_URL,
        secret_token=SECRET_TOKEN
    )
