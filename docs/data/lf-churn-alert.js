/**
 * LF Academy Churn Prediction v1.0
 * Early warning system for student/parent disengagement
 * Monitors activity, detects patterns, triggers alerts
 */
const LF_CHURN = {
    // Alert signal definitions
    signals: {
        frequency_drop: {
            label: '\u4f7f\u7528\u983b\u7387\u4e0b\u964d',
            check: function(data) {
                if (!data.lastActive) return 0;
                var daysSince = Math.ceil((Date.now() - new Date(data.lastActive).getTime()) / 86400000);
                if (daysSince >= 14) return 100; // Critical
                if (daysSince >= 7) return 70;  // High
                if (daysSince >= 3) return 40;  // Medium
                return 0;
            }
        },
        accuracy_stall: {
            label: '\u6b63\u78ba\u7387\u505c\u6eef',
            check: function(data) {
                var history = data.accuracyHistory || [];
                if (history.length < 3) return 0;
                var recent = history.slice(-3);
                var improving = recent.every(function(h, i) {
                    return i === 0 || h >= recent[i-1];
                });
                if (!improving) {
                    var latest = recent[recent.length-1];
                    if (latest < 60) return 85;
                    if (latest < 70) return 60;
                    return 30;
                }
                return 0;
            }
        },
        parent_disengaged: {
            label: '\u5bb6\u9577\u672a\u67e5\u770b\u5831\u544a',
            check: function(data) {
                if (!data.lastReportView) return 0;
                var daysSince = Math.ceil((Date.now() - new Date(data.lastReportView).getTime()) / 86400000);
                if (daysSince >= 14) return 80;
                if (daysSince >= 7) return 50;
                return 0;
            }
        },
        subscription_expiring: {
            label: '\u8a02\u95b1\u5373\u5c07\u5230\u671f',
            check: function(data) {
                if (!data.expiry) return 0;
                var daysUntil = Math.ceil((new Date(data.expiry).getTime() - Date.now()) / 86400000);
                if (daysUntil <= 3) return 90;
                if (daysUntil <= 7) return 60;
                if (daysUntil <= 14) return 30;
                return 0;
            }
        },
        streak_broken: {
            label: '\u9023\u7e8c\u7c3d\u5230\u4e2d\u65b7',
            check: function(data) {
                if (!data.streakHistory) return 0;
                // Check if streak went from >=7 to 0
                var history = data.streakHistory;
                if (history.length >= 2) {
                    var prev = history[history.length-2];
                    var curr = history[history.length-1];
                    if (prev >= 5 && curr === 0) return 65;
                    if (prev >= 3 && curr === 0) return 40;
                }
                return 0;
            }
        }
    },

    // Analyze a single student/member
    analyze(data) {
        var alerts = [];
        var totalRisk = 0;
        var count = 0;

        for (var key in this.signals) {
            if (!this.signals.hasOwnProperty(key)) continue;
            var risk = this.signals[key].check(data);
            if (risk > 0) {
                alerts.push({
                    signal: key,
                    label: this.signals[key].label,
                    risk: risk,
                    level: risk >= 80 ? 'critical' : risk >= 50 ? 'high' : 'medium'
                });
                totalRisk += risk;
                count++;
            }
        }

        var avgRisk = count > 0 ? Math.round(totalRisk / count) : 0;
        return {
            student: data.name || data.student || '\u672a\u77e5',
            grade: data.grade || '',
            overallRisk: avgRisk,
            level: avgRisk >= 70 ? 'critical' : avgRisk >= 40 ? 'high' : avgRisk > 0 ? 'low' : 'none',
            alerts: alerts
        };
    },

    // Analyze all members
    analyzeAll() {
        var results = [];
        var members = [];

        // Get from localStorage
        try { members = JSON.parse(localStorage.getItem('lf_members') || '[]'); } catch(e) {}

        // Also check demo class
        var demoClass = typeof LF_getDemoClass === 'function' ? LF_getDemoClass() : null;
        if (demoClass && demoClass.students) {
            demoClass.students.forEach(function(s) {
                members.push({
                    student: s.name,
                    grade: s.grade,
                    lastActive: s.lastActive,
                    accuracyHistory: s.accuracyHistory || [s.accuracy],
                    streakHistory: s.streakHistory || [s.streak],
                    expiry: null,
                    lastReportView: null
                });
            });
        }

        // Also scan individual member records
        for (var i = 0; i < localStorage.length; i++) {
            var key = localStorage.key(i);
            if (key.startsWith('lf_member_')) {
                try {
                    var m = JSON.parse(localStorage.getItem(key));
                    var phone = key.replace('lf_member_', '');
                    var exists = members.some(function(x) { return x.phone === phone; });
                    if (!exists) {
                        members.push({
                            student: m.student || '',
                            grade: m.grade || '',
                            phone: phone,
                            expiry: m.expiry,
                            lastActive: m.lastActive,
                            lastReportView: m.lastReportView
                        });
                    }
                } catch(e) {}
            }
        }

        members.forEach(function(m) {
            var analysis = LF_CHURN.analyze(m);
            if (analysis.overallRisk > 0) {
                results.push(analysis);
            }
        });

        // Sort by risk (highest first)
        results.sort(function(a, b) { return b.overallRisk - a.overallRisk; });

        return results;
    },

    // Render churn dashboard widget
    renderWidget() {
        var results = this.analyzeAll();

        if (!results.length) {
            return `
            <div class="card" style="background:#F0FDF4;border:1px solid #BBF7D0">
                <h2>\ud83d\udfe2 \u6d41\u5931\u9810\u8b66</h2>
                <div style="text-align:center;padding:20px;font-size:13px;color:#065F46">
                    \u2714\ufe0f \u76ee\u524d\u6c92\u6709\u9ad8\u98a8\u96aa\u5b78\u751f\uff0c\u6240\u6709\u5b78\u54e1\u6d3b\u8e8d\u5ea6\u826f\u597d\uff01
                </div>
            </div>`;
        }

        var criticalCount = results.filter(function(r) { return r.level === 'critical'; }).length;
        var highCount = results.filter(function(r) { return r.level === 'high'; }).length;

        var listHtml = results.slice(0, 10).map(function(r) {
            var badge = r.level === 'critical' ? '\ud83d\udd34 \u7dca\u6025'
                : r.level === 'high' ? '\ud83d\udfe1 \u8b66\u544a'
                : '\ud83d\udfe2 \u89c0\u5bdf';
            var badgeColor = r.level === 'critical' ? '#DC2626' : r.level === 'high' ? '#F59E0B' : '#3B82F6';

            var alertHtml = r.alerts.slice(0, 2).map(function(a) {
                return '<span style="font-size:10px;color:#6B7280">' + a.label + '</span>';
            }).join(' \u00b7 ');

            return `
            <div style="display:flex;align-items:center;padding:10px 0;border-bottom:1px solid #F3F4F6;gap:12px">
                <div style="width:42px;height:42px;border-radius:50%;background:' + badgeColor + '15;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">
                    ' + (r.level === 'critical' ? '\ud83d\udd34' : r.level === 'high' ? '\ud83d\udfe1' : '\ud83d\udfe2') + '
                </div>
                <div style="flex:1;min-width:0">
                    <div style="font-weight:700;font-size:13px">' + r.student + ' <span style="font-size:10px;color:#6B7280">' + r.grade + '</span></div>
                    <div style="font-size:10px;color:#9CA3AF">' + alertHtml + '</div>
                </div>
                <div style="text-align:center;flex-shrink:0">
                    <div style="font-size:20px;font-weight:900;color:' + badgeColor + '">' + r.overallRisk + '%</div>
                    <div style="font-size:9px;color:' + badgeColor + ';font-weight:700">' + badge + '</div>
                </div>
                <button class="btn btn-outline btn-sm" style="flex-shrink:0" onclick="alert(\u0027\u5df2\u767c\u9001\u63d0\u9192\u7d66 ' + r.student + '\u0027)">\ud83d\udcec \u63d0\u9192</button>
            </div>`;
        }).join('');

        return `
        <div class="card" style="border-left:3px solid ' + (criticalCount > 0 ? '#DC2626' : '#F59E0B') + '">
            <h2>\ud83d\udea8 \u6d41\u5931\u9810\u8b66\u7cfb\u7d71
                ' + (criticalCount > 0 ? '<span style="font-size:10px;background:#FEF2F2;color:#DC2626;padding:2px 8px;border-radius:6px">' + criticalCount + ' \u7dca\u6025</span>' : '') + '
                ' + (highCount > 0 ? '<span style="font-size:10px;background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:6px">' + highCount + ' \u8b66\u544a</span>' : '') + '
            </h2>
            <div style="font-size:11px;color:#6B7280;margin-bottom:12px">
                \u6bcf\u65e5\u81ea\u52d5\u76e3\u63a7\u5b78\u54e1\u6d3b\u8e8d\u5ea6\uff0c\u63d0\u524d\u9810\u8b66\u6d41\u5931\u98a8\u96aa
            </div>
            ' + listHtml + '
        </div>`;
    }
};

console.log('[LF Churn v1.0] Ready');