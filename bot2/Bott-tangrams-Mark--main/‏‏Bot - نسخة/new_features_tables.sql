-- ═══════════════════════════════════════════════════════════════
-- الجداول الجديدة للميزات المضافة
-- انسخ هذا الكود وألصقه في SQL Editor الخاص بـ Supabase
-- ═══════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════
-- 1. جدول مشتركي الإشعارات الفورية (/notify)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS notification_subscribers (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    student_id TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP DEFAULT NOW(),
    unsubscribed_at TIMESTAMP,
    last_results_hash TEXT,
    last_notification TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- فهرس للبحث السريع
CREATE INDEX IF NOT EXISTS idx_notify_subs_active 
ON notification_subscribers(is_active) WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_notify_subs_student 
ON notification_subscribers(student_id);


-- ═══════════════════════════════════════════════════════════════
-- 2. جدول جدول الامتحانات
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS exam_schedule (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    subject_name TEXT NOT NULL,
    exam_date DATE NOT NULL,
    exam_time TIME,
    location TEXT,
    duration_minutes INTEGER,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    created_by BIGINT
);

-- فهرس للبحث حسب التاريخ
CREATE INDEX IF NOT EXISTS idx_exam_schedule_date 
ON exam_schedule(exam_date);

CREATE INDEX IF NOT EXISTS idx_exam_schedule_subject 
ON exam_schedule(subject_name);


-- ═══════════════════════════════════════════════════════════════
-- 3. جدول مشتركي تذكيرات الامتحانات
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS exam_reminder_subscribers (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    subscribed_at TIMESTAMP DEFAULT NOW(),
    unsubscribed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exam_remind_active 
ON exam_reminder_subscribers(is_active) WHERE is_active = TRUE;


-- ═══════════════════════════════════════════════════════════════
-- 4. جدول الإشعارات المرسلة (للتتبع)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS sent_notifications (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id BIGINT NOT NULL,
    notification_type TEXT NOT NULL, -- 'result', 'exam_reminder', 'broadcast'
    content TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    status TEXT DEFAULT 'sent' -- 'sent', 'failed', 'delivered'
);

CREATE INDEX IF NOT EXISTS idx_sent_notif_chat 
ON sent_notifications(chat_id);

CREATE INDEX IF NOT EXISTS idx_sent_notif_type 
ON sent_notifications(notification_type);


-- ═══════════════════════════════════════════════════════════════
-- 5. جدول الرسائل الجماعية (Broadcast)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS broadcast_messages (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    message_text TEXT NOT NULL,
    sent_by BIGINT,
    total_recipients INTEGER DEFAULT 0,
    successful_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending', -- 'pending', 'sending', 'completed', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);


-- ═══════════════════════════════════════════════════════════════
-- 6. جدول سجل الأنشطة (Admin Activity Log)
-- ═══════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS admin_activity_log (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    admin_id BIGINT NOT NULL,
    action_type TEXT NOT NULL, -- 'add_exam', 'delete_exam', 'broadcast', 'block_user', etc.
    action_details JSONB,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_log_admin 
ON admin_activity_log(admin_id);

CREATE INDEX IF NOT EXISTS idx_admin_log_action 
ON admin_activity_log(action_type);


-- ═══════════════════════════════════════════════════════════════
-- 7. دالة RPC للإحصائيات السريعة (للوحة التحكم)
-- ═══════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION get_dashboard_stats()
RETURNS TABLE (
    total_students BIGINT,
    bot_users BIGINT,
    notify_subscribers BIGINT,
    exam_reminders BIGINT,
    blocked_users BIGINT,
    upcoming_exams BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(DISTINCT student_id) FROM all_marks)::BIGINT as total_students,
        (SELECT COUNT(*) FROM bot_users)::BIGINT as bot_users,
        (SELECT COUNT(*) FROM notification_subscribers WHERE is_active = TRUE)::BIGINT as notify_subscribers,
        (SELECT COUNT(*) FROM exam_reminder_subscribers WHERE is_active = TRUE)::BIGINT as exam_reminders,
        (SELECT COUNT(*) FROM blocked_users WHERE is_active = TRUE)::BIGINT as blocked_users,
        (SELECT COUNT(*) FROM exam_schedule WHERE exam_date >= CURRENT_DATE AND is_active = TRUE)::BIGINT as upcoming_exams;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════
-- 8. دالة لجلب الامتحانات القادمة
-- ═══════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION get_upcoming_exams(days_ahead INTEGER DEFAULT 30)
RETURNS TABLE (
    id BIGINT,
    subject_name TEXT,
    exam_date DATE,
    exam_time TIME,
    location TEXT,
    duration_minutes INTEGER,
    notes TEXT,
    days_until INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.subject_name,
        e.exam_date,
        e.exam_time,
        e.location,
        e.duration_minutes,
        e.notes,
        (e.exam_date - CURRENT_DATE)::INTEGER as days_until
    FROM exam_schedule e
    WHERE e.exam_date >= CURRENT_DATE 
      AND e.exam_date <= CURRENT_DATE + days_ahead
      AND e.is_active = TRUE
    ORDER BY e.exam_date, e.exam_time;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════
-- أمثلة على إضافة بيانات تجريبية (اختياري)
-- ═══════════════════════════════════════════════════════════════

-- إضافة امتحانات تجريبية
-- INSERT INTO exam_schedule (subject_name, exam_date, exam_time, location, duration_minutes, notes)
-- VALUES 
--     ('الرياضيات', '2026-02-01', '09:00', 'قاعة 101', 120, 'الامتحان النهائي'),
--     ('الفيزياء', '2026-02-03', '10:00', 'قاعة 102', 90, NULL),
--     ('الكيمياء', '2026-02-05', '08:30', 'قاعة 103', 120, 'يُسمح بالآلة الحاسبة');


-- ═══════════════════════════════════════════════════════════════
-- ملخص الجداول الجديدة:
-- ═══════════════════════════════════════════════════════════════
-- 
-- 1. notification_subscribers - مشتركي الإشعارات الفورية
-- 2. exam_schedule - جدول الامتحانات
-- 3. exam_reminder_subscribers - مشتركي تذكيرات الامتحانات
-- 4. sent_notifications - سجل الإشعارات المرسلة
-- 5. broadcast_messages - الرسائل الجماعية
-- 6. admin_activity_log - سجل أنشطة المسؤولين
--
-- الدوال:
-- - get_dashboard_stats() - إحصائيات لوحة التحكم
-- - get_upcoming_exams(days) - الامتحانات القادمة
--
-- ═══════════════════════════════════════════════════════════════
