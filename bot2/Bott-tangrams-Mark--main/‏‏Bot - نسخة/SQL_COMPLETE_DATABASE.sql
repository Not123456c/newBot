-- ══════════════════════════════════════════════════════════════════════════════
-- ██████╗  ██████╗ ████████╗    ███████╗██╗   ██╗██╗     ██╗     
-- ██╔══██╗██╔═══██╗╚══██╔══╝    ██╔════╝██║   ██║██║     ██║     
-- ██████╔╝██║   ██║   ██║       █████╗  ██║   ██║██║     ██║     
-- ██╔══██╗██║   ██║   ██║       ██╔══╝  ██║   ██║██║     ██║     
-- ██████╔╝╚██████╔╝   ██║       ██║     ╚██████╔╝███████╗███████╗
-- ╚═════╝  ╚═════╝    ╚═╝       ╚═╝      ╚═════╝ ╚══════╝╚══════╝
-- ══════════════════════════════════════════════════════════════════════════════
--
-- 🎓 بوت النتائج الجامعية - قاعدة البيانات الكاملة
-- University Results Bot - Complete Database Schema
--
-- 📅 تاريخ الإنشاء: يناير 2026
-- 📌 الإصدار: 2.0 (شامل جميع الجداول)
--
-- ══════════════════════════════════════════════════════════════════════════════
--
-- 📋 فهرس الجداول:
--
-- ═══ الجداول الأساسية (Core Tables) ═══
--   1.  all_marks                 - جدول النتائج والعلامات
--   2.  exam_schedule             - جدول الامتحانات
--   3.  channel_subscriptions     - اشتراكات القناة
--   4.  notification_subscribers  - المشتركين بالإشعارات
--   5.  exam_reminders           - تذكيرات الامتحانات
--   6.  backup_history           - سجل النسخ الاحتياطي
--   7.  usage_statistics         - إحصائيات الاستخدام
--
-- ═══ جداول الإنجازات والنقاط (Achievements & Points) ═══
--   8.  user_achievements        - إنجازات المستخدمين
--   9.  achievement_log          - سجل الإنجازات
--   10. points_log               - سجل النقاط
--   11. challenges               - التحديات
--   12. user_challenges          - تحديات المستخدمين
--
-- ═══ جداول الإعلانات والتحليلات (Announcements & Analytics) ═══
--   13. announcements            - الإعلانات
--   14. activity_log             - سجل النشاطات
--   15. semester_history         - تاريخ الفصول
--
-- ═══ جداول المستخدمين (Users) ═══
--   16. bot_users                - مستخدمي البوت
--   17. mini_app_profiles        - ملفات Mini App
--   18. admin_actions_log        - سجل أفعال المشرفين
--
-- ══════════════════════════════════════════════════════════════════════════════


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                                                                            ║
-- ║                    ═══ الجداول الأساسية (Core) ═══                         ║
-- ║                                                                            ║
-- ╚════════════════════════════════════════════════════════════════════════════╝


-- ══════════════════════════════════════════════════════════════════════════════
-- 1. جدول النتائج والعلامات (all_marks)
-- ══════════════════════════════════════════════════════════════════════════════
-- الجدول الرئيسي لتخزين جميع علامات الطلاب

