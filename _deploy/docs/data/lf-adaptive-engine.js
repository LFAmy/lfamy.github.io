/**
 * LF Adaptive Learning Engine v1.0
 * AI-powered personalized learning path generation
 * 診斷 → 弱點分析 → 自適應難度 → 個人化練習路徑
 * Include: <script src="/docs/data/lf-adaptive-engine.js"></script>
 */
var LFAdaptive = {
    // ═══ CONFIG ═══
    config: {
        minQuestionsForAnalysis: 10,
        masteryThreshold: 85,     // accuracy >= this = mastered
        focusThreshold: 60,       // accuracy < this = needs focus
        criticalThreshold: 40,    // accuracy < this = critical
        decayDays: 7,             // skill decay after days of no practice
        adaptiveWindow: 5,        // recent questions to consider for adaptation
    },

    // ═══ TRAP DEFINITIONS ═══
    traps: {
        T1: { name: "計算粗心", category: "careless", weight: 1.0, dependencies: [] },
        T2: { name: "小數除法", category: "decimal", weight: 1.2, dependencies: ["T1"] },
        T3: { name: "運算順序", category: "order", weight: 1.1, dependencies: ["T1"] },
        T4: { name: "面積公式", category: "geometry", weight: 1.3, dependencies: [] },
        T5: { name: "體積混淆", category: "geometry", weight: 1.2, dependencies: ["T4"] },
        T6: { name: "分數通分", category: "fraction", weight: 1.3, dependencies: ["T1"] },
        T7: { name: "百分比", category: "percent", weight: 1.4, dependencies: ["T6"] },
        T8: { name: "速率單位", category: "speed", weight: 1.3, dependencies: ["T1","T2"] },
        T9: { name: "代數移項", category: "algebra", weight: 1.2, dependencies: ["T3"] },
        T10: { name: "統計圖表", category: "stats", weight: 1.0, dependencies: [] },
    },

    // ═══ SSPA WEIGHT MAPPING ═══
    // Each trap's contribution to SSPA score (based on exam analysis)
    sspaWeights: {
        T1: 15, T2: 10, T3: 10, T4: 12, T5: 8,
        T6: 12, T7: 10, T8: 8, T9: 8, T10: 7
    },

    // ═══ STATE ═══
    state: {
        diagnosticComplete: false,
        currentPath: null,
        lastAnalysis: null,
    },

    // ═══ INIT ═══
    init: function() {
        // Load state
        try {
            var saved = JSON.parse(localStorage.getItem("lf_adaptive_state") || "null");
            if (saved) this.state = saved;
        } catch(e) {}
        // Check if diagnostic needed
        var totalQ = parseInt(localStorage.getItem("lf_total_q") || "0");
        this.state.diagnosticComplete = totalQ >= this.config.minQuestionsForAnalysis;
        console.log("[LFAdaptive] Initialized · Diagnostic: " + (this.state.diagnosticComplete ? "complete" : "needed") + " · Questions: " + totalQ);
    },

    // ═══ GET TRAP MASTERY ═══
    getTrapMastery: function() {
        var mastery = {};
        try {
            var raw = JSON.parse(localStorage.getItem("lf_trap_mastery") || "{}");
            // Normalize and apply decay
            var now = Date.now();
            Object.keys(this.traps).forEach(function(trapId) {
                var t = raw[trapId] || { correct: 0, attempts: 0, lastPractice: null };
                var accuracy = t.attempts > 0 ? Math.round(t.correct / t.attempts * 100) : null;

                // Apply skill decay
                if (t.lastPractice && accuracy !== null) {
                    var daysSince = (now - t.lastPractice) / (1000 * 60 * 60 * 24);
                    if (daysSince > 7) {
                        accuracy = Math.max(0, accuracy - Math.floor((daysSince - 7) * 2));
                    }
                }

                mastery[trapId] = {
                    accuracy: accuracy,
                    attempts: t.attempts || 0,
                    correct: t.correct || 0,
                    lastPractice: t.lastPractice || null,
                    status: accuracy === null ? "untested" :
                            accuracy >= 85 ? "mastered" :
                            accuracy >= 60 ? "improving" :
                            accuracy >= 40 ? "weak" : "critical",
                };
            });
        } catch(e) {}
        return mastery;
    },

    // ═══ DIAGNOSTIC ANALYSIS ═══
    analyze: function() {
        var mastery = this.getTrapMastery();
        var analysis = {
            mastery: mastery,
            overallAccuracy: 0,
            strengths: [],
            weaknesses: [],
            criticalGaps: [],
            recommendedPath: [],
            sspaEstimate: null,
            summary: "",
            timestamp: Date.now(),
        };

        var totalCorrect = 0, totalAttempts = 0, testedCount = 0;

        Object.keys(mastery).forEach(function(trapId) {
            var m = mastery[trapId];
            if (m.accuracy !== null) {
                totalCorrect += m.correct;
                totalAttempts += m.attempts;
                testedCount++;
                if (m.status === "mastered") analysis.strengths.push(trapId);
                else if (m.status === "weak") analysis.weaknesses.push(trapId);
                else if (m.status === "critical") analysis.criticalGaps.push(trapId);
            }
        });

        analysis.overallAccuracy = totalAttempts > 0 ? Math.round(totalCorrect / totalAttempts * 100) : 0;

        // Generate learning path (prioritize critical > weak > untested)
        var pathOrder = [];
        analysis.criticalGaps.forEach(function(t) { pathOrder.push({ trap: t, priority: 3 }); });
        analysis.weaknesses.forEach(function(t) { pathOrder.push({ trap: t, priority: 2 }); });
        Object.keys(mastery).forEach(function(t) {
            if (mastery[t].status === "untested") pathOrder.push({ trap: t, priority: 1 });
        });
        Object.keys(mastery).forEach(function(t) {
            if (mastery[t].status === "improving") pathOrder.push({ trap: t, priority: 0 });
        });

        analysis.recommendedPath = pathOrder;

        // SSPA estimate
        analysis.sspaEstimate = this.predictSSPA(mastery);

        // Generate summary
        analysis.summary = this.generateSummary(analysis);

        // Save state
        this.state.lastAnalysis = analysis;
        this.state.diagnosticComplete = true;
        try {
            localStorage.setItem("lf_adaptive_state", JSON.stringify(this.state));
        } catch(e) {}

        console.log("[LFAdaptive] Analysis complete · Accuracy: " + analysis.overallAccuracy + "% · SSPA: " + analysis.sspaEstimate.score);
        return analysis;
    },

    // ═══ SSPA SCORE PREDICTION ═══
    predictSSPA: function(mastery) {
        var totalWeight = 0, weightedScore = 0;
        var self = this;

        Object.keys(self.sspaWeights).forEach(function(trapId) {
            var m = mastery[trapId];
            var weight = self.sspaWeights[trapId];
            var accuracy = m.accuracy !== null ? m.accuracy : 50; // untested = 50% estimate
            totalWeight += weight;
            weightedScore += accuracy * weight / 100;
        });

        var rawScore = totalWeight > 0 ? Math.round(weightedScore / totalWeight * 100) : 0;

        // Map to SSPA grade bands (Hong Kong standard)
        var grade;
        if (rawScore >= 90) grade = "A (優異)";
        else if (rawScore >= 80) grade = "B (良好)";
        else if (rawScore >= 70) grade = "C (中等)";
        else if (rawScore >= 60) grade = "D (及格)";
        else grade = "E (需加強)";

        return {
            score: rawScore,
            grade: grade,
            band: rawScore >= 85 ? "Band 1" : rawScore >= 70 ? "Band 2" : "Band 3",
            confidence: mastery.T1 && mastery.T1.attempts > 5 ? "high" : "medium",
        };
    },

    // ═══ GENERATE PERSONALIZED QUESTION SEQUENCE ═══
    /**
     * Generate a sequence of questions tailored to student weaknesses
     * @param {number} count - number of questions to generate
     * @param {Array} questionBank - available questions
     * @returns {Array} personalized question sequence
     */
    generatePath: function(count, questionBank) {
        var mastery = this.getTrapMastery();
        var analysis = this.analyze();
        var selected = [];
        var self = this;

        // Calculate target distribution
        var distribution = {};
        var totalPriority = 0;
        analysis.recommendedPath.forEach(function(item) {
            distribution[item.trap] = item.priority + 1; // 1-4 weight
            totalPriority += distribution[item.trap];
        });

        // Normalize to percentages
        Object.keys(distribution).forEach(function(t) {
            distribution[t] = distribution[t] / totalPriority;
        });

        // Group questions by trap
        var byTrap = {};
        questionBank.forEach(function(q) {
            if (!byTrap[q.trap]) byTrap[q.trap] = [];
            byTrap[q.trap].push(q);
        });

        // Select questions based on distribution
        var trapAllocation = {};
        var remaining = count;
        Object.keys(distribution).forEach(function(trapId) {
            var alloc = Math.max(1, Math.round(distribution[trapId] * count));
            trapAllocation[trapId] = alloc;
            remaining -= alloc;
        });

        // Distribute remaining
        var trapKeys = Object.keys(distribution).sort(function(a, b) {
            return distribution[b] - distribution[a];
        });
        while (remaining > 0) {
            trapAllocation[trapKeys[0]] += 1;
            remaining--;
        }

        // Pick questions
        Object.keys(trapAllocation).forEach(function(trapId) {
            var pool = (byTrap[trapId] || []).slice();
            // Sort by difficulty appropriate to mastery
            var m = mastery[trapId];
            var targetDiff = m.accuracy === null ? 1 : m.accuracy < 50 ? 1 : m.accuracy < 75 ? 2 : 3;
            pool.sort(function(a, b) {
                var aDist = Math.abs((a.diff || 2) - targetDiff);
                var bDist = Math.abs((b.diff || 2) - targetDiff);
                return aDist - bDist;
            });
            // Shuffle within similar difficulty
            pool.sort(function() { return Math.random() - 0.5; });

            var needed = Math.min(trapAllocation[trapId], pool.length);
            for (var i = 0; i < needed; i++) {
                if (selected.indexOf(pool[i]) < 0) selected.push(pool[i]);
            }
        });

        // Fill remaining if any
        if (selected.length < count) {
            var remainingPool = questionBank.filter(function(q) { return selected.indexOf(q) < 0; });
            remainingPool.sort(function() { return Math.random() - 0.5; });
            while (selected.length < count && remainingPool.length > 0) {
                selected.push(remainingPool.shift());
            }
        }

        // Shuffle final order
        selected.sort(function() { return Math.random() - 0.5; });

        // Interleave: weak trap first, then mix
        var weakFirst = [], others = [];
        selected.forEach(function(q) {
            var m = mastery[q.trap];
            if (m && (m.status === "critical" || m.status === "weak")) weakFirst.push(q);
            else others.push(q);
        });
        // Place weak questions at positions 1, 4, 7, 10 (spaced repetition)
        var result = [];
        var wi = 0, oi = 0;
        for (var i = 0; i < count; i++) {
            if ((i % 3 === 0) && wi < weakFirst.length) result.push(weakFirst[wi++]);
            else if (oi < others.length) result.push(others[oi++]);
            else if (wi < weakFirst.length) result.push(weakFirst[wi++]);
            else result.push(others[oi++]);
        }

        return result;
    },

    // ═══ ADAPTIVE DIFFICULTY ═══
    /**
     * Determine next question difficulty based on recent performance
     * @param {Array} recentResults - array of {correct: bool} for last N questions
     * @returns {number} recommended difficulty 1-4
     */
    getAdaptiveDifficulty: function(recentResults) {
        if (!recentResults || recentResults.length === 0) return 1;
        var window = recentResults.slice(-this.config.adaptiveWindow);
        var correct = window.filter(function(r) { return r.correct; }).length;
        var accuracy = correct / window.length;

        if (accuracy >= 0.8 && window.length >= 3) return Math.min(4, Math.ceil(accuracy * 4));
        if (accuracy >= 0.6) return 2;
        if (accuracy >= 0.4) return 1;
        return 1; // stay at easy if struggling
    },

    // ═══ GENERATE SUMMARY ═══
    generateSummary: function(analysis) {
        var parts = [];
        var mastery = analysis.mastery;

        if (analysis.overallAccuracy === 0) {
            return "尚未有足夠練習數據。完成至少 " + this.config.minQuestionsForAnalysis + " 題後，系統將為你生成個人化學習分析。";
        }

        parts.push("整體正確率 " + analysis.overallAccuracy + "%");

        if (analysis.strengths.length > 0) {
            var sNames = analysis.strengths.map(function(t) { return mastery[t] ? (mastery[t].name || t) : t; });
            parts.push("強項：" + sNames.slice(0, 3).join("、"));
        }

        if (analysis.criticalGaps.length > 0) {
            var cNames = analysis.criticalGaps.map(function(t) { return mastery[t] ? (mastery[t].name || t) : t; });
            parts.push("🚨 急需加強：" + cNames.join("、"));
        } else if (analysis.weaknesses.length > 0) {
            var wNames = analysis.weaknesses.map(function(t) { return mastery[t] ? (mastery[t].name || t) : t; });
            parts.push("⚠️ 需要加強：" + wNames.join("、"));
        }

        if (analysis.sspaEstimate) {
            parts.push("預估SSPA等級：" + analysis.sspaEstimate.grade + " (" + analysis.sspaEstimate.band + ")");
        }

        return parts.join(" · ");
    },

    // ═══ LEARNING PATH VISUALIZATION DATA ═══
    /**
     * Generate data for radar chart visualization
     */
    getRadarData: function() {
        var mastery = this.getTrapMastery();
        var labels = [], data = [], background = [];

        Object.keys(this.traps).forEach(function(trapId) {
            var t = mastery[trapId];
            labels.push(trapId.replace("T", "陷阱") + " ");
            data.push(t.accuracy !== null ? t.accuracy : 0);
            background.push(
                t.status === "mastered" ? "rgba(22,163,74,0.2)" :
                t.status === "improving" ? "rgba(201,168,76,0.2)" :
                t.status === "weak" ? "rgba(245,158,11,0.2)" :
                t.status === "critical" ? "rgba(220,38,38,0.2)" :
                "rgba(148,163,184,0.1)"
            );
        });

        return { labels: labels, data: data, background: background };
    },

    // ═══ RECORD ANSWER ═══
    recordAnswer: function(trapId, correct) {
        try {
            var mastery = JSON.parse(localStorage.getItem("lf_trap_mastery") || "{}");
            if (!mastery[trapId]) mastery[trapId] = { correct: 0, attempts: 0, lastPractice: null };
            mastery[trapId].attempts = (mastery[trapId].attempts || 0) + 1;
            if (correct) mastery[trapId].correct = (mastery[trapId].correct || 0) + 1;
            mastery[trapId].lastPractice = Date.now();
            localStorage.setItem("lf_trap_mastery", JSON.stringify(mastery));

            // Update total
            var totalQ = parseInt(localStorage.getItem("lf_total_q") || "0") + 1;
            localStorage.setItem("lf_total_q", totalQ.toString());
            if (correct) {
                var totalC = parseInt(localStorage.getItem("lf_total_correct") || "0") + 1;
                localStorage.setItem("lf_total_correct", totalC.toString());
            }

            // Recent results for adaptive difficulty
            var recent = [];
            try { recent = JSON.parse(localStorage.getItem("lf_recent_results") || "[]"); } catch(e) {}
            recent.push({ trap: trapId, correct: correct, time: Date.now() });
            if (recent.length > 50) recent = recent.slice(-50);
            localStorage.setItem("lf_recent_results", JSON.stringify(recent));

            return mastery[trapId];
        } catch(e) {
            console.warn("[LFAdaptive] Failed to record answer:", e.message);
            return null;
        }
    },

    // ═══ GET RECENT RESULTS ═══
    getRecentResults: function() {
        try {
            return JSON.parse(localStorage.getItem("lf_recent_results") || "[]");
        } catch(e) { return []; }
    },

    // ═══ PROGRESS TREND ═══
    getProgressTrend: function(days) {
        days = days || 7;
        var results = this.getRecentResults();
        var now = Date.now();
        var dayMs = 24 * 60 * 60 * 1000;
        var trend = [];

        for (var d = days - 1; d >= 0; d--) {
            var dayStart = now - (d + 1) * dayMs;
            var dayEnd = now - d * dayMs;
            var dayResults = results.filter(function(r) {
                return r.time >= dayStart && r.time < dayEnd;
            });
            var correct = dayResults.filter(function(r) { return r.correct; }).length;
            var total = dayResults.length;
            trend.push({
                day: d,
                accuracy: total > 0 ? Math.round(correct / total * 100) : null,
                questions: total
            });
        }

        return trend;
    },
};

// Auto-init
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function() { LFAdaptive.init(); });
} else {
    LFAdaptive.init();
}

console.log("[LFAdaptive] Engine loaded · 10 traps · SSPA prediction · Adaptive difficulty");
