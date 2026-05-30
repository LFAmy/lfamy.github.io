/**
 * LF Academy AI Learning Suggestions v1.0
 * Generates actionable learning recommendations based on student progress
 * Rule-based engine + optional AI API enhancement
 */
const LF_SUGGEST = {

    // Knowledge point mastery thresholds
    thresholds: {
        mastered: 80,    // Above this = mastered
        proficient: 65,  // Above this = proficient
        weak: 50,        // Below this = needs work
        critical: 35     // Below this = urgent
    },

    // Knowledge point metadata
    topics: {
        'T1': { name: '\u9032\u9000\u4f4d\u8207\u9032\u4f4d', en: 'Place Value', grade: ['P3','P4'], priority: 10, avgDaysToImprove: 7 },
        'T2': { name: '\u5c0f\u6578\u9ede\u904b\u7b97', en: 'Decimal Point', grade: ['P4','P5'], priority: 9, avgDaysToImprove: 10 },
        'T3': { name: '\u904b\u7b97\u9806\u5e8f', en: 'Order of Operations', grade: ['P3','P4','P5'], priority: 10, avgDaysToImprove: 5 },
        'T4': { name: '\u9762\u7a4d\u516c\u5f0f\u6df7\u6dc6', en: 'Area Formulas', grade: ['P4','P5','P6'], priority: 8, avgDaysToImprove: 14 },
        'T5': { name: '\u5e7e\u4f55\u5716\u5f62\u6df7\u6dc6', en: 'Geometry Shapes', grade: ['P3','P4','P5','P6'], priority: 8, avgDaysToImprove: 12 },
        'T6': { name: '\u5206\u6578\u9677\u9631', en: 'Fraction Traps', grade: ['P3','P4','P5','P6'], priority: 9, avgDaysToImprove: 14 },
        'T7': { name: '\u767e\u5206\u6578\u9677\u9631', en: 'Percentage Traps', grade: ['P5','P6'], priority: 7, avgDaysToImprove: 10 },
        'T8': { name: '\u901f\u7387\u9677\u9631', en: 'Speed/Rate Traps', grade: ['P6'], priority: 6, avgDaysToImprove: 8 },
        'T9': { name: '\u65b9\u7a0b\u9677\u9631', en: 'Equation Traps', grade: ['P5','P6'], priority: 7, avgDaysToImprove: 12 },
        'T10': { name: '\u7d71\u8a08\u5716\u8868\u9677\u9631', en: 'Statistics Traps', grade: ['P4','P5','P6'], priority: 6, avgDaysToImprove: 8 }
    },

    // Analyze student data and generate suggestions
    analyze(studentData) {
        // studentData = { name, grade, radar: {T1: score, T2: score, ...}, weakTraps: [], strongTraps: [] }
        var suggestions = [];
        var radar = studentData.radar || {};
        var grade = studentData.grade || 'P5';

        // Analyze each topic
        for (var key in radar) {
            if (!radar.hasOwnProperty(key)) continue;
            var score = radar[key];
            var topic = this.topics[key];
            if (!topic) continue;

            // Only suggest if below mastery
            if (score >= this.thresholds.mastered) continue;

            // Check if topic is relevant to student's grade
            if (topic.grade && topic.grade.indexOf(grade) < 0) continue;

            var urgency = score <= this.thresholds.critical ? 'critical'
                : score <= this.thresholds.weak ? 'high'
                : score <= this.thresholds.proficient ? 'medium' : 'low';

            var daysTo80 = Math.ceil((this.thresholds.mastered - score) / 100 * topic.avgDaysToImprove * 7);
            var dailyQuestions = urgency === 'critical' ? 8 : urgency === 'high' ? 5 : urgency === 'medium' ? 3 : 2;

            suggestions.push({
                topicKey: key,
                topic: topic.name,
                score: score,
                urgency: urgency,
                priority: topic.priority * (urgency === 'critical' ? 3 : urgency === 'high' ? 2 : 1),
                daysToImprove: Math.max(3, daysTo80),
                dailyQuestions: dailyQuestions,
                goalScore: Math.min(this.thresholds.mastered, score + 20)
            });
        }

        // Sort by priority (highest first)
        suggestions.sort(function(a, b) { return b.priority - a.priority; });

        return {
            student: studentData.name || '\u5b78\u751f',
            grade: grade,
            suggestions: suggestions.slice(0, 5),
            totalWeak: suggestions.length,
            topPriority: suggestions.length > 0 ? suggestions[0] : null
        };
    },

    // Generate natural language summary
    generateSummary(analysis) {
        if (!analysis.suggestions.length) {
            return '\u592a\u597d\u4e86\uff01' + analysis.student + '\u5728\u6240\u6709\u77e5\u8b58\u9ede\u90fd\u8868\u73fe\u512a\u79c0\uff0c\u7e7c\u7e8c\u4fdd\u6301\uff01\ud83c\udf1f';
        }

        var top = analysis.suggestions[0];
        var lines = [];
        lines.push('\ud83d\udccb ' + analysis.student + ' \u00b7 ' + analysis.grade + ' \u00b7 \u672c\u9031\u5b78\u7fd2\u5efa\u8b70');
        lines.push('');

        analysis.suggestions.forEach(function(s, i) {
            var icon = s.urgency === 'critical' ? '\ud83d\udd34' : s.urgency === 'high' ? '\ud83d\udfe1' : '\ud83d\udfe2';
            lines.push((i+1) + '. ' + icon + ' \u512a\u5148\u7df4\u7fd2\uff1a' + s.topic);
            lines.push('   \u76ee\u524d\u6b63\u78ba\u7387 ' + s.score + '%\uff0c\u9810\u8a08 ' + s.daysToImprove + ' \u5929\u7df4\u7fd2\u53ef\u63d0\u5347\u81f3 ' + s.goalScore + '%');
            lines.push('   \u5efa\u8b70\u6bcf\u5929 ' + s.dailyQuestions + ' \u984c' + s.topic + '\u7df4\u7fd2');
            lines.push('');
        });

        if (analysis.totalWeak > 5) {
            lines.push('\u9084\u6709 ' + (analysis.totalWeak - 5) + ' \u500b\u5f31\u9805\u5f85\u6539\u5584\uff0c\u5efa\u8b70\u5148\u5c08\u6ce8\u4e0a\u8ff0\u512a\u5148\u9805\u3002');
        }

        return lines.join('\n');
    },

    // Render suggestions card HTML
    renderCard(analysis) {
        if (!analysis || !analysis.suggestions.length) {
            return `
            <div class="card" style="background:#F0FDF4;border:1px solid #BBF7D0">
                <h2>\ud83c\udf1f AI \u5b78\u7fd2\u5efa\u8b70</h2>
                <div style="text-align:center;padding:20px;font-size:14px;color:#065F46">
                    \u592a\u5f37\u4e86\uff01${analysis ? analysis.student : '\u5b78\u751f'}\u5728\u6240\u6709\u77e5\u8b58\u9ede\u90fd\u8868\u73fe\u512a\u79c0\uff01<br>\u7e7c\u7e8c\u4fdd\u6301\u9019\u500b\u6c34\u6e96\uff01
                </div>
            </div>`;
        }

        var top = analysis.suggestions[0];
        var listHtml = analysis.suggestions.map(function(s, i) {
            var urgencyColor = s.urgency === 'critical' ? '#DC2626' : s.urgency === 'high' ? '#F59E0B' : s.urgency === 'medium' ? '#3B82F6' : '#16A34A';
            var urgencyLabel = s.urgency === 'critical' ? '\u7dca\u6025' : s.urgency === 'high' ? '\u512a\u5148' : s.urgency === 'medium' ? '\u5efa\u8b70' : '\u53ef\u9078';
            return `
            <div style="padding:12px 0;border-bottom:1px solid #F3F4F6;display:flex;align-items:flex-start;gap:12px">
                <div style="width:32px;height:32px;border-radius:50%;background:' + urgencyColor + ';color:white;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;flex-shrink:0">' + (i+1) + '</div>
                <div style="flex:1">
                    <div style="font-weight:700;font-size:13px;margin-bottom:2px">' + s.topic + ' <span style="font-size:10px;background:' + urgencyColor + '15;color:' + urgencyColor + ';padding:2px 6px;border-radius:4px;font-weight:600">' + urgencyLabel + '</span></div>
                    <div style="font-size:11px;color:#6B7280;margin-bottom:4px">
                        \u76ee\u524d\u6b63\u78ba\u7387 <b style="color:' + urgencyColor + '">' + s.score + '%</b> \u2192 \u76ee\u6a19 <b style="color:#16A34A">' + s.goalScore + '%</b> \u00b7 \u9810\u8a08 <b>' + s.daysToImprove + '\u5929</b>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px">
                        <div style="flex:1;height:6px;background:#E5E7EB;border-radius:3px">
                            <div style="height:100%;width:' + s.score + '%;background:' + urgencyColor + ';border-radius:3px"></div>
                        </div>
                        <span style="font-size:10px;color:#6B7280;white-space:nowrap">\u6bcf\u5929' + s.dailyQuestions + '\u984c</span>
                    </div>
                </div>
            </div>`;
        }).join('');

        return `
        <div class="card" style="border-left:3px solid #1A3C6D">
            <h2>\ud83e\udde0 AI \u5b78\u7fd2\u5efa\u8b70 <span style="font-size:10px;background:#DBEAFE;color:#1E40AF;padding:2px 6px;border-radius:4px;font-weight:400">\u667a\u80fd\u5206\u6790</span></h2>
            <div style="font-size:12px;color:#6B7280;margin-bottom:12px">
                \u6839\u64da ${analysis.student} \u7684\u7b54\u984c\u8a18\u9304\u81ea\u52d5\u5206\u6790\uff0c\u5171\u767c\u73fe ${analysis.totalWeak} \u500b\u5f31\u9805\u3002\u4ee5\u4e0b\u662f\u512a\u5148\u5efa\u8b70\uff1a
            </div>
            ${listHtml}
            <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
                <a href="smart-test-gen.html?topic=${top.topicKey}&count=${top.dailyQuestions * 7}" class="btn btn-primary btn-sm" style="padding:8px 16px;font-size:12px">\ud83c\udfaf \u4e00\u9375\u751f\u6210\u91dd\u5c0d\u6027\u7df4\u7fd2</a>
                <a href="post-trial-report.html" class="btn btn-outline btn-sm" style="padding:8px 16px;font-size:12px">\ud83d\udcca \u67e5\u770b\u5b8c\u6574\u5831\u544a</a>
            </div>
            <div style="font-size:10px;color:#9CA3AF;margin-top:8px">\u26a0 \u5efa\u8b70\u57fa\u65bc\u6b77\u53f2\u6578\u64da\u5206\u6790\uff0c\u5be6\u969b\u9032\u5ea6\u56e0\u4eba\u800c\u7570\u3002</div>
        </div>`;
    },

    // Get or estimate student radar data
    getStudentData(studentName) {
        // Try to get from localStorage first
        var progress = null;
        if (typeof LFCore !== 'undefined') {
            progress = LFCore.getStudentProgress ? LFCore.getStudentProgress() : null;
        }

        // Try from demo data
        var demoClass = typeof LF_getDemoClass === 'function' ? LF_getDemoClass() : null;
        if (demoClass && demoClass.students) {
            var found = demoClass.students.find(function(s) { return s.name === studentName; });
            if (found) return found;
            // Return first student if name not found
            return demoClass.students[0];
        }

        // Fallback: use demo student data
        if (typeof LF_DEMO !== 'undefined' && LF_DEMO.demoClass) {
            return LF_DEMO.demoClass.students[0];
        }

        // Last resort: empty data
        return { name: studentName || '\u5b66\u751f', grade: 'P5', radar: {}, weakTraps: [], strongTraps: [] };
    },

    // Full pipeline: analyze + render
    render(studentName) {
        var data = this.getStudentData(studentName);
        var analysis = this.analyze(data);
        return this.renderCard(analysis);
    }
};

console.log('[LF Suggest v1.0] AI Learning Suggestions engine ready');