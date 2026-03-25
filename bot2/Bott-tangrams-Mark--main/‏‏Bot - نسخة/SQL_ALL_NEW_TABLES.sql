-- ══════════════════════════════════════════════════════════════════════════════
-- 🎓 بوت النتائج الجامعية - جميع جداول قاعدة البيانات الجديدة
-- University Results Bot - All New Database Tables
-- ══════════════════════════════════════════════════════════════════════════════
-- 
-- 📋 الجداول المضمنة:
--   1. user_achievements      - الإنجازات والشارات
--   2. achievement_log        - سجل الإنجازات
--   3. points_log             - سجل النقاط
--   4. announcements          - الإعلانات
--   5. activity_log           - سجل النشاطات
--   6. semester_history       - تاريخ الفصول
--   7. challenges             - التحديات
--   8. user_challenges        - تحديات المستخدمين
--   9. bot_users              - مستخدمي البوت
--   10. mini_app_profiles     - ملفات Mini App
--
-- 🚀 طريقة الاستخدام:
--   1. افتح Supabase Dashboard
--   2. اذهب إلى SQL Editor
--   3. انسخ كل المحتوى
--   4. اضغط Run
--
-- ══════════════════════════════════════════════════════════════════════════════


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                      1. جدول الإنجازات والشارات                            ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.user_achievements (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    
    -- الإنجازات (مصفوفة من IDs)
    achievements TEXT[] DEFAULT '{}',
    
    -- النقاط والمستوى
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    
    -- سلسلة الأيام
    streak_days INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    
    -- النشاط
    last_active TIMESTAMP WITH TIME ZONE DEFAULT now(),
    features_used TEXT[] DEFAULT '{}',
    
    -- الإحصائيات
    shares_count INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0,
    searches_count INTEGER DEFAULT 0,
    
    -- التواريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- الفهارس
CREATE INDEX IF NOT EXISTS idx_user_achievements_telegram_id ON public.user_achievements(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_total_points ON public.user_achievements(total_points DESC);
CREATE INDEX IF NOT EXISTS idx_user_achievements_level ON public.user_achievements(level);

-- RLS
ALTER TABLE public.user_achievements ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on user_achievements" ON public.user_achievements FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                         2. سجل الإنجازات                                   ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.achievement_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    achievement_id VARCHAR(50) NOT NULL,
    points_earned INTEGER DEFAULT 0,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    
    -- معلومات إضافية
    context JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_achievement_log_telegram_id ON public.achievement_log(telegram_id);
CREATE INDEX IF NOT EXISTS idx_achievement_log_earned_at ON public.achievement_log(earned_at);

ALTER TABLE public.achievement_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on achievement_log" ON public.achievement_log FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                           3. سجل النقاط                                    ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.points_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    points INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_points_log_telegram_id ON public.points_log(telegram_id);
CREATE INDEX IF NOT EXISTS idx_points_log_created_at ON public.points_log(created_at);

ALTER TABLE public.points_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on points_log" ON public.points_log FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                            4. الإعلانات                                    ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.announcements (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- محتوى الإعلان
    content TEXT NOT NULL,
    image_url TEXT,
    
    -- الاستهداف
    target_group VARCHAR(50) DEFAULT 'all',
    -- القيم: 'all', 'failing', 'at_risk', 'top_performers', 'inactive', 'new_users', 'subscribed'
    
    -- الجدولة
    scheduled_time TIMESTAMP WITH TIME ZONE,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_interval VARCHAR(20), -- 'daily', 'weekly', 'monthly'
    
    -- الحالة
    status VARCHAR(20) DEFAULT 'pending',
    -- القيم: 'pending', 'scheduled', 'sent', 'cancelled'
    
    -- الإحصائيات
    sent_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    
    -- المشرف
    created_by BIGINT NOT NULL,
    
    -- التواريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    sent_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_announcements_status ON public.announcements(status);
CREATE INDEX IF NOT EXISTS idx_announcements_scheduled_time ON public.announcements(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_announcements_created_by ON public.announcements(created_by);

ALTER TABLE public.announcements ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on announcements" ON public.announcements FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                          5. سجل النشاطات                                   ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.activity_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    
    -- نوع النشاط
    action VARCHAR(50) NOT NULL,
    -- أمثلة: 'search_result', 'view_top', 'view_chart', 'ai_analyze', 'share_result', etc.
    
    -- تفاصيل إضافية (JSON)
    details JSONB,
    
    -- معلومات الوقت
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    hour_of_day INTEGER, -- 0-23
    day_of_week INTEGER  -- 0-6 (الإثنين = 0)
);

CREATE INDEX IF NOT EXISTS idx_activity_log_telegram_id ON public.activity_log(telegram_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_action ON public.activity_log(action);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON public.activity_log(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_log_hour ON public.activity_log(hour_of_day);

ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on activity_log" ON public.activity_log FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                         6. تاريخ الفصول                                    ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.semester_history (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    
    -- معلومات الفصل
    semester VARCHAR(20) NOT NULL, -- مثال: '2024-1', '2024-2'
    academic_year VARCHAR(10),
    
    -- النتائج
    average DECIMAL(5,2),
    total_subjects INTEGER,
    passed_subjects INTEGER,
    failed_subjects INTEGER,
    
    -- التواريخ
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    
    UNIQUE(student_id, semester)
);

CREATE INDEX IF NOT EXISTS idx_semester_history_student_id ON public.semester_history(student_id);
CREATE INDEX IF NOT EXISTS idx_semester_history_semester ON public.semester_history(semester);

ALTER TABLE public.semester_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on semester_history" ON public.semester_history FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                           7. التحديات                                      ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.challenges (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- معلومات التحدي
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10) DEFAULT '🎯',
    
    -- المتطلبات
    challenge_type VARCHAR(50) NOT NULL,
    -- أنواع: 'daily_login', 'search_count', 'share_count', 'improve_grade', 'use_feature'
    
    target_value INTEGER NOT NULL, -- الهدف المطلوب
    
    -- المكافأة
    reward_points INTEGER DEFAULT 10,
    
    -- الفترة
    duration_type VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'monthly', 'one_time'
    
    -- الحالة
    is_active BOOLEAN DEFAULT TRUE,
    
    -- التواريخ
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_challenges_is_active ON public.challenges(is_active);
CREATE INDEX IF NOT EXISTS idx_challenges_duration_type ON public.challenges(duration_type);

ALTER TABLE public.challenges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on challenges" ON public.challenges FOR ALL USING (true) WITH CHECK (true);

-- إدخال تحديات افتراضية
INSERT INTO public.challenges (title, description, icon, challenge_type, target_value, reward_points, duration_type) VALUES
('🌅 طائر الصباح', 'استخدم البوت قبل الساعة 8 صباحاً', '🌅', 'early_login', 1, 5, 'daily'),
('🔍 باحث نشط', 'ابحث عن 3 نتائج اليوم', '🔍', 'search_count', 3, 10, 'daily'),
('📤 مُشارك', 'شارك نتيجتك مرة واحدة', '📤', 'share_count', 1, 15, 'weekly'),
('📊 محلل', 'استخدم ميزة التحليل الذكي', '📊', 'use_feature', 1, 10, 'weekly'),
('🔥 مثابر', 'استخدم البوت 7 أيام متتالية', '🔥', 'daily_login', 7, 50, 'weekly'),
('🏆 متفوق', 'احصل على معدل فوق 85%', '🏆', 'improve_grade', 85, 100, 'one_time')
ON CONFLICT DO NOTHING;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                        8. تحديات المستخدمين                                ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.user_challenges (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    challenge_id BIGINT NOT NULL REFERENCES public.challenges(id),
    
    -- التقدم
    current_value INTEGER DEFAULT 0,
    
    -- الحالة
    status VARCHAR(20) DEFAULT 'in_progress',
    -- القيم: 'in_progress', 'completed', 'claimed', 'expired'
    
    -- التواريخ
    started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    completed_at TIMESTAMP WITH TIME ZONE,
    period_start DATE, -- بداية الفترة للتحديات الدورية
    
    UNIQUE(telegram_id, challenge_id, period_start)
);

CREATE INDEX IF NOT EXISTS idx_user_challenges_telegram_id ON public.user_challenges(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_status ON public.user_challenges(status);

ALTER TABLE public.user_challenges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on user_challenges" ON public.user_challenges FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                          9. مستخدمي البوت                                  ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.bot_users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chat_id BIGINT NOT NULL UNIQUE,
    
    -- معلومات المستخدم
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    language_code VARCHAR(10),
    
    -- الحالة
    is_active BOOLEAN DEFAULT TRUE,
    is_blocked BOOLEAN DEFAULT FALSE,
    
    -- الإعدادات
    notifications_enabled BOOLEAN DEFAULT TRUE,
    
    -- التواريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_bot_users_chat_id ON public.bot_users(chat_id);
CREATE INDEX IF NOT EXISTS idx_bot_users_is_active ON public.bot_users(is_active);
CREATE INDEX IF NOT EXISTS idx_bot_users_created_at ON public.bot_users(created_at);

ALTER TABLE public.bot_users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on bot_users" ON public.bot_users FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                       10. ملفات Mini App                                   ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

CREATE TABLE IF NOT EXISTS public.mini_app_profiles (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    student_id VARCHAR(50) NOT NULL,
    
    -- معلومات الطالب
    student_name VARCHAR(255),
    
    -- معلومات Telegram
    telegram_name VARCHAR(255),
    telegram_username VARCHAR(100),
    
    -- الحالة
    is_active BOOLEAN DEFAULT TRUE,
    
    -- الإحصائيات
    last_access TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    
    -- الإعدادات
    settings JSONB DEFAULT '{}',
    
    -- التواريخ
    linked_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mini_app_profiles_telegram_id ON public.mini_app_profiles(telegram_id);
CREATE INDEX IF NOT EXISTS idx_mini_app_profiles_student_id ON public.mini_app_profiles(student_id);

ALTER TABLE public.mini_app_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow all on mini_app_profiles" ON public.mini_app_profiles FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                         دوال التحديث التلقائي                              ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

-- دالة تحديث updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers للتحديث التلقائي
DROP TRIGGER IF EXISTS trigger_user_achievements_updated_at ON public.user_achievements;
CREATE TRIGGER trigger_user_achievements_updated_at
    BEFORE UPDATE ON public.user_achievements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_mini_app_profiles_updated_at ON public.mini_app_profiles;
CREATE TRIGGER trigger_mini_app_profiles_updated_at
    BEFORE UPDATE ON public.mini_app_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                              عروض (Views)                                   ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

-- عرض لوحة الصدارة
CREATE OR REPLACE VIEW public.leaderboard AS
SELECT 
    ua.telegram_id,
    bu.first_name,
    bu.username,
    ua.total_points,
    ua.level,
    array_length(ua.achievements, 1) as achievements_count,
    ua.streak_days,
    ROW_NUMBER() OVER (ORDER BY ua.total_points DESC) as rank
FROM public.user_achievements ua
LEFT JOIN public.bot_users bu ON ua.telegram_id = bu.chat_id
ORDER BY ua.total_points DESC;

-- عرض إحصائيات الاستخدام اليومي
CREATE OR REPLACE VIEW public.daily_usage_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_actions,
    COUNT(DISTINCT telegram_id) as unique_users,
    action,
    COUNT(*) as action_count
FROM public.activity_log
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at), action
ORDER BY date DESC, action_count DESC;


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                            انتهى الملف ✅                                   ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

-- 📋 ملاحظات:
-- 1. جميع الجداول تستخدم RLS (Row Level Security)
-- 2. جميع الجداول لديها فهارس للأعمدة المستخدمة بكثرة
-- 3. التواريخ تستخدم timezone-aware timestamps
-- 4. الـ Triggers تحدث updated_at تلقائياً

-- 🎉 تم إنشاء جميع الجداول بنجاح!
