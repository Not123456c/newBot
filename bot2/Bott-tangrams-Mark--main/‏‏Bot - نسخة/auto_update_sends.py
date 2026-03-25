# -*- coding: utf-8 -*-
"""
سكريبت تحديث تلقائي لجميع bot.send_message/photo/document إلى safe_send
"""

import re
import sys

def update_bot_file():
    filepath = "final_bot_with_image.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_count = len(re.findall(r'bot\.send_', content))
    print(f"📊 عدد bot.send الأصلية: {original_count}")
    
    # تحديث bot.send_message
    # النمط: bot.send_message(chat_id_expression, message_text, ...)
    pattern1 = r'bot\.send_message\(([^,]+),\s*([^,]+),\s*'
    replacement1 = r'safe_send_message(bot, \1, \2, '
    content = re.sub(pattern1, replacement1, content)
    
    # تحديث bot.send_photo
    pattern2 = r'bot\.send_photo\(([^,]+),\s*([^,]+),\s*'
    replacement2 = r'safe_send_photo(bot, \1, \2, '
    content = re.sub(pattern2, replacement2, content)
    
    # تحديث bot.send_document
    pattern3 = r'bot\.send_document\(([^,]+),\s*([^,]+),\s*'
    replacement3 = r'safe_send_document(bot, \1, \2, '
    content = re.sub(pattern3, replacement3, content)
    
    # حالات بدون معاملات إضافية
    pattern4 = r'bot\.send_message\(([^,]+),\s*([^)]+)\)$'
    replacement4 = r'safe_send_message(bot, \1, \2)'
    content = re.sub(pattern4, replacement4, content, flags=re.MULTILINE)
    
    # حالات في نهاية السطر
    pattern5 = r'bot\.send_message\(([^,]+),\s*([^)]+)\)(\s*$)'
    replacement5 = r'safe_send_message(bot, \1, \2)\3'
    content = re.sub(pattern5, replacement5, content, flags=re.MULTILINE)
    
    new_count = len(re.findall(r'bot\.send_', content))
    print(f"📊 عدد bot.send المتبقية: {new_count}")
    
    if new_count < original_count:
        print(f"✅ تم تحديث {original_count - new_count} استدعاء")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    else:
        print("⚠️  لم يتم تحديث أي شيء - قد تحتاج لتحديث يدوي")
        return False


if __name__ == "__main__":
    try:
        if update_bot_file():
            print("\n✅ تم التحديث بنجاح!")
            sys.exit(0)
        else:
            print("\n⚠️  التحديث غير مكتمل - قد تحتاج تحديث يدوي")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        sys.exit(1)
