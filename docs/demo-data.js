/**
 * LF Academy Demo Data Seeder v2.0
 * Auto-populates dashboard with realistic demo data for new users
 * v2.0: 5-student demo class + 3 demo exams + analytics
 */
const LF_DEMO = {
    active: true,

    // Student demo data
    student: {
        name: '\u9673\u5c0f\u660e',
        grade: 'P5',
        totalScore: 847,
        streak: '12',
        rank: 3,
        'totalStudents': 28,
        accuracy: 72,
        trapsAvoided: 18,
        badges: ['\u9677\u9631\u7375\u4eba','\u9023\u7e8c7\u65e5','\u901f\u5ea6\u4e4b\u661f','\u5206\u6578\u9054\u4eba'],
        recentActivity: [
            {date:'5\u670826\u65e5', action:'\u5b8c\u6210\u300c\u5206\u6578\u9664\u6cd5\u300d\u7df4\u7fd2', score:85, time:'15\u5206\u9418'},
            {date:'5\u670825\u65e5', action:'\u5b8c\u6210\u300c\u767e\u5206\u6578\u8b8a\u5316\u300d\u7df4\u7fd2', score:68, time:'22\u5206\u9418'},
            {date:'5\u670824\u65e5', action:'\u907f\u958bT1\u9677\u9631', score:90, time:'10\u5206\u9418'},
        ],
        weakTraps: ['T5 \u5206\u6578','T9 \u767e\u5206\u6578'],
        strongTraps: ['T1 \u9032\u9000\u4f4d','T3 \u904b\u7b97\u9806\u5e8f'],
        nextLesson: {date:'5\u670828\u65e5(\u4e09)', time:'16:30-17:35', topic:'\u9762\u7a4d\u9677\u9631\u5c08\u9805', teacher:'\u674eSir'},
        goals: [
            {name:'\u6b63\u78ba\u7387\u905480%', progress:72},
            {name:'\u907f\u958b10\u500b\u9677\u9631', progress:70},
            {name:'\u9023\u7e8c14\u65e5\u7df4\u7fd2', progress:86},
        ]
    },

    // Teacher demo data
    teacher: {
        name: '\u674eSir',
        classes: [
            {id:'P5-A', grade:'P5', students:3, day:'\u9031\u4e09', time:'16:30', topic:'\u9762\u7a4d\u9677\u9631'},
            {id:'P5-B', grade:'P5', students:3, day:'\u9031\u56db', time:'17:00', topic:'\u5206\u6578\u9664\u6cd5'},
            {id:'P4-A', grade:'P4', students:3, day:'\u9031\u516d', time:'10:00', topic:'\u56db\u5247\u6df7\u5408'},
        ],
        'totalStudents': 9,
        todayClasses: 1,
        monthlyEarnings: 3840,
        avgAccuracy: 74,
        pendingReports: 2,
        recentStudents: [
            {name:'\u9673\u5c0f\u660e', grade:'P5', accuracy:72, lastClass:'\u6628\u65e5', alert:false},
            {name:'\u5f35\u5c0f\u5f37', grade:'P5', accuracy:85, lastClass:'\u6628\u65e5', alert:false},
            {name:'\u6797\u5c0f\u82b1', grade:'P5', accuracy:55, lastClass:'\u6628\u65e5', alert:true},
            {name:'\u9ec3\u5c0f\u7f8e', grade:'P4', accuracy:78, lastClass:'3\u5929\u524d', alert:false},
        ],
        nextActions: [
            '\u70ba\u6797\u5c0f\u82b1\u6e96\u5099T5\u5206\u6578\u88dc\u5e95\u7df4\u7fd2',
            'P5-A\u73ed\u8ab2\u5f8csend\u5bb6\u9577\u5831\u544a',
            '\u66f4\u65b0P4-A\u73ed\u6559\u5b78\u8a08\u5283',
        ]
    },

    // Parent demo data
    parent: {
        childName: '\u9673\u5c0f\u660e',
        childGrade: 'P5',
        monthlyProgress: [
            {week:'\u7b2c1\u9031', accuracy:62},
            {week:'\u7b2c2\u9031', accuracy:68},
            {week:'\u7b2c3\u9031', accuracy:70},
            {week:'\u7b2c4\u9031', accuracy:72},
        ],
        overallImprovement: '+10%',
        rank: 'Top 30%',
        classRank: '1/3',
        timeSpent: 320,
        trapsFixed: ['T1','T3'],
        trapsRemaining: ['T5','T9'],
        nextClass: {date:'5\u670828\u65e5 16:30', topic:'\u9762\u7a4d\u9677\u9631\u5c08\u9805'},
        teacherNote: '\u5c0f\u660e\u4e0a\u5802\u597d\u5c08\u6ce8\uff0c\u5206\u6578\u52a0\u6e1b\u5df2\u7d93\u597d\u719f\u3002\u4e0b\u500b\u6708\u6703\u4e3b\u529b\u6539\u5584\u767e\u5206\u6578\u8b8a\u5316\u9019\u500b\u5f31\u9805\u3002',
        recommendation: '\u5efa\u8b70\u7e7c\u7e8c8\u5802\u65b9\u6848\u3002\u4e0b\u500b\u6708\u5b8c\u6210\u5f8c\u9810\u8a08\u6b63\u78ba\u7387\u53ef\u905480%+\u3002',
        billInfo: {plan:'8\u5802\u65b9\u6848', nextPayment:'6\u670815\u65e5', amount:'$1,760'},
        communityNote: '\u540c\u73ed\u4ef2\u67092\u4f4d\u540c\u5b78\u4e00\u9f4a\u4e0a\u5802\uff0c3\u4eba\u5c0f\u7d44\u826f\u6027\u7af6\u722d\u6548\u679c\u597d\u597d\u3002',
    },

    // ========================================
    // v2.0: Full Demo Class with 5 Students
    // ========================================
    demoClass: {
        id: 'demo-class-001',
        name: '\ud83c\udf93 \u793a\u7bc4\u73ed\u7d1a',
        is_demo: true,
        createdAt: new Date().toISOString(),
        students: [
            {
                id: 'demo-s1', name: '\u5c0f\u660e', grade: 'P3',
                accuracy: 78, streak: 8, totalScore: 620,
                weakTraps: ['T1 \u9032\u9000\u4f4d', 'T6 \u5206\u6578'],
                strongTraps: ['T3 \u904b\u7b97\u9806\u5e8f'],
                lastActive: '2026-05-28',
                radar: { 'T1': 65, 'T2': 80, 'T3': 90, 'T4': 72, 'T5': 85, 'T6': 55, 'T7': 78, 'T8': 82, 'T9': 70, 'T10': 75 }
            },
            {
                id: 'demo-s2', name: '\u5bb6\u6021', grade: 'P4',
                accuracy: 85, streak: 15, totalScore: 890,
                weakTraps: ['T4 \u9762\u7a4d\u516c\u5f0f'],
                strongTraps: ['T1 \u9032\u9000\u4f4d', 'T3 \u904b\u7b97\u9806\u5e8f', 'T7 \u767e\u5206\u6578'],
                lastActive: '2026-05-28',
                radar: { 'T1': 95, 'T2': 88, 'T3': 92, 'T4': 60, 'T5': 82, 'T6': 85, 'T7': 90, 'T8': 80, 'T9': 78, 'T10': 88 }
            },
            {
                id: 'demo-s3', name: '\u5bb6\u8c6a', grade: 'P5',
                accuracy: 72, streak: 5, totalScore: 580,
                weakTraps: ['T5 \u5e7e\u4f55', 'T9 \u767e\u5206\u6578', 'T10 \u7d71\u8a08\u5716\u8868'],
                strongTraps: ['T1 \u9032\u9000\u4f4d'],
                lastActive: '2026-05-27',
                radar: { 'T1': 88, 'T2': 75, 'T3': 70, 'T4': 72, 'T5': 50, 'T6': 68, 'T7': 65, 'T8': 60, 'T9': 45, 'T10': 42 }
            },
            {
                id: 'demo-s4', name: 'Jason', grade: 'P6',
                accuracy: 90, streak: 22, totalScore: 1050,
                weakTraps: ['T10 \u7d71\u8a08\u5716\u8868'],
                strongTraps: ['T1\u2013T9 \u5168\u90e8\u638c\u63e1'],
                lastActive: '2026-05-29',
                radar: { 'T1': 98, 'T2': 95, 'T3': 96, 'T4': 92, 'T5': 90, 'T6': 88, 'T7': 94, 'T8': 91, 'T9': 85, 'T10': 62 }
            },
            {
                id: 'demo-s5', name: 'Chloe', grade: 'P3',
                accuracy: 65, streak: 3, totalScore: 420,
                weakTraps: ['T1 \u9032\u9000\u4f4d', 'T2 \u5c0f\u6578\u9ede', 'T6 \u5206\u6578'],
                strongTraps: [],
                lastActive: '2026-05-28',
                radar: { 'T1': 52, 'T2': 48, 'T3': 65, 'T4': 70, 'T5': 72, 'T6': 45, 'T7': 60, 'T8': 55, 'T9': 50, 'T10': 55 }
            }
        ],
        exams: [
            {
                id: 'demo-exam-p3', title: 'P3 \u7b2c\u4e00\u6bb5\u8003\u6a21\u64ec\u8a66\u5377',
                grade: 'P3', date: '2026-05-15',
                topics: ['\u9032\u9000\u4f4d', '\u904b\u7b97\u9806\u5e8f', '\u5206\u6578\u57fa\u790e'],
                avgScore: 72, totalQuestions: 20,
                results: [
                    { studentId: 'demo-s1', score: 75, timeMin: 28 },
                    { studentId: 'demo-s3', score: 62, timeMin: 35 },
                    { studentId: 'demo-s5', score: 78, timeMin: 32 }
                ]
            },
            {
                id: 'demo-exam-p4', title: 'P4 \u671f\u4e2d\u6e2c\u9a57',
                grade: 'P4', date: '2026-05-10',
                topics: ['\u56db\u5247\u6df7\u5408', '\u9762\u7a4d\u516c\u5f0f', '\u5206\u6578\u52a0\u6e1b'],
                avgScore: 68, totalQuestions: 25,
                results: [
                    { studentId: 'demo-s2', score: 82, timeMin: 30 },
                    { studentId: 'demo-s4', score: 91, timeMin: 22 }
                ]
            },
            {
                id: 'demo-exam-p5', title: 'P5-P6 SSPA\u6a21\u64ec\u5377',
                grade: 'P5', date: '2026-05-20',
                topics: ['\u7d9c\u5408\u8996\u5bdf', '\u767e\u5206\u6578\u8b8a\u5316', '\u7d71\u8a08\u5716\u8868'],
                avgScore: 65, totalQuestions: 30,
                results: [
                    { studentId: 'demo-s3', score: 58, timeMin: 42 },
                    { studentId: 'demo-s4', score: 88, timeMin: 35 },
                    { studentId: 'demo-s1', score: 70, timeMin: 38 }
                ]
            }
        ],
        // Analytics for dashboard
        analytics: {
            classAvgAccuracy: 78,
            classAvgStreak: 10.6,
            totalExamsCompleted: 3,
            totalQuestionsAnswered: 225,
            weakestTopic: 'T10 \u7d71\u8a08\u5716\u8868',
            strongestTopic: 'T1 \u9032\u9000\u4f4d',
            weeklyTrend: [65, 68, 72, 74, 78],
            studentRanking: [
                { name: 'Jason', accuracy: 90 },
                { name: '\u5bb6\u6021', accuracy: 85 },
                { name: '\u5c0f\u660e', accuracy: 78 },
                { name: '\u5bb6\u8c6a', accuracy: 72 },
                { name: 'Chloe', accuracy: 65 }
            ]
        }
    }
};

