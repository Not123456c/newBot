-- ══════════════════════════════════════
-- جدول الملفات الشخصية لـ Mini App
-- Supabase SQL
-- ══════════════════════════════════════

-- إنشاء جدول الملفات الشخصية
CREATE TABLE IF NOT EXISTS public.mini_app_profiles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    student_id VARCHAR(50) NOT NULL,
    student_name VARCHAR(255),
    telegram_name VARCHAR(255),
    telegram_username VARCHAR(100),
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- البيانات الإضافية
    last_access TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    settings JSONB DEFAULT '{}'::jsonb
);

-- الفهارس لتحسين الأداء
CREATE INDEX IF NOT EXISTS idx_mini_app_profiles_telegram_id 
ON public.mini_app_profiles(telegram_id);

CREATE INDEX IF NOT EXISTS idx_mini_app_profiles_student_id 
ON public.mini_app_profiles(student_id);

-- تفعيل RLS (Row Level Security)
ALTER TABLE public.mini_app_profiles ENABLE ROW LEVEL SECURITY;

-- سياسة للقراءة والكتابة
CREATE POLICY "Allow all operations on mini_app_profiles" 
ON public.mini_app_profiles 
FOR ALL 
USING (true) 
WITH CHECK (true);

-- دالة لتحديث updated_at تلقائياً
CREATE OR REPLACE FUNCTION update_mini_app_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger للتحديث التلقائي
DROP TRIGGER IF EXISTS trigger_mini_app_profiles_updated_at ON public.mini_app_profiles;
CREATE TRIGGER trigger_mini_app_profiles_updated_at
    BEFORE UPDATE ON public.mini_app_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_mini_app_profiles_updated_at();

-- ══════════════════════════════════════
-- إحصائيات الاستخدام
-- ══════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.mini_app_analytics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT,
    student_id VARCHAR(50),
    action_type VARCHAR(50) NOT NULL, -- 'view_results', 'view_charts', 'view_top', 'share', etc.
    action_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    user_agent TEXT,
    platform VARCHAR(50) -- 'android', 'ios', 'web', etc.
);

CREATE INDEX IF NOT EXISTS idx_mini_app_analytics_telegram_id 
ON public.mini_app_analytics(telegram_id);

CREATE INDEX IF NOT EXISTS idx_mini_app_analytics_created_at 
ON public.mini_app_analytics(created_at);

ALTER TABLE public.mini_app_analytics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on mini_app_analytics" 
ON public.mini_app_analytics 
FOR ALL 
USING (true) 
WITH CHECK (true);

-- ══════════════════════════════════════
-- عرض الإحصائيات
-- ══════════════════════════════════════

-- عدد المستخدمين المربوطين
-- SELECT COUNT(*) as total_linked_users FROM mini_app_profiles WHERE is_active = true;

-- أكثر الأوقات استخداماً
-- SELECT 
--     EXTRACT(HOUR FROM created_at) as hour,
--     COUNT(*) as actions_count
-- FROM mini_app_analytics
-- WHERE created_at > now() - INTERVAL '7 days'
-- GROUP BY hour
-- ORDER BY actions_count DESC;

-- ══════════════════════════════════════
-- تم الإنشاء بنجاح!
-- ══════════════════════════════════════
