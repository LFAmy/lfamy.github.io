/**
 * LF Academy Gamification Engine v2.0
 * 霖楓學苑遊戲化引擎
 * 
 * Features:
 * - Streak tracking with visual milestones
 * - 3-person group live ranking
 * - Daily challenges with countdown
 * - Badge unlock animations
 * - "Come back tomorrow" hooks
 * - Boss battle progression
 */
const LFGame = {
    // ==========================================
    // CONFIGURATION
    // ==========================================
    config: {
        streakMilestones: [3, 7, 14, 30, 60, 100],
        streakRewards: {
            3:  {badge:'🔥新手獵人', points:50,  msg:'連續3日！你開始建立習慣喇！'},
            7:  {badge:'⚡連續一週', points:150, msg:'一個禮拜！陷阱開始驚咗你！'},
            14: {badge:'💪兩週達人', points:300, msg:'半個月！你嘅陷阱雷達已經好敏銳！'},
            30: {badge:'👑月度冠軍', points:800, msg:'成個月冇停過！你係真正嘅陷阱獵人！'},
            60: {badge:'🏆季度傳奇', points:2000, msg:'兩個月堅持！全級嘅數學榜樣！'},
            100:{badge:'🌟百天至尊', points:5000, msg:'一百日！霖楓傳奇級別！'},
        },
        dailyChallengeTime: '16:00', // New challenge available at 4pm
    },

    // ==========================================
    // STREAK SYSTEM
    // ==========================================
    getStreak() {
        return parseInt(localStorage.getItem('lf_streak') || '0');
    },

    getLastActive() {
        return localStorage.getItem('lf_last_active') || '';
    },

    recordActivity() {
        var today = new Date().toISOString().split('T')[0];
        var lastActive = this.getLastActive();
        var streak = this.getStreak();
        
        if (lastActive === today) {
            return {streak: streak, isNewDay: false, milestone: null};
        }
        
        var yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        var yesterdayStr = yesterday.toISOString().split('T')[0];
        
        if (lastActive === yesterdayStr || lastActive === '') {
            streak += 1;
        } else {
            streak = 1; // streak broken
        }
        
        localStorage.setItem('lf_streak', streak.toString());
        localStorage.setItem('lf_last_active', today);
        
        // Check milestone
        var milestone = null;
        if (this.config.streakMilestones.indexOf(streak) >= 0) {
            milestone = this.config.streakRewards[streak];
            // Award points
            var pts = parseInt(localStorage.getItem('lf_points') || '0') + milestone.points;
            localStorage.setItem('lf_points', pts.toString());
            // Award badge
            var badges = JSON.parse(localStorage.getItem('lf_badges') || '[]');
            if (badges.indexOf(milestone.badge) < 0) {
                badges.push(milestone.badge);
                localStorage.setItem('lf_badges', JSON.stringify(badges));
            }
        }
        
        return {streak: streak, isNewDay: true, milestone: milestone};
    },

    isStreakAtRisk() {
        var lastActive = this.getLastActive();
        if (!lastActive) return false;
        var last = new Date(lastActive);
        var now = new Date();
        var daysSince = Math.floor((now - last) / (1000*60*60*24));
        return daysSince >= 1;
    },

    // ==========================================
    // DAILY CHALLENGE SYSTEM
    // ==========================================
    getDailyChallenge() {
        var today = new Date().toISOString().split('T')[0];
        var saved = localStorage.getItem('lf_daily_challenge_date');
        
        if (saved === today) {
            return JSON.parse(localStorage.getItem('lf_daily_challenge') || 'null');
        }
        
        // Generate new challenge
        var challenges = [
            {type:'accuracy', target:80, title:'準確度挑戰', desc:'今日完成10題，正確率達80%以上！', reward:'速度之星'},
            {type:'streak_q', target:5, title:'連續答對', desc:'連續答對5題唔斷！', reward:'連擊之王'},
            {type:'trap', target:3, title:'陷阱獵人', desc:'今日避開3個陷阱題！', reward:'陷阱雷達'},
            {type:'speed', target:300, title:'速度挑戰', desc:'5分鐘內完成8題！', reward:'閃電俠'},
            {type:'boss', target:1, title:'Boss戰', desc:'打敗今日Boss（超難陷阱題）！', reward:'Boss殺手'},
            {type:'review', target:1, title:'複習之星', desc:'重做昨日錯題，全部答啱！', reward:'記憶大師'},
        ];
        
        // Use date hash to pick a consistent challenge for the day
        var hash = 0;
        for (var i = 0; i < today.length; i++) hash = ((hash<<5)-hash) + today.charCodeAt(i);
        var challenge = challenges[Math.abs(hash) % challenges.length];
        
        localStorage.setItem('lf_daily_challenge_date', today);
        localStorage.setItem('lf_daily_challenge', JSON.stringify(challenge));
        
        return challenge;
    },

    // ==========================================
    // GROUP RANKING (3-person class)
    // ==========================================
    getGroupRanking() {
        // In production, this would fetch from Firebase
        // For demo: simulate 3 students
        var demo = [
            {name:'你', score:parseInt(localStorage.getItem('lf_points')||'847'), avatar:'👦'},
            {name:'隊友A', score:920, avatar:'👧'},
            {name:'隊友B', score:780, avatar:'👦'},
        ];
        demo.sort(function(a,b){return b.score - a.score});
        return demo;
    },

    // ==========================================
    // BOSS BATTLE SYSTEM
    // ==========================================
    getBossStatus() {
        var bossHP = parseInt(localStorage.getItem('lf_boss_hp') || '100');
        var bossLevel = parseInt(localStorage.getItem('lf_boss_level') || '1');
        var bossName = this.getBossName(bossLevel);
        
        return {
            name: bossName,
            level: bossLevel,
            hp: bossHP,
            maxHP: 100 + (bossLevel-1)*20,
            defeated: bossHP <= 0,
            trapType: 'T' + ((bossLevel % 10) || 10),
        };
    },

    getBossName(level) {
        var names = ['進位怪獸','小數惡魔','運算幽靈','零之影','分數巨龍',
                     '百分數女巫','圖形石像鬼','面積魔像','體積巨人','終極陷阱王'];
        return names[(level-1) % names.length];
    },

    damageBoss(damage) {
        var hp = parseInt(localStorage.getItem('lf_boss_hp') || '100');
        hp = Math.max(0, hp - damage);
        localStorage.setItem('lf_boss_hp', hp.toString());
        
        if (hp <= 0) {
            var level = parseInt(localStorage.getItem('lf_boss_level') || '1');
            localStorage.setItem('lf_boss_level', (level+1).toString());
            localStorage.setItem('lf_boss_hp', (100 + level*20).toString());
            return {defeated: true, newLevel: level+1};
        }
        return {defeated: false, remainingHP: hp};
    },

    // ==========================================
    // COME BACK TOMORROW HOOKS
    // ==========================================
    getTomorrowHook() {
        var streak = this.getStreak();
        var hooks = [];
        
        if (streak === 2) {
            hooks.push({priority:1, text:'聽日連續第3日！解鎖「🔥新手獵人」勳章 + 50分！', icon:'🔥'});
        } else if (streak === 6) {
            hooks.push({priority:1, text:'聽日連續第7日！解鎖「⚡連續一週」勳章 + 150分！', icon:'⚡'});
        } else if (streak >= 1) {
            hooks.push({priority:2, text:'聽日繼續簽到，保持你嘅'+streak+'日連續記錄！', icon:'📅'});
        }
        
        // Daily challenge hook
        hooks.push({priority:3, text:'聽日有新嘅每日挑戰等緊你！', icon:'🎯'});
        
        // Boss hook
        var boss = this.getBossStatus();
        if (!boss.defeated) {
            hooks.push({priority:1, text:'「'+boss.name+'」仲有'+boss.hp+'HP！聽日返嚟打低佢！', icon:'👾'});
        }
        
        hooks.sort(function(a,b){return a.priority - b.priority});
        return hooks.slice(0, 3);
    },

    // ==========================================
    // RENDER: Streak Bar
    // ==========================================
    renderStreakBar(containerId) {
        var streak = this.getStreak();
        var milestones = this.config.streakMilestones;
        var nextMilestone = milestones.find(function(m){return m > streak}) || 100;
        var progress = Math.min(100, (streak / nextMilestone) * 100);
        
        var html = '<div class="lf-streak-bar">';
        html += '<div class="lf-streak-header">';
        html += '<span class="lf-streak-count">'+streak+'日連續簽到</span>';
        html += '<span class="lf-streak-next">下個目標：'+nextMilestone+'日</span>';
        html += '</div>';
        html += '<div class="lf-streak-track"><div class="lf-streak-fill" style="width:'+progress+'%"></div></div>';
        
        // Milestone markers
        html += '<div class="lf-streak-milestones">';
        milestones.forEach(function(m){
            var reached = streak >= m;
            html += '<div class="lf-milestone '+(reached?'reached':'')+'">';
            html += '<div class="lf-milestone-dot"></div>';
            html += '<div class="lf-milestone-label">'+m+'日</div>';
            html += '</div>';
        });
        html += '</div></div>';
        
        if (containerId) {
            document.getElementById(containerId).innerHTML = html;
        }
        return html;
    },

    // ==========================================
    // RENDER: Group Ranking
    // ==========================================
    renderGroupRanking(containerId) {
        var ranking = this.getGroupRanking();
        var html = '<div class="lf-ranking">';
        html += '<h3>👥 小組排名（3人班）</h3>';
        
        ranking.forEach(function(p, i){
            var medal = i === 0 ? '🥇' : i === 1 ? '🥈' : '🥉';
            var bg = i === 0 ? '#FEF3C7' : i === 1 ? '#F3F4F6' : '#FAFAFA';
            var isMe = p.name === '你';
            html += '<div class="lf-rank-item" style="background:'+bg+'">';
            html += '<span class="lf-rank-pos">'+medal+'</span>';
            html += '<span class="lf-rank-name">'+p.avatar+' '+(isMe?'<b>'+p.name+'</b>':p.name)+'</span>';
            html += '<span class="lf-rank-score">'+p.score+'分</span>';
            html += '</div>';
        });
        html += '</div>';
        
        if (containerId) {
            document.getElementById(containerId).innerHTML = html;
        }
        return html;
    },

    // ==========================================
    // RENDER: Daily Challenge Card
    // ==========================================
    renderDailyChallenge(containerId) {
        var challenge = this.getDailyChallenge();
        var html = '<div class="lf-daily-challenge">';
        html += '<div class="lf-dc-header">🎯 今日挑戰</div>';
        html += '<div class="lf-dc-title">'+challenge.title+'</div>';
        html += '<div class="lf-dc-desc">'+challenge.desc+'</div>';
        html += '<div class="lf-dc-reward">完成獎勵：'+challenge.reward+'</div>';
        html += '<button class="lf-dc-btn" onclick="location.href=\'trap-quiz.html\'">接受挑戰 →</button>';
        html += '</div>';
        
        if (containerId) {
            document.getElementById(containerId).innerHTML = html;
        }
        return html;
    },

    // ==========================================
    // RENDER: Boss Battle Card
    // ==========================================
    renderBossCard(containerId) {
        var boss = this.getBossStatus();
        var hpPercent = (boss.hp / boss.maxHP) * 100;
        var hpColor = hpPercent > 50 ? '#16A34A' : hpPercent > 25 ? '#F59E0B' : '#DC2626';
        
        var html = '<div class="lf-boss-card">';
        if (boss.defeated) {
            html += '<div class="lf-boss-defeated">';
            html += '<div class="lf-boss-icon">🎉</div>';
            html += '<div>你打敗咗「'+boss.name+'」！</div>';
            html += '<div style="font-size:11px;color:#6B7280">新Boss聽日出現...</div>';
            html += '</div>';
        } else {
            html += '<div class="lf-boss-alive">';
            html += '<div class="lf-boss-icon">👾</div>';
            html += '<div class="lf-boss-name">Lv.'+boss.level+' '+boss.name+'</div>';
            html += '<div class="lf-boss-hp-bar"><div class="lf-boss-hp-fill" style="width:'+hpPercent+'%;background:'+hpColor+'"></div></div>';
            html += '<div class="lf-boss-hp-text">HP: '+boss.hp+'/'+boss.maxHP+'</div>';
            html += '<button class="lf-boss-btn" onclick="location.href=\'kids-boss-battle.html\'">⚔️ 攻擊！</button>';
            html += '</div>';
        }
        html += '</div>';
        
        if (containerId) {
            document.getElementById(containerId).innerHTML = html;
        }
        return html;
    },

    // ==========================================
    // RENDER: Tomorrow Hook
    // ==========================================
    renderTomorrowHook(containerId) {
        var hooks = this.getTomorrowHook();
        if (hooks.length === 0) return '';
        
        var html = '<div class="lf-tomorrow-hook">';
        html += '<div class="lf-th-title">💡 聽日返嚟可以...</div>';
        hooks.forEach(function(h){
            html += '<div class="lf-th-item">';
            html += '<span class="lf-th-icon">'+h.icon+'</span>';
            html += '<span>'+h.text+'</span>';
            html += '</div>';
        });
        html += '</div>';
        
        if (containerId) {
            document.getElementById(containerId).innerHTML = html;
        }
        return html;
    },

    // ==========================================
    // FULL GAMIFICATION DASHBOARD
    // ==========================================
    renderFullGamification(containerId) {
        var html = '';
        html += this.renderStreakBar();
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:12px 0">';
        html += this.renderDailyChallenge();
        html += this.renderBossCard();
        html += '</div>';
        html += this.renderGroupRanking();
        html += this.renderTomorrowHook();
        
        if (containerId) {
            document.getElementById(containerId).innerHTML = html;
        }
        return html;
    }
};