// ========================================
// DEMO DATA INJECTOR
// ========================================
function LF_hasRealData() {
    return localStorage.getItem('lf_has_data') === 'true';
}

function LF_setRealData() {
    localStorage.setItem('lf_has_data', 'true');
    LF_DEMO.active = false;
}

function LF_clearData() {
    localStorage.removeItem('lf_has_data');
    localStorage.removeItem('lf_demo_class');
    LF_DEMO.active = true;
    location.reload();
}

function LF_isDemoMode() {
    return LF_DEMO.active && !LF_hasRealData();
}

// ========================================
// v2.0: DEMO CLASS SEEDER
// Seeds the demo class into localStorage on first visit
// ========================================
function LF_seedDemoClass() {
    if (LF_hasRealData()) return false;
    var existing = localStorage.getItem('lf_demo_class');
    if (existing) return true; // Already seeded

    // Seed demo class data
    localStorage.setItem('lf_demo_class', JSON.stringify(LF_DEMO.demoClass));

    // Also seed into LFCore teacher_classes format
    if (typeof LFCore !== 'undefined') {
        var classes = LFCore.getData('teacher_classes', []);
        var hasDemo = classes.some(function(c) { return c.id === 'demo-class-001'; });
        if (!hasDemo) {
            classes.unshift({
                id: 'demo-class-001',
                name: '\ud83c\udf93 \u793a\u7bc4\u73ed\u7d1a',
                grade: 'P3-P6',
                students: 5,
                day: '\u2014',
                time: '\u2014',
                topic: '\u6df7\u5408\u7d1a\u5225',
                is_demo: true
            });
            LFCore.setData('teacher_classes', classes);
        }

        // Seed students into members format
        var members = LFCore.getData('members', []);
        LF_DEMO.demoClass.students.forEach(function(s) {
            var exists = members.some(function(m) { return m.student === s.name && m.grade === s.grade; });
            if (!exists) {
                members.push({
                    student: s.name,
                    grade: s.grade,
                    parent: s.name + '\u5bb6\u9577',
                    phone: '',
                    plan: 'free',
                    is_demo: true,
                    activated: new Date().toISOString(),
                    expiry: null
                });
            }
        });
        LFCore.setData('members', members);
    }

    console.log('[LF Demo] \u793a\u7bc4\u73ed\u7d1a\u5df2\u5efa\u7acb \u2014 5\u4f4d\u5b78\u751f \u00b7 3\u4efd\u8a66\u5377');
    return true;
}

