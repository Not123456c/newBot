// ══════════════════════════════════════════════════════════
// 🎓 بوت النتائج الجامعية - Mini App (نسخة محسّنة)
// ══════════════════════════════════════════════════════════

const API_BASE = window.location.origin;
const tg = window.Telegram.WebApp;

// حالة التطبيق
let currentUser = null;
let currentProfile = null;
let currentResults = null;
let chartsInstances = {};

// ══════════════════════════════════════════════════════════
// 🎨 إدارة شاشات التحميل بشكل صحيح
// ══════════════════════════════════════════════════════════

function showLoading(show = true) {
    const loadingScreen = document.getElementById('loading-screen');
    if (show) {
        loadingScreen.classList.add('active');
        loadingScreen.style.display = 'flex';
    } else {
        loadingScreen.classList.remove('active');
        // إخفاء بعد animation
        setTimeout(() => {
            loadingScreen.style.display = 'none';
        }, 300);
    }
}

function showScreen(screenId) {
    // إخفاء جميع الشاشات
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
        screen.style.display = 'none';
    });
    
    // إظهار الشاشة المطلوبة
    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.style.display = 'block';
        setTimeout(() => {
            targetScreen.classList.add('active');
        }, 10);
    }
    
    // إخفاء loading screen دائماً
    showLoading(false);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ══════════════════════════════════════════════════════════
// 🚀 التهيئة الأولية
// ══════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 تطبيق Mini App بدأ التحميل...');
    
    try {
        // تهيئة Telegram
        tg.ready();
        tg.expand();
        
        // تطبيق الثيم
        applyTelegramTheme();
        
        // جلب معلومات المستخدم
        currentUser = tg.initDataUnsafe?.user;
        console.log('👤 المستخدم:', currentUser);
        
        // تهيئة الأحداث
        initializeEventListeners();
        
        // التحقق من وجود حساب مرتبط
        const savedStudentId = localStorage.getItem('student_id');
        
        if (savedStudentId) {
            // إذا كان هناك حساب محفوظ، حاول تحميله
            console.log('💾 حساب محفوظ موجود');
            await checkUserProfile();
        } else {
            // إذا لم يكن هناك حساب، اعرض شاشة الربط مباشرة
            console.log('📝 لا يوجد حساب محفوظ - عرض شاشة الربط');
            showScreen('link-screen');
        }
        
    } catch (error) {
        console.error('❌ خطأ في التهيئة:', error);
        showToast('حدث خطأ في تحميل التطبيق', 'error');
        showScreen('link-screen');
    }
});

// ══════════════════════════════════════════════════════════
// 🎨 تطبيق ثيم Telegram
// ══════════════════════════════════════════════════════════

function applyTelegramTheme() {
    try {
        const root = document.documentElement;
        const theme = tg.themeParams;
        
        if (theme.bg_color) root.style.setProperty('--tg-bg', theme.bg_color);
        if (theme.text_color) root.style.setProperty('--tg-text', theme.text_color);
        if (theme.button_color) root.style.setProperty('--tg-button', theme.button_color);
        if (theme.button_text_color) root.style.setProperty('--tg-button-text', theme.button_text_color);
        
        console.log('✅ تم تطبيق ثيم Telegram');
    } catch (error) {
        console.log('⚠️ تعذر تطبيق الثيم:', error);
    }
}

// ══════════════════════════════════════════════════════════
// 📝 تهيئة الأحداث
// ══════════════════════════════════════════════════════════

function initializeEventListeners() {
    // ربط الحساب
    const linkBtn = document.getElementById('link-btn');
    const studentIdInput = document.getElementById('student-id-input');
    
    if (linkBtn) {
        linkBtn.addEventListener('click', linkAccount);
    }
    
    if (studentIdInput) {
        studentIdInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') linkAccount();
        });
    }
    
    // البحث بالاسم
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => searchByName(e.target.value), 500);
        });
    }
    
    // التبويبات
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // الإعدادات
    const settingsBtn = document.getElementById('settings-btn');
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => showToast('الإعدادات قريباً', 'info'));
    }
    
    // أزرار المشاركة
    const shareBtn = document.getElementById('share-btn');
    const pdfBtn = document.getElementById('pdf-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    
    if (shareBtn) {
        shareBtn.addEventListener('click', shareAsImage);
    }
    
    if (pdfBtn) {
        pdfBtn.addEventListener('click', downloadAsPDF);
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshResults);
    }
    
    console.log('✅ تم تهيئة الأحداث');
}

