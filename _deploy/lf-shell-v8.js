/* ═══════════════════════════════════════════════════════
   霖楓學苑 · LF Academy v8.0 — Shared Component Shell
   2026-06-04 · Nav · Auth · Membership · Events · Analytics
   Dependencies: lf-academy-v8.css, Firebase SDK (optional)
   ═══════════════════════════════════════════════════════ */

const LF = {
  version: '8.0.0',
  apiBase: 'https://lf-api-f80h.onrender.com',
  aiLocal: 'http://localhost:3687/v1/chat/completions',

  /* ── State ── */
  state: {
    user: null,
    role: null,
    membership: 'free',
    usage: { ai: 0, practice: 0, date: '' },
    online: true,
    page: document.title || ''
  },

  /* ── Config ── */
  tiers: {
    free:   { name: '免費體驗', aiDaily: 10,  practiceDaily: 5,   diagReport: false, price: '$0',      color: '#64748b' },
    basic:  { name: '基本會員', aiDaily: 50,  practiceDaily: 999, diagReport: true,  price: '$88/月',  color: '#16A34A' },
    pro:    { name: '專業會員', aiDaily: 999, practiceDaily: 9999,diagReport: true,  price: '$168/月', color: '#7C3AED' }
  },

  /* ═══════════════ INIT ═══════════════ */
  async init() {
    this._initFirebase();
    this._checkAPI();
    this._loadLocalState();
    this.renderNav();
    this.renderFooter();
    this._initOfflineDetection();
    this._initPerfMonitoring();
    this._initKeyboardShortcuts();`r`n    this._initPerfMonitoring();`r`n    this._initKeyboardShortcuts();
    this._setupCrossTab();
    console.log('[LF v8.0] Shell ready. User:', this.state.user ? this.state.user.email : 'guest');
    window.dispatchEvent(new CustomEvent('lf:ready', { detail: this.state }));
  },

  /* ═══════════════ FIREBASE ═══════════════ */
  _initFirebase() {
    if (typeof firebase === 'undefined' || typeof LF_FIREBASE_CONFIG === 'undefined') {
      console.log('[LF] Firebase not available, running in local mode');
      return;
    }
    try {
      if (firebase.apps && firebase.apps.length > 0) {
        this.auth = firebase.auth();
        this.db = firebase.firestore();
        this.auth.onAuthStateChanged(user => this._onAuthChange(user));
        console.log("[LF] Firebase already initialized, reusing");
        return;
      }
      firebase.initializeApp(LF_FIREBASE_CONFIG);
      this.auth = firebase.auth();
      this.db = firebase.firestore();
      this.auth.onAuthStateChanged(user => this._onAuthChange(user));
    } catch(e) { console.warn('[LF] Firebase init error:', e.message); }
  },

  async _onAuthChange(user) {
    this.state.user = user;
    if (user) {
      try {
        const doc = await this.db.collection('users').doc(user.uid).get();
        if (doc.exists) {
          const d = doc.data();
          this.state.role = d.role || 'student';
          this.state.membership = d.membership || 'free';
        }
        await this._loadUsage();
      } catch(e) {}
      try {
        localStorage.setItem('lf_user_name', user.displayName || '');
        localStorage.setItem('lf_user_email', user.email || '');
        localStorage.setItem('lf_user_role', this.state.role);
      } catch(e) {}
    } else {
      this.state.role = null;
      this.state.membership = 'free';
      this.state.usage = { ai: 0, practice: 0, date: '' };
    }
    this.refreshUI();
    window.dispatchEvent(new CustomEvent('lf:auth', { detail: this.state }));
  },

  _loadLocalState() {
    try {
      const name = localStorage.getItem('lf_user_name');
      const email = localStorage.getItem('lf_user_email');
      const role = localStorage.getItem('lf_user_role');
      if (email) {
        this.state.user = { email, displayName: name, isLocal: true };
        this.state.role = role || 'student';
      }
    } catch(e) {}
  },

  async _loadUsage() {
    if (!this.state.user || !this.db) return;
    const today = new Date().toISOString().slice(0,10);
    try {
      const doc = await this.db.collection('users').doc(this.state.user.uid)
        .collection('usage').doc(today).get();
      if (doc.exists) { this.state.usage = doc.data(); this.state.usage.date = today; }
    } catch(e) {
      const saved = localStorage.getItem('lf_usage_' + today);
      if (saved) { try { this.state.usage = JSON.parse(saved); } catch(e2) {} }
    }
  },

  async _checkAPI() {
    try {
      const r = await fetch(this.apiBase + '/api/health', { signal: AbortSignal.timeout(4000) });
      this.state.online = r.ok;
    } catch(e) { this.state.online = false; }
  },


  /* ═══════════════ OFFLINE DETECTION ═══════════════ */
  _initOfflineDetection() {
    this.state.isOnline = navigator.onLine;
    window.addEventListener('online', () => {
      this.state.isOnline = true;
      this.toast('網絡已恢復連線 🌐', 'success', 2000);
      this._checkAPI();
    });
    window.addEventListener('offline', () => {
      this.state.isOnline = false;
      this.toast('網絡離線 — 使用本地模式 📡', 'error', 4000);
    });
  },

  _setupCrossTab() {
    window.addEventListener('storage', (e) => {
      if (e.key === 'lf_session') { this._loadLocalState(); this.refreshUI(); }
    });
  },

  /* ═══════════════ USAGE ═══════════════ */
  async trackUsage(type) {
    const today = new Date().toISOString().slice(0,10);
    if (this.state.usage.date !== today) {
      this.state.usage = { ai: 0, practice: 0, date: today };
    }
    this.state.usage[type] = (this.state.usage[type] || 0) + 1;

    if (this.state.user && this.db) {
      try {
        await this.db.collection('users').doc(this.state.user.uid)
          .collection('usage').doc(today).set(this.state.usage, { merge: true });
      } catch(e) {}
    }
    try { localStorage.setItem('lf_usage_' + today, JSON.stringify(this.state.usage)); } catch(e) {}
    this.refreshUI();
  },

  checkLimit(type) {
    const tier = this.tiers[this.state.membership];
    if (!tier) return true;
    const limit = type === 'ai' ? tier.aiDaily : tier.practiceDaily;
    return (this.state.usage[type] || 0) < limit;
  },

  remainingText(type) {
    const tier = this.tiers[this.state.membership];
    const limit = type === 'ai' ? tier.aiDaily : tier.practiceDaily;
    const used = this.state.usage[type] || 0;
    return Math.max(0, limit - used) + '/' + limit;
  },

  /* ═══════════════ NAV RENDER ═══════════════ */
  renderNav() {
    const existing = document.querySelector('.lf-nav');
    if (existing) existing.remove();

    const mobileExisting = document.querySelector('.lf-nav-mobile');
    if (mobileExisting) mobileExisting.remove();

    const nav = document.createElement('nav');
    nav.className = 'lf-nav';
    nav.id = 'lfNav';
    nav.innerHTML = `
      <div class="lf-nav-inner">
        <a href="/" class="lf-nav-brand">
          <img src="/logo.png" alt="霖楓學苑" onerror="this.style.display='none'">
          霖楓學苑
        </a>
        <div class="lf-nav-links" id="lfNavLinks">
          <a href="/">首頁</a>
          <a href="/ai-tutor.html" class="nav-ai">🤖 AI導師</a>`n          <a href="/mimo-vision.html">🔬 MiMo</a>`n          <a href="/ai-diagnostic.html">🔬 診斷</a>
          <a href="/practice.html">📝 做題</a>`n          <a href="/smart-generate.html">🤖 出題</a>`n          <a href="/leaderboard.html">🏆 排行榜</a>`n      <a href="/bar-model.html">📐 圖解</a>`n          <a href="/bar-model.html">📐 圖解</a>`n          <a href="/student.html">🎒 學生</a>
          <a href="/membership.html">⭐ 會員</a>`n          <a href="/講義/master_index.html">📚 講義</a>
          <span id="lfNavUser"></span>
        </div>
        <button class="lf-nav-toggle" id="lfNavToggle" aria-label="Menu">
          <span></span><span></span><span></span>
        </button>
      </div>`;
    document.body.prepend(nav);

    const mobile = document.createElement('div');
    mobile.className = 'lf-nav-mobile';
    mobile.id = 'lfNavMobile';
    mobile.innerHTML = `
      <a href="/">🏠 首頁</a>
      <a href="/ai-tutor.html">🤖 AI導師</a>`n      <a href="/mimo-vision.html">🔬 MiMo Vision</a>`n      <a href="/ai-diagnostic.html">🔬 AI 診斷</a>
      <a href="/practice.html">📝 做題練習</a>`n      <a href="/smart-generate.html">🤖 AI出題</a>`n      <a href="/leaderboard.html">🏆 排行榜</a>`n      <a href="/bar-model.html">📐 圖解</a>`n          <a href="/bar-model.html">📐 圖解</a>`n      <a href="/student.html">🎒 學生中心</a>
      <a href="/membership.html">⭐ 會員中心</a>`n      <a href="/講義/master_index.html">📚 講義總索引</a>
      <a href="/launchpad.html">🚀 控制台</a>
      <span id="lfNavMobileUser"></span>`;
    document.body.appendChild(mobile);

    document.getElementById('lfNavToggle').addEventListener('click', () => {
      const btn = document.getElementById('lfNavToggle');
      const m = document.getElementById('lfNavMobile');
      btn.classList.toggle('open');
      m.classList.toggle('open');
    });

    window.addEventListener('scroll', () => {
      document.getElementById('lfNav').classList.toggle('scrolled', window.scrollY > 50);
    });

    this.refreshUI();
  },

  /* ═══════════════ FOOTER RENDER ═══════════════ */
  renderFooter() {
    const existing = document.querySelector('.lf-footer');
    if (existing) existing.remove();

    const footer = document.createElement('footer');
    footer.className = 'lf-footer';
    footer.innerHTML = `
      <div class="lf-footer-grid">
        <div>
          <h4>霖楓學苑 · LF Academy</h4>
          <p style="font-size:0.82em">不教數學，教避開陷阱。<br>香港小學數學陷阱診斷專家。<br>P3-P6 · 呈分試 · SSPA專家。</p>
        </div>
        <div>
          <h4>學習</h4>
          <a href="/ai-tutor.html">AI 數學導師</a>
          <a href="/practice.html">做題練習</a>
          <a href="/docs/ai-diagnostic.html">陷阱診斷</a>
          <a href="/docs/system-index.html">講義總索引</a>
        </div>
        <div>
          <h4>課程</h4>
          <a href="/docs/enroll.html">常規課程 P3-P6</a>
          <a href="/docs/sspa_rescue_package.html">SSPA 急救包</a>
          <a href="/membership.html">會員方案</a>
          <a href="/docs/testimonials.html">學生見證</a>
        </div>
        <div>
          <h4>聯絡</h4>
          <a href="https://wa.me/85294796459">WhatsApp 查詢</a>
          <a href="/auth.html">登入/註冊</a>
          <a href="/launchpad.html">內部系統</a>
        </div>
      </div>
      <div class="lf-footer-bottom">
        © 2026 霖楓學苑 · LF Academy. All rights reserved. · 不教數學，教避開陷阱。
      </div>`;
    document.body.appendChild(footer);
  },

  /* ═══════════════ UI REFRESH ═══════════════ */
  refreshUI() {
    const user = this.state.user;
    const tier = this.tiers[this.state.membership];
    const navUser = document.getElementById('lfNavUser');
    const mobileUser = document.getElementById('lfNavMobileUser');

    const userHTML = user
      ? `<a href="/membership.html" style="display:inline-flex;align-items:center;gap:6px;font-size:0.78em">
           <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${tier.color}"></span>
           ${user.displayName || user.email || '已登入'}
         </a>
         <button onclick="LF.logout()" class="lf-btn lf-btn-ghost lf-btn-sm" style="font-size:0.72em">登出</button>`
      : `<a href="/auth.html" class="lf-btn lf-btn-primary lf-btn-sm">🔑 登入</a>`;

    if (navUser) navUser.innerHTML = userHTML;
    if (mobileUser) mobileUser.innerHTML = user
      ? `<a href="/membership.html">👤 ${user.displayName || '會員中心'}</a>
         <a href="javascript:void(0)" onclick="LF.logout()" style="color:var(--red)">🚪 登出</a>`
      : `<a href="/auth.html" class="nav-cta">🔑 登入/註冊</a>`;

    // Update all usage displays
    document.querySelectorAll('[data-lf-usage]').forEach(el => {
      el.textContent = this.remainingText(el.dataset.lfUsage);
    });
  },

  /* ═══════════════ AUTH ═══════════════ */
  async login(email, password) {
    if (this.auth) {
      await this.auth.signInWithEmailAndPassword(email, password);
    } else {
      this.state.user = { email, displayName: email.split('@')[0], isLocal: true };
      this.state.role = 'student';
      this._saveLocalSession();
      this.refreshUI();
      window.dispatchEvent(new CustomEvent('lf:auth', { detail: this.state }));
    }
  },

  async signup(email, password, name, role) {
    if (this.auth) {
      const cred = await this.auth.createUserWithEmailAndPassword(email, password);
      await cred.user.updateProfile({ displayName: name || email.split('@')[0] });
      await this.db.collection('users').doc(cred.user.uid).set({
        email, displayName: name, role: role || 'student',
        membership: 'free', createdAt: firebase.firestore.FieldValue.serverTimestamp()
      });
    } else {
      this.state.user = { email, displayName: name || email.split('@')[0], isLocal: true };
      this.state.role = role || 'student';
      this.state.membership = 'free';
      this._saveLocalSession();
      this.refreshUI();
      window.dispatchEvent(new CustomEvent('lf:auth', { detail: this.state }));
    }
  },

  async googleLogin() {
    if (!this.auth) { this.toast('Google 登入暫不可用（離線模式）', 'error'); return; }
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });
    try {
      await this.auth.signInWithPopup(provider);
    } catch(e) {
      if (e.code === 'auth/popup-blocked') {
        await this.auth.signInWithRedirect(provider);
      } else {
        this.toast('Google 登入失敗: ' + e.message, 'error');
      }
    }
  },

  async logout() {
    if (this.auth) { await this.auth.signOut(); }
    localStorage.removeItem('lf_user_name');
    localStorage.removeItem('lf_user_email');
    localStorage.removeItem('lf_user_role');
    localStorage.removeItem('lf_session');
    this.state.user = null;
    this.state.role = null;
    this.state.membership = 'free';
    this.refreshUI();
    window.dispatchEvent(new CustomEvent('lf:auth', { detail: this.state }));
  },

  _saveLocalSession() {
    try {
      localStorage.setItem('lf_user_name', this.state.user.displayName || '');
      localStorage.setItem('lf_user_email', this.state.user.email || '');
      localStorage.setItem('lf_user_role', this.state.role || 'student');
      localStorage.setItem('lf_session', JSON.stringify({
        email: this.state.user.email,
        role: this.state.role,
        name: this.state.user.displayName,
        ts: Date.now()
      }));
    } catch(e) {}
  },

  /* ═══════════════ TOAST ═══════════════ */
  toast(msg, type = 'info', duration = 3000) {
    let container = document.querySelector('.lf-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'lf-toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = 'lf-toast lf-toast-' + type;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; }, duration - 300);
    setTimeout(() => toast.remove(), duration);
  },

  /* ═══════════════ MODAL ═══════════════ */
  modal(html, onClose) {
    const overlay = document.createElement('div');
    overlay.className = 'lf-modal-overlay';
    overlay.innerHTML = `<div class="lf-modal">${html}</div>`;
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) { overlay.remove(); if (onClose) onClose(); }
    });
    document.body.appendChild(overlay);
    return {
      close: () => { overlay.remove(); if (onClose) onClose(); },
      el: overlay.querySelector('.lf-modal')
    };
  },

  /* ═══════════════ AI CALL ═══════════════ */
  async aiAsk(prompt, systemPrompt) {
    // Try MiMo v2.5 API first (Xiaomi, best math reasoning)
    if (typeof MIMO !== 'undefined') {
      try {
        var result = await MIMO.tutorAsk(prompt, systemPrompt);
        if (result && result.content) return result.content;
      } catch(e) {}
    }

    // Try local frellmapi first (fallback)
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 8000);
      const r = await fetch(this.aiLocal, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'auto',
          messages: [
            { role: 'system', content: systemPrompt || '你係霖楓學苑AI數學導師。用繁體中文+廣東話回答。' },
            { role: 'user', content: prompt }
          ],
          max_tokens: 800, temperature: 0.7
        }),
        signal: ctrl.signal
      });
      clearTimeout(t);
      if (r.ok) {
        const d = await r.json();
        return d.choices?.[0]?.message?.content || null;
      }
    } catch(e) {}

    // Try Render API
    try {
      const r = await fetch(this.apiBase + '/api/ai/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, system: systemPrompt }),
        signal: AbortSignal.timeout(10000)
      });
      if (r.ok) {
        const d = await r.json();
        return d.response || d.text || null;
      }
    } catch(e) {}

    return null;
  },


  /* Returns: 'ok' | 'warn' | 'limit' — graduated usage check */
  checkLimitGraduated(type) {
    const tier = this.tiers[this.state.membership];
    if (!tier) return 'ok';
    const limit = type === 'ai' ? tier.aiDaily : tier.practiceDaily;
    const used = this.state.usage[type] || 0;
    if (used >= limit) return 'limit';
    if (used >= limit * 0.8) return 'warn';
    return 'ok';
  },

  /* Smart upgrade prompt — warns at 80%, prompts upgrade at limit */
  showUpgradePrompt(type) {
    const status = this.checkLimitGraduated(type);
    const tier = this.tiers[this.state.membership];
    const limit = type === 'ai' ? tier.aiDaily : tier.practiceDaily;
    const used = this.state.usage[type] || 0;
    const label = type === 'ai' ? 'AI問答' : '練習';

    if (status === 'limit') {
      this.toast('今日' + label + '次數已用完（' + used + '/' + limit + '）。升級解鎖更多！', 'error', 5000);
      return {
        blocked: true,
        msg: '⚠️ **' + tier.name + '** 今日' + label + '限額（' + limit + '次）已用完！' +
          '\n\n🔓 升級解鎖更多：\n⭐ 基本會員 ($88/月)：每日50次AI + 無限練習\n💎 專業會員 ($168/月)：無限AI + 每週診斷\n\n👉 <a href="/membership.html">查看會員方案</a>'
      };
    }

    if (status === 'warn') {
      this.toast('今日' + label + '剩餘 ' + (limit - used) + ' 次。考慮升級解鎖更多！', 'info', 3000);
      return { blocked: false, msg: '💡 今日' + label + '剩餘 **' + (limit - used) + '** 次。想無限使用？👉 <a href="/membership.html">升級會員</a>' };
    }

    return { blocked: false, msg: '' };
  },
  /* ═══════════════ EVENT BUS ═══════════════ */

  /* ═══ Performance Monitoring ═══ */
  _initPerfMonitoring() {
    if ('performance' in window && 'getEntriesByType' in performance) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const paint = performance.getEntriesByType('paint');
          const fcp = paint.find(e => e.name === 'first-contentful-paint');
          if (fcp) console.log('[LF Perf] FCP: ' + Math.round(fcp.startTime) + 'ms');
        }, 1000);
      });
    }
  },

  /* ═══ Keyboard Shortcuts ═══ */
  _initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (e.altKey && e.key === 's') {
        e.preventDefault();
        const input = document.querySelector('input[type="text"], input[type="search"], textarea');
        if (input) input.focus();
      }
      if (e.key === 'Escape') {
        document.querySelectorAll('.lf-modal-overlay').forEach(m => m.remove());
      }
    });
  },
  _events: {},
  on(event, fn) {
    if (!this._events[event]) this._events[event] = [];
    this._events[event].push(fn);
    return () => { this._events[event] = this._events[event].filter(f => f !== fn); };
  },
  emit(event, data) {
    if (this._events[event]) {
      this._events[event].forEach(fn => { try { fn(data); } catch(e) {} });
    }
  }
};

/* ── Auto-init on DOM ready ── */
document.addEventListener('DOMContentLoaded', () => LF.init());