// ========================================
// v2.0: FETCH DEMO CLASS DATA
// ========================================
function LF_getDemoClass() {
    try {
        var cached = localStorage.getItem('lf_demo_class');
        if (cached) return JSON.parse(cached);
    } catch(e) {}
    return LF_DEMO.demoClass;
}

// ========================================
// DEMO DATA BANNER
// ========================================
function LF_demoBanner() {
    if (!LF_isDemoMode()) return '';
    return `
    <div style="background:linear-gradient(135deg,#FEF3C7,#FFEDD5);border:1px solid #F59E0B;border-radius:10px;padding:10px 14px;margin:0 16px 4px;display:flex;align-items:center;justify-content:space-between;font-size:11px">
        <span>\ud83d\udccb <b>\u793a\u7bc4\u6a21\u5f0f</b> \u2014 \u8a3b\u518a\u5f8c\u4fdd\u5b58\u4f60\u7684\u8cc7\u6599</span>
        <a href="signup.html" style="background:#F59E0B;color:white;padding:4px 14px;border-radius:14px;text-decoration:none;font-weight:700;font-size:11px">\u7acb\u5373\u8a3b\u518a \u2192</a>
    </div>`;
}
// ========================================
// STUDENT DASHBOARD (with demo data)
// ========================================
function LF_studentDash() {
    var d = LF_DEMO.student;
    var isDemo = LF_isDemoMode();
    var badgeHtml = d.badges.map(function(b){
        return '<span style="display:inline-block;background:#D1FAE5;color:#065F46;padding:4px 10px;border-radius:12px;font-size:11px;font-weight:700">'+b+'</span>';
    }).join(' ');

    var activityHtml = d.recentActivity.map(function(a){
        return '<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:12px"><span>'+a.date+' \u00b7 '+a.action+'</span><span style="font-weight:700;color:var(--b)">'+a.score+'%</span></div>';
    }).join('');

    var goalHtml = d.goals.map(function(g){
        var color = g.progress >= 80 ? '#16A34A' : g.progress >= 50 ? '#F59E0B' : '#DC2626';
        return '<div style="margin-bottom:8px"><div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px"><span>'+g.name+'</span><span>'+g.progress+'%</span></div><div style="height:6px;background:#E5E7EB;border-radius:3px"><div style="height:100%;width:'+g.progress+'%;background:'+color+';border-radius:3px"></div></div></div>';
    }).join('');

    return LF_demoBanner() + `
    <div class="card" style="text-align:center;background:linear-gradient(135deg,#0A1A35,var(--b));color:white">
        <div style="font-size:13px;opacity:0.7">${d.grade} \u00b7 \u9716\u6953\u5b78\u82d1</div>
        <div style="font-family:\u0027Noto Serif HK\u0027,serif;font-size:20px;margin:4px 0">${d.name}</div>
        <div style="font-size:11px;opacity:0.6">\ud83c\udfc6 \u6392\u540d\u7b2c${d.rank}/${d.totalStudents} \u00b7 \u9023\u7e8c${d.streak}\u65e5</div>
    </div>

    <div class="stat-row">
        <div class="stat-card"><div class="sv">${d.totalScore}</div><div class="sl">\u7e3d\u5f97\u5206</div></div>
        <div class="stat-card highlight"><div class="sv">${d.streak}\ud83d\udd25</div><div class="sl">\u9023\u7e8c\u7c3d\u5230</div></div>
        <div class="stat-card"><div class="sv">${d.accuracy}%</div><div class="sl">\u6b63\u78ba\u7387</div></div>
    </div>

    <div class="card">
        <h2>\ud83c\udfaf \u76ee\u6a19\u9032\u5ea6</h2>
        ${goalHtml}
    </div>

    <div class="card">
        <h2>\ud83c\udfc5 \u5df2\u7372\u52f3\u7ae0</h2>
        <div style="display:flex;flex-wrap:wrap;gap:6px">${badgeHtml}</div>
    </div>

    <div class="card">
        <h2>\u26a0 \u5f31\u9805\u9677\u9631</h2>
        <div style="display:flex;gap:8px">
            ${d.weakTraps.map(function(t){return '<span style="background:#FEE2E2;color:#DC2626;padding:6px 12px;border-radius:16px;font-size:12px;font-weight:700">'+t+'</span>';}).join('')}
        </div>
        <div style="font-size:11px;color:var(--g600);margin-top:8px">\u2705 \u5df2\u638c\u63e1\uff1a${d.strongTraps.join('\u3001')}</div>
    </div>

    <div class="card">
        <h2>\ud83d\udcc5 \u4e0b\u5802\u9810\u544a</h2>
        <div style="font-size:13px"><b>${d.nextLesson.date}</b> \u00b7 ${d.nextLesson.time}</div>
        <div style="font-size:12px;color:var(--g600)">\u8ab2\u984c\uff1a${d.nextLesson.topic} \u00b7 \u5c0e\u5e2b\uff1a${d.nextLesson.teacher}</div>
    </div>

    <div class="card">
        <h2>\ud83d\udcdd \u6700\u8fd1\u6d3b\u52d5</h2>
        ${activityHtml}
    </div>

    <div class="quick-grid">
        <a class="quick-item" href="trap-quiz.html"><span class="qi">\ud83c\udfaf</span>\u9677\u9631\u8a3a\u65b7</a>
        <a class="quick-item" href="homework-tracker.html"><span class="qi">\ud83d\udcdd</span>\u4eca\u65e5\u7df4\u7fd2</a>
        <a class="quick-item" href="kids-boss-battle.html"><span class="qi">\u2694\ufe0f</span>Boss\u6230</a>
        <a class="quick-item" href="achievement-wall.html"><span class="qi">\ud83c\udfc6</span>\u6210\u5c31\u7246</a>
    </div>`;
}