// ══════════════════════════════════════════════════════════
// 👤 التحقق من الملف الشخصي
// ══════════════════════════════════════════════════════════

async function checkUserProfile() {
    const telegramId = currentUser?.id || getStoredTelegramId();
    
    if (!telegramId) {
        console.log('❌ لا يوجد telegram_id');
        showScreen('link-screen');
        return;
    }
    
    console.log('✅ التحقق من الملف الشخصي:', telegramId);
    showLoading(true);
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        
        const response = await fetch(`${API_BASE}/api/user/profile?telegram_id=${telegramId}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        console.log('📡 API Response:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📦 البيانات:', data);
        
        if (data.success && data.has_profile) {
            currentProfile = data.profile;
            console.log('✅ تم العثور على الملف الشخصي');
            
            // حفظ في localStorage
            localStorage.setItem('student_id', currentProfile.student_id);
            localStorage.setItem('student_name', currentProfile.student_name);
            
            await loadResults(currentProfile.student_id);
            showScreen('main-screen');
            updateProfileUI();
        } else {
            console.log('ℹ️ لا يوجد ملف شخصي');
            showScreen('link-screen');
        }
    } catch (error) {
        console.error('❌ خطأ:', error);
        
        // Fallback: استخدام البيانات المحفوظة
        const savedStudentId = localStorage.getItem('student_id');
        if (savedStudentId) {
            console.log('💾 استخدام البيانات المحفوظة');
            showToast('⚠️ وضع عدم الاتصال', 'warning');
            
            currentProfile = {
                telegram_id: telegramId,
                student_id: savedStudentId,
                student_name: localStorage.getItem('student_name') || 'طالب'
            };
            
            await loadResults(savedStudentId);
            showScreen('main-screen');
            updateProfileUI();
        } else {
            showScreen('link-screen');
        }
    }
}

// ══════════════════════════════════════════════════════════
// 🔗 ربط الحساب
// ══════════════════════════════════════════════════════════

async function linkAccount() {
    const studentIdInput = document.getElementById('student-id-input');
    const studentId = studentIdInput.value.trim();
    
    if (!studentId) {
        showToast('⚠️ الرجاء إدخال الرقم الامتحاني', 'warning');
        return;
    }
    
    const telegramId = currentUser?.id || Date.now();
    
    console.log('🔗 ربط الحساب:', { studentId, telegramId });
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/user/link`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ telegram_id: telegramId, student_id: studentId })
        });
        
        const data = await response.json();
        console.log('📡 استجابة الربط:', data);
        
        if (data.success) {
            storeTelegramId(telegramId);
            localStorage.setItem('student_id', studentId);
            localStorage.setItem('student_name', data.student_name || 'طالب');
            
            currentProfile = {
                telegram_id: telegramId,
                student_id: studentId,
                student_name: data.student_name
            };
            
            showToast('✅ تم ربط الحساب بنجاح', 'success');
            await loadResults(studentId);
            showScreen('main-screen');
            updateProfileUI();
        } else {
            showLoading(false);
            showToast('❌ ' + (data.error || 'فشل الربط'), 'error');
        }
    } catch (error) {
        console.error('❌ خطأ في الربط:', error);
        showLoading(false);
        showToast('❌ خطأ في الاتصال', 'error');
    }
}

// ══════════════════════════════════════════════════════════
// 📊 تحميل النتائج (محسّن)
// ══════════════════════════════════════════════════════════

async function loadResults(studentId) {
    console.log('📊 تحميل النتائج للطالب:', studentId);
    showLoading(true);
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        const response = await fetch(`${API_BASE}/api/results/${studentId}`, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ النتائج:', data);
        
        if (data.success) {
            currentResults = data;
            
            // حفظ في localStorage
            localStorage.setItem('cached_results', JSON.stringify(data));
            localStorage.setItem('cached_time', Date.now().toString());
            
            updateResultsUI();
            loadChartData(studentId);
            loadTopStudents(); // تحميل الأوائل
            
            showLoading(false);
        } else {
            throw new Error(data.error || 'لا توجد نتائج');
        }
    } catch (error) {
        console.error('❌ خطأ في تحميل النتائج:', error);
        showLoading(false);
        
        // Fallback: استخدام البيانات المحفوظة
        tryLoadCachedResults();
    }
}

