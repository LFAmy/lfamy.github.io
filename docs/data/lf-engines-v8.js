/* ═══════════════════════════════════════════════════════
   霖楓學苑 · LF Academy v8.0 — Shared Engine Stubs
   2026-06-04 · GAMIFICATION · BKT · SRS · ANALYTICS
   Lightweight localStorage-backed implementations.
   ═══════════════════════════════════════════════════════ */

/* ── GAMIFICATION: 7-Level Badge System ── */
const GAMIFICATION = {
  _data: null,
  BADGES: [
    { name: '銅章', icon: '🥉', min: 0, color: '#CD7F32' },
    { name: '銀章', icon: '🥈', min: 100, color: '#C0C0C0' },
    { name: '金章', icon: '🥇', min: 300, color: '#FFD700' },
    { name: '白金章', icon: '📎', min: 600, color: '#E5E4E2' },
    { name: '鑽石章', icon: '💎', min: 1000, color: '#B9F2FF' },
    { name: '大師章', icon: '🏆', min: 2000, color: '#FF6B6B' },
    { name: '傳奇章', icon: '👑', min: 5000, color: '#FFD700' }
  ],

  _load() {
    if (this._data) return;
    try {
      this._data = JSON.parse(localStorage.getItem('lf_gamification') || '{"points":0,"streak":0,"maxStreak":0,"badges":[],"dailyDone":0,"dailyDate":"","dailyGoal":5}');
    } catch(e) {
      this._data = { points: 0, streak: 0, maxStreak: 0, badges: [], dailyDone: 0, dailyDate: '', dailyGoal: 5 };
    }
  },

  _save() {
    try { localStorage.setItem('lf_gamification', JSON.stringify(this._data)); } catch(e) {}
  },

  recordAnswer(correct) {
    this._load();
    this._data.points += correct ? 10 : 2;
    this._trackDaily();
    if (correct) {
      this._data.streak++;
      if (this._data.streak > this._data.maxStreak) this._data.maxStreak = this._data.streak;
      // Streak bonus
      let bonus = 0;
      if (this._data.streak >= 20) bonus = 5;
      else if (this._data.streak >= 10) bonus = 3;
      else if (this._data.streak >= 5) bonus = 1;
      if (bonus > 0) this._data.points += bonus;
    } else {
      this._data.streak = 0;
    }
    const newBadges = this._checkBadges();
    this._save();
    return {
      points: this._data.points,
      streak: this._data.streak,
      bonus: correct ? (this._data.streak >= 20 ? 5 : this._data.streak >= 10 ? 3 : this._data.streak >= 5 ? 1 : 0) : 0,
      correct,
      badge: this.getCurrentBadge(),
      daily: this.getDailyProgress(),
      newBadges
    };
  },

  _trackDaily() {
    const today = new Date().toISOString().slice(0, 10);
    if (this._data.dailyDate !== today) { this._data.dailyDate = today; this._data.dailyDone = 0; }
    this._data.dailyDone++;
  },

  _checkBadges() {
    const newBadges = [];
    for (const b of this.BADGES) {
      if (this._data.points >= b.min && !this._data.badges.includes(b.name)) {
        this._data.badges.push(b.name);
        newBadges.push(b);
      }
    }
    return newBadges;
  },

  getCurrentBadge() {
    this._load();
    let current = this.BADGES[0];
    for (const b of this.BADGES) { if (this._data.points >= b.min) current = b; }
    return current;
  },

  getDailyProgress() {
    this._load();
    return { done: this._data.dailyDone, goal: this._data.dailyGoal, pct: Math.min(100, Math.round(this._data.dailyDone / this._data.dailyGoal * 100)) };
  },

  getStats() {
    this._load();
    return {
      points: this._data.points,
      streak: this._data.streak,
      maxStreak: this._data.maxStreak,
      badge: this.getCurrentBadge(),
      daily: this.getDailyProgress(),
      badges: this._data.badges
    };
  }
};

/* ── BKT: Bayesian Knowledge Tracing ── */
const BKT = {
  _data: null,

  _load() {
    if (this._data) return;
    try { this._data = JSON.parse(localStorage.getItem('lf_bkt_data') || '{}'); } catch(e) { this._data = {}; }
  },

  _save() {
    try { localStorage.setItem('lf_bkt_data', JSON.stringify(this._data)); } catch(e) {}
  },

  getMastery(topicId) {
    this._load();
    const d = this._data[topicId] || { correct: 0, total: 0 };
    if (d.total === 0) return 0.5;
    return (d.correct + 1) / (d.total + 2);
  },

  record(topicId, correct) {
    this._load();
    if (!this._data[topicId]) this._data[topicId] = { correct: 0, total: 0, lastSeen: Date.now() };
    this._data[topicId].total++;
    if (correct) this._data[topicId].correct++;
    this._data[topicId].lastSeen = Date.now();
    this._save();
    return this.getMastery(topicId);
  },

  getRecommendation(topicId) {
    const m = this.getMastery(topicId);
    if (m > 0.85) return { level: 'mastered', action: '挑戰更難題目', color: '#10B981' };
    if (m > 0.6) return { level: 'practicing', action: '繼續練習鞏固', color: '#F59E0B' };
    return { level: 'relearn', action: '需要重新學習基礎', color: '#EF4444' };
  }
};

/* ── SRS: Spaced Repetition System ── */
const SRS = {
  _schedule: null,

  _load() {
    if (this._schedule) return;
    try { this._schedule = JSON.parse(localStorage.getItem('lf_srs_schedule') || '{}'); } catch(e) { this._schedule = {}; }
  },

  _save() {
    try { localStorage.setItem('lf_srs_schedule', JSON.stringify(this._schedule)); } catch(e) {}
  },

  record(topicId, correctRate) {
    this._load();
    const intervals = { critical: 86400000, weak: 259200000, moderate: 604800000, good: 1209600000 };
    let interval;
    if (correctRate < 0.5) interval = intervals.critical;
    else if (correctRate < 0.7) interval = intervals.weak;
    else if (correctRate < 0.85) interval = intervals.moderate;
    else interval = intervals.good;
    this._schedule[topicId] = { nextReview: Date.now() + interval, interval, correctRate, lastReviewed: Date.now() };
    this._save();
  },

  isDue(topicId) {
    this._load();
    const s = this._schedule[topicId];
    if (!s) return true;
    return Date.now() >= s.nextReview;
  },

  getDueTopics() {
    this._load();
    const due = [];
    for (const [id, s] of Object.entries(this._schedule)) {
      if (this.isDue(id)) {
        due.push({ topicId: id, correctRate: s.correctRate, daysSince: Math.round((Date.now() - s.lastReviewed) / 86400000), urgency: s.correctRate < 0.5 ? 'critical' : s.correctRate < 0.7 ? 'warning' : 'normal' });
      }
    }
    return due.sort((a, b) => a.correctRate - b.correctRate);
  }
};

/* ── ANALYTICS: Class Analytics ── */
const ANALYTICS = {
  _data: null,
  _load() { if (!this._data) { try { this._data = JSON.parse(localStorage.getItem('lf_analytics') || '{}'); } catch(e) { this._data = {}; } } },
  _save() { try { localStorage.setItem('lf_analytics', JSON.stringify(this._data)); } catch(e) {} },
  recordResult(studentId, topicId, correct) {
    this._load();
    if (!this._data[topicId]) this._data[topicId] = { total: 0, correct: 0, students: {} };
    this._data[topicId].total++;
    if (correct) this._data[topicId].correct++;
    this._save();
  }
};

console.log('[LF Engines v8.0] GAMIFICATION + BKT + SRS + ANALYTICS ready');
