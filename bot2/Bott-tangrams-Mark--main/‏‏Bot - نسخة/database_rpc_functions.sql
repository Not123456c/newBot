-- ═══════════════════════════════════════════════════════════════
-- دوال RPC للأداء المحسن - Supabase
-- تُستخدم للاستعلامات المعقدة بشكل أسرع
-- ═══════════════════════════════════════════════════════════════

-- دالة جلب أفضل N طلاب مباشرة (أسرع بكثير)
CREATE OR REPLACE FUNCTION get_top_students(limit_n INTEGER DEFAULT 10)
RETURNS TABLE (
    student_id TEXT,
    student_name TEXT,
    average_grade DECIMAL,
    total_subjects BIGINT,
    rank BIGINT
) AS $$
BEGIN
    RETURN QUERY
    WITH student_averages AS (
        SELECT 
            m.student_id,
            m.student_name,
            AVG(m.total_grade) as avg_grade,
            COUNT(*) as subject_count
        FROM all_marks m
        WHERE m.total_grade IS NOT NULL
        GROUP BY m.student_id, m.student_name
    ),
    max_subjects AS (
        SELECT MAX(subject_count) as max_count FROM student_averages
    )
    SELECT 
        sa.student_id,
        sa.student_name,
        ROUND(sa.avg_grade, 2) as average_grade,
        sa.subject_count as total_subjects,
        ROW_NUMBER() OVER (ORDER BY sa.avg_grade DESC) as rank
    FROM student_averages sa, max_subjects ms
    WHERE sa.subject_count = ms.max_count
    ORDER BY sa.avg_grade DESC
    LIMIT limit_n;
END;
$$ LANGUAGE plpgsql;


-- دالة جلب إحصائيات الدفعة
CREATE OR REPLACE FUNCTION get_cohort_stats()
RETURNS TABLE (
    total_students BIGINT,
    total_records BIGINT,
    pass_count BIGINT,
    fail_count BIGINT,
    pass_rate DECIMAL,
    overall_average DECIMAL,
    highest_grade DECIMAL,
    lowest_grade DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT student_id)::BIGINT as total_students,
        COUNT(*)::BIGINT as total_records,
        COUNT(*) FILTER (WHERE total_grade >= 60)::BIGINT as pass_count,
        COUNT(*) FILTER (WHERE total_grade < 60)::BIGINT as fail_count,
        ROUND(COUNT(*) FILTER (WHERE total_grade >= 60) * 100.0 / NULLIF(COUNT(*), 0), 2) as pass_rate,
        ROUND(AVG(total_grade), 2) as overall_average,
        MAX(total_grade) as highest_grade,
        MIN(total_grade) as lowest_grade
    FROM all_marks
    WHERE total_grade IS NOT NULL;
END;
$$ LANGUAGE plpgsql;


-- دالة البحث عن طالب بالرقم
CREATE OR REPLACE FUNCTION search_student_by_id(search_id TEXT)
RETURNS TABLE (
    student_id TEXT,
    student_name TEXT,
    father_name TEXT,
    subject_name TEXT,
    theoretical_grade DECIMAL,
    practical_grade DECIMAL,
    total_grade DECIMAL,
    result TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.student_id,
        m.student_name,
        m.father_name,
        m.subject_name,
        m.theoretical_grade,
        m.practical_grade,
        m.total_grade,
        m.result
    FROM all_marks m
    WHERE m.student_id = search_id
    ORDER BY m.subject_name;
END;
$$ LANGUAGE plpgsql;


-- دالة البحث عن طالب بالاسم
CREATE OR REPLACE FUNCTION search_student_by_name(search_name TEXT, max_results INTEGER DEFAULT 15)
RETURNS TABLE (
    student_id TEXT,
    student_name TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT 
        m.student_id,
        m.student_name
    FROM all_marks m
    WHERE m.student_name ILIKE '%' || search_name || '%'
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;


-- دالة جلب توزيع التقديرات
CREATE OR REPLACE FUNCTION get_grade_distribution()
RETURNS TABLE (
    grade_range TEXT,
    count BIGINT,
    percentage DECIMAL
) AS $$
DECLARE
    total_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO total_count FROM all_marks WHERE total_grade IS NOT NULL;
    
    RETURN QUERY
    SELECT 
        CASE 
            WHEN total_grade >= 90 THEN 'A (90-100)'
            WHEN total_grade >= 80 THEN 'B (80-89)'
            WHEN total_grade >= 70 THEN 'C (70-79)'
            WHEN total_grade >= 60 THEN 'D (60-69)'
            ELSE 'F (< 60)'
        END as grade_range,
        COUNT(*)::BIGINT as count,
        ROUND(COUNT(*) * 100.0 / NULLIF(total_count, 0), 2) as percentage
    FROM all_marks
    WHERE total_grade IS NOT NULL
    GROUP BY grade_range
    ORDER BY 
        CASE grade_range
            WHEN 'A (90-100)' THEN 1
            WHEN 'B (80-89)' THEN 2
            WHEN 'C (70-79)' THEN 3
            WHEN 'D (60-69)' THEN 4
            ELSE 5
        END;
END;
$$ LANGUAGE plpgsql;


-- دالة جلب أفضل طلاب في مادة معينة
CREATE OR REPLACE FUNCTION get_top_in_subject(subject TEXT, limit_n INTEGER DEFAULT 10)
RETURNS TABLE (
    student_id TEXT,
    student_name TEXT,
    total_grade DECIMAL,
    rank BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.student_id,
        m.student_name,
        m.total_grade,
        ROW_NUMBER() OVER (ORDER BY m.total_grade DESC) as rank
    FROM all_marks m
    WHERE m.subject_name = subject
      AND m.total_grade IS NOT NULL
    ORDER BY m.total_grade DESC
    LIMIT limit_n;
END;
$$ LANGUAGE plpgsql;


-- دالة جلب عدد المستخدمين النشطين
CREATE OR REPLACE FUNCTION get_active_users_count()
RETURNS BIGINT AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM bot_users);
END;
$$ LANGUAGE plpgsql;


-- ═══════════════════════════════════════════════════════════════
-- فهارس إضافية للأداء
-- ═══════════════════════════════════════════════════════════════

-- فهرس مركب للبحث السريع
CREATE INDEX IF NOT EXISTS idx_all_marks_student_grade 
ON all_marks(student_id, total_grade);

-- فهرس للبحث بالاسم (case insensitive)
CREATE INDEX IF NOT EXISTS idx_all_marks_student_name_lower 
ON all_marks(LOWER(student_name));

-- فهرس للمادة والدرجة
CREATE INDEX IF NOT EXISTS idx_all_marks_subject_grade 
ON all_marks(subject_name, total_grade DESC);


-- ═══════════════════════════════════════════════════════════════
-- استخدام الدوال (أمثلة)
-- ═══════════════════════════════════════════════════════════════

-- جلب أفضل 10 طلاب:
-- SELECT * FROM get_top_students(10);

-- جلب إحصائيات الدفعة:
-- SELECT * FROM get_cohort_stats();

-- البحث عن طالب:
-- SELECT * FROM search_student_by_id('12345');
-- SELECT * FROM search_student_by_name('أحمد');

-- توزيع التقديرات:
-- SELECT * FROM get_grade_distribution();