// ==========================================
// AUTO-INIT: Record activity on any page load
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    var result = LFGame.recordActivity();
    
    // Show milestone toast if triggered
    if (result.milestone) {
        var toast = document.createElement('div');
        toast.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#1A3C6D,#C9A84C);color:white;padding:16px 24px;border-radius:16px;z-index:9999;font-size:14px;font-weight:700;box-shadow:0 4px 20px rgba(0,0,0,0.3);animation:lfSlideDown 0.5s ease';
        toast.innerHTML = '<div style="font-size:28px">'+result.milestone.badge.split(' ')[0]+'</div>'+
            '<div>'+result.milestone.badge+' 解鎖！</div>'+
            '<div style="font-size:12px;opacity:0.8">'+result.milestone.msg+'</div>'+
            '<div style="font-size:11px;opacity:0.6;margin-top:4px">+'+result.milestone.points+'分</div>';
        document.body.appendChild(toast);
        setTimeout(function(){toast.style.opacity='0';toast.style.transition='opacity 0.5s';setTimeout(function(){toast.remove()},500)},4000);
        
        // Add animation keyframes
        var style = document.createElement('style');
        style.textContent = '@keyframes lfSlideDown{from{opacity:0;transform:translateX(-50%) translateY(-30px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}';
        document.head.appendChild(style);
    }
    
    console.log('[LF Game] Streak: ' + result.streak + ' | New day: ' + result.isNewDay);
});

