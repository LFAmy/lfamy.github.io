/**
 * LF Academy Demo Data Seeder
 * Auto-populates dashboard with realistic demo data for new users
 */
const LF_DEMO = {
    active: true,
    
    // Student demo data
    student: {
        name: '陳小明',
        grade: 'P5',
        totalScore: 847,
        streak: '12',
        rank: 3,
        'totalStudents': 28,
        accuracy: 72,
        trapsAvoided: 18,
        badges: ['陷阱獵人','連續7日','速度之星','分數達人'],
        recentActivity: [
            {date:'5月26日', action:'完成「分數除法」練習', score:85, time:'15分鐘'},
            {date:'5月25日', action:'完成「百分數變化」練習', score:68, time:'22分鐘'},
            {date:'5月24日', action:'避開T1陷阱', score:90, time:'10分鐘'},
        ],
        weakTraps: ['T5 分數','T9 百分數'],
        strongTraps: ['T1 進退位','T3 運算順序'],
        nextLesson: {date:'5月28日(三)', time:'16:30-17:35', topic:'面積陷阱專項', teacher:'李Sir'},
        goals: [
            {name:'正確率達80%', progress:72},
            {name:'避開10個陷阱', progress:70},
            {name:'連續14日練習', progress:86},
        ]
    },
    
    // Teacher demo data
    teacher: {
        name: '李Sir',
        classes: [
            {id:'P5-A', grade:'P5', students:3, day:'週三', time:'16:30', topic:'面積陷阱'},
            {id:'P5-B', grade:'P5', students:3, day:'週四', time:'17:00', topic:'分數除法'},
            {id:'P4-A', grade:'P4', students:3, day:'週六', time:'10:00', topic:'四則混合'},
        ],
        'totalStudents': 9,
        todayClasses: 1,
        monthlyEarnings: 3840,
        avgAccuracy: 74,
        pendingReports: 2,
        recentStudents: [
            {name:'陳小明', grade:'P5', accuracy:72, lastClass:'昨日', alert:false},
            {name:'張小強', grade:'P5', accuracy:85, lastClass:'昨日', alert:false},
            {name:'林小花', grade:'P5', accuracy:55, lastClass:'昨日', alert:true},
            {name:'黃小美', grade:'P4', accuracy:78, lastClass:'3天前', alert:false},
        ],
        nextActions: [
            '為林小花準備T5分數補底練習',
            'P5-A班課後send家長報告',
            '更新P4-A班教學計劃',
        ]
    },
    
    // Parent demo data
    parent: {
        childName: '陳小明',
        childGrade: 'P5',
        monthlyProgress: [
            {week:'第1週', accuracy:62},
            {week:'第2週', accuracy:68},
            {week:'第3週', accuracy:70},
            {week:'第4週', accuracy:72},
        ],
        overallImprovement: '+10%',
        rank: 'Top 30%',
        classRank: '1/3',
        timeSpent: 320,
        trapsFixed: ['T1','T3'],
        trapsRemaining: ['T5','T9'],
        nextClass: {date:'5月28日 16:30', topic:'面積陷阱專項'},
        teacherNote: '小明上堂好專注，分數加減已經好熟。下個月會主力改善百分數變化呢個弱項。',
        recommendation: '建議繼續8堂方案。下個月完成後預計正確率可達80%+。',
        billInfo: {plan:'8堂方案', nextPayment:'6月15日', amount:'$1,760'},
        communityNote: '同班仲有2位同學一齊上堂，3人小組良性競爭效果好好。',
    },
};

// ========================================
// DEMO DATA INJECTOR
// ========================================
function LF_hasRealData() {
    // Check if user has any real data in localStorage
    return localStorage.getItem('lf_has_data') === 'true';
}

function LF_setRealData() {
    localStorage.setItem('lf_has_data', 'true');
    LF_DEMO.active = false;
}

function LF_clearData() {
    localStorage.removeItem('lf_has_data');
    LF_DEMO.active = true;
    location.reload();
}

