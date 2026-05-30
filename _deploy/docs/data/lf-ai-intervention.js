/**
 * LF AI Intervention Engine v1.0
 * 智能干預引擎 — 自動檢測學習危機，生成干預建議
 * 
 * Monitors student progress, detects learning crises,
 * and auto-generates intervention recommendations.
 * 
 * Integrates with: lf-adaptive-engine.js, lf-sspa-widget.js
 * Usage: <script src="/docs/data/lf-ai-intervention.js"></script>
 */
const LFAIIntervention = (() => {
  const STORAGE_KEY = 'lf_intervention_log';
  const THRESHOLDS = {
    mastery_drop: 0.3,      // 30% drop triggers alert
    streak_fail: 3,          // 3 consecutive failures
    inactivity_days: 7,      // 7 days no practice
    sspa_band_drop: 1,       // Drop 1 band level
    accuracy_below: 0.5,     // Below 50% accuracy
  };

  let _interventions = [];
  let _lastCheck = null;

  function init() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try { _interventions = JSON.parse(saved); } catch(e) {}
    }
    console.log('[AI-Intervention] Initialized,', _interventions.length, 'historical interventions');
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(_interventions.slice(-50)));
  }

  /**
   * Run a full diagnostic and generate interventions
   * @param {Object} studentData - { name, trapMastery, recentScores, lastActive, sspaPrediction }
   * @returns {Array} New interventions generated
   */
  function analyze(studentData = {}) {
    const newInterventions = [];
    const now = Date.now();
    _lastCheck = now;

    const traps = studentData.trapMastery || {};
    const recentScores = studentData.recentScores || [];
    const lastActive = studentData.lastActive || now;
    const sspaPrediction = studentData.sspaPrediction || {};

    // Check 1: Inactivity alert
    const daysInactive = (now - lastActive) / (1000 * 60 * 60 * 24);
    if (daysInactive > THRESHOLDS.inactivity_days) {
      newInterventions.push({
        type: 'inactivity',
        severity: daysInactive > 14 ? 'critical' : 'warning',
        title: `學習中斷 ${Math.floor(daysInactive)} 天`,
        message: `${studentData.name || '學生'} 已 ${Math.floor(daysInactive)} 天未有練習記錄。建議發送提醒訊息。`,
        action: 'send_reminder',
        actionLabel: '發送提醒',
        timestamp: now
      });
    }

    // Check 2: Mastery drop
    let droppedTraps = [];
    for (const [trap, level] of Object.entries(traps)) {
      if (typeof level === 'object' && level.previous && level.current) {
        const drop = level.previous - level.current;
        if (drop > THRESHOLDS.mastery_drop) {
          droppedTraps.push({ trap, drop: Math.round(drop * 100) });
        }
      }
    }
    if (droppedTraps.length > 0) {
      const trapNames = droppedTraps.map(d => `${d.trap}(-${d.drop}%)`).join('、');
      newInterventions.push({
        type: 'mastery_drop',
        severity: droppedTraps.length > 2 ? 'critical' : 'warning',
        title: `能力下滑警報`,
        message: `以下陷阱掌握度明顯下降：${trapNames}。建議針對性補底練習。`,
        action: 'generate_remedial',
        actionLabel: '生成補底練習',
        traps: droppedTraps.map(d => d.trap),
        timestamp: now
      });
    }

    // Check 3: Consecutive failures
    if (recentScores.length >= THRESHOLDS.streak_fail) {
      const lastN = recentScores.slice(-THRESHOLDS.streak_fail);
      if (lastN.every(s => (s.correct / s.total) < THRESHOLDS.accuracy_below)) {
        newInterventions.push({
          type: 'streak_fail',
          severity: 'critical',
          title: '連續低分警報',
          message: `最近 ${THRESHOLDS.streak_fail} 次練習正確率均低於 50%。建議切換到基礎模式或安排一對一輔導。`,
          action: 'switch_to_basic',
          actionLabel: '切換基礎模式',
          timestamp: now
        });
      }
    }

    // Check 4: SSPA band drop
    const prevBand = sspaPrediction.previousBand;
    const currBand = sspaPrediction.currentBand;
    if (prevBand && currBand && currBand > prevBand) {
      newInterventions.push({
        type: 'sspa_drop',
        severity: 'critical',
        title: `SSPA 預測降級：Band ${prevBand} → Band ${currBand}`,
        message: `呈分試預測從 Band ${prevBand} 降至 Band ${currBand}。需要立即加強 SSPA 重點題型訓練。`,
        action: 'sspa_boost',
        actionLabel: 'SSPA 特訓',
        timestamp: now
      });
    }

    // Log and save
    _interventions.push(...newInterventions);
    save();

    if (newInterventions.length > 0) {
      console.warn('[AI-Intervention]', newInterventions.length, 'alerts generated');
    }

    return newInterventions;
  }

  /**
   * Get all active (unresolved) interventions
   */
  function getActive() {
    return _interventions.filter(i => !i.resolved);
  }

  /**
   * Get intervention history
   */
  function getHistory(limit = 20) {
    return _interventions.slice(-limit);
  }

  /**
   * Resolve an intervention
   */
  function resolve(index) {
    if (_interventions[index]) {
      _interventions[index].resolved = true;
      _interventions[index].resolvedAt = Date.now();
      save();
    }
  }

  /**
   * Generate a parent/teacher alert HTML
   */
  function generateAlertHTML(interventions) {
    if (!interventions || interventions.length === 0) {
      return '<div style="color:#16A34A;padding:10px">✅ 目前無警報，學生進度正常。</div>';
    }

    const severityColors = { critical: '#DC2626', warning: '#EA580C', info: '#3B82F6' };
    const severityIcons = { critical: '🔴', warning: '🟡', info: '🔵' };

    return interventions.map((iv, i) => `
      <div style="background:white;border-left:4px solid ${severityColors[iv.severity]};padding:12px 16px;margin:8px 0;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.08)">
        <div style="font-weight:700;font-size:14px;margin-bottom:4px">
          ${severityIcons[iv.severity]} ${iv.title}
        </div>
        <div style="color:#6B7280;font-size:12px;margin-bottom:8px">${iv.message}</div>
        <button onclick="LFAIIntervention.resolve(${i})" 
          style="padding:4px 12px;background:#1A3C6D;color:white;border:none;border-radius:4px;cursor:pointer;font-size:11px">
          ${iv.actionLabel || '處理'}
        </button>
        <span style="font-size:10px;color:#9CA3AF;margin-left:8px">
          ${new Date(iv.timestamp).toLocaleString('zh-HK')}
        </span>
      </div>
    `).join('');
  }

  /**
   * Run scheduled check (call periodically)
   */
  function scheduledCheck(studentData) {
    if (_lastCheck && Date.now() - _lastCheck < 30 * 60 * 1000) {
      return []; // Don't check more than every 30 min
    }
    return analyze(studentData);
  }

  // Initialize on load
  init();

  return { analyze, getActive, getHistory, resolve, generateAlertHTML, scheduledCheck, THRESHOLDS };
})();

console.log('[AI-Intervention] Engine loaded - ready to monitor');
