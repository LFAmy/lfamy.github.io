// ═══════════════════════════════════════════
// 霖楓學苑 LF Academy · Service Worker v2.0
// 離線快取 + 背景同步 + App-like 體驗
// ═══════════════════════════════════════════
const CACHE_NAME = 'lf-academy-v2';
const CRITICAL_ASSETS = [
  '/',
  '/index.html',
  '/ai-tutor.html',
  '/auth.html',
  '/logo.png',
  '/manifest.json',
  '/docs/data/lf-core.js',
  '/docs/data/lf-firebase-config.js',
  '/docs/data/lf-api-client.js',
  '/docs/enroll.html',
  '/docs/ai-diagnostic.html',
  '/docs/trap-system.html',
  '/docs/pricing.html',
  '/docs/blog/',
  '/docs/faq.html'
];

// ═══ Install: Cache critical assets ═══
self.addEventListener('install', event => {
  console.log('[SW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] Caching critical assets');
      return cache.addAll(CRITICAL_ASSETS).catch(err => {
        console.warn('[SW] Some assets failed to cache:', err);
      });
    })
  );
  self.skipWaiting();
});

// ═══ Activate: Clean old caches ═══
self.addEventListener('activate', event => {
  console.log('[SW] Activating...');
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => {
          console.log('[SW] Deleting old cache:', key);
          return caches.delete(key);
        })
      );
    })
  );
  self.clients.claim();
});

// ═══ Fetch: Cache-first for assets, Network-first for HTML ═══
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Don't cache API calls or Firebase
  if (url.pathname.includes('/api/') || url.hostname.includes('firebase') || url.hostname.includes('googleapis')) {
    return;
  }
  
  // Cache-first for static assets (JS, CSS, images, fonts)
  if (event.request.destination === 'script' || 
      event.request.destination === 'style' || 
      event.request.destination === 'image' ||
      event.request.destination === 'font') {
    event.respondWith(
      caches.match(event.request).then(cached => {
        const fetchPromise = fetch(event.request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        });
        return cached || fetchPromise;
      })
    );
    return;
  }
  
  // Network-first for HTML (always try to get fresh content)
  event.respondWith(
    fetch(event.request).then(response => {
      if (response.ok) {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
      }
      return response;
    }).catch(() => {
      return caches.match(event.request).then(cached => {
        return cached || caches.match('/index.html');
      });
    })
  );
});

// ═══ Push Notifications (future) ═══
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.body || '霖楓學苑有新消息',
    icon: '/logo.png',
    badge: '/logo.png',
    data: { url: data.url || '/' }
  };
  event.waitUntil(
    self.registration.showNotification(data.title || '霖楓學苑', options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/')
  );
});

console.log('[SW] 🍁 霖楓學苑 Service Worker v2.0 ready');

// ═══ v2.1 — Enhanced caching: stale-while-revalidate for API · offline page ═══

// Cache API responses with stale-while-revalidate
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // API requests: network first, fallback to cache
  if (url.pathname.startsWith('/api/') || url.hostname.includes('render.com')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Static assets: cache first (already handled by install)
  // HTML pages: network first for freshness
  if (url.pathname.endsWith('.html') || url.pathname === '/') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        })
        .catch(() => caches.match(event.request).then(cached => {
          return cached || caches.match('/offline.html');
        }))
    );
    return;
  }

  // Default: network first (updates cache in background)
  event.respondWith(
    caches.match(event.request).then(cached => {
      const fetchPromise = fetch(event.request).then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => cached);
      return cached || fetchPromise;
    })
  );
});

// Clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// Background sync for offline submissions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-leads') {
    event.waitUntil(syncLeads());
  }
});

async function syncLeads() {
  try {
    const db = await openDB();
    const leads = await db.getAll('leads');
    for (const lead of leads) {
      try {
        await fetch(lead.url, { method: 'POST', body: lead.data });
        await db.delete('leads', lead.id);
      } catch(e) {}
    }
  } catch(e) {}
}

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('lf-offline', 1);
    request.onupgradeneeded = e => e.target.result.createObjectStore('leads', { keyPath: 'id' });
    request.onsuccess = e => resolve(e.target.result);
    request.onerror = e => reject(e.target.error);
  });
}