// ========================================
// TEACHER DASHBOARD (with demo data) v2.0
// Now includes 5-student demo class view
// ========================================
function LF_teacherDash() {
    var d = LF_DEMO.teacher;
    var isDemo = LF_isDemoMode();
    var demoClass = LF_getDemoClass();

    var studentHtml = d.recentStudents.map(function(s){
        var alertIcon = s.alert ? ' \ud83d\udd34' : '';
        return '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:12px"><div><b>'+s.name+'</b> '+s.grade+alertIcon+'</div><div style="text-align:right"><span style="font-weight:700;color:'+(s.accuracy>=70?'#16A34A':'#DC2626')+'">'+s.accuracy+'%</span><br><span style="font-size:10px;color:var(--g600)">'+s.lastClass+'</span></div></div>';
    }).join('');

    var actionHtml = d.nextActions.map(function(a){
        return '<div style="padding:6px 0;font-size:12px;display:flex;align-items:center;gap:8px"><span style="color:var(--g)">\u25b8</span> '+a+'</div>';
    }).join('');

    var classHtml = d.classes.map(function(c){
        return '<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:12px"><div><b>'+c.id+'</b> '+c.grade+'</div><div style="text-align:right">'+c.day+' '+c.time+'<br><span style="font-size:10px;color:var(--g600)">'+c.topic+' \u00b7 '+c.students+'\u4eba</span></div></div>';
    }).join('');

    // Build demo class student list
    var demoStudentListHtml = '';
    if (isDemo && demoClass) {
        demoStudentListHtml = demoClass.students.map(function(s, i) {
            var rankColors = ['#C9A84C', '#9CA3AF', '#CD7F32', '#6B7280', '#6B7280'];
            return '<tr>'+
                '<td>'+(i+1)+'</td>'+
                '<td><b>'+s.name+'</b></td>'+
                '<td>'+s.grade+'</td>'+
                '<td><span style="font-weight:700;color:'+(s.accuracy>=80?'#16A34A':s.accuracy>=60?'#F59E0B':'#DC2626')+'">'+s.accuracy+'%</span></td>'+
                '<td>'+s.streak+'\u65e5</td>'+
                '<td>'+s.weakTraps.slice(0,2).join(', ')+'</td>'+
                '<td><span style="font-size:10px;background:#F3F4F6;padding:3px 8px;border-radius:6px">\u67e5\u770b</span></td>'+
            '</tr>';
        }).join('');
    }

    return LF_demoBanner() + `
    <div class="card" style="text-align:center;background:linear-gradient(135deg,#0A1A35,var(--b));color:white">
        <div style="font-size:13px;opacity:0.7">\u9716\u6953\u5b78\u82d1 \u00b7 \u5c0e\u5e2b\u5e73\u53f0</div>
        <div style="font-family:\u0027Noto Serif HK\u0027,serif;font-size:20px;margin:4px 0">${d.name}</div>
        <div style="font-size:11px;opacity:0.6">\u4eca\u6708\u6536\u5165 HK$${d.monthlyEarnings.toLocaleString()} \u00b7 \u6559\u5b78\u4e2d</div>
    </div>

    <div class="stat-row">
        <div class="stat-card"><div class="sv">${d.totalStudents}</div><div class="sl">\u5b78\u751f\u7e3d\u6578</div></div>
        <div class="stat-card highlight"><div class="sv">${d.todayClasses}</div><div class="sl">\u4eca\u65e5\u8ab2\u5802</div></div>
        <div class="stat-card"><div class="sv">${d.avgAccuracy}%</div><div class="sl">\u5e73\u5747\u6b63\u78ba\u7387</div></div>
    </div>

    ${isDemo && demoClass ? `
    <div class="card" style="border-left:3px solid #C9A84C">
        <h2>\ud83c\udf93 \u793a\u7bc4\u73ed\u7d1a \u2014 ${demoClass.students.length}\u4f4d\u865b\u64ec\u5b78\u751f <span style="font-size:10px;background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:6px;font-weight:400">is_demo</span></h2>
        <table style="font-size:11px;margin-top:0">
            <thead><tr><th>#</th><th>\u59d3\u540d</th><th>\u5e74\u7d1a</th><th>\u6b63\u78ba\u7387</th><th>\u7c3d\u5230</th><th>\u5f31\u9805</th><th></th></tr></thead>
            <tbody>${demoStudentListHtml}</tbody>
        </table>
        <div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap">
            <a href="teacher-class-monitor.html" class="btn btn-gold btn-sm">\ud83d\udcca \u67e5\u770b\u5b78\u60c5\u770b\u677f</a>
            <a href="smart-test-gen.html" class="btn btn-primary btn-sm">\ud83d\udcdd \u751f\u6210\u793a\u7bc4\u8a66\u5377</a>
            <button class="btn btn-outline btn-sm" onclick="if(confirm(\u0027\u522a\u9664\u793a\u7bc4\u73ed\u7d1a\uff1f\u0027)){localStorage.removeItem(\u0027lf_demo_class\u0027);location.reload()}">\ud83d\uddd1 \u522a\u9664\u793a\u7bc4\u73ed\u7d1a</button>
        </div>
        <div style="margin-top:8px;font-size:10px;color:var(--g600)">\u26a0 \u793a\u7bc4\u5b78\u751f\u8cc7\u6599\u70ba\u975c\u614b\u9810\u8a2d\uff0c\u4e0d\u6d89\u53ca\u771f\u5be6\u5b78\u751f\u3002\u53ef\u96a8\u6642\u522a\u9664\u3002</div>
    </div>
    ` : ''}

    <div class="card">
        <h2>\ud83d\udcc5 \u8ab2\u5802\u6642\u9593\u8868</h2>
        ${classHtml}
    </div>

    <div class="card">
        <h2>\ud83d\udc68\u200d\ud83c\udf93 \u5b78\u751f\u6982\u89bd</h2>
        ${studentHtml}
    </div>

    <div class="card" style="border-left:3px solid #F59E0B">
        <h2>\u26a1 \u5f85\u8fa6\u4e8b\u9805</h2>
        ${actionHtml}
        <div style="margin-top:8px;font-size:11px;color:var(--r)">\ud83d\udccb ${d.pendingReports}\u4efd\u5bb6\u9577\u5831\u544a\u672a\u767c\u9001</div>
    </div>

    ${isDemo ? `
    <div class="card" style="background:#F0FDF4;border:2px dashed #16A34A;text-align:center;padding:24px">
        <div style="font-size:28px;margin-bottom:8px">\ud83d\ude80</div>
        <div style="font-size:14px;font-weight:700;color:#065F46;margin-bottom:6px">\u6e96\u5099\u597d\u958b\u59cb\u4e86\uff1f</div>
        <div style="font-size:12px;color:#6B7280;margin-bottom:12px">\u5efa\u7acb\u4f60\u7684\u7b2c\u4e00\u500b\u771f\u6b63\u73ed\u7d1a\uff0c\u958b\u59cb\u7ba1\u7406\u5b78\u751f</div>
        <a href="teacher-class-monitor.html" class="btn btn-green" style="padding:12px 28px;font-size:14px">\u2728 \u5efa\u7acb\u6211\u7684\u7b2c\u4e00\u500b\u73ed\u7d1a</a>
    </div>
    ` : ''}

    <div class="quick-grid">
        <a class="quick-item" href="teacher-live.html"><span class="qi">\ud83c\udfa5</span>\u4e0a\u5802\u76f4\u64ad</a>
        <a class="quick-item" href="teacher-lesson-planner.html"><span class="qi">\ud83d\udccb</span>\u5099\u8ab2</a>
        <a class="quick-item" href="smart-test-gen.html"><span class="qi">\ud83d\udcdd</span>\u51fa\u5377</a>
        <a class="quick-item" href="post-trial-report.html"><span class="qi">\ud83d\udcca</span>\u5bb6\u9577\u5831\u544a</a>
    </div>`;
}

