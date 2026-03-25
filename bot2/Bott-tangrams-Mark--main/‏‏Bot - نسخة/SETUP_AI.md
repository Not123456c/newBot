# دليل التثبيت والبدء
**AI Integration Setup Guide**

---

## 🚀 خطوات البدء السريع

### 1️⃣ تثبيت المكتبات الجديدة
```bash
pip install -r requirements.txt
```

### 2️⃣ إضافة توكن Orbit Provider إلى `.env`
```env
ANTHROPIC_BASE_URL=https://api.orbit-provider.com/api/provider/agy
ANTHROPIC_AUTH_TOKEN=sk-orbit-xxxxxxxxxxxxxxxx  # ضع توكنك هنا
ANTHROPIC_MODEL=gemini-3-flash
```

### 3️⃣ تشغيل البوت
```bash
python final_bot_with_image.py
```

---

## 📋 الأوامر الجديدة

### `/analyze` - تحليل الضعف
```
/analyze
→ أرسل رقمك الجامعي أو اسمك
→ يحلل النظام المواد الضعيفة
→ تتلقى تحليل ذكي مفصل
```

### `/plan` - خطة الدراسة
```
/plan
→ أرسل رقمك الجامعي أو اسمك
→ يولد جدول دراسة مخصص
→ تتلقى خطة أسبوعية ذكية
```

### `/ask` - سؤال أكاديمي
```
/ask
→ اكتب سؤالك
→ يحلل ويفهم السؤال
→ تتلقى إجابة شاملة
```

### `💡 نصائح` - (الزر الموجود)
- الآن توليد ذكي بدل نصائح قديمة
- مخصصة تماماً لكل طالب

---

## ⚙️ المتطلبات

| العنصر | الحالة | ملاحظة |
|--------|--------|--------|
| Python | ✅ 3.8+ | |
| pyTelegramBotAPI | ✅ 4.10+ | موجود |
| Supabase | ✅ موجود | موجود |
| Anthropic | ⚠️ جديد | تثبيت: `pip install anthropic` |
| Orbit Token | ⚠️ مطلوب | ضعه في `.env` |

---

## 🔐 الترتيب الأماني للتوكن

```
❌ لا تفعل:
ANTHROPIC_AUTH_TOKEN=sk-orbit-xxxxxx (مباشرة في الكود)

✅ افعل:
في `.env`:
ANTHROPIC_AUTH_TOKEN=sk-orbit-xxxxxx
```

---

## 🧪 اختبار سريع

```python
# لاختبار ما إذا كان كل شيء يعمل
python -c "
from ai_service import ai_service
print('AI Service Status:', 'Enabled ✅' if ai_service.enabled else 'Disabled (Fallback) ⚠️')
"
```

---

## 🐛 استكشاف الأخطاء

### ❌ `ModuleNotFoundError: No module named 'anthropic'`
```bash
pip install anthropic>=0.7.0
```

### ❌ `ANTHROPIC_AUTH_TOKEN غير موجود`
- أضف التوكن إلى `.env`
- أعد تشغيل البوت

### ❌ `لا يوجد رد من AI`
- تأكد من الاتصال بالإنترنت
- تحقق من صحة التوكن
- البوت سيستخدم نصائح افتراضية (Fallback)

---

## 📊 معلومات الأداء

- **استجابة الـ AI:** 1-3 ثواني
- **استهلاك الذاكرة:** منخفض جداً
- **عدد الطلبات:** مفتوح (حسب حدود API)
- **اللغة المدعومة:** العربية والإنجليزية

---

## ✅ النقاط المهمة

1. 🔒 توكنك آمن في `.env` فقط
2. 🔄 الواجهة تعمل حتى إذا كان AI معطلاً (Fallback mode)
3. 🌐 يحتاج اتصال بالإنترنت فقط عند استخدام الأوامر الذكية
4. 🚀 جاهز للإنتاج الآن

---

## 📞 الدعم

- 📖 اقرأ `AI_FEATURES.md` للمزيد
- 💬 اختبر الأوامر مباشرة
- 🆘 افحص `.env` أولاً

---

**تاريخ التحديث:** 19 مارس 2026  
**الحالة:** جاهز للاستخدام ✅
