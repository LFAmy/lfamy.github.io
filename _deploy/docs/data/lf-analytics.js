// ═══════════════════════════════════════════
// 霖楓學苑 LF Academy · GA4 Analytics
// 追蹤：頁面瀏覽、診斷完成、註冊、付費意向
// ═══════════════════════════════════════════
(function() {
  const GA_MEASUREMENT_ID = 'G-NZME21MJ3C'; // 與 Firebase 共用
  
  // Load gtag
  const script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_MEASUREMENT_ID;
  document.head.appendChild(script);
  
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', GA_MEASUREMENT_ID, {
    page_title: document.title,
    page_location: window.location.href,
    send_page_view: true
  });
  
  // ═══ Custom Events ═══
  window.LF_Analytics = {
    // 診斷完成
    diagnosticComplete: function(grade, trapResults) {
      gtag('event', 'diagnostic_complete', {
        grade: grade,
        trap_count: trapResults ? Object.keys(trapResults).length : 0
      });
    },
    // 註冊
    signup: function(method, role) {
      gtag('event', 'signup', { method: method, role: role });
    },
    // 開始免費試用
    freeTrialStart: function() {
      gtag('event', 'free_trial_start');
    },
    // 查看定價
    viewPricing: function() {
      gtag('event', 'view_pricing');
    },
    // 點擊付款
    checkoutClick: function(plan) {
      gtag('event', 'checkout_click', { plan: plan });
    },
    // AI 練習完成
    practiceComplete: function(topic, correct) {
      gtag('event', 'practice_complete', { topic: topic, correct: correct });
    },
    // WhatsApp 查詢
    whatsappClick: function(page) {
      gtag('event', 'whatsapp_click', { page: page });
    }
  };
  
  console.log('[LF] GA4 Analytics loaded');
})();