function tryLoadCachedResults() {
    try {
        const cached = localStorage.getItem('cached_results');
        const cachedTime = localStorage.getItem('cached_time');
        
        if (cached) {
            const data = JSON.parse(cached);
            const age = Date.now() - parseInt(cachedTime || '0');
            const ageHours = Math.floor(age / (1000 * 60 * 60));
            
            currentResults = data;
            updateResultsUI();
            
            if (data.stats) {
                loadChartData(null, data);
            }
            
            showToast(`📂 بيانات محفوظة (منذ ${ageHours} ساعة)`, 'info');
            console.log('✅ تم تحميل البيانات المحفوظة');
        } else {
            showToast('❌ لا توجد بيانات', 'error');
        }
    } catch (error) {
        console.error('❌ خطأ:', error);
        showToast('❌ خطأ في تحميل البيانات', 'error');
    }
}

// ══════════════════════════════════════════════════════════
// 🎨 تحديث واجهة النتائج
// ══════════════════════════════════════════════════════════

function updateResultsUI() {
    if (!currentResults) return;
    
    const { stats, marks } = currentResults;
    
    // تحديث الإحصائيات الرئيسية
    document.getElementById('average-grade').textContent = stats.average.toFixed(1) + '%';
    document.getElementById('passed-count').textContent = stats.passed;
    document.getElementById('failed-count').textContent = stats.failed;
    document.getElementById('success-rate').textContent = stats.success_rate.toFixed(1) + '%';
    
    // تحديث قائمة المواد
    const subjectsList = document.getElementById('subjects-list');
    subjectsList.innerHTML = '';
    
    marks.forEach((mark, index) => {
        const subjectCard = document.createElement('div');
        subjectCard.className = 'subject-card';
        
        const passed = (mark.total_grade || 0) >= 60;
        const gradeClass = passed ? 'success' : 'danger';
        
        subjectCard.innerHTML = `
            <div class="subject-header">
                <span class="subject-number">${index + 1}</span>
                <h3 class="subject-name">${mark.subject_name || 'مادة'}</h3>
                <span class="grade-badge ${gradeClass}">${mark.total_grade || 0}</span>
            </div>
            <div class="grade-details">
                <div class="grade-item">
                    <span class="label">نظري:</span>
                    <span class="value">${mark.theoretical_grade || 0}</span>
                </div>
                <div class="grade-item">
                    <span class="label">عملي:</span>
                    <span class="value">${mark.practical_grade || 0}</span>
                </div>
                <div class="grade-item">
                    <span class="label">النتيجة:</span>
                    <span class="value ${gradeClass}">${mark.result || 'غير محدد'}</span>
                </div>
            </div>
        `;
        
        subjectsList.appendChild(subjectCard);
    });
    
    console.log('✅ تم تحديث واجهة النتائج');
}

function updateProfileUI() {
    if (!currentProfile) return;
    
    document.getElementById('student-name').textContent = currentProfile.student_name || 'طالب';
    document.getElementById('student-id-display').textContent = currentProfile.student_id || '';
    
    // تحديث الأفاتار
    const avatar = document.getElementById('user-avatar');
    if (currentUser?.first_name) {
        avatar.textContent = currentUser.first_name.charAt(0).toUpperCase();
    }
    
    console.log('✅ تم تحديث الملف الشخصي');
}

// ══════════════════════════════════════════════════════════
// 🏆 تحميل الأوائل (محسّن ومصلّح)
// ══════════════════════════════════════════════════════════

async function loadTopStudents() {
    console.log('🏆 تحميل قائمة الأوائل...');
    
    try {
        const response = await fetch(`${API_BASE}/api/top-students`);
        const data = await response.json();
        
        console.log('📊 بيانات الأوائل:', data);
        
        if (data.success && data.students) {
            displayTopStudents(data.students);
        } else {
            throw new Error(data.error || 'فشل تحميل الأوائل');
        }
    } catch (error) {
        console.error('❌ خطأ في تحميل الأوائل:', error);
        document.getElementById('top-list').innerHTML = `
            <div class="empty-state">
                <p>❌ تعذر تحميل قائمة الأوائل</p>
                <p class="error-detail">${error.message}</p>
            </div>
        `;
    }
}

