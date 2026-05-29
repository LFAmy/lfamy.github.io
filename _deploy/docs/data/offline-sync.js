
// LF Offline Sync — detect, queue, replay
var LFOffline = {
  _online: navigator.onLine,
  _queue: JSON.parse(localStorage.getItem('lf_sync_queue') || '[]'),
  _banner: null,

  init: function() {
    var self = this;
    this._showBanner();
    window.addEventListener('online', function() { self._online = true; self._sync(); self._showBanner(); });
    window.addEventListener('offline', function() { self._online = false; self._showBanner(); });
    if (this._queue.length > 0 && this._online) this._sync();
  },

  get online() { return this._online; },

  queue: function(action, data) {
    this._queue.push({action: action, data: data, ts: Date.now()});
    localStorage.setItem('lf_sync_queue', JSON.stringify(this._queue));
    this._showBanner();
  },

  _sync: function() {
    var self = this;
    if (this._queue.length === 0) { this._showBanner(); return; }
    var batch = this._queue.slice();
    this._queue = [];
    localStorage.setItem('lf_sync_queue', '[]');

    // Process locally-stored actions
    var count = 0;
    batch.forEach(function(item) {
      if (item.action === 'save_test_result') {
        var results = JSON.parse(localStorage.getItem('lf_test_results') || '[]');
        results.push(item.data);
        localStorage.setItem('lf_test_results', JSON.stringify(results));
        count++;
      } else if (item.action === 'save_progress') {
        var key = 'lf_progress_' + (item.data.student || 'default');
        var prog = JSON.parse(localStorage.getItem(key) || '{}');
        Object.assign(prog, item.data);
        localStorage.setItem(key, JSON.stringify(prog));
        count++;
      } else if (item.action === 'save_badge') {
        var badges = JSON.parse(localStorage.getItem('lf_badges') || '[]');
        badges.push(item.data);
        localStorage.setItem('lf_badges', JSON.stringify(badges));
        count++;
      }
    });

    if (count > 0) {
      localStorage.setItem('lf_last_sync', new Date().toISOString());
      localStorage.setItem('lf_synced_count', String(Number(localStorage.getItem('lf_synced_count') || '0') + count));
    }
    this._showBanner();
    if (navigator.serviceWorker && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({type: 'REPLAY_SYNC'});
    }
  },

  _showBanner: function() {
    var existing = document.getElementById('lf-offline-banner');
    if (existing) existing.remove();

    var banner = document.createElement('div');
    banner.id = 'lf-offline-banner';
    banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;padding:8px 16px;text-align:center;font-size:12px;font-weight:700;font-family:sans-serif;transition:all 0.3s';

    if (!this._online) {
      banner.style.background = '#FEF2F2';
      banner.style.color = '#991B1B';
      banner.textContent = '⚡ 離線模式 — 你的答案會自動儲存，恢復連線後同步';
    } else if (this._queue.length > 0) {
      banner.style.background = '#FEF3C7';
      banner.style.color = '#92400E';
      banner.textContent = '正在同步 ' + this._queue.length + ' 項資料…';
      banner.style.cursor = 'pointer';
      banner.onclick = function() { LFOffline._sync(); };
    } else {
      return; // No banner needed
    }
    document.body.prepend(banner);
  },

  getStatus: function() {
    return {
      online: this._online,
      queued: this._queue.length,
      lastSync: localStorage.getItem('lf_last_sync'),
      syncedCount: Number(localStorage.getItem('lf_synced_count') || 0)
    };
  }
};

// Auto-init
if (typeof window !== 'undefined') {
  document.addEventListener('DOMContentLoaded', function() { LFOffline.init(); });
}