function LF_isDemoMode() {
    return LF_DEMO.active && !LF_hasRealData();
}

// ========================================
// DEMO DATA BANNER
// ========================================
function LF_demoBanner() {
    if (!LF_isDemoMode()) return '';
    return `
    <div style="background:linear-gradient(135deg,#FEF3C7,#FFEDD5);border:1px solid #F59E0B;border-radius:10px;padding:10px 14px;margin:0 16px 4px;display:flex;align-items:center;justify-content:space-between;font-size:11px">
        <span>📋 <b>示範模式</b> — 以下係模擬數據，幫助你了解平台功能</span>
        <button onclick="LF_clearData()" style="background:#F59E0B;color:white;border:none;padding:4px 12px;border-radius:14px;font-size:10px;font-weight:700;cursor:pointer">清除示範數據</button>
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
        return '<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:12px"><span>'+a.date+' · '+a.action+'</span><span style="font-weight:700;color:var(--b)">'+a.score+'%</span></div>';
    }).join('');
    
    var goalHtml = d.goals.map(function(g){
        var color = g.progress >= 80 ? '#16A34A' : g.progress >= 50 ? '#F59E0B' : '#DC2626';
        return '<div style="margin-bottom:8px"><div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:2px"><span>'+g.name+'</span><span>'+g.progress+'%</span></div><div style="height:6px;background:#E5E7EB;border-radius:3px"><div style="height:100%;width:'+g.progress+'%;background:'+color+';border-radius:3px"></div></div></div>';
    }).join('');
    
    return LF_demoBanner() + `
    <div class="card" style="text-align:center;background:linear-gradient(135deg,#0A1A35,var(--b));color:white">
        <div style="font-size:13px;opacity:0.7">${d.grade} · 霖楓學苑</div>
        <div style="font-family:'Noto Serif HK',serif;font-size:20px;margin:4px 0">${d.name}</div>
        <div style="font-size:11px;opacity:0.6">🏆 排名第${d.rank}/${d.totalStudents} · 連續${d.streak}日</div>
    </div>
    
    <div class="stat-row">
        <div class="stat-card"><div class="sv">${d.totalScore}</div><div class="sl">總得分</div></div>
        <div class="stat-card highlight"><div class="sv">${d.streak}🔥</div><div class="sl">連續簽到</div></div>
        <div class="stat-card"><div class="sv">${d.accuracy}%</div><div class="sl">正確率</div></div>
    </div>
    
    <div class="card">
        <h2>🎯 目標進度</h2>
        ${goalHtml}
    </div>
    
    <div class="card">
        <h2>🏅 已獲勳章</h2>
        <div style="display:flex;flex-wrap:wrap;gap:6px">${badgeHtml}</div>
    </div>
    
    <div class="card">
        <h2>⚠ 弱項陷阱</h2>
        <div style="display:flex;gap:8px">
            ${d.weakTraps.map(function(t){return '<span style="background:#FEE2E2;color:#DC2626;padding:6px 12px;border-radius:16px;font-size:12px;font-weight:700">'+t+'</span>';}).join('')}
        </div>
        <div style="font-size:11px;color:var(--g600);margin-top:8px">✅ 已掌握：${d.strongTraps.join('、')}</div>
    </div>
    
    <div class="card">
        <h2>📅 下堂預告</h2>
        <div style="font-size:13px"><b>${d.nextLesson.date}</b> · ${d.nextLesson.time}</div>
        <div style="font-size:12px;color:var(--g600)">課題：${d.nextLesson.topic} · 導師：${d.nextLesson.teacher}</div>
    </div>
    
    <div class="card">
        <h2>📝 最近活動</h2>
        ${activityHtml}
    </div>
    
    <div class="quick-grid">
        <a class="quick-item" href="trap-quiz.html"><span class="qi">🎯</span>陷阱診斷</a>
        <a class="quick-item" href="homework-tracker.html"><span class="qi">📝</span>今日練習</a>
        <a class="quick-item" href="kids-boss-battle.html"><span class="qi">⚔️</span>Boss戰</a>
        <a class="quick-item" href="achievement-wall.html"><span class="qi">🏆</span>成就牆</a>
    </div>`;
}

// ========================================
// TEACHER DASHBOARD (with demo data)
// ========================================
function LF_teacherDash() {
    var d = LF_DEMO.teacher;
    var isDemo = LF_isDemoMode();
    
    var studentHtml = d.recentStudents.map(function(s){
        var alertIcon = s.alert ? ' 🔴' : '';
        return '<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:12px"><div><b>'+s.name+'</b> '+s.grade+alertIcon+'</div><div style="text-align:right"><span style="font-weight:700;color:'+(s.accuracy>=70?'#16A34A':'#DC2626')+'">'+s.accuracy+'%</span><br><span style="font-size:10px;color:var(--g600)">'+s.lastClass+'</span></div></div>';
    }).join('');
    
    var actionHtml = d.nextActions.map(function(a){
        return '<div style="padding:6px 0;font-size:12px;display:flex;align-items:center;gap:8px"><span style="color:var(--g)">▸</span> '+a+'</div>';
    }).join('');
    
    var classHtml = d.classes.map(function(c){
        return '<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #F3F4F6;font-size:12px"><div><b>'+c.id+'</b> '+c.grade+'</div><div style="text-align:right">'+c.day+' '+c.time+'<br><span style="font-size:10px;color:var(--g600)">'+c.topic+' · '+c.students+'人</span></div></div>';
    }).join('');
    
    return LF_demoBanner() + `
    <div class="card" style="text-align:center;background:linear-gradient(135deg,#0A1A35,var(--b));color:white">
        <div style="font-size:13px;opacity:0.7">霖楓學苑 · 導師平台</div>
        <div style="font-family:'Noto Serif HK',serif;font-size:20px;margin:4px 0">${d.name}</div>
        <div style="font-size:11px;opacity:0.6">今月收入 HK$${d.monthlyEarnings.toLocaleString()} · 教學中</div>
    </div>
    
    <div class="stat-row">
        <div class="stat-card"><div class="sv">${d.totalStudents}</div><div class="sl">學生總數</div></div>
        <div class="stat-card highlight"><div class="sv">${d.todayClasses}</div><div class="sl">今日課堂</div></div>
        <div class="stat-card"><div class="sv">${d.avgAccuracy}%</div><div class="sl">平均正確率</div></div>
    </div>
    
    <div class="card">
        <h2>📅 課堂時間表</h2>
        ${classHtml}
    </div>
    
    <div class="card">
        <h2>👨‍🎓 學生概覽</h2>
        ${studentHtml}
    </div>
    
    <div class="card" style="border-left:3px solid #F59E0B">
        <h2>⚡ 待辦事項</h2>
        ${actionHtml}
        <div style="margin-top:8px;font-size:11px;color:var(--r)">📋 ${d.pendingReports}份家長報告未發送</div>
    </div>
    
    <div class="quick-grid">
        <a class="quick-item" href="teacher-live.html"><span class="qi">🎥</span>上堂直播</a>
        <a class="quick-item" href="teacher-lesson-planner.html"><span class="qi">📋</span>備課</a>
        <a class="quick-item" href="smart-test-gen.html"><span class="qi">📝</span>出卷</a>
        <a class="quick-item" href="post-trial-report.html"><span class="qi">📊</span>家長報告</a>
    </div>`;
}

// ========================================
// PARENT DASHBOARD (with demo data)
// ========================================
function LF_parentDash() {
    var d = LF_DEMO.parent;
    var isDemo = LF_isDemoMode();
    
    // Progress trend text
    var trendText = '';
    var lastAcc = d.monthlyProgress[d.monthlyProgress.length-1].accuracy;
    var firstAcc = d.monthlyProgress[0].accuracy;
    trendText = firstAcc+'% → '+lastAcc+'% ('+(lastAcc-firstAcc>=0?'+':'')+(lastAcc-firstAcc)+'%)';
    
    return LF_demoBanner() + `
    <div class="card" style="text-align:center;background:linear-gradient(135deg,#0A1A35,var(--b));color:white">
        <div style="font-size:13px;opacity:0.7">霖楓學苑 · 家長中心</div>
        <div style="font-family:'Noto Serif HK',serif;font-size:20px;margin:4px 0">${d.childName} · ${d.childGrade}</div>
        <div style="font-size:11px;opacity:0.6">📈 本月進步 ${d.overallImprovement} · 同級 ${d.rank}</div>
    </div>
    
    <div class="stat-row">
        <div class="stat-card"><div class="sv" style="color:#16A34A">${d.overallImprovement}</div><div class="sl">本月進步</div></div>
        <div class="stat-card highlight"><div class="sv">${d.classRank}</div><div class="sl">班上排名</div></div>
        <div class="stat-card"><div class="sv">${d.timeSpent}min</div><div class="sl">練習時間</div></div>
    </div>
    
    <div class="card">
        <h2>📈 進步趨勢</h2>
        <div style="font-size:13px;margin-bottom:8px">${trendText}</div>
        <div style="display:flex;align-items:flex-end;gap:8px;height:80px">
            ${d.monthlyProgress.map(function(w,i){
                var h = w.accuracy;
                return '<div style="flex:1;text-align:center"><div style="background:'+(i>=3?'#16A34A':'#F59E0B')+';height:'+h+'px;border-radius:4px 4px 0 0;transition:height 0.5s"></div><div style="font-size:10px;margin-top:4px">'+w.week+'</div><div style="font-size:10px;font-weight:700">'+w.accuracy+'%</div></div>';
            }).join('')}
        </div>
    </div>
    
    <div class="card">
        <h2>⚠ 學習狀況</h2>
        <div style="display:flex;gap:16px;margin-bottom:8px">
            <div style="flex:1"><div style="font-size:11px;color:var(--g600)">已解決陷阱</div><div style="font-weight:700;color:#16A34A">${d.trapsFixed.join('、')}</div></div>
            <div style="flex:1"><div style="font-size:11px;color:var(--g600)">尚需加強</div><div style="font-weight:700;color:#DC2626">${d.trapsRemaining.join('、')}</div></div>
        </div>
    </div>
    
    <div class="card" style="border-left:3px solid var(--g)">
        <h2>💬 導師評語</h2>
        <div style="font-size:13px;font-style:italic;color:var(--g800);line-height:1.6">「${d.teacherNote}」</div>
        <div style="font-size:11px;color:var(--g600);margin-top:6px">${d.recommendation}</div>
    </div>
    
    <div class="card">
        <h2>📅 下堂預告</h2>
        <div style="font-size:13px"><b>${d.nextClass.date}</b></div>
        <div style="font-size:12px;color:var(--g600)">課題：${d.nextClass.topic}</div>
    </div>
    
    <div class="card">
        <h2>💳 帳單資訊</h2>
        <div style="display:flex;justify-content:space-between;font-size:12px">
            <span>${d.billInfo.plan}</span>
            <span>下次付款：${d.billInfo.nextPayment}</span>
            <span style="font-weight:900">${d.billInfo.amount}</span>
        </div>
    </div>
    
    <div class="card" style="background:#F0FDF4;border:1px solid #BBF7D0">
        <div style="font-size:12px;color:#065F46">👨‍👩‍👧 ${d.communityNote}</div>
    </div>
    
    <div class="quick-grid">
        <a class="quick-item" href="post-trial-report.html"><span class="qi">📊</span>學情報告</a>
        <a class="quick-item" href="parent-comms.html"><span class="qi">💬</span>聯絡導師</a>
        <a class="quick-item" href="booking.html"><span class="qi">📅</span>課堂管理</a>
        <a class="quick-item" href="share-card.html"><span class="qi">📤</span>分享進步</a>
    </div>`;
}

// Auto-init when script loads
console.log('LF Demo Data Engine ready. Demo mode: ' + LF_isDemoMode());
