// ============================================================
// Engine: CONTENT PIPELINE (Auto Variant Generation)
// v15.0 EdTech AI · 內容管線引擎
// ============================================================
const CONTENT_PIPELINE = {
  _cache: {},
  _hashCache: {},

  // Simple hash for change detection
  _hash(str) {
    let h = 0;
    for (let i = 0; i < str.length; i++) { h = ((h << 5) - h) + str.charCodeAt(i); h |= 0; }
    return h.toString(36);
  },

  // Check if content has changed
  hasChanged(id, content) {
    const h = this._hash(content);
    const prev = this._hashCache[id];
    this._hashCache[id] = h;
    this._saveHashCache();
    return prev !== h;
  },

  // Generate variants from main content
  generateVariants(mainContent, options = {}) {
    const variants = { main: mainContent };
    
    // Short version (first 2 sentences)
    const sentences = mainContent.split(/[。！？\.!?]/);
    if (sentences.length >= 2) {
      variants.short = sentences.slice(0, 2).join('。') + '。';
    } else {
      variants.short = mainContent.substring(0, 150);
    }

    // Bullet point version
    const lines = mainContent.split('\n').filter(l => l.trim());
    const bullets = [];
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('u{2705}') || trimmed.startsWith('u{1F4CD}') || trimmed.startsWith('u{1F539}') || trimmed.startsWith('-') || trimmed.startsWith('u{2022}')) {
        bullets.push(trimmed);
      } else if (trimmed.length > 10) {
        bullets.push('u{2022} ' + trimmed.substring(0, 100));
      }
    }
    variants.bullets = bullets.slice(0, 5).join('\n');

    // Hashtag extraction
    const hashtags = mainContent.match(/#[\w\u4e00-\u9fff]+/g) || [];
    variants.hashtags = [...new Set(hashtags)].join(' ');

    // CTA extraction
    const ctaMatch = mainContent.match(/u{1F449}[^\n]+/);
    variants.cta = ctaMatch ? ctaMatch[0] : '';

    return variants;
  },

  // Sync check: what needs updating
  syncCheck(items) {
    const needsUpdate = [];
    for (const item of items) {
      if (this.hasChanged(item.id, item.content)) {
        needsUpdate.push(item.id);
      }
    }
    return needsUpdate;
  },

  _saveHashCache() {
    try { localStorage.setItem('lf_content_hash', JSON.stringify(this._hashCache)); } catch(e) {}
  },
  _loadHashCache() {
    try { const s = localStorage.getItem('lf_content_hash'); if (s) this._hashCache = JSON.parse(s); } catch(e) { this._hashCache = {}; }
  },
  init() { this._loadHashCache(); return this; }
};
