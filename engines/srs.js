// ============================================================
// Engine: SRS (Spaced Repetition System)
// v15.0 EdTech AI · 間隔複習引擎
// ============================================================
const SRS = {
  _schedule: {},
  INTERVALS: {
    critical: 1 * 24 * 60 * 60 * 1000,
    weak: 3 * 24 * 60 * 60 * 1000,
    moderate: 7 * 24 * 60 * 60 * 1000,
    good: 14 * 24 * 60 * 60 * 1000,
  },
  record(topicId, correctRate) {
    let interval;
    if (correctRate < 0.5) interval = this.INTERVALS.critical;
    else if (correctRate < 0.7) interval = this.INTERVALS.weak;
    else if (correctRate < 0.85) interval = this.INTERVALS.moderate;
    else interval = this.INTERVALS.good;
    this._schedule[topicId] = { nextReview: Date.now()+interval, interval, correctRate, lastReviewed: Date.now() };
    this._save();
    return this.getSchedule(topicId);
  },
  isDue(topicId) {
    const s = this._schedule[topicId];
    if (!s) return true;
    return Date.now() >= s.nextReview;
  },
  getDueTopics() {
    const due = [];
    for (const [id, s] of Object.entries(this._schedule)) {
      if (this.isDue(id)) due.push({ topicId: id, correctRate: s.correctRate, daysSince: Math.round((Date.now()-s.lastReviewed)/86400000), urgency: s.correctRate<0.5?'critical':s.correctRate<0.7?'warning':'normal' });
    }
    return due.sort((a,b)=>a.correctRate-b.correctRate);
  },
  getTimeUntilReview(topicId) {
    const s = this._schedule[topicId];
    if (!s) return { due: true, hours: 0 };
    const r = s.nextReview - Date.now();
    return { due: r<=0, hours: Math.max(0,Math.round(r/3600000)), days: Math.max(0,Math.round(r/86400000)) };
  },
  getSchedule(topicId) { return this._schedule[topicId] || null; },
  getAllSchedules() {
    const r = {};
    for (const [id, s] of Object.entries(this._schedule)) r[id] = { ...s, ...this.getTimeUntilReview(id) };
    return r;
  },
  _save() { try { localStorage.setItem('lf_srs_schedule', JSON.stringify(this._schedule)); } catch(e) {} },
  _load() { try { const s = localStorage.getItem('lf_srs_schedule'); if (s) this._schedule = JSON.parse(s); } catch(e) { this._schedule = {}; } },
  init() { this._load(); return this; }
};
