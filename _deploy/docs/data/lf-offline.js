/**
 * LF Academy Offline Engine v1.0
 * 離線答題隊列 · 自動同步 · 離線指示器
 */
const LFOffline = {
    queue: [],
    syncInProgress: false,

    init() {
        this.loadQueue();
        this.setupListeners();
        this.showIndicator();
        console.log('[LF Offline] Engine initialized. Queue:', this.queue.length, 'items');
    },

    // ==========================================
    // QUEUE MANAGEMENT
    // ==========================================
    loadQueue() {
        try {
            this.queue = JSON.parse(localStorage.getItem('lf_offline_queue') || '[]');
        } catch(e) {
            this.queue = [];
        }
    },

    saveQueue() {
        localStorage.setItem('lf_offline_queue', JSON.stringify(this.queue));
    },

    enqueue(answer) {
        this.queue.push({
            ...answer,
            timestamp: Date.now(),
            queued: true,
        });
        this.saveQueue();
        
        // Try to register background sync
        if ('serviceWorker' in navigator && 'SyncManager' in window) {
            navigator.serviceWorker.ready.then(reg => {
                reg.sync.register('sync-offline-answers').catch(() => {});
            });
        }
        
        console.log('[LF Offline] Answer queued. Total:', this.queue.length);
        return this.queue.length;
    },

    async syncNow() {
        if (this.syncInProgress || this.queue.length === 0) return;
        if (!navigator.onLine) return;
        
        this.syncInProgress = true;
        console.log('[LF Offline] Syncing', this.queue.length, 'answers...');
        
        let succeeded = [];
        let failed = [];
        
        for (const item of this.queue) {
            try {
                // In production: POST to Firebase/API
                // For now: simulate sync success
                await this.simulateSync(item);
                succeeded.push(item);
            } catch(e) {
                failed.push(item);
            }
        }
        
        // Remove succeeded items from queue
        this.queue = failed;
        this.saveQueue();
        
        this.syncInProgress = false;
        console.log('[LF Offline] Sync complete:', succeeded.length, 'ok,', failed.length, 'failed');
        
        // Notify
        if (succeeded.length > 0) {
            this.showToast('已同步 ' + succeeded.length + ' 條離線答題記錄');
        }
        
        return { succeeded: succeeded.length, failed: failed.length };
    },

    async simulateSync(item) {
        // Simulate network request
        return new Promise((resolve) => setTimeout(resolve, 50));
    },

    // ==========================================
    // ONLINE/OFFLINE LISTENERS
    // ==========================================
    setupListeners() {
        window.addEventListener('online', () => {
            console.log('[LF Offline] Back online!');
            this.showIndicator();
            this.syncNow();
        });
        
        window.addEventListener('offline', () => {
            console.log('[LF Offline] Went offline');
            this.showIndicator();
        });
        
        // Listen for SW messages
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', (event) => {
                const { type } = event.data || {};
                if (type === 'SYNC_OFFLINE_ANSWERS') {
                    this.syncNow();
                } else if (type === 'SW_ACTIVATED') {
                    console.log('[LF Offline] SW activated, caching ready');
                }
            });
        }
    },

    // ==========================================
    // OFFLINE INDICATOR
    // ==========================================
    showIndicator() {
        // Remove existing
        const existing = document.getElementById('lf-offline-indicator');
        if (existing) existing.remove();
        
        if (navigator.onLine) {
            // Show brief "online" toast, then show queue status if any
            if (this.queue.length > 0) {
                this.showQueueBadge();
            }
            return;
        }
        
        // Create offline banner
        const banner = document.createElement('div');
        banner.id = 'lf-offline-indicator';
        banner.innerHTML = '<span>📡 你目前離線中</span><span style="font-size:10px;opacity:0.7">答題記錄會自動儲存，連線後同步</span>';
        banner.style.cssText = `
            position:fixed;top:0;left:0;right:0;z-index:10000;
            background:#F59E0B;color:#1A1A1A;
            padding:8px 16px;font-size:13px;font-weight:700;
            display:flex;justify-content:space-between;align-items:center;
            animation:lfSlideDown 0.3s ease;
        `;
        document.body.prepend(banner);
        
        // Push body down
        document.body.style.paddingTop = '40px';
    },

    showQueueBadge() {
        if (this.queue.length === 0) return;
        
        const existing = document.getElementById('lf-queue-badge');
        if (existing) existing.remove();
        
        const badge = document.createElement('div');
        badge.id = 'lf-queue-badge';
        badge.innerHTML = '🔄 ' + this.queue.length + ' 條記錄待同步';
        badge.style.cssText = `
            position:fixed;bottom:20px;right:20px;z-index:9999;
            background:#1A3C6D;color:white;
            padding:10px 16px;border-radius:20px;font-size:12px;font-weight:700;
            box-shadow:0 2px 10px rgba(0,0,0,0.2);cursor:pointer;
            animation:lfPulse 2s infinite;
        `;
        badge.onclick = () => this.syncNow().then(() => badge.remove());
        document.body.appendChild(badge);
    },

    // ==========================================
    // TOAST
    // ==========================================
    showToast(msg) {
        const toast = document.createElement('div');
        toast.textContent = msg;
        toast.style.cssText = `
            position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:9999;
            background:#333;color:white;padding:10px 24px;border-radius:20px;
            font-size:13px;opacity:0;transition:opacity 0.3s;
        `;
        document.body.appendChild(toast);
        requestAnimationFrame(() => { toast.style.opacity = '1'; });
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // ==========================================
    // PRE-CACHE LECTURES (called by teacher before class)
    // ==========================================
    async preCacheLectures(lectureUrls) {
        if (!('serviceWorker' in navigator)) return;
        const reg = await navigator.serviceWorker.ready;
        reg.active.postMessage({
            type: 'CACHE_LECTURES_BULK',
            data: { urls: lectureUrls }
        });
        console.log('[LF Offline] Requested pre-cache of', lectureUrls.length, 'lectures');
    },

    async preCacheLecture(url) {
        if (!('serviceWorker' in navigator)) return;
        const reg = await navigator.serviceWorker.ready;
        reg.active.postMessage({
            type: 'CACHE_LECTURE',
            data: { url }
        });
    },

    // ==========================================
    // CACHE STATUS
    // ==========================================
    async getCacheStatus() {
        if (!('serviceWorker' in navigator)) return null;
        const reg = await navigator.serviceWorker.ready;
        return new Promise((resolve) => {
            const channel = new MessageChannel();
            channel.port1.onmessage = (event) => resolve(event.data);
            reg.active.postMessage({ type: 'GET_CACHE_STATUS' }, [channel.port2]);
        });
    }
};

// ==========================================
// AUTO-INIT
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    LFOffline.init();
});

// ==========================================
// CSS: Pulse animation for queue badge
// ==========================================
const style = document.createElement('style');
style.textContent = `
@keyframes lfSlideDown {
    from { opacity: 0; transform: translateY(-40px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes lfPulse {
    0%, 100% { box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
    50% { box-shadow: 0 2px 20px rgba(26,60,109,0.4); }
}
`;
document.head.appendChild(style);

console.log('LF Offline Engine v1.0 loaded');
