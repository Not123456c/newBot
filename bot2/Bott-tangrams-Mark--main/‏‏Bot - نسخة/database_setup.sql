-- ═══════════════════════════════════════════════════════════════
-- إعداد قاعدة بيانات بوت النتائج الجامعية
-- انسخ هذا الكود وألصقه في SQL Editor الخاص بـ Supabase
-- ═══════════════════════════════════════════════════════════════

-- جدول النتائج الرئيسي (إذا لم يكن موجوداً)
CREATE TABLE IF NOT EXISTS all_marks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    student_id TEXT NOT NULL,
    student_name TEXT,
    father_name TEXT,
    subject_name TEXT,
    theoretical_grade DECIMAL(5,2),
    practical_grade DECIMAL(5,2),
    total_grade DECIMAL(5,2),
    result TEXT,
    rank INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول مستخدمي البوت
CREATE TABLE IF NOT EXISTS bot_users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول اشتراكات القناة
CREATE TABLE IF NOT EXISTS channel_subscriptions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    is_subscribed BOOLEAN DEFAULT FALSE,
    subscription_date TIMESTAMP,
    reminder_count INT DEFAULT 0,
    last_reminder TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول المستخدمين المحظورين
CREATE TABLE IF NOT EXISTS blocked_users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT UNIQUE NOT NULL,
    reason TEXT DEFAULT 'طلبات متتالية',
    blocked_at TIMESTAMP DEFAULT NOW(),
    unblock_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    unblocked_at TIMESTAMP,
    admin_decision TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول حوادث السبام
CREATE TABLE IF NOT EXISTS spam_incidents (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    request_count INT NOT NULL,
    detected_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'pending',
    admin_decision TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول تسجيل الطلبات
CREATE TABLE IF NOT EXISTS request_log (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    request_time TIMESTAMP DEFAULT NOW(),
    request_type TEXT DEFAULT 'search',
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول اشتراكات المستخدمين (للإشعارات)
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    student_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- جدول الدرجات المعروفة (للإشعارات)
CREATE TABLE IF NOT EXISTS known_grades (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    student_id TEXT UNIQUE NOT NULL,
    grades_data JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════
-- الفهارس لتحسين الأداء
-- ═══════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_all_marks_student_id ON all_marks(student_id);
CREATE INDEX IF NOT EXISTS idx_all_marks_student_name ON all_marks(student_name);
CREATE INDEX IF NOT EXISTS idx_all_marks_subject ON all_marks(subject_name);
CREATE INDEX IF NOT EXISTS idx_blocked_users_active ON blocked_users(is_active);
CREATE INDEX IF NOT EXISTS idx_spam_incidents_status ON spam_incidents(status);
CREATE INDEX IF NOT EXISTS idx_request_log_user ON request_log(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_student ON user_subscriptions(student_id);
CREATE INDEX IF NOT EXISTS idx_bot_users_chat ON bot_users(chat_id);
CREATE INDEX IF NOT EXISTS idx_channel_subscriptions_chat ON channel_subscriptions(chat_id);

-- ═══════════════════════════════════════════════════════════════
-- تفعيل Row Level Security (اختياري - للأمان)
-- ═══════════════════════════════════════════════════════════════

-- ALTER TABLE all_marks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE bot_users ENABLE ROW LEVEL SECURITY;

-- ═══════════════════════════════════════════════════════════════
-- انتهى الإعداد ✅
-- ═══════════════════════════════════════════════════════════════
