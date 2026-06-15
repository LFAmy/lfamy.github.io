// ============================================================
// Engine: CLASS ANALYTICS (Heatmap + AI Recommendations)
// v15.0 EdTech AI · 班級分析引擎
// ============================================================
const ANALYTICS = {
  _data: {},
  
  recordResult(studentId, topicId, correct, attempt) {
    if (!this._data[topicId]) this._data[topicId] = { total: 0, correct: 0, students: {} };
    this._data[topicId].total++;
    if (correct) this._data[topicId].correct++;
    if (!this._data[topicId].students[studentId]) this._data[topicId].students[studentId] = { correct: 0, total: 0 };
    this._data[topicId].students[studentId].total++;
    if (correct) this._data[topicId].students[studentId].correct++;
    this._save();
  },
  
  getTopicAccuracy(topicId) {
    const d = this._data[topicId];
    if (!d || d.total === 0) return null;
    return { accuracy: Math.round(d.correct / d.total * 100), total: d.total, studentCount: Object.keys(d.students).length };
  },

  getHeatmap() {
    const map = {};
    for (const [topicId, d] of Object.entries(this._data)) {
      const acc = d.total > 0 ? d.correct / d.total : 0;
      let severity, color;
      if (acc < 0.4) { severity = 'critical'; color = '#EF4444'; }
      else if (acc < 0.6) { severity = 'warning'; color = '#F59E0B'; }
      else if (acc < 0.8) { severity = 'moderate'; color = '#3B82F6'; }
      else { severity = 'good'; color = '#10B981'; }
      map[topicId] = { accuracy: Math.round(acc*100), severity, color, attempts: d.total, students: Object.keys(d.students).length };
    }
    return map;
  },

  getRecommendations() {
    const hm = this.getHeatmap();
    const critical = [], warning = [];
    for (const [id, d] of Object.entries(hm)) {
      if (d.severity === 'critical') critical.push(id);
      else if (d.severity === 'warning') warning.push(id);
    }
    let text = '';
    if (critical.length > 0) text += 'u{1F534} 急需改善: ' + critical.join(', ') + '\n';
    if (warning.length > 0) text += 'u{1F7E1} 需要關注: ' + warning.join(', ') + '\n';
    if (critical.length === 0 && warning.length === 0) text = 'u{1F7E2} 整體表現良好，繼續保持！';
    return { critical, warning, text, heatmap: hm };
  },

  getStudentReport(studentId) {
    const report = {};
    for (const [topicId, d] of Object.entries(this._data)) {
      const sd = d.students[studentId];
      if (sd && sd.total > 0) report[topicId] = { accuracy: Math.round(sd.correct/sd.total*100), attempts: sd.total };
    }
    return report;
  },

  _save() { try { localStorage.setItem('lf_analytics', JSON.stringify(this._data)); } catch(e) {} },
  _load() { try { const s = localStorage.getItem('lf_analytics'); if (s) this._data = JSON.parse(s); } catch(e) { this._data = {}; } },
  init() { this._load(); return this; }
};
