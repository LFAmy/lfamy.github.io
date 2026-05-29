
// LF Gamification Engine v1.0 — XP, levels, badges (35), monsters, boss battles, daily quests, power-ups
var LFG = {
  _state: null,

  // --- DEFAULT STATE ---
  _defaultState: function() {
    return {
      xp: 0, level: 1, totalCorrect: 0, totalWrong: 0, totalQuestions: 0,
      currentStreak: 0, bestStreak: 0, fastestMs: 999999,
      lastActiveDate: null, joinDate: new Date().toISOString(),
      trapDefeats: {T1:0,T2:0,T3:0,T4:0,T5:0,T6:0,T7:0,T8:0,T9:0,T10:0},
      badges: {},
      bossDefeats: {},
      dailyQuests: [], dailyQuestDate: null, dailyQuestsDone: 0,
      weeklyQuests: [], weeklyQuestDate: null,
      powerUps: {doubleXp:0, hint:0, skip:0, timeFreeze:0},
      activePowerUp: null, powerUpExpiry: null,
      monsterStages: {T1:0,T2:0,T3:0,T4:0,T5:0,T6:0,T7:0,T8:0,T9:0,T10:0},
      title: '', profileFrame: 'default',
      nightOwls: 0, earlyBirds: 0, weekendWarrior: 0,
      storyChaptersDone: []
    };
  },

  // --- LEVEL THRESHOLDS (XP needed per level, 1-50) ---
  _levelXp: (function() {
    var thresholds = [0];
    for (var i = 1; i <= 50; i++) {
      thresholds.push(Math.floor(100 * Math.pow(1.45, i - 1)));
    }
    return thresholds;
  })(),

  // --- MONSTER DEFINITIONS (10 trap types) ---
  monsters: {
    T1: {name:'進退位怪獸', emoji:'👾', stages:['👾 幼體','🦠 成長體','🐲 完全體'], color:'#FF6B6B'},
    T2: {name:'單位換算龍', emoji:'🐉', stages:['🐍 幼體','🦎 成長體','🐉 完全體'], color:'#4ECDC4'},
    T3: {name:'運算順序機械人', emoji:'🤖', stages:['⚙️ 幼體','🦾 成長體','🤖 完全體'], color:'#45B7D1'},
    T4: {name:'漏寫0幽靈', emoji:'👻', stages:['💨 幼體','🌫️ 成長體','👻 完全體'], color:'#A78BFA'},
    T5: {name:'分數怪獸', emoji:'🍕', stages:['🍕 幼體','🥧 成長體','🎂 完全體'], color:'#F59E0B'},
    T6: {name:'百分數Boss', emoji:'💯', stages:['💯 幼體','📊 成長體','🏦 完全體'], color:'#DC2626'},
    T7: {name:'應用題迷宮', emoji:'📖', stages:['📄 幼體','📋 成長體','📖 完全體'], color:'#8B5CF6'},
    T8: {name:'圖形守護者', emoji:'📐', stages:['📏 幼體','🔷 成長體','📐 完全體'], color:'#059669'},
    T9: {name:'時間換算獸', emoji:'⏰', stages:['⏱ 幼體','🕐 成長體','⏰ 完全體'], color:'#EC4899'},
    T10:{name:'餘數幽靈', emoji:'🔮', stages:['💠 幼體','🌀 成長體','🔮 完全體'], color:'#7C3AED'}
  },

  // --- BADGE DEFINITIONS (35) ---
  badgeDefs: {
    streak_3:  {id:'streak_3',  name:'三日連擊',   desc:'連續3日練習',    icon:'🔥', cat:'streak',  rarity:'common'},
    streak_7:  {id:'streak_7',  name:'一週之王',   desc:'連續7日練習',    icon:'🔥', cat:'streak',  rarity:'uncommon'},
    streak_14: {id:'streak_14', name:'雙週戰士',   desc:'連續14日練習',   icon:'💪', cat:'streak',  rarity:'rare'},
    streak_30: {id:'streak_30', name:'月之傳說',   desc:'連續30日練習',   icon:'💎', cat:'streak',  rarity:'epic'},
    streak_60: {id:'streak_60', name:'學期霸主',   desc:'連續60日練習',   icon:'👑', cat:'streak',  rarity:'legendary'},
    streak_100:{id:'streak_100',name:'不朽傳奇',   desc:'連續100日練習',  icon:'🏆', cat:'streak',  rarity:'mythic'},
    speed_30s: {id:'speed_30s', name:'快槍手',     desc:'平均作答時間<30秒', icon:'⚡', cat:'speed', rarity:'common'},
    speed_15s: {id:'speed_15s', name:'閃電俠',     desc:'平均作答時間<15秒', icon:'⚡', cat:'speed', rarity:'uncommon'},
    speed_10s: {id:'speed_10s', name:'速算王',     desc:'平均作答時間<10秒', icon:'💨', cat:'speed', rarity:'rare'},
    speed_5s:  {id:'speed_5s',  name:'秒殺達人',   desc:'單題作答<5秒',   icon:'💥', cat:'speed',  rarity:'epic'},
    acc_80:    {id:'acc_80',    name:'神射手',     desc:'20題+正確率達80%', icon:'🎯', cat:'accuracy', rarity:'common'},
    acc_90:    {id:'acc_90',    name:'狙擊手',     desc:'20題+正確率達90%', icon:'🎯', cat:'accuracy', rarity:'uncommon'},
    acc_95:    {id:'acc_95',    name:'精英射手',   desc:'20題+正確率達95%', icon:'🎯', cat:'accuracy', rarity:'rare'},
    acc_100:   {id:'acc_100',   name:'完美主義者', desc:'10題全部正確',   icon:'⭐', cat:'accuracy', rarity:'epic'},
    vol_50:    {id:'vol_50',    name:'初心者',     desc:'完成50題練習',   icon:'📝', cat:'volume', rarity:'common'},
    vol_100:   {id:'vol_100',   name:'練習生',     desc:'完成100題練習',  icon:'📝', cat:'volume', rarity:'uncommon'},
    vol_500:   {id:'vol_500',   name:'學霸',       desc:'完成500題練習',  icon:'📚', cat:'volume', rarity:'rare'},
    vol_1000:  {id:'vol_1000',  name:'題庫終結者', desc:'完成1000題練習', icon:'💪', cat:'volume', rarity:'epic'},
    vol_5000:  {id:'vol_5000',  name:'永恆傳說',   desc:'完成5000題練習', icon:'🗿', cat:'volume', rarity:'legendary'},
    trap_T1:   {id:'trap_T1',   name:'進退位剋星', desc:'擊敗進退位怪獸20次', icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T2:   {id:'trap_T2',   name:'單位換算剋星',desc:'擊敗單位換算龍20次', icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T3:   {id:'trap_T3',   name:'運算順序剋星',desc:'擊敗運算機械人20次', icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T4:   {id:'trap_T4',   name:'漏寫0剋星',  desc:'擊敗漏寫0幽靈20次', icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T5:   {id:'trap_T5',   name:'分數剋星',   desc:'擊敗分數怪獸20次',  icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T6:   {id:'trap_T6',   name:'百分數剋星', desc:'擊敗百分數Boss20次', icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T7:   {id:'trap_T7',   name:'應用題剋星', desc:'擊敗應用題迷宮20次', icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T8:   {id:'trap_T8',   name:'圖形剋星',   desc:'擊敗圖形守護者20次', icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T9:   {id:'trap_T9',   name:'時間換算剋星',desc:'擊敗時間獸20次',   icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_T10:  {id:'trap_T10',  name:'餘數剋星',   desc:'擊敗餘數幽靈20次',  icon:'🎖', cat:'trap', rarity:'uncommon'},
    trap_master:{id:'trap_master',name:'陷阱大師',  desc:'全部10種陷阱各擊敗20次', icon:'🌟', cat:'trap', rarity:'legendary'},
    nightowl:  {id:'nightowl',  name:'夜貓子',     desc:'夜晚10點後練習5次', icon:'🦉', cat:'special', rarity:'uncommon'},
    earlybird: {id:'earlybird', name:'早起鳥',     desc:'早上7點前練習5次', icon:'🌅', cat:'special', rarity:'uncommon'},
    weekend:   {id:'weekend',   name:'周末戰士',   desc:'周末練習10次',    icon:'⚔️', cat:'special', rarity:'uncommon'},
    boss3:     {id:'boss3',     name:'Boss Slayer',desc:'擊敗3個Boss',   icon:'💀', cat:'special', rarity:'rare'},
    collector: {id:'collector', name:'怪獸收藏家', desc:'收集10隻怪獸',   icon:'🃏', cat:'special', rarity:'epic'},
    story_all: {id:'story_all', name:'故事之王',   desc:'通關故事模式全部章節', icon:'📖', cat:'special', rarity:'legendary'}
  },

  // --- DAILY QUEST POOL ---
  _dailyQuestPool: [
    {text:'做10題練習', check:function(s){return s._todayCorrect>=10}, xp:30},
    {text:'連續答對5題', check:function(s){return s._sessionBestStreak>=5}, xp:25},
    {text:'挑戰一個Boss', check:function(s){return s._bossDone}, xp:50},
    {text:'擊敗3次陷阱怪獸', check:function(s){return s._trapKills>=3}, xp:35},
    {text:'在30秒內完成一題', check:function(s){return s._fastest<30000}, xp:20},
    {text:'做5題分數練習', check:function(s){return s._trapDone.T5>=5}, xp:25},
    {text:'達到80%正確率', check:function(s){return s._todayCorrect/Math.max(s._todayTotal,1)>=0.8}, xp:30},
    {text:'完成一次5分鐘挑戰', check:function(s){return s._challengeDone}, xp:40},
    {text:'收集2隻怪獸', check:function(s){return s._monstersCaptured>=2}, xp:35},
    {text:'查看怪獸圖鑑', check:function(s){return s._monsterBoxOpened}, xp:15},
    {text:'答對3題不同陷阱類型', check:function(s){return s._trapTypes>=3}, xp:30},
    {text:'在早上練習', check:function(s){return s._morningDone}, xp:20},
    {text:'分享進度給家長', check:function(s){return s._shared}, xp:25},
    {text:'做3題應用題', check:function(s){return s._trapDone.T7>=3}, xp:30},
    {text:'連續答對3題同一陷阱', check:function(s){return s._sameTrapStreak>=3}, xp:25}
  ],

  // --- INIT ---
  init: function() {
    var saved = null;
    try { saved = JSON.parse(localStorage.getItem('lf_gamification')); } catch(e) {}
    this._state = saved || this._defaultState();
    if (!this._state._sessionVars) this._resetSession();
    this._checkDailyReset();
    this._checkBadges();
  },

  _resetSession: function() {
    this._state._sessionVars = true;
    this._state._todayCorrect = 0;
    this._state._todayTotal = 0;
    this._state._sessionBestStreak = 0;
    this._state._bossDone = false;
    this._state._trapKills = 0;
    this._state._fastest = 999999;
    this._state._challengeDone = false;
    this._state._monstersCaptured = 0;
    this._state._monsterBoxOpened = false;
    this._state._trapTypes = 0;
    this._state._morningDone = false;
    this._state._shared = false;
    this._state._sameTrapStreak = 0;
    this._state._trapDone = {T1:0,T2:0,T3:0,T4:0,T5:0,T6:0,T7:0,T8:0,T9:0,T10:0};
    this._state._lastTrap = null;
    this._save();
  },

  _save: function() {
    var copy = Object.assign({}, this._state);
    delete copy._sessionVars;
    localStorage.setItem('lf_gamification', JSON.stringify(copy));
    // Cloud sync
    if (typeof LFCloud !== 'undefined' && LFCloud.configured) {
      LFCloud.push({type: 'gamification', student_id: LFCloud._studentId, data: copy});
    }
  },

  // --- CORE: RECORD ANSWER ---
  recordAnswer: function(correct, trapType, timeMs) {
    var s = this._state;
    var today = new Date().toISOString().split('T')[0];

    // Streak tracking
    if (s.lastActiveDate !== today) {
      var yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      if (s.lastActiveDate === yesterday) {
        s.currentStreak++;
      } else if (s.lastActiveDate !== today) {
        s.currentStreak = 1;
      }
      s.lastActiveDate = today;
      s._todayCorrect = 0; s._todayTotal = 0;
      this._checkDailyReset();
    }

    s.totalQuestions++;
    s._todayTotal++;
    if (correct) {
      s.totalCorrect++;
      s._todayCorrect++;
      if (s.currentStreak > s.bestStreak) s.bestStreak = s.currentStreak;
      if (s._sessionBestStreak < (s.currentStreak || 0)) s._sessionBestStreak = s.currentStreak;

      // Per-trap tracking
      if (trapType && s.trapDefeats[trapType] !== undefined) {
        s.trapDefeats[trapType]++;
        s._trapKills++;
        if (!s._trapDone[trapType]) s._trapDone[trapType] = 0;
        s._trapDone[trapType]++;

        // Same trap streak
        if (s._lastTrap === trapType) { s._sameTrapStreak++; }
        else { s._sameTrapStreak = 1; s._lastTrap = trapType; s._trapTypes++; }

        // Monster evolution check
        var defs = s.trapDefeats[trapType];
        if (defs >= 50 && s.monsterStages[trapType] < 3) {
          s.monsterStages[trapType] = 3;
          this._fireEvent('monster_evolve', {trap: trapType, stage: 3});
          if (typeof LFCloud !== 'undefined' && LFCloud.configured) LFCloud.pushMonster(trapType, 3, defs);
        } else if (defs >= 30 && s.monsterStages[trapType] < 2) {
          s.monsterStages[trapType] = 2;
          this._fireEvent('monster_evolve', {trap: trapType, stage: 2});
          if (typeof LFCloud !== 'undefined' && LFCloud.configured) LFCloud.pushMonster(trapType, 2, defs);
        } else if (defs >= 10 && s.monsterStages[trapType] < 1) {
          s.monsterStages[trapType] = 1;
          s._monstersCaptured++;
          this._fireEvent('monster_evolve', {trap: trapType, stage: 1});
          if (typeof LFCloud !== 'undefined' && LFCloud.configured) LFCloud.pushMonster(trapType, 1, defs);
        }
      }

      // Speed tracking
      if (timeMs && timeMs < s.fastestMs) s.fastestMs = timeMs;
      if (timeMs && timeMs < s._fastest) s._fastest = timeMs;

      // Time-of-day badges
      var hour = new Date().getHours();
      if (hour >= 22) s.nightOwls++;
      if (hour < 7) s.earlyBirds++;
      var day = new Date().getDay();
      if (day === 0 || day === 6) s.weekendWarrior++;

      // XP gain
      var xp = 10;
      if (timeMs && timeMs < 10000) xp += 5; // Speed bonus
      if (s.currentStreak >= 7) xp *= 2; // Streak bonus
      if (s.activePowerUp === 'doubleXp' && Date.now() < s.powerUpExpiry) xp *= 2;
      this.addXP(xp);
    } else {
      s.totalWrong++;
      s.currentStreak = 0;
    }

    this._save();
    this._checkBadges();
    this._checkDailyComplete();
    return {xpGained: 10, leveledUp: false};
  },

  // --- XP & LEVELING ---
  addXP: function(amount) {
    var s = this._state;
    var oldLevel = s.level;
    s.xp += amount;
    while (s.level < 50 && s.xp >= this._levelXp[s.level]) {
      s.level++;
    }
    this._save();
    if (s.level > oldLevel) {
      this._fireEvent('level_up', {level: s.level, oldLevel: oldLevel});
      // Level rewards
      if (s.level === 5) this._unlockBadge('level_5');
      if (s.level === 10) this._unlockBadge('level_10');
      if (s.level === 25) this._unlockBadge('level_25');
      if (s.level === 50) this._unlockBadge('level_50');
    }
    return {leveledUp: s.level > oldLevel, newLevel: s.level};
  },

  getLevel: function() { return this._state.level; },
  getXP: function() { return this._state.xp; },
  getXPToNext: function() {
    var lv = this._state.level;
    return lv < 50 ? this._levelXp[lv] : 0;
  },
  getXPProgress: function() {
    var lv = this._state.level;
    if (lv >= 50) return 1;
    var current = this._levelXp[lv - 1] || 0;
    var next = this._levelXp[lv] || 1;
    return Math.min(1, (this._state.xp - current) / (next - current));
  },

  // --- BADGES ---
  _checkBadges: function() {
    var s = this._state;
    var checks = {
      streak_3: function() { return s.currentStreak >= 3; },
      streak_7: function() { return s.currentStreak >= 7; },
      streak_14: function() { return s.currentStreak >= 14; },
      streak_30: function() { return s.currentStreak >= 30; },
      streak_60: function() { return s.currentStreak >= 60; },
      streak_100: function() { return s.currentStreak >= 100; },
      vol_50: function() { return s.totalCorrect >= 50; },
      vol_100: function() { return s.totalCorrect >= 100; },
      vol_500: function() { return s.totalCorrect >= 500; },
      vol_1000: function() { return s.totalCorrect >= 1000; },
      vol_5000: function() { return s.totalCorrect >= 5000; },
      nightowl: function() { return s.nightOwls >= 5; },
      earlybird: function() { return s.earlyBirds >= 5; },
      weekend: function() { return s.weekendWarrior >= 10; },
    };
    // Trap hunter badges
    for (var t = 1; t <= 10; t++) {
      var key = 'T' + t;
      (function(k) {
        checks['trap_' + k] = function() { return s.trapDefeats[k] >= 20; };
      })(key);
    }
    // Trap master
    checks.trap_master = function() {
      for (var t = 1; t <= 10; t++) { if (s.trapDefeats['T' + t] < 20) return false; }
      return true;
    };
    // Boss
    checks.boss3 = function() { return Object.keys(s.bossDefeats).length >= 3; };
    checks.collector = function() {
      var count = 0;
      for (var t = 1; t <= 10; t++) { if (s.monsterStages['T' + t] >= 1) count++; }
      return count >= 10;
    };
    checks.story_all = function() { return s.storyChaptersDone.length >= 10; };

    var self = this;
    Object.keys(checks).forEach(function(badgeId) {
      if (!s.badges[badgeId] && checks[badgeId]()) {
        self._unlockBadge(badgeId);
      }
    });
  },

  _unlockBadge: function(badgeId) {
    var s = this._state;
    if (s.badges[badgeId]) return;
    s.badges[badgeId] = new Date().toISOString();
    this._save();
    this._fireEvent('badge_unlock', {badge: badgeId, def: this.badgeDefs[badgeId]});
    // Cloud sync badge
    if (typeof LFCloud !== 'undefined' && LFCloud.configured) {
      LFCloud.pushBadge(badgeId, this.badgeDefs[badgeId] ? this.badgeDefs[badgeId].name : badgeId);
    }
    // Bonus XP for unlocking
    var rarityXp = {common:20, uncommon:50, rare:100, epic:250, legendary:500, mythic:1000};
    var def = this.badgeDefs[badgeId];
    if (def) this.addXP(rarityXp[def.rarity] || 20);
  },

  getBadges: function() {
    var s = this._state;
    var result = [];
    var self = this;
    Object.keys(this.badgeDefs).forEach(function(id) {
      result.push({
        id: id, def: self.badgeDefs[id],
        earned: !!s.badges[id],
        date: s.badges[id] || null
      });
    });
    return result;
  },

  getEarnedBadges: function() {
    return this.getBadges().filter(function(b) { return b.earned; });
  },

  // --- DAILY QUESTS ---
  _checkDailyReset: function() {
    var s = this._state;
    var today = new Date().toISOString().split('T')[0];
    if (s.dailyQuestDate !== today) {
      s.dailyQuestDate = today;
      s.dailyQuestsDone = 0;
      // Pick 3 random quests
      var pool = this._dailyQuestPool.slice();
      s.dailyQuests = [];
      for (var i = 0; i < 3 && pool.length > 0; i++) {
        var idx = Math.floor(Math.random() * pool.length);
        s.dailyQuests.push(pool.splice(idx, 1)[0]);
        s.dailyQuests[i].done = false;
      }
      this._save();
    }
  },

  getDailyQuests: function() { return this._state.dailyQuests || []; },

  _checkDailyComplete: function() {
    var s = this._state;
    var allDone = true;
    s.dailyQuests.forEach(function(q) {
      if (!q.done && q.check(s)) { q.done = true; s.dailyQuestsDone++; }
      if (!q.done) allDone = false;
    });
    if (allDone && s.dailyQuestsDone >= 3) {
      this.addXP(100); // Bonus for completing all 3
      this._fireEvent('daily_complete', {});
    }
    this._save();
  },

  // --- BOSS BATTLE ---
  startBossBattle: function(trapType) {
    return {
      trapType: trapType,
      bossHP: 5,
      questionsCorrect: 0,
      questionsWrong: 0,
      maxWrong: 3,
      active: true,
      monster: this.monsters[trapType]
    };
  },

  recordBossAnswer: function(battle, correct) {
    if (!battle.active) return battle;
    if (correct) {
      battle.questionsCorrect++;
      battle.bossHP = Math.max(0, battle.bossHP - 1);
    } else {
      battle.questionsWrong++;
    }
    if (battle.bossHP <= 0) {
      battle.active = false;
      battle.won = true;
      var s = this._state;
      s.bossDefeats[battle.trapType] = (s.bossDefeats[battle.trapType] || 0) + 1;
      s._bossDone = true;
      this.addXP(200);
      this._save();
      this._checkBadges();
    } else if (battle.questionsWrong >= battle.maxWrong) {
      battle.active = false;
      battle.won = false;
    }
    return battle;
  },

  // --- POWER-UPS ---
  usePowerUp: function(type) {
    var s = this._state;
    if (!s.powerUps[type] || s.powerUps[type] <= 0) return false;
    s.powerUps[type]--;
    s.activePowerUp = type;
    s.powerUpExpiry = Date.now() + 600000; // 10 minutes
    this._save();
    return true;
  },

  addPowerUp: function(type, amount) {
    this._state.powerUps[type] = (this._state.powerUps[type] || 0) + (amount || 1);
    this._save();
  },

  // --- PROFILE ---
  getTitle: function() {
    var s = this._state;
    if (s.level >= 50) return '數學之神';
    if (s.level >= 40) return '至尊學者';
    if (s.level >= 30) return '傳奇大師';
    if (s.level >= 25) return '精英導師';
    if (s.level >= 20) return '資深學者';
    if (s.level >= 15) return '高級學徒';
    if (s.level >= 10) return '中級學者';
    if (s.level >= 5) return '初級學徒';
    return '新手探險家';
  },

  getStats: function() {
    var s = this._state;
    return {
      level: s.level, xp: s.xp, xpToNext: this.getXPToNext(),
      xpProgress: this.getXPProgress(),
      totalQuestions: s.totalQuestions, totalCorrect: s.totalCorrect,
      accuracy: s.totalQuestions > 0 ? Math.round(s.totalCorrect / s.totalQuestions * 100) : 0,
      currentStreak: s.currentStreak, bestStreak: s.bestStreak,
      fastestMs: s.fastestMs < 999999 ? s.fastestMs : 0,
      badgesEarned: Object.keys(s.badges).length,
      title: this.getTitle(),
      monstersCaptured: Object.values(s.monsterStages).filter(function(v){return v>=1}).length,
      bossDefeats: Object.keys(s.bossDefeats).length
    };
  },

  // --- EVENT SYSTEM ---
  _listeners: {},
  on: function(event, fn) {
    if (!this._listeners[event]) this._listeners[event] = [];
    this._listeners[event].push(fn);
  },
  _fireEvent: function(event, data) {
    var fns = this._listeners[event] || [];
    fns.forEach(function(fn) { try { fn(data); } catch(e) {} });
  }
};

// Auto-init
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function() { LFG.init(); });
}
