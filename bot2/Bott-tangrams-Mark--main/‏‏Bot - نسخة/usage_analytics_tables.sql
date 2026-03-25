-- ═══════════════════════════════════════════════════════════════
-- جدول إحصائيات الاستخدام
-- انسخ هذا الكود وألصقه في SQL Editor الخاص بـ Supabase
-- ═══════════════════════════════════════════════════════════════

-- جدول تسجيل الاستخدام الرئيسي
CREATE TABLE IF NOT EXISTS usage_analytics (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    username TEXT,
    first_name TEXT,
    action_type TEXT NOT NULL,
    action_details JSONB,
    hour_of_day INTEGER,
    day_of_week INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- فهارس للأداء السريع
CREATE INDEX IF NOT EXISTS idx_usage_user ON usage_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_action ON usage_analytics(action_type);
CREATE INDEX IF NOT EXISTS idx_usage_date ON usage_analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_usage_hour ON usage_analytics(hour_of_day);
CREATE INDEX IF NOT EXISTS idx_usage_day ON usage_analytics(day_of_week);

-- فهرس مركب للاستعلامات الشائعة
CREATE INDEX IF NOT EXISTS idx_usage_user_date ON usage_analytics(user_id, created_at DESC);


-- ═══════════════════════════════════════════════════════════════
-- دوال RPC للإحصائيات السريعة
-- ═══════════════════════════════════════════════════════════════

-- إحصائيات اليوم
CREATE OR REPLACE FUNCTION get_today_usage_stats()
RETURNS TABLE (
    total_requests BIGINT,
    unique_users BIGINT,
    avg_per_user DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_requests,
        COUNT(DISTINCT user_id)::BIGINT as unique_users,
        ROUND(COUNT(*)::DECIMAL / NULLIF(COUNT(DISTINCT user_id), 0), 2) as avg_per_user
    FROM usage_analytics
    WHERE created_at >= CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;


-- أكثر المستخدمين نشاطاً
CREATE OR REPLACE FUNCTION get_top_active_users(days_back INTEGER DEFAULT 7, limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    user_id BIGINT,
    username TEXT,
    first_name TEXT,
    request_count BIGINT,
    rank BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.user_id,
        MAX(u.username) as username,
        MAX(u.first_name) as first_name,
        COUNT(*)::BIGINT as request_count,
        ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC)::BIGINT as rank
    FROM usage_analytics u
    WHERE u.created_at >= CURRENT_DATE - days_back
    GROUP BY u.user_id
    ORDER BY request_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;


-- أوقات الذروة
CREATE OR REPLACE FUNCTION get_peak_hours(days_back INTEGER DEFAULT 7)
RETURNS TABLE (
    hour_of_day INTEGER,
    request_count BIGINT,
    percentage DECIMAL
) AS $$
DECLARE
    total_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO total_count 
    FROM usage_analytics 
    WHERE created_at >= CURRENT_DATE - days_back;
    
    RETURN QUERY
    SELECT 
        u.hour_of_day,
        COUNT(*)::BIGINT as request_count,
        ROUND(COUNT(*) * 100.0 / NULLIF(total_count, 0), 2) as percentage
    FROM usage_analytics u
    WHERE u.created_at >= CURRENT_DATE - days_back
    GROUP BY u.hour_of_day
    ORDER BY request_count DESC;
END;
$$ LANGUAGE plpgsql;


-- إحصائيات الأوامر
CREATE OR REPLACE FUNCTION get_command_usage_stats(days_back INTEGER DEFAULT 7)
RETURNS TABLE (
    action_type TEXT,
    request_count BIGINT,
    percentage DECIMAL
) AS $$
DECLARE
    total_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO total_count 
    FROM usage_analytics 
    WHERE created_at >= CURRENT_DATE - days_back;
    
    RETURN QUERY
    SELECT 
        u.action_type,
        COUNT(*)::BIGINT as request_count,
        ROUND(COUNT(*) * 100.0 / NULLIF(total_count, 0), 2) as percentage
    FROM usage_analytics u
    WHERE u.created_at >= CURRENT_DATE - days_back
    GROUP BY u.action_type
    ORDER BY request_count DESC;
END;
$$ LANGUAGE plpgsql;


-- الاتجاه اليومي
CREATE OR REPLACE FUNCTION get_daily_trend(days_back INTEGER DEFAULT 7)
RETURNS TABLE (
    date DATE,
    total_requests BIGINT,
    unique_users BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(u.created_at) as date,
        COUNT(*)::BIGINT as total_requests,
        COUNT(DISTINCT u.user_id)::BIGINT as unique_users
    FROM usage_analytics u
    WHERE u.created_at >= CURRENT_DATE - days_back
    GROUP BY DATE(u.created_at)
    ORDER BY date DESC;
END;
$$ LANGUAGE plpgsql;


-- سجل مستخدم معين
CREATE OR REPLACE FUNCTION get_user_usage_history(p_user_id BIGINT, limit_count INTEGER DEFAULT 20)
RETURNS TABLE (
    id BIGINT,
    action_type TEXT,
    action_details JSONB,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.action_type,
        u.action_details,
        u.created_at
    FROM usage_analytics u
    WHERE u.user_id = p_user_id
    ORDER BY u.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;


-- تقرير شامل سريع
CREATE OR REPLACE FUNCTION get_full_usage_report(days_back INTEGER DEFAULT 7)
RETURNS TABLE (
    metric_name TEXT,
    metric_value TEXT
) AS $$
DECLARE
    total_req BIGINT;
    unique_usr BIGINT;
    top_user_name TEXT;
    top_command TEXT;
    peak_hour INTEGER;
BEGIN
    -- إجمالي الطلبات
    SELECT COUNT(*) INTO total_req FROM usage_analytics WHERE created_at >= CURRENT_DATE - days_back;
    
    -- المستخدمين الفريدين
    SELECT COUNT(DISTINCT user_id) INTO unique_usr FROM usage_analytics WHERE created_at >= CURRENT_DATE - days_back;
    
    -- أكثر مستخدم نشاط
    SELECT COALESCE(first_name, username, user_id::TEXT) INTO top_user_name
    FROM usage_analytics
    WHERE created_at >= CURRENT_DATE - days_back
    GROUP BY user_id, first_name, username
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    
    -- أكثر أمر استخدام
    SELECT action_type INTO top_command
    FROM usage_analytics
    WHERE created_at >= CURRENT_DATE - days_back
    GROUP BY action_type
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    
    -- ساعة الذروة
    SELECT hour_of_day INTO peak_hour
    FROM usage_analytics
    WHERE created_at >= CURRENT_DATE - days_back
    GROUP BY hour_of_day
    ORDER BY COUNT(*) DESC
    LIMIT 1;
    
    RETURN QUERY VALUES
        ('إجمالي الطلبات', total_req::TEXT),
        ('المستخدمين الفريدين', unique_usr::TEXT),
        ('متوسط لكل مستخدم', ROUND(total_req::DECIMAL / NULLIF(unique_usr, 0), 2)::TEXT),
        ('أكثر مستخدم نشاطاً', top_user_name),
        ('أكثر أمر استخداماً', top_command),
        ('ساعة الذروة', peak_hour::TEXT || ':00');
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════
-- جدول ملخص يومي (للأرشيف)
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS usage_daily_summary (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    date DATE UNIQUE NOT NULL,
    total_requests INTEGER DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    top_user_id BIGINT,
    top_command TEXT,
    peak_hour INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- دالة لحفظ ملخص اليوم (تُشغّل نهاية كل يوم)
CREATE OR REPLACE FUNCTION save_daily_summary()
RETURNS void AS $$
DECLARE
    yesterday DATE := CURRENT_DATE - 1;
    total_req INTEGER;
    unique_usr INTEGER;
    top_usr BIGINT;
    top_cmd TEXT;
    peak_hr INTEGER;
BEGIN
    -- حساب الإحصائيات
    SELECT COUNT(*), COUNT(DISTINCT user_id) INTO total_req, unique_usr
    FROM usage_analytics
    WHERE DATE(created_at) = yesterday;
    
    SELECT user_id INTO top_usr
    FROM usage_analytics WHERE DATE(created_at) = yesterday
    GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 1;
    
    SELECT action_type INTO top_cmd
    FROM usage_analytics WHERE DATE(created_at) = yesterday
    GROUP BY action_type ORDER BY COUNT(*) DESC LIMIT 1;
    
    SELECT hour_of_day INTO peak_hr
    FROM usage_analytics WHERE DATE(created_at) = yesterday
    GROUP BY hour_of_day ORDER BY COUNT(*) DESC LIMIT 1;
    
    -- حفظ الملخص
    INSERT INTO usage_daily_summary (date, total_requests, unique_users, top_user_id, top_command, peak_hour)
    VALUES (yesterday, total_req, unique_usr, top_usr, top_cmd, peak_hr)
    ON CONFLICT (date) DO UPDATE SET
        total_requests = EXCLUDED.total_requests,
        unique_users = EXCLUDED.unique_users,
        top_user_id = EXCLUDED.top_user_id,
        top_command = EXCLUDED.top_command,
        peak_hour = EXCLUDED.peak_hour;
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════
-- أمثلة الاستخدام:
-- ═══════════════════════════════════════════════════════════════

-- إحصائيات اليوم
-- SELECT * FROM get_today_usage_stats();

-- أكثر 10 مستخدمين نشاطاً في آخر 7 أيام
-- SELECT * FROM get_top_active_users(7, 10);

-- أوقات الذروة
-- SELECT * FROM get_peak_hours(7);

-- إحصائيات الأوامر
-- SELECT * FROM get_command_usage_stats(7);

-- الاتجاه اليومي
-- SELECT * FROM get_daily_trend(7);

-- تقرير شامل
-- SELECT * FROM get_full_usage_report(7);
