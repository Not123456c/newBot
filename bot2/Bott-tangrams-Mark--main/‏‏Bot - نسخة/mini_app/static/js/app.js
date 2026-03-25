/**
 * Telegram Mini App - JavaScript
 * بوت النتائج الجامعية
 */

// ══════════════════════════════════════
// المتغيرات العامة
// ══════════════════════════════════════

const API_BASE = '';
let tg = window.Telegram?.WebApp;
let currentUser = null;
let currentProfile = null;
let currentResults = null;
let charts = {};

// ══════════════════════════════════════
// التهيئة
// ══════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    // تهيئة Telegram Web App
    if (tg) {
        tg.ready();
        tg.expand();
        
        // تطبيق ثيم Telegram
        document.body.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
        document.body.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
        document.body.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
        document.body.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');
        document.body.style.setProperty('--tg-theme-button-text-color', tg.themeParams.button_text_color || '#ffffff');
        document.body.style.setProperty('--tg-theme-secondary-bg-color', tg.themeParams.secondary_bg_color || '#f0f0f0');
        
        // الحصول على بيانات المستخدم
        currentUser = tg.initDataUnsafe?.user;
    }
    
    // التحقق من الملف الشخصي
    await checkUserProfile();
    
    // تهيئة الأحداث
    initEventListeners();
});

// ══════════════════════════════════════
// فحص الملف الشخصي
// ══════════════════════════════════════

async function checkUserProfile() {
    const telegramId = currentUser?.id || getStoredTelegramId();
    
    if (!telegramId) {
        showScreen('link-screen');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/user/profile?telegram_id=${telegramId}`);
        const data = await response.json();
        
        if (data.success && data.has_profile) {
            currentProfile = data.profile;
            await loadResults(currentProfile.student_id);
            showScreen('main-screen');
            updateProfileUI();
        } else {
            showScreen('link-screen');
        }
    } catch (error) {
        console.error('Error checking profile:', error);
        showScreen('link-screen');
    }
}

function getStoredTelegramId() {
    return localStorage.getItem('telegram_id');
}

function storeTelegramId(id) {
    localStorage.setItem('telegram_id', id);
}

// ══════════════════════════════════════
// تحميل النتائج
// ══════════════════════════════════════

async function loadResults(studentId) {
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/results/${studentId}`);
        const data = await response.json();
        
        if (data.success) {
            currentResults = data;
            updateResultsUI();
            loadChartData(studentId);
        } else {
            showToast('❌ ' + (data.error || 'خطأ في تحميل النتائج'));
        }
    } catch (error) {
        console.error('Error loading results:', error);
        showToast('❌ خطأ في الاتصال');
    } finally {
        showLoading(false);
    }
}

// ══════════════════════════════════════
// تحديث واجهة المستخدم
// ══════════════════════════════════════

function updateProfileUI() {
    if (!currentProfile) return;
    
    document.getElementById('student-name').textContent = currentProfile.student_name || 'طالب';
    document.getElementById('student-id-display').textContent = currentProfile.student_id;
    document.getElementById('linked-student-id').textContent = currentProfile.student_id;
    
    // تحديث الأفاتار
    const avatar = document.getElementById('user-avatar');
    if (currentUser?.photo_url) {
        avatar.innerHTML = `<img src="${currentUser.photo_url}" style="width:100%;height:100%;border-radius:50%;">`;
    } else {
        const firstLetter = (currentProfile.student_name || 'ط')[0];
        avatar.textContent = firstLetter;
    }
}

function updateResultsUI() {
    if (!currentResults) return;
    
    const { stats, marks, student_name } = currentResults;
    
    // تحديث الإحصائيات
    document.getElementById('average-grade').textContent = stats.average_grade.toFixed(1);
    document.getElementById('passed-count').textContent = stats.passed_subjects;
    document.getElementById('failed-count').textContent = stats.failed_subjects;
    document.getElementById('success-rate').textContent = stats.success_rate + '%';
    
    // تحديث قائمة المواد
    const subjectsList = document.getElementById('subjects-list');
    subjectsList.innerHTML = '';
    
    marks.forEach(mark => {
        const grade = mark.total_grade || 0;
        const passed = parseFloat(grade) >= 60;
        
        const item = document.createElement('div');
        item.className = `subject-item ${passed ? 'passed' : 'failed'}`;
        item.innerHTML = `
            <div class="subject-info">
                <h4>${mark.subject_name || 'مادة'}</h4>
                <p>نظري: ${mark.theoretical_grade || 0} | عملي: ${mark.practical_grade || 0}</p>
            </div>
            <div class="subject-grade">
                <span class="grade ${passed ? 'success' : 'danger'}">${grade}</span>
                <span class="status">${mark.result || (passed ? 'ناجح' : 'راسب')}</span>
            </div>
        `;
        subjectsList.appendChild(item);
    });
}

// ══════════════════════════════════════
// الرسوم البيانية
// ══════════════════════════════════════

