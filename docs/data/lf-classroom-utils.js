/**
 * LF Academy Classroom Utilities v1.0
 * #13 Visual Step Solver · #15 Voice Reader · #14 Data Download · #12 Batch Notify
 */
const LF_UTILS = {

    // ══════════════════════════════════
    // #13 VISUAL STEP SOLVER
    // ══════════════════════════════════
    visualSolver: {
        // Render step-by-step solution with animations
        render(containerId, steps) {
            // steps = [{title, content, hint, svg?}]
            var container = document.getElementById(containerId);
            if (!container) return;

            var html = '<div class="lf-solver">';
            steps.forEach(function(step, i) {
                var animDelay = (i * 0.15) + 's';
                html += `
                <div class="lf-solver-step" style="animation: lfSolverIn 0.4s ease ${animDelay} both">
                    <div class="lf-step-num">${i+1}</div>
                    <div class="lf-step-content">
                        <div class="lf-step-title">${step.title}</div>
                        <div class="lf-step-detail">${step.content}</div>
                        ${step.hint ? `<div class="lf-step-hint">\ud83d\udca1 ${step.hint}</div>` : ''}
                        ${step.svg ? `<div class="lf-step-svg">${step.svg}</div>` : ''}
                    </div>
                </div>`;
            });
            html += '</div>';
            container.innerHTML = html;

            // Inject CSS if needed
            if (!document.getElementById('lf-solver-css')) {
                var style = document.createElement('style');
                style.id = 'lf-solver-css';
                style.textContent = `
                    @keyframes lfSolverIn { from{opacity:0;transform:translateX(-20px)} to{opacity:1;transform:translateX(0)} }
                    .lf-solver { max-width:700px; margin:0 auto; }
                    .lf-solver-step { display:flex; gap:14px; padding:14px 0; border-bottom:1px solid #F3F4F6; }
                    .lf-step-num { width:36px; height:36px; border-radius:50%; background:#1A3C6D; color:white;
                        display:flex; align-items:center; justify-content:center; font-weight:900; font-size:14px; flex-shrink:0; }
                    .lf-step-content { flex:1; }
                    .lf-step-title { font-weight:700; font-size:14px; color:#1A3C6D; margin-bottom:4px; }
                    .lf-step-detail { font-size:13px; color:#374151; line-height:1.6; }
                    .lf-step-hint { background:#FFFBEB; border-left:3px solid #F59E0B; padding:8px 12px;
                        font-size:12px; color:#92400E; margin-top:8px; border-radius:0 8px 8px 0; }
                    .lf-step-svg { margin-top:8px; text-align:center; }
                    @media (max-width:768px) {
                        .lf-solver-step { flex-direction:column; gap:6px; }
                        .lf-step-num { width:28px; height:28px; font-size:12px; }
                    }
                `;
                document.head.appendChild(style);
            }
        },

        // Pre-built solution templates for common math problems
        getTemplate(trapType) {
            var templates = {
                'T4': [ // Area trap example
                    { title: '\u78ba\u8a8d\u5716\u5f62\u985e\u578b', content: '\u4ed4\u7d30\u89c0\u5bdf\u5716\u5f62\uff0c\u78ba\u5b9a\u662f\u5e73\u884c\u56db\u908a\u5f62\u3001\u4e09\u89d2\u5f62\u908a\u662f\u68af\u5f62\u3002\u6ce8\u610f\uff1a\u4e09\u89d2\u5f62\u9762\u7a4d\u516c\u5f0f\u662f\u300c\u5e95\u00d7\u9ad8\u00f72\u300d\uff0c\u4e0d\u80fd\u6f0f\u6389\u96642\uff01', hint: '\u5148\u7528\u925b\u7b46\u5c07\u5716\u5f62\u540d\u7a31\u5beb\u5728\u65c1\u908a\uff0c\u907f\u514d\u7528\u932f\u516c\u5f0f' },
                    { title: '\u627e\u51fa\u5e95\u548c\u9ad8', content: '\u5e73\u884c\u56db\u908a\u5f62\uff1a\u5e95 = \u4efb\u4f55\u4e00\u908a\uff0c\u9ad8 = \u5f9e\u5c0d\u908a\u5782\u76f4\u5230\u5e95\u7684\u8ddd\u96e2<br>\u4e09\u89d2\u5f62\uff1a\u5e95 = \u4efb\u4f55\u4e00\u908a\uff0c\u9ad8 = \u5f9e\u5c0d\u89d2\u5782\u76f4\u5230\u5e95\u7684\u8ddd\u96e2', hint: '\u5982\u679c\u5716\u4e2d\u6c92\u6709\u6a19\u660e\u9ad8\uff0c\u81ea\u5df1\u7528\u865b\u7dda\u756b\u51fa\u4f86\uff01' },
                    { title: '\u5957\u7528\u516c\u5f0f\u8a08\u7b97', content: '\u5c07\u5e95\u548c\u9ad8\u7684\u6578\u503c\u4ee3\u5165\u516c\u5f0f\u3002<br>\u25b6 \u5e73\u884c\u56db\u908a\u5f62\u9762\u7a4d = \u5e95 \u00d7 \u9ad8<br>\u25b6 \u4e09\u89d2\u5f62\u9762\u7a4d = \u5e95 \u00d7 \u9ad8 \u00f7 2', hint: '\u8a18\u4f4f\u53e3\u8a23\uff1a\u300c\u5e95\u4e58\u9ad8\u4fc2\u5e73\u884c\u56db\uff0c\u5e95\u4e58\u9ad8\u9664\u4e8c\u4fc2\u4e09\u89d2\u300d' },
                    { title: '\u6aa2\u67e5\u55ae\u4f4d\u548c\u7b54\u53e5', content: '\u78ba\u8a8d\u7b54\u6848\u55ae\u4f4d\u662f cm\u00b2 \u6216 m\u00b2\u3002\u5beb\u4e0a\u5b8c\u6574\u7b54\u53e5\uff1a\u300cXX\u5716\u5f62\u7684\u9762\u7a4d\u662f ___ cm\u00b2\u300d', hint: '\u6f0f\u5beb\u7b54\u53e5 = \u6263 1 \u5206\uff01' }
                ],
                'T6': [ // Fraction trap example
                    { title: '\u78ba\u8a8d\u5206\u6bcd\u662f\u5426\u76f8\u540c', content: '\u6aa2\u67e5\u5169\u500b\u5206\u6578\u7684\u5206\u6bcd\u662f\u5426\u4e00\u6a23\u3002\u5982\u679c\u4e0d\u540c\uff0c\u9700\u8981\u5148\u901a\u5206\uff08\u627e\u6700\u5c0f\u516c\u500d\u6578 LCM\uff09\u3002', hint: '\u5206\u6bcd\u4e0d\u540c\u5c31\u505a\u52a0\u6e1b = \u5fc5\u6b7b\u9677\u9631\uff01' },
                    { title: '\u901a\u5206', content: '\u627e\u51fa\u5169\u500b\u5206\u6bcd\u7684 LCM\uff0c\u5c07\u5169\u500b\u5206\u6578\u8f49\u5316\u70ba\u540c\u5206\u6bcd\u3002\u8a18\u4f4f\u5206\u5b50\u4e5f\u8981\u540c\u6a23\u500d\u6578\u8b8a\u5316\uff01', hint: '\u5206\u6bcd\u00d7N \u2192 \u5206\u5b50\u4e5f\u8981 \u00d7N\uff01' },
                    { title: '\u5206\u5b50\u52a0\u6e1b', content: '\u5206\u6bcd\u4e0d\u8b8a\uff0c\u53ea\u5c07\u5206\u5b50\u76f8\u52a0\u6216\u76f8\u6e1b\u3002\u6700\u5f8c\u6aa2\u67e5\u662f\u5426\u53ef\u4ee5\u7d04\u5206\u3002', hint: '\u5206\u6bcd\u6c38\u9060\u4e0d\u8b8a\u5728\u52a0\u6e1b\u4e2d\uff01' }
                ]
            };
            return templates[trapType] || templates['T4'];
        }
    },

    // ══════════════════════════════════
    // #15 VOICE READER (Web Speech API)
    // ══════════════════════════════════
    voiceReader: {
        speaking: false,
        utterance: null,

        read(text, lang) {
            if (!('speechSynthesis' in window)) {
                alert('\u4f60\u7684\u700f\u89bd\u5668\u4e0d\u652f\u63f4\u8a9e\u97f3\u529f\u80fd\u3002\u8acb\u4f7f\u7528 Chrome \u6216 Edge\u3002');
                return;
            }
            window.speechSynthesis.cancel();
            this.utterance = new SpeechSynthesisUtterance(text);
            this.utterance.lang = lang || 'zh-HK';
            this.utterance.rate = 0.9;
            this.utterance.pitch = 1;
            this.speaking = true;
            window.speechSynthesis.speak(this.utterance);
            this.utterance.onend = function() { LF_UTILS.voiceReader.speaking = false; };
        },

        stop() {
            window.speechSynthesis.cancel();
            this.speaking = false;
        },

        // Read a math question aloud (with pauses for comprehension)
        readQuestion(questionText, hints) {
            if (this.speaking) this.stop();
            this.read(questionText, 'zh-HK');
            if (hints && hints.length) {
                // Read hints after a pause
                var self = this;
                setTimeout(function() {
                    self.read('\u63d0\u793a\uff1a' + hints[0], 'zh-HK');
                }, 3000);
            }
        },

        renderButton(containerId, text) {
            var container = document.getElementById(containerId);
            if (!container) return;
            var self = this;
            var btn = document.createElement('button');
            btn.className = 'btn btn-outline btn-sm';
            btn.innerHTML = `\ud83d\udd0a ${this.speaking ? '\u505c\u6b62\u64ad\u5831' : '\u8a9e\u97f3\u8b80\u984c'}`;
            btn.onclick = function() {
                if (self.speaking) { self.stop(); btn.innerHTML = '\ud83d\udd0a \u8a9e\u97f3\u8b80\u984c'; }
                else { self.read(text || container.textContent || '\u6c92\u6709\u5167\u5bb9'); btn.innerHTML = '\ud83d\udd0a \u505c\u6b62\u64ad\u5831'; }
            };
            container.appendChild(btn);
        }
    },

    // ══════════════════════════════════
    // #14 DATA DOWNLOAD
    // ══════════════════════════════════
    dataDownload: {
        // Download any data as CSV
        downloadCSV(data, filename) {
            // data = array of objects
            if (!data || !data.length) { alert('\u6c92\u6709\u6578\u64da\u53ef\u4e0b\u8f09'); return; }
            var headers = Object.keys(data[0]);
            var csv = headers.join(',') + '\n';
            data.forEach(function(row) {
                var vals = headers.map(function(h) {
                    var v = (row[h] || '').toString();
                    return v.includes(',') || v.includes('"') ? '"' + v.replace(/"/g, '""') + '"' : v;
                });
                csv += vals.join(',') + '\n';
            });
            var blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' });
            var url = URL.createObjectURL(blob);
            var a = document.createElement('a');
            a.href = url;
            a.download = (filename || 'data') + '_' + new Date().toISOString().slice(0,10) + '.csv';
            a.click();
            URL.revokeObjectURL(url);
        },

        // Download student progress report as CSV
        downloadStudentReport(studentName) {
            var members = [];
            try { members = JSON.parse(localStorage.getItem('lf_members') || '[]'); } catch(e) {}

            var data = members.map(function(m) {
                return {
                    '\u5b78\u751f': m.student || '',
                    '\u5e74\u7d1a': m.grade || '',
                    '\u5bb6\u9577': m.parent || '',
                    '\u96fb\u8a71': m.phone || '',
                    '\u8a08\u5283': m.plan || 'free',
                    '\u5230\u671f\u65e5': m.expiry ? new Date(m.expiry).toLocaleDateString('zh-HK') : '\u6c38\u4e45',
                    '\u6ce8\u518a\u65e5': m.activated ? new Date(m.activated).toLocaleDateString('zh-HK') : ''
                };
            });
            this.downloadCSV(data, '\u5b78\u751f\u540d\u55ae');
        },

        // Download analytics as CSV
        downloadAnalytics(analyticsData) {
            this.downloadCSV(analyticsData || [], '\u5b78\u60c5\u5206\u6790');
        }
    },

    // ══════════════════════════════════
    // #12 BATCH NOTIFICATIONS
    // ══════════════════════════════════
    batchNotify: {
        // Send notification to all members via WhatsApp (simulated)
        sendToAll(message) {
            var members = [];
            try { members = JSON.parse(localStorage.getItem('lf_members') || '[]'); } catch(e) {}
            var withPhone = members.filter(function(m) { return m.phone; });

            if (!withPhone.length) {
                alert('\u6c92\u6709\u5b78\u751f\u6709\u96fb\u8a71\u865f\u78bc\uff0c\u8acb\u5148\u5c0e\u5165\u5b78\u751f\u3002');
                return;
            }

            if (!confirm('\u5c07\u767c\u9001\u7d66 ' + withPhone.length + ' \u4f4d\u5b78\u751f\u5bb6\u9577\uff1a\n' + message)) return;

            // In production: call WhatsApp Business API
            // For demo: simulate
            var sent = 0;
            withPhone.forEach(function(m) {
                // Simulate sending
                sent++;
                console.log('[Batch Notify] Sent to ' + m.phone + ' (' + m.student + ')');
            });

            alert('\u2705 \u5df2\u767c\u9001\u7d66 ' + sent + ' \u4f4d\u5b78\u751f\u5bb6\u9577\uff01');
            return sent;
        },

        // Send class reminder
        sendClassReminder(className, date, time) {
            var msg = '\ud83d\udce2 \u9716\u6953\u5b78\u82d1\u63d0\u9192\uff1a' + (className || '\u60a8\u7684\u73ed\u7d1a') + '\n\u4e0b\u5802\u6642\u9593\uff1a' + (date || '\u5f85\u78ba\u5b9a') + ' ' + (time || '');
            msg += '\n\u8acb\u6e96\u6642\u51fa\u5e2d\uff01\u5982\u6709\u8b8a\u52d5\u8acb\u63d0\u524d\u901a\u77e5\u3002';
            return this.sendToAll(msg);
        },

        // Send payment reminder
        sendPaymentReminder(daysBeforeExpiry) {
            var members = [];
            try { members = JSON.parse(localStorage.getItem('lf_members') || '[]'); } catch(e) {}

            var expiring = members.filter(function(m) {
                if (!m.expiry) return false;
                var days = Math.ceil((new Date(m.expiry) - Date.now()) / 86400000);
                return days > 0 && days <= (daysBeforeExpiry || 7);
            });

            if (!expiring.length) {
                alert('\u6c92\u6709\u5373\u5c07\u5230\u671f\u7684\u6703\u54e1\u3002');
                return;
            }

            var msg = '\ud83d\udcb3 \u9716\u6953\u5b78\u82d1\u7e8c\u8cbb\u63d0\u9192\n\u60a8\u7684\u8a02\u95b1\u5373\u5c07\u5230\u671f\uff0c\u8acb\u76e1\u5feb\u7e8c\u8cbb\u4ee5\u514d\u5f71\u97ff\u5b78\u7fd2\u9032\u5ea6\u3002\n\u67e5\u770b\u8a73\u60c5\uff1a' + window.location.origin + '/docs/pricing.html';
            return this.sendToAll(msg);
        },

        renderButton(containerId, message) {
            var container = document.getElementById(containerId);
            if (!container) return;
            var btn = document.createElement('button');
            btn.className = 'btn btn-gold btn-sm';
            btn.textContent = '\ud83d\udce3 \u6279\u91cf\u901a\u77e5';
            btn.onclick = function() { LF_UTILS.batchNotify.sendToAll(message || '\u8acb\u67e5\u770b\u6700\u65b0\u8ab2\u7a0b\u5b89\u6392\uff01'); };
            container.appendChild(btn);
        }
    }
};

console.log('[LF Utils v1.0] Visual Solver · Voice Reader · Data Download · Batch Notify ready');