function displayTopStudents(students) {
    const topList = document.getElementById('top-list');
    topList.innerHTML = '';
    
    if (!students || students.length === 0) {
        topList.innerHTML = `
            <div class="empty-state">
                <p>📭 لا توجد بيانات</p>
            </div>
        `;
        return;
    }
    
    const medals = ['🥇', '🥈', '🥉'];
    
    students.forEach((student, index) => {
        const medal = medals[index] || '🏅';
        const rank = index + 1;
        
        const studentCard = document.createElement('div');
        studentCard.className = 'top-student-card';
        if (index < 3) studentCard.classList.add(`rank-${rank}`);
        
        // استخدام average بدلاً من avg
        const average = student.average || student.avg || 0;
        
        studentCard.innerHTML = `
            <div class="rank-badge">${medal} ${rank}</div>
            <div class="student-info">
                <h4>${student.name || student.student_name || 'طالب'}</h4>
                <p class="student-id-small">${student.student_id || ''}</p>
            </div>
            <div class="student-average">${average.toFixed(1)}%</div>
        `;
        
        topList.appendChild(studentCard);
    });
    
    console.log(`✅ تم عرض ${students.length} طالب في قائمة الأوائل`);
}

// ══════════════════════════════════════════════════════════
// 📈 الرسوم البيانية (محسّن)
// ══════════════════════════════════════════════════════════

async function loadChartData(studentId, cachedData = null) {
    console.log('📈 تحميل بيانات الرسوم...');
    
    try {
        let data;
        
        if (cachedData && cachedData.marks) {
            data = { success: true, chart_data: prepareChartDataFromResults(cachedData) };
        } else if (studentId) {
            const response = await fetch(`${API_BASE}/api/chart/grades/${studentId}`);
            data = await response.json();
        } else if (currentResults) {
            data = { success: true, chart_data: prepareChartDataFromResults(currentResults) };
        } else {
            return;
        }
        
        if (data && data.success && data.chart_data) {
            createCharts(data.chart_data);
        }
    } catch (error) {
        console.error('❌ خطأ في الرسوم:', error);
        if (currentResults) {
            const chartData = prepareChartDataFromResults(currentResults);
            createCharts(chartData);
        }
    }
}

function prepareChartDataFromResults(results) {
    const chartData = {
        labels: [],
        grades: [],
        theoretical: [],
        practical: [],
        colors: []
    };
    
    if (!results || !results.marks) return chartData;
    
    results.marks.forEach(m => {
        chartData.labels.push((m.subject_name || '').substring(0, 15));
        chartData.grades.push(parseFloat(m.total_grade) || 0);
        chartData.theoretical.push(parseFloat(m.theoretical_grade) || 0);
        chartData.practical.push(parseFloat(m.practical_grade) || 0);
        
        const grade = parseFloat(m.total_grade) || 0;
        chartData.colors.push(grade >= 60 ? '#10b981' : '#ef4444');
    });
    
    return chartData;
}

function createCharts(chartData) {
    // تدمير الرسوم القديمة
    Object.values(chartsInstances).forEach(chart => chart.destroy());
    chartsInstances = {};
    
    // رسم بياني للدرجات
    const ctx1 = document.getElementById('grades-chart');
    if (ctx1) {
        chartsInstances.grades = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'الدرجة الكلية',
                    data: chartData.grades,
                    backgroundColor: chartData.colors,
                    borderRadius: 8,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
    
    // رسم بياني نظري/عملي
    const ctx2 = document.getElementById('comparison-chart');
    if (ctx2) {
        chartsInstances.comparison = new Chart(ctx2, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'النظري',
                        data: chartData.theoretical,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'العملي',
                        data: chartData.practical,
                        borderColor: '#8b5cf6',
                        backgroundColor: 'rgba(139, 92, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { usePointStyle: true }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
    
    console.log('✅ تم إنشاء الرسوم البيانية');
}

// ══════════════════════════════════════════════════════════
// 🔄 التبويبات
// ══════════════════════════════════════════════════════════

function switchTab(tabName) {
    // تحديث أزرار التبويبات
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        }
    });
    
    // تحديث لوحات المحتوى
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    const targetPanel = document.getElementById(`${tabName}-tab`);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
    
    // تحميل المحتوى حسب التبويب
    if (tabName === 'top') {
        loadTopStudents();
    } else if (tabName === 'charts') {
        if (currentResults) {
            loadChartData(null, currentResults);
        }
    }
    
    console.log('✅ تم التبديل إلى:', tabName);
}

// ══════════════════════════════════════════════════════════
// 🔍 البحث بالاسم
// ══════════════════════════════════════════════════════════