// ========================================
// PARENT DASHBOARD (with demo data)
// ========================================
function LF_parentDash() {
    var d = LF_DEMO.parent;
    var isDemo = LF_isDemoMode();

    var trendText = '';
    var lastAcc = d.monthlyProgress[d.monthlyProgress.length-1].accuracy;
    var firstAcc = d.monthlyProgress[0].accuracy;
    trendText = firstAcc+'% \u2192 '+lastAcc+'% ('+(lastAcc-firstAcc>=0?'+':'')+(lastAcc-firstAcc)+'%)';

    return LF_demoBanner() + `
    <div class="card" style="text-align:center;background:linear-gradient(135deg,#0A1A35,var(--b));color:white">
        <div style="font-size:13px;opacity:0.7">\u9716\u6953\u5b78\u82d1 \u00b7 \u5bb6\u9577\u4e2d\u5fc3</div>
        <div style="font-family:\u0027Noto Serif HK\u0027,serif;font-size:20px;margin:4px 0">${d.childName} \u00b7 ${d.childGrade}</div>
        <div style="font-size:11px;opacity:0.6">\ud83d\udcc8 \u672c\u6708\u9032\u6b65 ${d.overallImprovement} \u00b7 \u540c\u7d1a ${d.rank}</div>
    </div>

    <div class="stat-row">
        <div class="stat-card"><div class="sv" style="color:#16A34A">${d.overallImprovement}</div><div class="sl">\u672c\u6708\u9032\u6b65</div></div>
        <div class="stat-card highlight"><div class="sv">${d.classRank}</div><div class="sl">\u73ed\u4e0a\u6392\u540d</div></div>
        <div class="stat-card"><div class="sv">${d.timeSpent}min</div><div class="sl">\u7df4\u7fd2\u6642\u9593</div></div>
    </div>

    <div class="card">
        <h2>\ud83d\udcc8 \u9032\u6b65\u8da8\u52e2</h2>
        <div style="font-size:13px;margin-bottom:8px">${trendText}</div>
        <div style="display:flex;align-items:flex-end;gap:8px;height:80px">
            ${d.monthlyProgress.map(function(w,i){
                var h = w.accuracy;
                return '<div style="flex:1;text-align:center"><div style="background:'+(i>=3?'#16A34A':'#F59E0B')+';height:'+h+'px;border-radius:4px 4px 0 0;transition:height 0.5s"></div><div style="font-size:10px;margin-top:4px">'+w.week+'</div><div style="font-size:10px;font-weight:700">'+w.accuracy+'%</div></div>';
            }).join('')}
        </div>
    </div>

    <div class="card">
        <h2>\u26a0 \u5b78\u7fd2\u72c0\u6cc1</h2>
        <div style="display:flex;gap:16px;margin-bottom:8px">
            <div style="flex:1"><div style="font-size:11px;color:var(--g600)">\u5df2\u89e3\u6c7a\u9677\u9631</div><div style="font-weight:700;color:#16A34A">${d.trapsFixed.join('\u3001')}</div></div>
            <div style="flex:1"><div style="font-size:11px;color:var(--g600)">\u5c1a\u9700\u52a0\u5f37</div><div style="font-weight:700;color:#DC2626">${d.trapsRemaining.join('\u3001')}</div></div>
        </div>
    </div>

    <div class="card" style="border-left:3px solid var(--g)">
        <h2>\ud83d\udcac \u5c0e\u5e2b\u8a55\u8a9e</h2>
        <div style="font-size:13px;font-style:italic;color:var(--g800);line-height:1.6">\u300c${d.teacherNote}\u300d</div>
        <div style="font-size:11px;color:var(--g600);margin-top:6px">${d.recommendation}</div>
    </div>

    <div class="card">
        <h2>\ud83d\udcc5 \u4e0b\u5802\u9810\u544a</h2>
        <div style="font-size:13px"><b>${d.nextClass.date}</b></div>
        <div style="font-size:12px;color:var(--g600)">\u8ab2\u984c\uff1a${d.nextClass.topic}</div>
    </div>

    <div class="card">
        <h2>\ud83d\udcb3 \u5e33\u55ae\u8cc7\u8a0a</h2>
        <div style="display:flex;justify-content:space-between;font-size:12px">
            <span>${d.billInfo.plan}</span>
            <span>\u4e0b\u6b21\u4ed8\u6b3e\uff1a${d.billInfo.nextPayment}</span>
            <span style="font-weight:900">${d.billInfo.amount}</span>
        </div>
    </div>

    <div class="card" style="background:#F0FDF4;border:1px solid #BBF7D0">
        <div style="font-size:12px;color:#065F46">\ud83d\udc68\u200d\ud83d\udc69\u200d\ud83d\udc67 ${d.communityNote}</div>
    </div>

    <div class="quick-grid">
        <a class="quick-item" href="post-trial-report.html"><span class="qi">\ud83d\udcca</span>\u5b78\u60c5\u5831\u544a</a>
        <a class="quick-item" href="parent-comms.html"><span class="qi">\ud83d\udcac</span>\u806f\u7d61\u5c0e\u5e2b</a>
        <a class="quick-item" href="booking.html"><span class="qi">\ud83d\udcc5</span>\u8ab2\u5802\u7ba1\u7406</a>
        <a class="quick-item" href="share-card.html"><span class="qi">\ud83d\udce4</span>\u5206\u4eab\u9032\u6b65</a>
    </div>`;
}

