
// LF Voice Reader — Cantonese text-to-speech via Web Speech API
var LFVoice = {
  _synth: window.speechSynthesis,
  _voice: null,
  _rate: 0.9,
  _pitch: 1.1,
  _speaking: false,
  _queue: [],

  init: function() {
    var self = this;
    // Voices load async on Chrome
    if (this._synth.onvoiceschanged !== undefined) {
      this._synth.onvoiceschanged = function() { self._loadVoice(); };
    }
    this._loadVoice();
  },

  _loadVoice: function() {
    var voices = this._synth.getVoices();
    // Priority: zh-HK > yue > zh-TW > zh-CN > any Chinese
    this._voice = voices.find(function(v) { return v.lang === 'zh-HK'; })
              || voices.find(function(v) { return v.lang.startsWith('yue'); })
              || voices.find(function(v) { return v.lang === 'zh-TW'; })
              || voices.find(function(v) { return v.lang === 'zh-CN'; })
              || voices.find(function(v) { return v.lang.startsWith('zh'); })
              || voices[0];
  },

  speak: function(text, opts) {
    if (!this._synth) return;
    opts = opts || {};
    this._synth.cancel();
    this._speaking = true;
    var u = new SpeechSynthesisUtterance(text);
    u.voice = this._voice;
    u.rate = opts.rate || this._rate;
    u.pitch = opts.pitch || this._pitch;
    u.volume = opts.volume || 1;
    var self = this;
    u.onend = function() { self._speaking = false; self._next(); };
    u.onerror = function() { self._speaking = false; self._next(); };
    this._synth.speak(u);
  },

  speakQuestion: function(textEl, answerEls) {
    if (textEl) this.speak(textEl.textContent.trim());
    if (answerEls && answerEls.length) {
      var self = this;
      setTimeout(function() {
        answerEls.forEach(function(el, i) {
          setTimeout(function() { self.speak('選項' + ['A','B','C','D'][i] + '，' + el.textContent.trim()); }, i * 2500);
        });
      }, 2000);
    }
  },

  _next: function() {
    if (this._queue.length > 0) {
      this.speak(this._queue.shift());
    }
  },

  stop: function() {
    this._synth.cancel();
    this._speaking = false;
    this._queue = [];
  },

  createButton: function(text, label) {
    var self = this;
    var btn = document.createElement('button');
    btn.className = 'lf-voice-btn';
    btn.title = label || '聽題目';
    btn.style.cssText = 'display:inline-flex;align-items:center;gap:4px;padding:6px 12px;border-radius:20px;border:2px solid #C9A84C;background:white;color:#1A3C6D;cursor:pointer;font-size:13px;font-weight:700;font-family:inherit;transition:all 0.2s;vertical-align:middle;margin:0 4px';
    btn.innerHTML = '🔊 聽題目';
    btn.onmouseenter = function() { btn.style.background = '#FEF3C7'; };
    btn.onmouseleave = function() { btn.style.background = 'white'; };
    btn.onclick = function(e) {
      e.preventDefault();
      e.stopPropagation();
      if (self._speaking) { self.stop(); btn.innerHTML = '🔊 聽題目'; return; }
      btn.innerHTML = '⏹ 停止';
      self.speak(text, {rate: 0.85, pitch: 1.15});
      var checkDone = setInterval(function() {
        if (!self._speaking) { btn.innerHTML = '🔊 聽題目'; clearInterval(checkDone); }
      }, 500);
    };
    return btn;
  },

  createAutoReadToggle: function() {
    var self = this;
    var label = document.createElement('label');
    label.style.cssText = 'display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#6B7280;cursor:pointer';
    var cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.style.cssText = 'width:16px;height:16px;cursor:pointer';
    cb.onchange = function() {
      localStorage.setItem('lf_autoread', cb.checked ? '1' : '0');
    };
    cb.checked = localStorage.getItem('lf_autoread') === '1';
    label.appendChild(cb);
    label.appendChild(document.createTextNode('自動讀題'));
    return label;
  },

  get isAvailable() {
    return !!this._synth;
  },

  get hasCantonese() {
    return this._voice && (this._voice.lang === 'zh-HK' || this._voice.lang.startsWith('yue'));
  }
};

// Auto-init
if (typeof window !== 'undefined') {
  LFVoice.init();
}
