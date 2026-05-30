/**
 * LF Academy UX Enhance v2.0
 * Error boundary · Loading · Toast · Skeleton · Pull-to-refresh · Offline indicator · Form validation
 * Include: <script src="/docs/data/lf-ux-enhance.js"></script>
 */
(function() {
    "use strict";

    // ═══ GLOBAL ERROR BOUNDARY ═══
    var originalError = window.onerror;
    window.onerror = function(msg, url, line, col, err) {
        console.error("[LF UX] Error:", msg, "at", url, line);
        LF_Toast.show("出現了一些問題，請重新整理。", "error");
        if (typeof LFEventBus !== "undefined" && LFEventBus.track) {
            LFEventBus.track("js_error", { message: String(msg).substring(0, 200), url: String(url), line: line });
        }
        if (originalError) return originalError.apply(this, arguments);
        return false;
    };

    // ═══ TOAST NOTIFICATION ═══
    window.LF_Toast = {
        _container: null,
        _ensureContainer: function() {
            if (this._container) return;
            this._container = document.createElement("div");
            this._container.id = "lf-toast-container";
            this._container.style.cssText = "position:fixed;top:60px;right:16px;z-index:99999;display:flex;flex-direction:column;gap:8px;max-width:360px;pointer-events:none";
            document.body.appendChild(this._container);
        },
        show: function(message, type, duration) {
            this._ensureContainer();
            type = type || "info"; duration = duration || 3000;
            var colors = {
                success: {bg:"#F0FDF4",border:"#BBF7D0",text:"#065F46",icon:"✅"},
                error:   {bg:"#FEF2F2",border:"#FECACA",text:"#991B1B",icon:"❌"},
                warning: {bg:"#FFFBEB",border:"#FDE68A",text:"#92400E",icon:"⚠️"},
                info:    {bg:"#F0F7FF",border:"#BFDBFE",text:"#1E40AF",icon:"ℹ️"}
            };
            var c = colors[type] || colors.info;
            var toast = document.createElement("div");
            toast.style.cssText = "background:"+c.bg+";border:1px solid "+c.border+";color:"+c.text+";padding:10px 14px;border-radius:10px;font-size:13px;font-weight:500;box-shadow:0 4px 16px rgba(0,0,0,0.1);animation:lfToastIn 0.3s ease;display:flex;align-items:center;gap:8px;pointer-events:auto;cursor:pointer;max-width:340px";
            toast.innerHTML = '<span style="font-size:16px;flex-shrink:0">'+c.icon+'</span><span style="flex:1;line-height:1.4">'+message+'</span>';
            toast.onclick = function(){ toast.remove(); };
            this._container.appendChild(toast);
            setTimeout(function(){
                toast.style.opacity = "0"; toast.style.transform = "translateX(20px)";
                toast.style.transition = "all 0.3s ease";
                setTimeout(function(){ if(toast.parentNode) toast.remove(); }, 300);
            }, duration);
            if (!document.getElementById("lf-toast-css")) {
                var s = document.createElement("style"); s.id = "lf-toast-css";
                s.textContent = "@keyframes lfToastIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}";
                document.head.appendChild(s);
            }
        }
    };

    // ═══ LOADING OVERLAY ═══
    window.LF_Loading = {
        _overlay: null,
        show: function(message) {
            if (this._overlay) return;
            message = message || "載入中...";
            this._overlay = document.createElement("div");
            this._overlay.id = "lf-loading-overlay";
            this._overlay.style.cssText = "position:fixed;inset:0;background:rgba(255,255,255,0.85);z-index:99998;display:flex;flex-direction:column;align-items:center;justify-content:center;backdrop-filter:blur(2px)";
            this._overlay.innerHTML = '<div style="width:40px;height:40px;border:3px solid #E5E7EB;border-top-color:#1A3C6D;border-radius:50%;animation:lfSpin 0.8s linear infinite;margin-bottom:12px"></div><div style="font-size:13px;color:#6B7280;font-weight:500">'+message+'</div>';
            document.body.appendChild(this._overlay);
            if (!document.getElementById("lf-spin-css")) {
                var s = document.createElement("style"); s.id = "lf-spin-css";
                s.textContent = "@keyframes lfSpin{to{transform:rotate(360deg)}}";
                document.head.appendChild(s);
            }
        },
        hide: function() {
            if (!this._overlay) return;
            this._overlay.style.opacity = "0"; this._overlay.style.transition = "opacity 0.2s";
            var self = this;
            setTimeout(function(){ if(self._overlay&&self._overlay.parentNode) self._overlay.remove(); self._overlay = null; }, 200);
        }
    };

    // ═══ SKELETON LOADING ═══
    window.LF_Skeleton = {
        /**
         * Inject skeleton HTML into container, auto-removes when content loads
         * @param {string|Element} container - CSS selector or element
         * @param {string} type - "card" | "list" | "text" | "avatar"
         * @param {number} count - number of skeleton items
         */
        inject: function(container, type, count) {
            if (typeof container === "string") container = document.querySelector(container);
            if (!container) return;
            count = count || 1; type = type || "card";
            var html = "";
            for (var i = 0; i < count; i++) {
                if (type === "card") html += '<div class="lf-skeleton lf-sk-card" style="background:#f1f5f9;border-radius:12px;padding:20px;margin:8px 0;height:120px;animation:lfSkPulse 1.5s infinite"></div>';
                else if (type === "list") html += '<div class="lf-skeleton lf-sk-list" style="display:flex;gap:12px;padding:12px;margin:4px 0;align-items:center"><div style="width:40px;height:40px;background:#e2e8f0;border-radius:50%;animation:lfSkPulse 1.5s infinite;flex-shrink:0"></div><div style="flex:1"><div style="height:14px;background:#e2e8f0;border-radius:4px;margin:4px 0;width:70%;animation:lfSkPulse 1.5s infinite"></div><div style="height:10px;background:#f1f5f9;border-radius:4px;width:50%;animation:lfSkPulse 1.5s infinite"></div></div></div>';
                else if (type === "text") html += '<div class="lf-skeleton lf-sk-text" style="height:14px;background:#e2e8f0;border-radius:4px;margin:8px 0;width:'+(60+Math.random()*40)+'%;animation:lfSkPulse 1.5s infinite"></div>';
                else if (type === "avatar") html += '<div class="lf-skeleton lf-sk-avatar" style="width:48px;height:48px;background:#e2e8f0;border-radius:50%;animation:lfSkPulse 1.5s infinite;display:inline-block;margin:4px"></div>';
            }
            container.innerHTML = html;
            if (!document.getElementById("lf-sk-css")) {
                var s = document.createElement("style"); s.id = "lf-sk-css";
                s.textContent = "@keyframes lfSkPulse{0%,100%{opacity:1}50%{opacity:0.5}}";
                document.head.appendChild(s);
            }
            return container;
        },
        clear: function(container) {
            if (typeof container === "string") container = document.querySelector(container);
            if (!container) return;
            var skels = container.querySelectorAll(".lf-skeleton");
            skels.forEach(function(s){ s.remove(); });
        }
    };

    // ═══ PULL-TO-REFRESH (Mobile) ═══
    window.LF_PullRefresh = {
        init: function(callback, options) {
            if (window.innerWidth > 768) return; // desktop skip
            options = options || {};
            var ptr = document.createElement("div");
            ptr.id = "lf-ptr";
            ptr.style.cssText = "position:fixed;top:52px;left:0;right:0;height:0;overflow:hidden;display:flex;align-items:center;justify-content:center;background:#F0F7FF;z-index:9997;transition:height 0.3s;font-size:13px;color:#1A3C6D;font-weight:500";
            ptr.textContent = "⬇️ 下拉重新整理";
            document.body.insertBefore(ptr, document.body.firstChild);
            var startY = 0, pulling = false, refreshing = false;
            document.addEventListener("touchstart", function(e){ if(window.scrollY===0){ startY=e.touches[0].clientY; pulling=true; } }, {passive:true});
            document.addEventListener("touchmove", function(e){
                if(!pulling||refreshing) return;
                var diff = e.touches[0].clientY - startY;
                if(diff > 0){ ptr.style.height = Math.min(diff, 60)+"px"; ptr.textContent = diff>50?"放開以重新整理":"⬇️ 下拉重新整理"; }
            }, {passive:true});
            document.addEventListener("touchend", function(){
                if(!pulling||refreshing) return;
                if(parseInt(ptr.style.height) > 50){
                    refreshing = true; ptr.style.height = "44px"; ptr.textContent = "🔄 重新整理中...";
                    if(callback) callback().finally(function(){ resetPtr(); });
                    else { setTimeout(function(){ resetPtr(); }, 1500); }
                } else { resetPtr(); }
                pulling = false;
            });
            function resetPtr(){ ptr.style.height = "0"; ptr.textContent = "⬇️ 下拉重新整理"; refreshing = false; }
        }
    };

    // ═══ OFFLINE INDICATOR ═══
    window.LF_OfflineIndicator = {
        init: function() {
            var indicator = document.createElement("div");
            indicator.id = "lf-offline-indicator";
            indicator.style.cssText = "position:fixed;top:52px;left:0;right:0;background:#FEF2F2;color:#991B1B;text-align:center;padding:4px;font-size:11px;font-weight:700;z-index:9996;display:none;transition:all 0.3s";
            indicator.textContent = "📡 目前處於離線模式 · 資料將在連線後自動同步";
            document.body.insertBefore(indicator, document.body.firstChild);
            window.addEventListener("online", function(){ indicator.style.display = "none"; if(document.body.style.paddingTop==="72px") document.body.style.paddingTop="52px"; LF_Toast.show("已恢復連線 ✅", "success", 2000); });
            window.addEventListener("offline", function(){ indicator.style.display = "block"; document.body.style.paddingTop = "72px"; LF_Toast.show("目前離線中，部分功能可能受限", "warning", 4000); });
            if (!navigator.onLine) { indicator.style.display = "block"; document.body.style.paddingTop = "72px"; }
        }
    };

    // ═══ FORM VALIDATION HELPERS ═══
    window.LF_Validate = {
        email: function(val) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val); },
        phone: function(val) { return /^[0-9]{8}$/.test(val.replace(/\s|-/g,"")); },
        required: function(val) { return val && val.trim().length > 0; },
        minLength: function(val, len) { return val && val.length >= len; },
        /**
         * Validate form fields and show inline errors
         * @param {HTMLFormElement} form
         * @param {Object} rules - {fieldName: [{test:"email",msg:"..."},{test:fn,msg:"..."}]}
         * @returns {boolean} valid
         */
        form: function(form, rules) {
            var valid = true;
            Object.keys(rules).forEach(function(name) {
                var field = form.querySelector('[name="'+name+'"]');
                if (!field) return;
                var val = field.value;
                var fieldRules = rules[name];
                for (var i = 0; i < fieldRules.length; i++) {
                    var r = fieldRules[i];
                    var pass = false;
                    if (typeof r.test === "function") pass = r.test(val);
                    else if (r.test === "email") pass = LF_Validate.email(val);
                    else if (r.test === "phone") pass = LF_Validate.phone(val);
                    else if (r.test === "required") pass = LF_Validate.required(val);
                    if (!pass) {
                        LF_Validate._showFieldError(field, r.msg || "此欄位無效");
                        valid = false;
                        break;
                    }
                }
                if (valid || field.dataset.lfError) { LF_Validate._clearFieldError(field); }
            });
            return valid;
        },
        _showFieldError: function(field, msg) {
            field.style.borderColor = "#DC2626";
            field.dataset.lfError = "1";
            var existing = field.parentNode.querySelector(".lf-field-error");
            if (existing) existing.textContent = msg;
            else {
                var err = document.createElement("div");
                err.className = "lf-field-error";
                err.style.cssText = "color:#DC2626;font-size:11px;margin-top:4px;font-weight:500";
                err.textContent = msg;
                field.parentNode.insertBefore(err, field.nextSibling);
            }
        },
        _clearFieldError: function(field) {
            field.style.borderColor = "";
            delete field.dataset.lfError;
            var err = field.parentNode.querySelector(".lf-field-error");
            if (err) err.remove();
        }
    };

    // ═══ PAGE TRANSITION ═══
    document.addEventListener("DOMContentLoaded", function() {
        document.body.style.opacity = "0";
        document.body.style.transition = "opacity 0.3s ease";
        requestAnimationFrame(function(){ document.body.style.opacity = "1"; });
    });

    // ═══ AUTO-RETRY FETCH ═══
    window.LF_Retry = {
        fetch: function(url, options, maxRetries) {
            maxRetries = maxRetries || 2;
            var self = this;
            return fetch(url, options).catch(function(err) {
                if (maxRetries <= 0) throw err;
                console.warn("[LF Retry] Fetch failed, retrying... ("+maxRetries+" left)");
                return new Promise(function(resolve) {
                    setTimeout(function(){ resolve(self.fetch(url, options, maxRetries-1)); }, 1000);
                });
            });
        }
    };

    // ═══ INIT ═══
    LF_OfflineIndicator.init();
    console.log("[LF UX v2.0] Error · Toast · Loading · Skeleton · PTR · Offline · Validation ready");
})();