CREATE TABLE IF NOT EXISTS public.all_marks (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- معلومات الطالب
    student_id VARCHAR(50) NOT NULL,
    student_name VARCHAR(255),
    father_name VARCHAR(255),
    
    -- معلومات المادة
    subject_name VARCHAR(255),
    subject_code VARCHAR(50),
    
    -- الدرجات
    theoretical_grade DECIMAL(5,2),    -- درجة النظري
    practical_grade DECIMAL(5,2),       -- درجة العملي
    midterm_grade DECIMAL(5,2),         -- درجة منتصف الفصل
    final_grade DECIMAL(5,2),           -- درجة النهائي
    total_grade DECIMAL(5,2),           -- المجموع الكلي
    
    -- النتيجة
    result VARCHAR(50),                 -- ناجح/راسب
    
    -- معلومات إضافية
    semester VARCHAR(20),               -- الفصل الدراسي
    academic_year VARCHAR(20),          -- السنة الأكاديمية
    department VARCHAR(100),            -- القسم
    
    -- التواريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- الفهارس
CREATE INDEX IF NOT EXISTS idx_all_marks_student_id ON public.all_marks(student_id);
CREATE INDEX IF NOT EXISTS idx_all_marks_student_name ON public.all_marks(student_name);
CREATE INDEX IF NOT EXISTS idx_all_marks_subject_name ON public.all_marks(subject_name);
CREATE INDEX IF NOT EXISTS idx_all_marks_total_grade ON public.all_marks(total_grade);

-- RLS
ALTER TABLE public.all_marks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on all_marks" ON public.all_marks;
CREATE POLICY "Allow all on all_marks" ON public.all_marks FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 2. جدول الامتحانات (exam_schedule)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.exam_schedule (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- معلومات الامتحان
    subject_name VARCHAR(255) NOT NULL,
    subject_code VARCHAR(50),
    
    -- التوقيت
    exam_date DATE NOT NULL,
    exam_time TIME,
    duration_minutes INTEGER,
    
    -- المكان
    location VARCHAR(255),
    hall VARCHAR(100),
    
    -- معلومات إضافية
    exam_type VARCHAR(50),              -- نهائي/نصفي/عملي
    notes TEXT,
    
    -- المشرف الذي أضافه
    added_by BIGINT,
    
    -- التواريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_exam_schedule_exam_date ON public.exam_schedule(exam_date);
CREATE INDEX IF NOT EXISTS idx_exam_schedule_subject_name ON public.exam_schedule(subject_name);

ALTER TABLE public.exam_schedule ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on exam_schedule" ON public.exam_schedule;
CREATE POLICY "Allow all on exam_schedule" ON public.exam_schedule FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 3. اشتراكات القناة (channel_subscriptions)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.channel_subscriptions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    chat_id BIGINT NOT NULL UNIQUE,
    
    -- حالة الاشتراك
    is_subscribed BOOLEAN DEFAULT FALSE,
    
    -- التذكيرات
    reminder_count INTEGER DEFAULT 0,
    last_reminder TIMESTAMP WITH TIME ZONE,
    
    -- التواريخ
    first_check TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_check TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_channel_subscriptions_chat_id ON public.channel_subscriptions(chat_id);

ALTER TABLE public.channel_subscriptions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on channel_subscriptions" ON public.channel_subscriptions;
CREATE POLICY "Allow all on channel_subscriptions" ON public.channel_subscriptions FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 4. المشتركين بالإشعارات (notification_subscribers)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.notification_subscribers (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- معلومات المشترك
    telegram_id BIGINT NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    
    -- حالة الاشتراك
    is_active BOOLEAN DEFAULT TRUE,
    
    -- للكشف عن التغييرات
    last_results_hash VARCHAR(64),
    
    -- التواريخ
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_notification TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(telegram_id, student_id)
);

CREATE INDEX IF NOT EXISTS idx_notification_subscribers_telegram_id ON public.notification_subscribers(telegram_id);
CREATE INDEX IF NOT EXISTS idx_notification_subscribers_student_id ON public.notification_subscribers(student_id);
CREATE INDEX IF NOT EXISTS idx_notification_subscribers_is_active ON public.notification_subscribers(is_active);

ALTER TABLE public.notification_subscribers ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on notification_subscribers" ON public.notification_subscribers;
CREATE POLICY "Allow all on notification_subscribers" ON public.notification_subscribers FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 5. تذكيرات الامتحانات (exam_reminders)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.exam_reminders (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    telegram_id BIGINT NOT NULL,
    
    -- إعدادات التذكير
    is_active BOOLEAN DEFAULT TRUE,
    reminder_hours INTEGER DEFAULT 24,    -- قبل كم ساعة
    
    -- التواريخ
    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    last_reminder TIMESTAMP WITH TIME ZONE,
    
    UNIQUE(telegram_id)
);

CREATE INDEX IF NOT EXISTS idx_exam_reminders_telegram_id ON public.exam_reminders(telegram_id);
CREATE INDEX IF NOT EXISTS idx_exam_reminders_is_active ON public.exam_reminders(is_active);

ALTER TABLE public.exam_reminders ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on exam_reminders" ON public.exam_reminders;
CREATE POLICY "Allow all on exam_reminders" ON public.exam_reminders FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 6. سجل النسخ الاحتياطي (backup_history)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.backup_history (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- معلومات النسخة
    backup_type VARCHAR(50),              -- 'auto', 'manual'
    file_name VARCHAR(255),
    file_size BIGINT,
    
    -- الإحصائيات
    records_count INTEGER,
    tables_backed_up TEXT[],
    
    -- الحالة
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT,
    
    -- المشرف (للنسخ اليدوي)
    created_by BIGINT,
    
    -- التواريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_backup_history_created_at ON public.backup_history(created_at);

ALTER TABLE public.backup_history ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on backup_history" ON public.backup_history;
CREATE POLICY "Allow all on backup_history" ON public.backup_history FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 7. إحصائيات الاستخدام (usage_statistics)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.usage_statistics (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- التاريخ
    date DATE NOT NULL UNIQUE,
    
    -- إحصائيات المستخدمين
    total_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    
    -- إحصائيات الاستخدام
    total_searches INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    
    -- أكثر الأوقات نشاطاً
    peak_hour INTEGER,
    
    -- التحديث
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_usage_statistics_date ON public.usage_statistics(date);

ALTER TABLE public.usage_statistics ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on usage_statistics" ON public.usage_statistics;
CREATE POLICY "Allow all on usage_statistics" ON public.usage_statistics FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                                                                            ║
-- ║              ═══ جداول الإنجازات والنقاط (Achievements) ═══                ║
-- ║                                                                            ║
-- ╚════════════════════════════════════════════════════════════════════════════╝


-- ══════════════════════════════════════════════════════════════════════════════
-- 8. إنجازات المستخدمين (user_achievements)
-- ══════════════════════════════════════════════════════════════════════════════

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

CREATE INDEX IF NOT EXISTS idx_user_achievements_telegram_id ON public.user_achievements(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_achievements_total_points ON public.user_achievements(total_points DESC);
CREATE INDEX IF NOT EXISTS idx_user_achievements_level ON public.user_achievements(level);

ALTER TABLE public.user_achievements ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on user_achievements" ON public.user_achievements;
CREATE POLICY "Allow all on user_achievements" ON public.user_achievements FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 9. سجل الإنجازات (achievement_log)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.achievement_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    achievement_id VARCHAR(50) NOT NULL,
    points_earned INTEGER DEFAULT 0,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    context JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_achievement_log_telegram_id ON public.achievement_log(telegram_id);
CREATE INDEX IF NOT EXISTS idx_achievement_log_earned_at ON public.achievement_log(earned_at);

ALTER TABLE public.achievement_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on achievement_log" ON public.achievement_log;
CREATE POLICY "Allow all on achievement_log" ON public.achievement_log FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 10. سجل النقاط (points_log)
-- ══════════════════════════════════════════════════════════════════════════════

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
DROP POLICY IF EXISTS "Allow all on points_log" ON public.points_log;
CREATE POLICY "Allow all on points_log" ON public.points_log FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 11. التحديات (challenges)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.challenges (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- معلومات التحدي
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10) DEFAULT '🎯',
    
    -- المتطلبات
    challenge_type VARCHAR(50) NOT NULL,
    target_value INTEGER NOT NULL,
    
    -- المكافأة
    reward_points INTEGER DEFAULT 10,
    
    -- الفترة
    duration_type VARCHAR(20) DEFAULT 'daily',
    
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
DROP POLICY IF EXISTS "Allow all on challenges" ON public.challenges;
CREATE POLICY "Allow all on challenges" ON public.challenges FOR ALL USING (true) WITH CHECK (true);

-- إدخال التحديات الافتراضية
INSERT INTO public.challenges (title, description, icon, challenge_type, target_value, reward_points, duration_type) VALUES
('🌅 طائر الصباح', 'استخدم البوت قبل الساعة 8 صباحاً', '🌅', 'early_login', 1, 5, 'daily'),
('🔍 باحث نشط', 'ابحث عن 3 نتائج اليوم', '🔍', 'search_count', 3, 10, 'daily'),
('📤 مُشارك', 'شارك نتيجتك مرة واحدة', '📤', 'share_count', 1, 15, 'weekly'),
('📊 محلل', 'استخدم ميزة التحليل الذكي', '📊', 'use_feature', 1, 10, 'weekly'),
('🔥 مثابر', 'استخدم البوت 7 أيام متتالية', '🔥', 'daily_login', 7, 50, 'weekly'),
('🏆 متفوق', 'احصل على معدل فوق 85%', '🏆', 'improve_grade', 85, 100, 'one_time')
ON CONFLICT DO NOTHING;


-- ══════════════════════════════════════════════════════════════════════════════
-- 12. تحديات المستخدمين (user_challenges)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.user_challenges (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    challenge_id BIGINT NOT NULL,
    
    -- التقدم
    current_value INTEGER DEFAULT 0,
    
    -- الحالة
    status VARCHAR(20) DEFAULT 'in_progress',
    
    -- التواريخ
    started_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    completed_at TIMESTAMP WITH TIME ZONE,
    period_start DATE,
    
    UNIQUE(telegram_id, challenge_id, period_start)
);

CREATE INDEX IF NOT EXISTS idx_user_challenges_telegram_id ON public.user_challenges(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_challenges_status ON public.user_challenges(status);

ALTER TABLE public.user_challenges ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on user_challenges" ON public.user_challenges;
CREATE POLICY "Allow all on user_challenges" ON public.user_challenges FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                                                                            ║
-- ║          ═══ جداول الإعلانات والتحليلات (Analytics) ═══                    ║
-- ║                                                                            ║
-- ╚════════════════════════════════════════════════════════════════════════════╝


-- ══════════════════════════════════════════════════════════════════════════════
-- 13. الإعلانات (announcements)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.announcements (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- محتوى الإعلان
    content TEXT NOT NULL,
    image_url TEXT,
    
    -- الاستهداف
    target_group VARCHAR(50) DEFAULT 'all',
    
    -- الجدولة
    scheduled_time TIMESTAMP WITH TIME ZONE,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_interval VARCHAR(20),
    
    -- الحالة
    status VARCHAR(20) DEFAULT 'pending',
    
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
DROP POLICY IF EXISTS "Allow all on announcements" ON public.announcements;
CREATE POLICY "Allow all on announcements" ON public.announcements FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 14. سجل النشاطات (activity_log)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.activity_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    
    -- نوع النشاط
    action VARCHAR(50) NOT NULL,
    
    -- تفاصيل إضافية
    details JSONB,
    
    -- معلومات الوقت
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    hour_of_day INTEGER,
    day_of_week INTEGER
);

CREATE INDEX IF NOT EXISTS idx_activity_log_telegram_id ON public.activity_log(telegram_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_action ON public.activity_log(action);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON public.activity_log(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_log_hour ON public.activity_log(hour_of_day);

ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on activity_log" ON public.activity_log;
CREATE POLICY "Allow all on activity_log" ON public.activity_log FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 15. تاريخ الفصول (semester_history)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.semester_history (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    
    -- معلومات الفصل
    semester VARCHAR(20) NOT NULL,
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
DROP POLICY IF EXISTS "Allow all on semester_history" ON public.semester_history;
CREATE POLICY "Allow all on semester_history" ON public.semester_history FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                                                                            ║
-- ║                  ═══ جداول المستخدمين (Users) ═══                          ║
-- ║                                                                            ║
-- ╚════════════════════════════════════════════════════════════════════════════╝


-- ══════════════════════════════════════════════════════════════════════════════
-- 16. مستخدمي البوت (bot_users)
-- ══════════════════════════════════════════════════════════════════════════════

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
DROP POLICY IF EXISTS "Allow all on bot_users" ON public.bot_users;
CREATE POLICY "Allow all on bot_users" ON public.bot_users FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 17. ملفات Mini App (mini_app_profiles)
-- ══════════════════════════════════════════════════════════════════════════════

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
DROP POLICY IF EXISTS "Allow all on mini_app_profiles" ON public.mini_app_profiles;
CREATE POLICY "Allow all on mini_app_profiles" ON public.mini_app_profiles FOR ALL USING (true) WITH CHECK (true);


-- ══════════════════════════════════════════════════════════════════════════════
-- 18. سجل أفعال المشرفين (admin_actions_log)
-- ══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS public.admin_actions_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- المشرف
    admin_id BIGINT NOT NULL,
    admin_name VARCHAR(255),
    
    -- الفعل
    action_type VARCHAR(100) NOT NULL,
    action_details JSONB,
    
    -- الهدف (إن وجد)
    target_user_id BIGINT,
    target_student_id VARCHAR(50),
    
    -- التاريخ
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_admin_actions_log_admin_id ON public.admin_actions_log(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_actions_log_action_type ON public.admin_actions_log(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_actions_log_created_at ON public.admin_actions_log(created_at);

ALTER TABLE public.admin_actions_log ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all on admin_actions_log" ON public.admin_actions_log;
CREATE POLICY "Allow all on admin_actions_log" ON public.admin_actions_log FOR ALL USING (true) WITH CHECK (true);


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                                                                            ║
-- ║                    ═══ الدوال والـ Triggers ═══                            ║
-- ║                                                                            ║
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
DROP TRIGGER IF EXISTS trigger_all_marks_updated_at ON public.all_marks;
CREATE TRIGGER trigger_all_marks_updated_at
    BEFORE UPDATE ON public.all_marks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_exam_schedule_updated_at ON public.exam_schedule;
CREATE TRIGGER trigger_exam_schedule_updated_at
    BEFORE UPDATE ON public.exam_schedule
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_user_achievements_updated_at ON public.user_achievements;
CREATE TRIGGER trigger_user_achievements_updated_at
    BEFORE UPDATE ON public.user_achievements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_mini_app_profiles_updated_at ON public.mini_app_profiles;
CREATE TRIGGER trigger_mini_app_profiles_updated_at
    BEFORE UPDATE ON public.mini_app_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ╔════════════════════════════════════════════════════════════════════════════╗
-- ║                                                                            ║
-- ║                         ═══ العروض (Views) ═══                             ║
-- ║                                                                            ║
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


-- عرض إحصائيات الطلاب
CREATE OR REPLACE VIEW public.student_stats AS
SELECT 
    student_id,
    student_name,
    COUNT(*) as subjects_count,
    AVG(total_grade) as average,
    MAX(total_grade) as highest,
    MIN(total_grade) as lowest,
    SUM(CASE WHEN total_grade >= 60 THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN total_grade < 60 THEN 1 ELSE 0 END) as failed
FROM public.all_marks
WHERE total_grade IS NOT NULL
GROUP BY student_id, student_name;


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
-- ║                                                                            ║
-- ║                            ✅ انتهى الملف                                  ║
-- ║                                                                            ║
-- ╚════════════════════════════════════════════════════════════════════════════╝

-- ══════════════════════════════════════════════════════════════════════════════
-- 📋 ملخص الجداول:
-- ══════════════════════════════════════════════════════════════════════════════
--
--   الجداول الأساسية:     7 جداول
--   جداول الإنجازات:      5 جداول
--   جداول التحليلات:      3 جداول
--   جداول المستخدمين:     3 جداول
--   ─────────────────────────────
--   المجموع:              18 جدول
--
--   + 3 عروض (Views)
--   + 4 Triggers
--   + 1 Function
--
-- ══════════════════════════════════════════════════════════════════════════════
-- 
-- 🎉 تم بنجاح! قاعدة البيانات جاهزة للاستخدام
--
-- ══════════════════════════════════════════════════════════════════════════════
