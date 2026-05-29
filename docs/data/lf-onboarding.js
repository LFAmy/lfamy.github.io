/**
 * LF Academy Onboarding v1.0
 * Interactive guided tour for new teachers
 * Auto-triggers on first visit after signup
 */
const LF_ONBOARD = {
    active: false,
    currentStep: 0,
    steps: [],

    // Default teacher onboarding steps
    teacherSteps: [
        {
            id: 'create-class',
            title: '\ud83c\udf93 \u5efa\u7acb\u4f60\u7684\u7b2c\u4e00\u500b\u73ed\u7d1a',
            desc: '\u9ede\u64ca\u9019\u88e1\u5efa\u7acb\u73ed\u7d1a\uff0c\u7cfb\u7d71\u5df2\u9810\u586b\u793a\u7bc4\u540d\u7a31\u3002\u4f60\u4e5f\u53ef\u4ee5\u76f4\u63a5\u4f7f\u7528\u793a\u7bc4\u73ed\u7d1a\u9ad4\u9a57\u529f\u80fd\uff01',
            target: '.stats, .card:first-of-type',
            position: 'bottom',
            highlight: true
        },
        {
            id: 'generate-exam',
            title: '\ud83d\udcdd \u751f\u6210\u7b2c\u4e00\u4efd\u8a66\u5377',
            desc: '\u9078\u64c7\u5e74\u7d1a \u2192 \u9078\u64c7\u77e5\u8b58\u9ede \u2192 \u9ede\u64ca\u751f\u6210\u300230\u79d2\u5c31\u80fd\u770b\u5230\u5c08\u696d\u6c34\u6e96\u7684\u8a66\u5377\uff01',
            target: '.quick-grid a[href*="smart-test-gen"], .quick-grid a[href*="test"]',
            position: 'top',
            highlight: true
        },
        {
            id: 'view-analytics',
            title: '\ud83d\udcca \u67e5\u770b\u5b78\u60c5\u770b\u677f',
            desc: '\u9ede\u64ca\u793a\u7bc4\u5b78\u751f\u67e5\u770b\u5b8c\u6574\u7684\u5b78\u60c5\u5206\u6790\uff1a\u96f7\u9054\u5716\u3001\u9032\u6b65\u66f2\u7dda\u3001\u77e5\u8b58\u9ede\u5206\u4f48\u3002\u6240\u6709\u6578\u64da\u5373\u6642\u66f4\u65b0\u3002',
            target: 'table, .card:nth-of-type(2)',
            position: 'top',
            highlight: true
        },
        {
            id: 'share-link',
            title: '\ud83d\udce4 \u5206\u4eab\u7df4\u7fd2\u9023\u7d50',
            desc: '\u8907\u88fd\u9019\u500b\u9023\u7d50\uff0c\u767c\u7d66\u4f60\u7684\u5b78\u751f\u3002\u4ed6\u5011\u9ede\u64ca\u5c31\u80fd\u76f4\u63a5\u958b\u59cb\u7df4\u7fd2\uff0c\u4e0d\u7528\u5b89\u88dd\u4efb\u4f55App\uff01',
            target: '.quick-grid a[href*="share"], .quick-grid a[href*="teacher-live"]',
            position: 'top',
            highlight: true
        },
        {
            id: 'complete',
            title: '\ud83c\udf89 \u4f60\u5df2\u638c\u63e1\u6838\u5fc3\u529f\u80fd\uff01',
            desc: '\u73fe\u5728\u4f60\u53ef\u4ee5\u958b\u59cb\u5efa\u7acb\u81ea\u5df1\u7684\u771f\u6b63\u73ed\u7d1a\uff0c\u5c0e\u5165\u5b78\u751f\uff0c\u958b\u59cb\u6559\u5b78\u3002\u9716\u6953\u5b78\u82d1\u6703\u4e00\u76f4\u966a\u4f4f\u4f60\uff01',
            target: '.header, h1',
            position: 'bottom',
            highlight: false
        }
    ],

    // Init
    init(steps) {
        // Only show for demo/new users
        if (typeof LFCore !== 'undefined' && LFCore.isOnboarded && LFCore.isOnboarded('teacher')) return;
        if (localStorage.getItem('lf_onboarded_teacher') === 'true') return;

        this.steps = steps || this.teacherSteps;
        this.currentStep = 0;
        this.active = true;
        this._createOverlay();
        this._showStep(0);
    },

    // Create overlay container
    _createOverlay() {
        // Remove existing
        var existing = document.getElementById('lf-onboard-overlay');
        if (existing) existing.remove();

        var overlay = document.createElement('div');
        overlay.id = 'lf-onboard-overlay';
        overlay.innerHTML = `
            <style>
                #lf-onboard-overlay { position:fixed; inset:0; z-index:9999; pointer-events:none; }
                .lf-ob-backdrop { position:fixed; inset:0; background:rgba(0,0,0,0.5); transition:all 0.3s; }
                .lf-ob-spotlight { position:fixed; border-radius:12px; box-shadow:0 0 0 9999px rgba(0,0,0,0.5); transition:all 0.4s cubic-bezier(0.4,0,0.2,1); z-index:1; pointer-events:none; }
                .lf-ob-tooltip { position:fixed; background:white; border-radius:16px; padding:24px; box-shadow:0 20px 60px rgba(0,0,0,0.3); max-width:380px; z-index:2; pointer-events:auto; animation:lfObIn 0.3s ease; }
                @keyframes lfObIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
                .lf-ob-tooltip h3 { font-size:18px; color:#1A3C6D; margin-bottom:8px; font-family:'Noto Sans HK',sans-serif; }
                .lf-ob-tooltip p { font-size:13px; color:#6B7280; line-height:1.6; margin-bottom:16px; }
                .lf-ob-progress { display:flex; gap:4px; margin-bottom:14px; }
                .lf-ob-dot { width:24px; height:4px; background:#E5E7EB; border-radius:2px; transition:all 0.3s; }
                .lf-ob-dot.done { background:#16A34A; }
                .lf-ob-dot.active { background:#1A3C6D; width:32px; }
                .lf-ob-btns { display:flex; gap:8px; align-items:center; }
                .lf-ob-btn { padding:10px 20px; border-radius:25px; font-weight:700; font-size:13px; cursor:pointer; border:none; font-family:'Noto Sans HK',sans-serif; transition:all 0.2s; }
                .lf-ob-btn-primary { background:#1A3C6D; color:white; }
                .lf-ob-btn-primary:hover { background:#1E4D8C; transform:translateY(-1px); }
                .lf-ob-btn-ghost { background:transparent; color:#9CA3AF; padding:10px 8px; }
                .lf-ob-btn-ghost:hover { color:#6B7280; }
                .lf-ob-step-count { font-size:11px; color:#9CA3AF; }
            </style>
            <div class="lf-ob-backdrop" id="lfObBackdrop"></div>
            <div class="lf-ob-spotlight" id="lfObSpotlight"></div>
            <div class="lf-ob-tooltip" id="lfObTooltip">
                <h3 id="lfObTitle"></h3>
                <p id="lfObDesc"></p>
                <div class="lf-ob-progress" id="lfObProgress"></div>
                <div class="lf-ob-btns">
                    <button class="lf-ob-btn lf-ob-btn-ghost" id="lfObSkip">\u8df3\u904e\u5c0e\u89bd</button>
                    <span style="flex:1"></span>
                    <span class="lf-ob-step-count" id="lfObStepCount"></span>
                    <button class="lf-ob-btn lf-ob-btn-primary" id="lfObNext">\u4e0b\u4e00\u6b65 \u2192</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        // Events
        document.getElementById('lfObNext').addEventListener('click', function() { LF_ONBOARD._next(); });
        document.getElementById('lfObSkip').addEventListener('click', function() { LF_ONBOARD._skip(); });
        document.getElementById('lfObBackdrop').addEventListener('click', function() { LF_ONBOARD._next(); });
    },

    _showStep(index) {
        if (index >= this.steps.length) {
            this._complete();
            return;
        }
        this.currentStep = index;
        var step = this.steps[index];
        var target = document.querySelector(step.target);

        // Update tooltip content
        document.getElementById('lfObTitle').textContent = step.title;
        document.getElementById('lfObDesc').textContent = step.desc;
        document.getElementById('lfObStepCount').textContent = 'Step ' + (index+1) + ' / ' + this.steps.length;

        // Update progress dots
        var dotsHtml = '';
        for (var i = 0; i < this.steps.length; i++) {
            var cls = i < index ? 'done' : i === index ? 'active' : '';
            dotsHtml += '<div class="lf-ob-dot ' + cls + '"></div>';
        }
        document.getElementById('lfObProgress').innerHTML = dotsHtml;

        // Update button text on last step
        var nextBtn = document.getElementById('lfObNext');
        if (index === this.steps.length - 1) {
            nextBtn.textContent = '\ud83c\udf89 \u5b8c\u6210\uff01';
        } else {
            nextBtn.textContent = '\u4e0b\u4e00\u6b65 \u2192';
        }

        // Position spotlight and tooltip
        var spotlight = document.getElementById('lfObSpotlight');
        var tooltip = document.getElementById('lfObTooltip');

        if (target && step.highlight) {
            var rect = target.getBoundingClientRect();
            var pad = 8;
            spotlight.style.display = 'block';
            spotlight.style.top = (rect.top - pad) + 'px';
            spotlight.style.left = (rect.left - pad) + 'px';
            spotlight.style.width = (rect.width + pad*2) + 'px';
            spotlight.style.height = (rect.height + pad*2) + 'px';
        } else {
            spotlight.style.display = 'none';
        }

        // Position tooltip near target or center
        if (target) {
            var rect = target.getBoundingClientRect();
            var tw = 380;
            var th = 250; // approximate
            if (step.position === 'bottom') {
                tooltip.style.top = Math.min(rect.bottom + 16, window.innerHeight - 280) + 'px';
                tooltip.style.left = Math.max(16, Math.min(rect.left + rect.width/2 - tw/2, window.innerWidth - tw - 16)) + 'px';
            } else if (step.position === 'top') {
                tooltip.style.top = Math.max(16, rect.top - 280) + 'px';
                tooltip.style.left = Math.max(16, Math.min(rect.left + rect.width/2 - tw/2, window.innerWidth - tw - 16)) + 'px';
            } else {
                tooltip.style.top = Math.max(16, rect.top + 16) + 'px';
                tooltip.style.left = Math.max(16, Math.min(rect.left + rect.width/2 - tw/2, window.innerWidth - tw - 16)) + 'px';
            }
        } else {
            // Center if no target
            tooltip.style.top = '50%';
            tooltip.style.left = '50%';
            tooltip.style.transform = 'translate(-50%,-50%)';
        }
    },

    _next() {
        if (this.currentStep < this.steps.length - 1) {
            this._showStep(this.currentStep + 1);
        } else {
            this._complete();
        }
    },

    _skip() {
        this._complete();
    },

    _complete() {
        this.active = false;
        // Mark as onboarded
        localStorage.setItem('lf_onboarded_teacher', 'true');
        if (typeof LFCore !== 'undefined' && LFCore.completeOnboarding) {
            LFCore.completeOnboarding('teacher');
        }
        // Remove overlay
        var overlay = document.getElementById('lf-onboard-overlay');
        if (overlay) overlay.remove();
        console.log('[LF Onboard] Tour completed!');
    },

    // Reset (for testing)
    reset() {
        localStorage.removeItem('lf_onboarded_teacher');
        if (typeof LFCore !== 'undefined') {
            LFCore.setData('onboarded_teacher', false);
        }
    }
};

// ========================================
// AUTO-TRIGGER FOR TEACHER DASHBOARD
// ========================================
(function() {
    // Wait for DOM + LFCore to be ready
    var attempts = 0;
    function tryInit() {
        attempts++;
        if (document.readyState === 'loading' && attempts < 20) {
            setTimeout(tryInit, 300);
            return;
        }
        // Check if we should show onboarding
        var isTeacher = (typeof LFCore !== 'undefined' && LFCore.getRole && LFCore.getRole() === 'teacher')
                     || window.location.pathname.includes('teacher-dashboard')
                     || window.location.pathname.includes('teacher-command');
        var isOnboarded = localStorage.getItem('lf_onboarded_teacher') === 'true';
        var hasRealData = localStorage.getItem('lf_has_data') === 'true';

        if (isTeacher && !isOnboarded && hasRealData) {
            // Delay slightly for page to render
            setTimeout(function() { LF_ONBOARD.init(); }, 800);
        }
    }
    // Auto-start check
    if (document.readyState !== 'loading') {
        setTimeout(tryInit, 500);
    } else {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(tryInit, 500);
        });
    }
})();

console.log('[LF Onboard v1.0] Ready');