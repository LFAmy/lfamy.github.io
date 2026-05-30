/**
 * LF SSPA Prediction Widget v1.0
 * Real-time SSPA score prediction based on trap mastery
 * Auto-injects an SSPA prediction card into target container
 * Include: <script src="/docs/data/lf-sspa-widget.js"></script>
 */
var LFSSPAWidget = {
    /**
     * Inject SSPA prediction card into target element
     * @param {string|Element} target - CSS selector or element
     * @param {string} studentName - student display name
     */
    inject: function(target, studentName) {
        if (typeof target === "string") target = document.querySelector(target);
        if (!target) return;

        var mastery = {};
        try {
            if (typeof LFAdaptive !== "undefined") {
                mastery = LFAdaptive.getTrapMastery();
            } else {
                mastery = JSON.parse(localStorage.getItem("lf_trap_mastery") || "{}");
            }
        } catch(e) {}

        // Calculate SSPA
        var sspaWeights = { T1:15,T2:10,T3:10,T4:12,T5:8,T6:12,T7:10,T8:8,T9:8,T10:7 };
        var trapNames = { T1:"計算粗心",T2:"小數除法",T3:"運算順序",T4:"面積公式",T5:"體積混淆",T6:"分數通分",T7:"百分比",T8:"速率單位",T9:"代數移項",T10:"統計圖表" };
        var totalW = 0, weightedS = 0;
        var details = [];

        Object.keys(sspaWeights).forEach(function(t) {
            var m = mastery[t] || {};
            var acc = m.accuracy !== undefined ? m.accuracy : (m.correct && m.attempts ? Math.round(m.correct/m.attempts*100) : null);
            var w = sspaWeights[t];
            totalW += w;
            if (acc !== null) weightedS += acc * w / 100;
            details.push({
                trap: t, name: trapNames[t], weight: w,
                accuracy: acc, attempts: m.attempts || 0,
                status: acc === null ? "untested" : acc >= 85 ? "mastered" : acc >= 60 ? "improving" : acc >= 40 ? "weak" : "critical"
            });
        });

        var rawScore = totalW > 0 ? Math.round(weightedS / totalW * 100) : 0;
        var grade = rawScore >= 90 ? "A" : rawScore >= 80 ? "B" : rawScore >= 70 ? "C" : rawScore >= 60 ? "D" : "E";
        var band = rawScore >= 85 ? "Band 1" : rawScore >= 70 ? "Band 2" : "Band 3";
        var gradeColors = { A:"#16A34A", B:"#2563EB", C:"#C9A84C", D:"#F59E0B", E:"#DC2626" };

        // Sort details by priority (weakest first)
        details.sort(function(a, b) {
            if (a.status === "critical" && b.status !== "critical") return -1;
            if (b.status === "critical" && a.status !== "critical") return 1;
            if (a.status === "weak" && b.status !== "weak") return -1;
            if (b.status === "weak" && a.status !== "weak") return 1;
            return (a.accuracy || 0) - (b.accuracy || 0);
        });

        // Build HTML
        var html = '<div class="lf-sspa-card" style="background:white;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,0.06);margin:16px 0">';
        html += '<h3 style="font-size:16px;color:#1A3C6D;margin-bottom:16px;display:flex;align-items:center;gap:8px">🎯 SSPA 呈分試預測' + (studentName ? ' — ' + studentName : '') + '</h3>';

        // Score circle
        html += '<div style="display:flex;align-items:center;gap:20px;margin-bottom:20px;flex-wrap:wrap">';
        html += '<div style="width:100px;height:100px;border-radius:50%;background:conic-gradient(' + gradeColors[grade] + ' ' + rawScore * 3.6 + 'deg, #E5E7EB 0);display:flex;align-items:center;justify-content:center;position:relative">';
        html += '<div style="width:80px;height:80px;border-radius:50%;background:white;display:flex;flex-direction:column;align-items:center;justify-content:center">';
        html += '<div style="font-size:28px;font-weight:900;color:' + gradeColors[grade] + '">' + rawScore + '</div>';
        html += '<div style="font-size:9px;color:#6B7280">/100</div></div></div>';
        html += '<div><div style="font-size:24px;font-weight:900;color:' + gradeColors[grade] + '">' + grade + ' 級</div>';
        html += '<div style="font-size:13px;color:#6B7280">' + band + '</div>';
        html += '<div style="font-size:10px;color:#9CA3AF;margin-top:4px">基於陷阱掌握度推算</div></div></div>';

        // Detail bars
        html += '<div style="margin-top:12px">';
        details.slice(0, 5).forEach(function(d) {
            var barColor = d.status === "critical" ? "#DC2626" : d.status === "weak" ? "#F59E0B" : d.status === "improving" ? "#C9A84C" : d.status === "mastered" ? "#16A34A" : "#9CA3AF";
            var barWidth = d.accuracy !== null ? d.accuracy : 0;
            html += '<div style="display:flex;align-items:center;gap:8px;margin:6px 0">';
            html += '<span style="font-size:11px;width:70px;text-align:right;color:#374151;flex-shrink:0">' + d.name + '</span>';
            html += '<div style="flex:1;background:#F1F5F9;border-radius:4px;height:8px;overflow:hidden">';
            html += '<div style="height:100%;width:' + barWidth + '%;background:' + barColor + ';border-radius:4px;transition:width 0.8s"></div></div>';
            html += '<span style="font-size:10px;color:#6B7280;width:32px;flex-shrink:0">' + (d.accuracy !== null ? d.accuracy + '%' : '—') + '</span></div>';
        });
        html += '</div>';

        // Summary
        var untested = details.filter(function(d) { return d.status === "untested"; }).length;
        var critical = details.filter(function(d) { return d.status === "critical"; }).length;
        if (untested > 3) html += '<div style="margin-top:12px;padding:10px 14px;background:#FEF3C7;border-radius:8px;font-size:11px;color:#92400E">⚠️ 有 ' + untested + ' 個陷阱尚未測試，預測僅供參考。建議完成全診斷。</div>';
        if (critical > 0) html += '<div style="margin-top:8px;padding:10px 14px;background:#FEE2E2;border-radius:8px;font-size:11px;color:#991B1B">🚨 ' + critical + ' 個陷阱急需加強，建議針對練習。</div>';

        html += '</div>';
        target.innerHTML += html;

        console.log("[LF SSPA Widget] Injected · Score: " + rawScore + " · Grade: " + grade);
        return { score: rawScore, grade: grade, band: band, details: details };
    }
};