async function searchByName(query) {
    if (!query || query.length < 2) {
        document.getElementById('search-results').innerHTML = '';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        const resultsContainer = document.getElementById('search-results');
        
        if (data.success && data.results && data.results.length > 0) {
            resultsContainer.innerHTML = data.results.map(student => `
                <div class="search-result-item" onclick="selectStudent('${student.student_id}')">
                    <div class="result-name">${student.name}</div>
                    <div class="result-id">${student.student_id}</div>
                </div>
            `).join('');
        } else {
            resultsContainer.innerHTML = '<div class="no-results">لا توجد نتائج</div>';
        }
    } catch (error) {
        console.error('❌ خطأ في البحث:', error);
    }
}

function selectStudent(studentId) {
    document.getElementById('student-id-input').value = studentId;
    document.getElementById('search-results').innerHTML = '';
    linkAccount();
}

// ══════════════════════════════════════════════════════════
// 💾 التخزين المحلي
// ══════════════════════════════════════════════════════════

function storeTelegramId(id) {
    localStorage.setItem('telegram_id', id);
}

function getStoredTelegramId() {
    return localStorage.getItem('telegram_id');
}

// ══════════════════════════════════════════════════════════
// 📤 المشاركة والتصدير
// ══════════════════════════════════════════════════════════

async function shareAsImage() {
    if (!currentProfile || !currentResults) {
        showToast('⚠️ لا توجد بيانات للمشاركة', 'warning');
        return;
    }
    
    console.log('📤 مشاركة كصورة...');
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-image/${currentProfile.student_id}`);
        
        if (!response.ok) {
            throw new Error('فشل توليد الصورة');
        }
        
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        
        // محاولة استخدام Web Share API
        if (navigator.share && navigator.canShare) {
            try {
                const file = new File([blob], 'نتيجتي.png', { type: 'image/png' });
                
                if (navigator.canShare({ files: [file] })) {
                    await navigator.share({
                        title: 'نتيجتي الجامعية',
                        text: `نتائج ${currentProfile.student_name}`,
                        files: [file]
                    });
                    
                    showLoading(false);
                    showToast('✅ تم المشاركة بنجاح', 'success');
                    return;
                }
            } catch (shareError) {
                console.log('Web Share فشل، استخدام التحميل:', shareError);
            }
        }
        
        // Fallback: تحميل الصورة
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `نتيجة_${currentProfile.student_id}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(imageUrl);
        
        showLoading(false);
        showToast('✅ تم تحميل الصورة', 'success');
        
    } catch (error) {
        console.error('❌ خطأ في المشاركة:', error);
        showLoading(false);
        showToast('❌ فشل توليد الصورة', 'error');
    }
}

async function downloadAsPDF() {
    if (!currentProfile || !currentResults) {
        showToast('⚠️ لا توجد بيانات للتصدير', 'warning');
        return;
    }
    
    console.log('📥 تحميل PDF...');
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-pdf/${currentProfile.student_id}`);
        
        if (!response.ok) {
            throw new Error('فشل توليد PDF');
        }
        
        const blob = await response.blob();
        const pdfUrl = URL.createObjectURL(blob);
        
        // تحميل الملف
        const link = document.createElement('a');
        link.href = pdfUrl;
        link.download = `نتيجة_${currentProfile.student_id}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(pdfUrl);
        
        showLoading(false);
        showToast('✅ تم تحميل PDF', 'success');
        
    } catch (error) {
        console.error('❌ خطأ في تحميل PDF:', error);
        showLoading(false);
        showToast('❌ فشل توليد PDF', 'error');
    }
}

async function refreshResults() {
    if (!currentProfile) {
        showToast('⚠️ لا يوجد حساب مربوط', 'warning');
        return;
    }
    
    console.log('🔄 تحديث النتائج...');
    showToast('🔄 جاري التحديث...', 'info');
    
    try {
        // مسح Cache
        localStorage.removeItem('cached_results');
        localStorage.removeItem('cached_time');
        
        // إعادة تحميل
        await loadResults(currentProfile.student_id);
        
        showToast('✅ تم التحديث بنجاح', 'success');
    } catch (error) {
        console.error('❌ خطأ في التحديث:', error);
        showToast('❌ فشل التحديث', 'error');
    }
}

// جعل الدوال عالمية
window.selectStudent = selectStudent;
window.switchTab = switchTab;

console.log('✅ تم تحميل Mini App بنجاح');