// v2.0: Demo class analytics dashboard (for class-monitor and analytics pages)
function LF_demoAnalyticsDash() {
    var dc = LF_getDemoClass();
    if (!dc) return '';

    var analytics = dc.analytics;
    var rankHtml = analytics.studentRanking.map(function(s, i) {
        var medals = ['\ud83e\udd47', '\ud83e\udd48', '\ud83e\udd49', '4', '5'];
        var colors = ['#C9A84C', '#9CA3AF', '#CD7F32', '#6B7280', '#6B7280'];
        return '<div style="display:flex;align-items:center;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:12px">'+
            '<span style="font-size:16px;width:28px">'+medals[i]+'</span>'+
            '<span style="flex:1;font-weight:600">'+s.name+'</span>'+
            '<span style="font-weight:700;color:'+colors[i]+'">'+s.accuracy+'%</span>'+
        '</div>';
    }).join('');

    var examHtml = dc.exams.map(function(e) {
        return '<div style="padding:10px 0;border-bottom:1px solid #F3F4F6">'+
            '<div style="font-weight:700;font-size:13px">'+e.title+'</div>'+
            '<div style="font-size:11px;color:#6B7280;margin:2px 0">'+e.grade+' \u00b7 '+e.date+' \u00b7 '+e.totalQuestions+'\u984c \u00b7 \u5e73\u5747 '+e.avgScore+'\u5206</div>'+
            '<div style="font-size:10px;color:#9CA3AF">'+e.topics.join(' \u00b7 ')+'</div>'+
        '</div>';
    }).join('');

    return `
    <div class="card">
        <h2>\ud83c\udfc6 \u73ed\u7d1a\u6392\u540d</h2>
        ${rankHtml}
    </div>
    <div class="card">
        <h2>\ud83d\udcca \u73ed\u7d1a\u6578\u64da\u6982\u89bd</h2>
        <div class="stat-row">
            <div class="stat-card"><div class="sv">${analytics.classAvgAccuracy}%</div><div class="sl">\u73ed\u7d1a\u5e73\u5747\u6b63\u78ba\u7387</div></div>
            <div class="stat-card"><div class="sv">${analytics.classAvgStreak}</div><div class="sl">\u5e73\u5747\u7c3d\u5230\u65e5</div></div>
            <div class="stat-card"><div class="sv">${analytics.totalQuestionsAnswered}</div><div class="sl">\u7e3d\u7b54\u984c\u6578</div></div>
        </div>
        <div style="font-size:11px;color:#6B7280;margin-top:8px">
            \ud83d\udd34 \u6700\u5f31\u77e5\u8b58\u9ede\uff1a<b>${analytics.weakestTopic}</b> \u00b7 
            \ud83d\udfe2 \u6700\u5f37\u77e5\u8b58\u9ede\uff1a<b>${analytics.strongestTopic}</b>
        </div>
    </div>
    <div class="card">
        <h2>\ud83d\udcdd \u793a\u7bc4\u8a66\u5377 (${dc.exams.length}\u4efd)</h2>
        ${examHtml}
    </div>`;
}

// Auto-init when script loads
console.log('\u005bLF Demo v2.0\u005d Engine ready. Demo mode: ' + LF_isDemoMode());

// Auto-seed demo class on first load
if (LF_isDemoMode()) {
    LF_seedDemoClass();
}