// ==========================================
// CSS Injection
// ==========================================
(function injectStyles() {
    var css = `
.lf-streak-bar{background:white;border-radius:14px;padding:16px;margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
.lf-streak-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.lf-streak-count{font-weight:900;font-size:16px;color:#1A3C6D}
.lf-streak-next{font-size:11px;color:#6B7280}
.lf-streak-track{height:8px;background:#E5E7EB;border-radius:4px;overflow:hidden;margin:8px 0}
.lf-streak-fill{height:100%;background:linear-gradient(90deg,#F59E0B,#DC2626);border-radius:4px;transition:width 0.5s ease}
.lf-streak-milestones{display:flex;justify-content:space-between;padding:0 2px}
.lf-milestone{text-align:center;position:relative}
.lf-milestone-dot{width:8px;height:8px;border-radius:50%;background:#D1D5DB;margin:0 auto 2px}
.lf-milestone.reached .lf-milestone-dot{background:#16A34A;box-shadow:0 0 6px rgba(22,163,74,0.4)}
.lf-milestone-label{font-size:9px;color:#9CA3AF}
.lf-milestone.reached .lf-milestone-label{color:#16A34A;font-weight:700}

.lf-ranking{background:white;border-radius:14px;padding:16px;margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
.lf-ranking h3{font-size:14px;color:#1A3C6D;margin-bottom:10px}
.lf-rank-item{display:flex;align-items:center;padding:10px 12px;border-radius:10px;margin-bottom:6px;gap:10px}
.lf-rank-pos{font-size:20px;min-width:28px}
.lf-rank-name{flex:1;font-size:13px}
.lf-rank-score{font-weight:900;font-size:14px;color:#1A3C6D}

.lf-daily-challenge{background:linear-gradient(135deg,#FFFDF5,#FFFBEB);border:2px solid #C9A84C;border-radius:14px;padding:14px}
.lf-dc-header{font-size:11px;color:#92400E;margin-bottom:2px}
.lf-dc-title{font-weight:900;font-size:15px;color:#1A3C6D;margin-bottom:4px}
.lf-dc-desc{font-size:11px;color:#6B7280;margin-bottom:6px}
.lf-dc-reward{font-size:10px;color:#16A34A;margin-bottom:8px}
.lf-dc-btn{width:100%;padding:10px;background:#1A3C6D;color:white;border:none;border-radius:8px;font-size:13px;font-weight:700;cursor:pointer}

.lf-boss-card{background:white;border-radius:14px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,0.04)}
.lf-boss-defeated{text-align:center;font-size:13px;color:#16A34A}
.lf-boss-icon{font-size:32px;margin-bottom:4px}
.lf-boss-name{font-weight:900;font-size:14px;color:#1A3C6D;margin-bottom:6px}
.lf-boss-hp-bar{height:6px;background:#E5E7EB;border-radius:3px;overflow:hidden;margin:6px 0}
.lf-boss-hp-fill{height:100%;border-radius:3px;transition:width 0.3s}
.lf-boss-hp-text{font-size:10px;color:#6B7280}
.lf-boss-btn{width:100%;padding:8px;background:#DC2626;color:white;border:none;border-radius:8px;font-size:12px;font-weight:700;cursor:pointer;margin-top:8px}

.lf-tomorrow-hook{background:linear-gradient(135deg,#F0FDF4,#DCFCE7);border:1px solid #BBF7D0;border-radius:14px;padding:14px;margin:12px 0}
.lf-th-title{font-weight:700;font-size:13px;color:#065F46;margin-bottom:8px}
.lf-th-item{display:flex;align-items:center;gap:8px;font-size:12px;color:#374151;padding:4px 0}
.lf-th-icon{font-size:18px;min-width:24px}
`;
    var style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
})();

console.log('LF Gamification Engine v2.0 loaded - streaks, ranking, bosses, daily challenges');
