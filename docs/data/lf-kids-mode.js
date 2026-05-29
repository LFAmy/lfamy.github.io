/**
 * LF Academy Kids Mode v1.0
 * Child-friendly interface for P1-P4 students
 * Large fonts, big buttons, cute animations, voice encouragement
 */
const LF_KIDS = {
    enabled: false,
    grade: null,

    // Grade thresholds
    kidsGrades: ['P1','P2','P3'],

    init() {
        // Check URL param
        var params = new URLSearchParams(window.location.search);
        if (params.get('kids') === '1') {
            this.enable();
            return;
        }
        if (params.get('kids') === '0') {
            this.disable();
            return;
        }

        // Check localStorage
        var saved = localStorage.getItem('lf_kids_mode');
        if (saved === 'true') {
            this.enable();
            return;
        }
        if (saved === 'false') {
            this.disable();
            return;
        }

        // Auto-detect from student grade
        var grade = this._detectGrade();
        if (grade && this.kidsGrades.indexOf(grade) >= 0) {
            this.enable(true); // auto mode
        }
    },

    _detectGrade() {
        // Try from URL
        var params = new URLSearchParams(window.location.search);
        var grade = params.get('grade');
        if (grade) return grade;

        // Try from localStorage
        try {
            var user = JSON.parse(localStorage.getItem('lf_session') || 'null');
            if (user && user.grade) return user.grade;
        } catch(e) {}

        // Try from current student
        try {
            var progress = JSON.parse(localStorage.getItem('lf_student_progress') || 'null');
            if (progress && progress.grade) return progress.grade;
        } catch(e) {}

        return null;
    },

    enable(auto) {
        if (this.enabled) return;
        this.enabled = true;
        document.body.classList.add('lf-kids-mode');
        if (!auto) localStorage.setItem('lf_kids_mode', 'true');

        // Inject kids-mode CSS
        if (!document.getElementById('lf-kids-css')) {
            var style = document.createElement('style');
            style.id = 'lf-kids-css';
            style.textContent = `
                body.lf-kids-mode {
                    font-size: 18pt !important;
                    --kids-bg: #FFF8F0;
                    --kids-card: #FFFFFF;
                    --kids-accent: #FF6B6B;
                    --kids-green: #4ECDC4;
                    --kids-yellow: #FFE66D;
                    --kids-blue: #45B7D1;
                    --kids-purple: #A06CD5;
                }
                body.lf-kids-mode .card {
                    border-radius: 24px !important;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.08) !important;
                    border: 3px solid #FFE0E0 !important;
                    font-size: 16pt !important;
                }
                body.lf-kids-mode button, body.lf-kids-mode .btn {
                    font-size: 16pt !important;
                    padding: 16px 28px !important;
                    border-radius: 30px !important;
                    min-height: 48px !important;
                    min-width: 48px !important;
                    font-weight: 900 !important;
                }
                body.lf-kids-mode input, body.lf-kids-mode select {
                    font-size: 16pt !important;
                    padding: 14px 18px !important;
                    min-height: 48px !important;
                }
                body.lf-kids-mode h1 { font-size: 28pt !important; }
                body.lf-kids-mode h2 { font-size: 22pt !important; }
                body.lf-kids-mode td, body.lf-kids-mode th { font-size: 14pt !important; padding: 12px !important; }

                /* Cute animations */
                body.lf-kids-mode .card:hover {
                    transform: scale(1.02) rotate(-0.5deg) !important;
                    transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55) !important;
                }
                body.lf-kids-mode button:hover {
                    transform: scale(1.1) !important;
                    transition: all 0.2s cubic-bezier(0.68, -0.55, 0.27, 1.55) !important;
                }

                /* Rainbow progress bars */
                body.lf-kids-mode .bar-fill, body.lf-kids-mode [style*="width:%"] {
                    background: linear-gradient(90deg, #FF6B6B, #FFE66D, #4ECDC4, #45B7D1, #A06CD5) !important;
                    background-size: 200% 100% !important;
                    animation: lfKidsRainbow 3s linear infinite !important;
                }
                @keyframes lfKidsRainbow {
                    0% { background-position: 0% 50%; }
                    100% { background-position: 200% 50%; }
                }

                /* Star decorations */
                body.lf-kids-mode .card h2::before { content: '\u2B50 '; }
                body.lf-kids-mode .header { background: linear-gradient(135deg, #FF6B6B, #A06CD5) !important; }

                /* Bigger emojis */
                body.lf-kids-mode { --emoji-scale: 1.5; }
            `;
            document.head.appendChild(style);
        }

        // Inject encouragement system
        this._injectEncouragement();

        console.log('[LF Kids] Kids mode ' + (auto ? 'auto-' : '') + 'enabled for ' + (this._detectGrade() || 'unknown grade'));
    },

    disable() {
        this.enabled = false;
        document.body.classList.remove('lf-kids-mode');
        localStorage.setItem('lf_kids_mode', 'false');
        var css = document.getElementById('lf-kids-css');
        if (css) css.remove();
        var enc = document.getElementById('lf-kids-encourage');
        if (enc) enc.remove();
        console.log('[LF Kids] Kids mode disabled');
    },

    toggle() {
        if (this.enabled) this.disable();
        else this.enable();
    },

    _injectEncouragement() {
        if (document.getElementById('lf-kids-encourage')) return;

        var div = document.createElement('div');
        div.id = 'lf-kids-encourage';
        div.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:999;pointer-events:none;';

        var messages = [
            '\ud83c\udf1f \u505a\u5f97\u597d\uff01',
            '\ud83d\udc4f \u592a\u68d2\u4e86\uff01',
            '\ud83d\ude80 \u7e7c\u7e8c\u52a0\u6cb9\uff01',
            '\ud83e\udd47 \u4f60\u662f\u6700\u68d2\u7684\uff01',
            '\ud83c\udf38 \u771f\u53b2\u5bb3\uff01',
            '\ud83e\uddb8 \u9b54\u6cd5\u4e00\u822c\uff01',
            '\ud83e\udd73 \u592a\u5f37\u4e86\uff01'
        ];

        // Show encouragement on button clicks
        document.addEventListener('click', function(e) {
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('button')) {
                var msg = messages[Math.floor(Math.random() * messages.length)];
                var el = document.createElement('div');
                el.textContent = msg;
                el.style.cssText = 'position:fixed;bottom:80px;right:20px;font-size:24pt;animation:lfKidsPop 1.5s ease forwards;pointer-events:none;z-index:999';
                document.body.appendChild(el);
                setTimeout(function() { el.remove(); }, 1500);
            }
        });

        // Add CSS animation
        var animStyle = document.createElement('style');
        animStyle.textContent = '@keyframes lfKidsPop { 0%{opacity:0;transform:scale(0.5) translateY(0)} 30%{opacity:1;transform:scale(1.2) translateY(-20px)} 100%{opacity:0;transform:scale(0.8) translateY(-60px)} }';
        document.head.appendChild(animStyle);

        document.body.appendChild(div);
    },

    // Toggle button UI
    renderToggle() {
        var isKids = this.enabled;
        return `
        <div style="display:inline-flex;align-items:center;gap:6px;font-size:11px">
            <span>' + (isKids ? '\ud83e\uddb8' : '\ud83d\udc74') + '</span>
            <label style="position:relative;display:inline-block;width:40px;height:22px">
                <input type="checkbox" ' + (isKids ? 'checked' : '') + ' onchange="LF_KIDS.toggle()" style="opacity:0;width:0;height:0">
                <span style="position:absolute;cursor:pointer;inset:0;background:' + (isKids ? '#A06CD5' : '#E5E7EB') + ';border-radius:22px;transition:0.3s"></span>
                <span style="position:absolute;height:18px;width:18px;left:2px;bottom:2px;background:white;border-radius:50%;transition:0.3s;' + (isKids ? 'transform:translateX(18px)' : '') + '"></span>
            </label>
            <span style="font-weight:600;color:' + (isKids ? '#A06CD5' : '#9CA3AF') + '">\u5152\u7ae5\u6a21\u5f0f</span>
        </div>`;
    }
};

// Auto-init
(function() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { LF_KIDS.init(); });
    } else {
        LF_KIDS.init();
    }
})();

console.log('[LF Kids v1.0] Ready');