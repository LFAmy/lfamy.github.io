// ============================================================
// Engine: BKT (Bayesian Knowledge Tracing)
// v15.0 EdTech AI · 自適應難度引擎
// ============================================================
const BKT = {
  _data: {},
  getMastery(topicId) {
    const d = this._data[topicId] || { correct: 0, total: 0 };
    if (d.total === 0) return 0.5;
    return (d.correct + 1) / (d.total + 2);
  },
  getConfidence(topicId) {
    const d = this._data[topicId] || { total: 0 };
    if (d.total < 3) return 'low';
    if (d.total <= 7) return 'medium';
    return 'high';
  },
  getRecommendation(topicId) {
    const m = this.getMastery(topicId);
    if (m > 0.85) return { level: 'mastered', action: '挑戰更難題目', color: '#10B981' };
    if (m > 0.6) return { level: 'practicing', action: '繼續練習鞏固', color: '#F59E0B' };
    return { level: 'relearn', action: '需要重新學習基礎', color: '#EF4444' };
  },
  record(topicId, correct) {
    if (!this._data[topicId]) this._data[topicId] = { correct: 0, total: 0, lastSeen: Date.now() };
    this._data[topicId].total++;
    if (correct) this._data[topicId].correct++;
    this._data[topicId].lastSeen = Date.now();
    this._save();
    return this.getMastery(topicId);
  },
  getAllMastery() {
    const result = {};
    for (const [id, d] of Object.entries(this._data)) {
      result[id] = { mastery: Math.round(this.getMastery(id)*100), attempts: d.total, confidence: this.getConfidence(id), recommendation: this.getRecommendation(id) };
    }
    return result;
  },
  selectDifficulty(topicId, questions) {
    if (!questions || questions.length === 0) return questions;
    const rec = this.getRecommendation(topicId);
    let filtered;
    if (rec.level === 'mastered') {
      filtered = questions.filter(q => q.diff === 'u2605u2605u2605' || q.diff === 'u2605u2605');
      if (filtered.length === 0) filtered = questions;
    } else if (rec.level === 'relearn') {
      filtered = questions.filter(q => q.diff === 'u2605' || q.diff === 'u2605u2605');
      if (filtered.length === 0) filtered = questions;
    } else { filtered = questions; }
    return filtered;
  },
  _save() { try { localStorage.setItem('lf_bkt_data', JSON.stringify(this._data)); } catch(e) {} },
  _load() { try { const s = localStorage.getItem('lf_bkt_data'); if (s) this._data = JSON.parse(s); } catch(e) { this._data = {}; } },
  init() { this._load(); return this; }
};