async function loadChartData(studentId) {
    try {
        const response = await fetch(`${API_BASE}/api/chart/grades/${studentId}`);
        const data = await response.json();
        
        if (data.success) {
            createCharts(data.chart_data);
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

function createCharts(chartData) {
    // تدمير الرسوم القديمة
    Object.values(charts).forEach(chart => chart?.destroy());
    
    // رسم درجات المواد
    const gradesCtx = document.getElementById('grades-chart').getContext('2d');
    charts.grades = new Chart(gradesCtx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'الدرجة',
                data: chartData.grades,
                backgroundColor: chartData.colors,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
    
    // رسم النظري vs العملي
    const theoryCtx = document.getElementById('theory-practical-chart').getContext('2d');
    charts.theory = new Chart(theoryCtx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'نظري',
                    data: chartData.theoretical,
                    backgroundColor: '#3b82f6',
                    borderRadius: 5
                },
                {
                    label: 'عملي',
                    data: chartData.practical,
                    backgroundColor: '#f59e0b',
                    borderRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
    
    // رسم دائري
    if (currentResults) {
        const pieCtx = document.getElementById('pie-chart').getContext('2d');
        charts.pie = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['ناجح', 'راسب'],
                datasets: [{
                    data: [
                        currentResults.stats.passed_subjects,
                        currentResults.stats.failed_subjects
                    ],
                    backgroundColor: ['#16a34a', '#dc2626']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// ══════════════════════════════════════
// الأوائل
// ══════════════════════════════════════

async function loadTopStudents(count = 10) {
    try {
        const topList = document.getElementById('top-list');
        topList.innerHTML = '<div class="loader" style="margin:auto;"></div>';
        
        const response = await fetch(`${API_BASE}/api/top/${count}`);
        const data = await response.json();
        
        if (data.success && data.top_students.length > 0) {
            topList.innerHTML = '';
            
            data.top_students.forEach((student, index) => {
                const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : '';
                
                const item = document.createElement('div');
                item.className = `top-item ${rankClass}`;
                item.innerHTML = `
                    <div class="rank">${index + 1}</div>
                    <div class="top-info">
                        <h4>${student.student_name}</h4>
                        <p>${student.student_id} • ${student.subjects_count} مادة</p>
                    </div>
                    <div class="top-average">${student.average.toFixed(1)}</div>
                `;
                topList.appendChild(item);
            });
        } else {
            topList.innerHTML = `
                <div class="empty-state">
                    <span>📭</span>
                    <p>لا توجد بيانات</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading top students:', error);
    }
}

// ══════════════════════════════════════
// جدول الامتحانات
// ══════════════════════════════════════

async function loadExams() {
    try {
        const examsList = document.getElementById('exams-list');
        examsList.innerHTML = '<div class="loader" style="margin:auto;"></div>';
        
        const response = await fetch(`${API_BASE}/api/exams`);
        const data = await response.json();
        
        if (data.success && data.exams.length > 0) {
            examsList.innerHTML = '';
            
            data.exams.forEach(exam => {
                const item = document.createElement('div');
                item.className = 'exam-item';
                item.innerHTML = `
                    <h4>📝 ${exam.subject_name}</h4>
                    <div class="exam-details">
                        <span>📅 ${exam.exam_date}</span>
                        <span>⏰ ${exam.exam_time || 'غير محدد'}</span>
                        ${exam.location ? `<span>📍 ${exam.location}</span>` : ''}
                    </div>
                    ${exam.notes ? `<p style="margin-top:8px;font-size:0.85rem;color:var(--tg-theme-hint-color);">${exam.notes}</p>` : ''}
                `;
                examsList.appendChild(item);
            });
        } else {
            examsList.innerHTML = `
                <div class="empty-state">
                    <span>📅</span>
                    <p>لا توجد امتحانات قادمة</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading exams:', error);
        document.getElementById('exams-list').innerHTML = `
            <div class="empty-state">
                <span>⚠️</span>
                <p>خطأ في تحميل الامتحانات</p>
            </div>
        `;
    }
}

// ══════════════════════════════════════
// ربط الحساب
// ══════════════════════════════════════

async function linkAccount(studentId) {
    const telegramId = currentUser?.id || Date.now();
    const telegramName = currentUser?.first_name || '';
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE}/api/user/link`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                telegram_id: telegramId,
                student_id: studentId,
                telegram_name: telegramName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            storeTelegramId(telegramId);
            currentProfile = {
                telegram_id: telegramId,
                student_id: studentId,
                student_name: data.student_name
            };
            
            showToast('✅ تم ربط الحساب بنجاح');
            await loadResults(studentId);
            showScreen('main-screen');
            updateProfileUI();
            
            // إغلاق Mini App مع إرسال بيانات للبوت
            if (tg) {
                tg.sendData(JSON.stringify({
                    action: 'linked',
                    student_id: studentId
                }));
            }
        } else {
            showToast('❌ ' + (data.error || 'فشل في ربط الحساب'));
        }
    } catch (error) {
        console.error('Error linking account:', error);
        showToast('❌ خطأ في الاتصال');
    } finally {
        showLoading(false);
    }
}

async function unlinkAccount() {
    const telegramId = currentUser?.id || getStoredTelegramId();
    
    if (!telegramId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/user/unlink`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ telegram_id: telegramId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            localStorage.removeItem('telegram_id');
            currentProfile = null;
            currentResults = null;
            showToast('✅ تم إلغاء الربط');
            closeModal('settings-modal');
            showScreen('link-screen');
        }
    } catch (error) {
        console.error('Error unlinking:', error);
        showToast('❌ خطأ');
    }
}

// ══════════════════════════════════════
// البحث
// ══════════════════════════════════════

let searchTimeout;

async function searchStudents(query) {
    clearTimeout(searchTimeout);
    
    if (query.length < 2) {
        document.getElementById('search-results').innerHTML = '';
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            const resultsContainer = document.getElementById('search-results');
            
            if (data.success && data.results.length > 0) {
                resultsContainer.innerHTML = data.results.map(r => `
                    <div class="search-result-item" onclick="selectStudent('${r.student_id}', '${r.student_name}')">
                        <strong>${r.student_name}</strong>
                        <br><small>${r.student_id}</small>
                    </div>
                `).join('');
            } else {
                resultsContainer.innerHTML = '<div class="empty-state"><p>لا توجد نتائج</p></div>';
            }
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
}

function selectStudent(studentId, studentName) {
    document.getElementById('student-id-input').value = studentId;
    document.getElementById('search-results').innerHTML = '';
}

// ══════════════════════════════════════
// المشاركة والتصدير
// ══════════════════════════════════════

function shareResults() {
    if (!currentResults) return;
    
    const text = `📊 نتائجي الدراسية
👤 ${currentResults.student_name}
📈 المعدل: ${currentResults.stats.average_grade}%
✅ ناجح في ${currentResults.stats.passed_subjects} مادة
❌ راسب في ${currentResults.stats.failed_subjects} مادة

عبر بوت النتائج الجامعية 🎓`;
    
    if (tg) {
        tg.switchInlineQuery(text, ['users', 'groups', 'channels']);
    } else {
        navigator.clipboard?.writeText(text);
        showToast('✅ تم نسخ النتائج');
    }
}

function downloadPDF() {
    if (!currentProfile) return;
    showToast('📥 جاري تحميل PDF...');
    // سيتم إضافة تحميل PDF لاحقاً
    setTimeout(() => showToast('⚠️ هذه الميزة قيد التطوير'), 1000);
}

// ══════════════════════════════════════
// الأدوات المساعدة
// ══════════════════════════════════════

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId)?.classList.add('active');
}

function showLoading(show) {
    const loadingScreen = document.getElementById('loading-screen');
    if (show) {
        loadingScreen.classList.add('active');
    } else {
        loadingScreen.classList.remove('active');
    }
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function openModal(modalId) {
    document.getElementById(modalId)?.classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId)?.classList.remove('active');
}

// ══════════════════════════════════════
// الأحداث
// ══════════════════════════════════════

function initEventListeners() {
    // ربط الحساب
    document.getElementById('link-btn')?.addEventListener('click', () => {
        const studentId = document.getElementById('student-id-input').value.trim();
        if (studentId) {
            linkAccount(studentId);
        } else {
            showToast('❌ أدخل الرقم الامتحاني');
        }
    });
    
    // البحث
    document.getElementById('search-input')?.addEventListener('input', (e) => {
        searchStudents(e.target.value);
    });
    
    // التبويبات
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            
            tab.classList.add('active');
            const tabId = tab.dataset.tab + '-tab';
            document.getElementById(tabId)?.classList.add('active');
            
            // تحميل البيانات حسب التبويب
            if (tab.dataset.tab === 'top') {
                loadTopStudents(document.getElementById('top-count').value);
            } else if (tab.dataset.tab === 'exams') {
                loadExams();
            }
        });
    });
    
    // اختيار عدد الأوائل
    document.getElementById('top-count')?.addEventListener('change', (e) => {
        loadTopStudents(e.target.value);
    });
    
    // الإعدادات
    document.getElementById('settings-btn')?.addEventListener('click', () => openModal('settings-modal'));
    document.getElementById('close-settings')?.addEventListener('click', () => closeModal('settings-modal'));
    document.getElementById('unlink-btn')?.addEventListener('click', unlinkAccount);
    
    // الأزرار السفلية
    document.getElementById('share-btn')?.addEventListener('click', shareResults);
    document.getElementById('pdf-btn')?.addEventListener('click', downloadPDF);
    document.getElementById('refresh-btn')?.addEventListener('click', () => {
        if (currentProfile) {
            loadResults(currentProfile.student_id);
            showToast('🔄 جاري التحديث...');
        }
    });
    
    // إغلاق النافذة عند الضغط خارجها
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    });
}

// جعل الدوال متاحة عالمياً
window.selectStudent = selectStudent;
