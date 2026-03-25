"""
وحدة الذكاء الاصطناعي (AI Service)
استخدام Google Gemini API من Google AI Studio
الإصدار الأحدث: google-genai مع Extended Thinking
"""

import os
import sys

# حل مشاكل الترميز
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class AIService:
    def __init__(self):
        """تهيئة خدمة AI باستخدام Google Gemini API الأحدث"""
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = os.environ.get("GOOGLE_AI_MODEL", "gemini-flash-lite-latest")
        
        if not self.api_key:
            self.enabled = False
            print("تحذير: Google Gemini API Key غير موجود. تاكد من GEMINI_API_KEY في .env")
            print("احصل على API Key من: https://aistudio.google.com/")
            return
        
        if not GENAI_AVAILABLE:
            self.enabled = False
            print("تحذير: مكتبة google-genai غير مثبتة")
            return
        
        self.enabled = True
        try:
            self.client = genai.Client(api_key=self.api_key)
            print(f"Google Gemini API متصل: {self.model_name}")
        except Exception as e:
            self.enabled = False
            print(f"تحذير: فشل الاتصال بـ Google Gemini: {str(e)[:100]}")
            self.client = None

    def _call_gemini(self, prompt, use_thinking=True):
        """استدعاء Google Gemini API مع Extended Thinking"""
        if not self.enabled or not self.client:
            return None
        
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            config = types.GenerateContentConfig(
                temperature=0.7,
            )
            
            # إضافة ThinkingConfig للنماذج التي تدعمها
            if use_thinking and "thinking" in self.model_name.lower():
                config.thinking_config = types.ThinkingConfig(
                    thinking_level="HIGH",
                )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None

    def generate_smart_recommendations(self, student_name, analysis_data):
        """توليد نصائح ذكية ومخصصة بناءً على بيانات الطالب"""
        if not self.enabled:
            return self._fallback_recommendations(analysis_data)
        
        try:
            weak_subjects = [s['name'] for s in analysis_data.get('weak_subjects', [])]
            strong_subjects = [s['name'] for s in analysis_data.get('strong_subjects', [])]
            avg = analysis_data.get('average_grade', 0)
            performance = analysis_data.get('performance_level', 'unknown')
            
            prompt = f"""أنت معلم خبير في التعليم والتدريس. قدّم نصائح ذكية ومخصصة للطالب:

**معلومات الطالب:**
- الاسم: {student_name}
- المعدل العام: {avg}
- مستوى الأداء: {performance}
- المواد القوية: {', '.join(strong_subjects) if strong_subjects else 'لا توجد'}
- المواد الضعيفة: {', '.join(weak_subjects) if weak_subjects else 'لا توجد'}

**المطلوب:**
اكتب 5 نصائح دراسية ذكية وقابلة للتطبيق فوراً. كن محددًا وعملياً:
1. اجعل كل نصيحة قصيرة وواضحة
2. ركز على المواد الضعيفة
3. أضف استراتيجية دراسة فعالة
4. كن إيجابياً وتحفيزياً

الرد باللغة العربية فقط. كن مختصراً وعملياً."""
            
            result = self._call_gemini(prompt, use_thinking=True)
            return result if result else self._fallback_recommendations(analysis_data)
            
        except Exception as e:
            print(f"Error in AI recommendations: {e}")
            return self._fallback_recommendations(analysis_data)

    def analyze_weak_subjects(self, student_name, weak_subjects_data):
        """تحليل ذكي لأسباب الضعف في المواد"""
        if not self.enabled:
            return "خدمة الذكاء الاصطناعي غير متاحة حالياً"
        
        try:
            subjects_info = "\n".join([
                f"- {s.get('name')}: {s.get('grade')}% (نظري: {s.get('theoretical', 0)}, عملي: {s.get('practical', 0)})"
                for s in weak_subjects_data[:5]
            ])
            
            prompt = f"""أنت مستشار تعليمي متخصص. حلّل أسباب ضعف الطالب في هذه المواد وقدّم حلولاً:

**الطالب:** {student_name}

**المواد الضعيفة:**
{subjects_info}

**المطلوب:**
1. ما أسباب الضعف المحتملة؟
2. ما هي الصعوبات الشائعة؟
3. كيف يمكن التحسن بسرعة؟

كن عملياً وواضحاً. الرد باللغة العربية."""
            
            result = self._call_gemini(prompt, use_thinking=True)
            return result if result else "لم نتمكن من تحليل الضعف حالياً"
            
        except Exception as e:
            print(f"Error in analyzing weak subjects: {e}")
            return f"خطأ في التحليل"

    def generate_study_plan(self, student_name, weak_subjects, available_days=7):
        """توليد خطة دراسة مخصصة"""
        if not self.enabled:
            return "خدمة الذكاء الاصطناعي غير متاحة"
        
        try:
            subjects_list = ", ".join([s.get('name') for s in weak_subjects[:5]])
            
            prompt = f"""أنت مشرف دراسي متخصص. اكتب خطة دراسة عملية:

**الطالب:** {student_name}
**المواد المطلوب التركيز عليها:** {subjects_list}
**عدد الأيام المتاحة:** {available_days} أيام

**المطلوب:**
اكتب جدول دراسة مفصل:
- التوزيع اليومي للمواد
- ساعات الدراسة المقترحة
- نصائح للمراجعة الفعالة
- طرق تذكر المعلومات

كن دقيقاً وعملياً. الرد باللغة العربية."""
            
            result = self._call_gemini(prompt, use_thinking=True)
            return result if result else "لم نتمكن من توليد الخطة حالياً"
            
        except Exception as e:
            print(f"Error in study plan generation: {e}")
            return f"خطأ في توليد الخطة"

    def answer_student_question(self, question, context=""):
        """الرد على أسئلة الطلاب بشكل ذكي"""
        if not self.enabled:
            return "خدمة الذكاء الاصطناعي غير متاحة حالياً"
        
        try:
            prompt = f"""أنت معلم خبير متخصص في الإجابة على أسئلة الطلاب.

**السؤال:** {question}
**السياق الإضافي:** {context if context else 'لا يوجد'}

**المطلوب:**
- أجب بشكل واضح ومباشر
- اشرح بطريقة يفهمها الطالب
- أضف مثال إن أمكن
- كن مختصراً وشاملاً

الرد باللغة العربية."""
            
            result = self._call_gemini(prompt, use_thinking=False)
            return result if result else "اعتذر، لم أتمكن من الإجابة الآن"
            
        except Exception as e:
            print(f"Error in answering question: {e}")
            return "اعتذر، حدث خطأ في الإجابة"

    def _fallback_recommendations(self, analysis_data):
        """نصائح افتراضية عند عدم توفر AI"""
        weak_subjects = analysis_data.get('weak_subjects', [])
        strong_subjects = analysis_data.get('strong_subjects', [])
        
        msg = "نصائح دراسية:\n\n"
        
        if weak_subjects:
            msg += "المواد الضعيفة - المطلوب تحسنها:\n"
            for s in weak_subjects[:3]:
                msg += f"• {s.get('name', 'مادة')}: ركز على المراجعة المكثفة\n"
            msg += "\n"
        
        if strong_subjects:
            msg += "المواد القوية - حافظ عليها:\n"
            for s in strong_subjects[:3]:
                msg += f"• {s.get('name', 'مادة')}: أضف تمارين إضافية\n"
        
        return msg


# إنشاء instance عام
ai_service = AIService()

