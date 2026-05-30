/**
 * LF Performance Optimizer v1.0
 * Resource hints · Critical CSS · Lazy loading · Preconnect
 * Auto-optimizes page load performance
 */
(function() {
    "use strict";

    // ═══ PRECONNECT TO CRITICAL ORIGINS ═══
    var origins = [
        "https://fonts.googleapis.com",
        "https://fonts.gstatic.com",
        "https://cdn.jsdelivr.net",
        "https://www.gstatic.com",  // Firebase
        "https://lfady-b1761.firebaseapp.com",
    ];

    origins.forEach(function(origin) {
        if (document.querySelector('link[rel="preconnect"][href="' + origin + '"]')) return;
        var link = document.createElement("link");
        link.rel = "preconnect";
        link.href = origin;
        link.crossOrigin = "anonymous";
        document.head.appendChild(link);
    });

    // ═══ LAZY LOAD NON-CRITICAL SCRIPTS ═══
    // Scripts that can wait until after page load
    var lazyScripts = [
        "/docs/data/lf-offline.js",
        "/docs/data/lf-churn-alert.js",
        "/docs/data/lf-bilingual.js",
    ];

    if ("requestIdleCallback" in window) {
        requestIdleCallback(function() {
            lazyScripts.forEach(function(src) {
                if (document.querySelector('script[src="' + src + '"]')) return; // already loaded
                var s = document.createElement("script");
                s.src = src;
                s.async = true;
                document.body.appendChild(s);
            });
        });
    } else {
        setTimeout(function() {
            lazyScripts.forEach(function(src) {
                if (document.querySelector('script[src="' + src + '"]')) return;
                var s = document.createElement("script");
                s.src = src;
                s.async = true;
                document.body.appendChild(s);
            });
        }, 2000);
    }

    // ═══ IMAGE LAZY LOADING ═══
    document.addEventListener("DOMContentLoaded", function() {
        document.querySelectorAll("img:not([loading])").forEach(function(img) {
            if (!img.hasAttribute("loading") && !img.closest(".hero, .header, .topbar, #lf-navbar")) {
                img.loading = "lazy";
                img.decoding = "async";
            }
        });
    });

    // ═══ FONT DISPLAY OPTIMIZATION ═══
    if (!document.getElementById("lf-font-opt")) {
        var style = document.createElement("style");
        style.id = "lf-font-opt";
        style.textContent = "@font-face{font-display:swap}";
        document.head.appendChild(style);
    }

    console.log("[LF Perf] Optimized: " + origins.length + " preconnects, " + lazyScripts.length + " lazy scripts");
})();
