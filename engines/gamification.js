// ============================================================
// Engine: GAMIFICATION (7-Level Badge System)
// v15.0 EdTech AI · 遊戲化引擎
// ============================================================
const GAMIFICATION = {
  _data: { points: 0, streak: 0, maxStreak: 0, lastActive: null, badges: [], dailyGoal: 5, dailyDone: 0, dailyDate: '' },
  BADGES: [
    { name: '銅章', icon: 'u{1F949}', min: 0, color: '#CD7F32' },
    { name: '銀章', icon: 'u{1F948}', min: 100, color: '#C0C0C0' },
    { name: '金章', icon: 'u{1F947}', min: 300, color: '#FFD700' },
    { name: '白金章', icon: 'u{1F4CE}', min: 600, color: '#E5E4E2' },
    { name: '鑽石章', icon: 'u{1F48E}', min: 1000, color: '#B9F2FF' },
    { name: '大師章', icon: 'u{1F3C6}', min: 2000, color: '#FF6B6B' },
    { name: '傳奇章', icon: 'u{1F451}', min: 5000, color: '#FFD700' },
  ],
  addPoints(amount) {
    this._data.points += amount;
    this._checkBadges();
    this._save();
    return { points: this._data.points, newBadges: this._newBadges || [] };
  },
  recordAnswer(correct) {
    this._data.points += correct ? 10 : 2;
    this._trackDaily();
    if (correct) { this._data.streak++; if (this._data.streak > this._data.maxStreak) this._data.maxStreak = this._data.streak; }
    else { this._data.streak = 0; }
    this._data.lastActive = new Date().toISOString();
    const bonus = this._getStreakBonus();
    if (bonus > 0) this._data.points += bonus;
    this._checkBadges();
    this._save();
    return { points: this._data.points, streak: this._data.streak, bonus, correct, newBadges: this._newBadges || [] };
  },
  _getStreakBonus() {
    if (this._data.streak >= 20) return 5;
    if (this._data.streak >= 10) return 3;
    if (this._data.streak >= 5) return 1;
    return 0;
  },
  _trackDaily() {
    const today = new Date().toISOString().slice(0,10);
    if (this._data.dailyDate !== today) { this._data.dailyDate = today; this._data.dailyDone = 0; }
    this._data.dailyDone++;
  },
  getDailyProgress() {
    return { done: this._data.dailyDone, goal: this._data.dailyGoal, pct: Math.min(100, Math.round(this._data.dailyDone/this._data.dailyGoal*100)) };
  },
  _checkBadges() {
    this._newBadges = [];
    for (const b of this.BADGES) {
      if (this._data.points >= b.min && !this._data.badges.includes(b.name)) {
        this._data.badges.push(b.name);
        this._newBadges.push(b);
      }
    }
  },
  getCurrentBadge() {
    let current = this.BADGES[0];
    for (const b of this.BADGES) { if (this._data.points >= b.min) current = b; }
    return current;
  },
  getNextBadge() {
    for (const b of this.BADGES) { if (this._data.points < b.min) return b; }
    return null;
  },
  getStats() {
    return {
      points: this._data.points,
      streak: this._data.streak,
      maxStreak: this._data.maxStreak,
      badge: this.getCurrentBadge(),
      nextBadge: this.getNextBadge(),
      daily: this.getDailyProgress(),
      badges: this._data.badges
    };
  },
  _save() { try { localStorage.setItem('lf_gamification', JSON.stringify(this._data)); } catch(e) {} },
  _load() { try { const s = localStorage.getItem('lf_gamification'); if (s) this._data = { ...this._data, ...JSON.parse(s) }; } catch(e) {} },
  init() { this._load(); return this; }
};
