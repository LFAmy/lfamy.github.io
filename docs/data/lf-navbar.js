/**
 * LF Academy Unified Navbar v2.0
 * 跨頁面統一頂部導航 · 角色自適應 · 身份感知
 * Include: <script src="/docs/data/lf-navbar.js"></script>
 * Auto-injects #lf-navbar at top of body
 */
(function() {
    "use strict";

    // ═══ CONFIG ═══
    const BRAND = "霖楓學苑";
    const BRAND_SHORT = "LF Academy";
    const LOGO = "/logo.png";
    const HOME = "/";

    // ═══ ROLE DETECTION ═══
    function detectRole() {
        // Check localStorage first
        try {
            const session = JSON.parse(localStorage.getItem("lf_session") || "{}");
            if (session.role) return session.role;
        } catch(e) {}
        // Check URL path
        const path = window.location.pathname;
        if (/student|practice|quiz|trap|boss|achieve|kids|app/i.test(path)) return "student";
        if (/parent|report|portal|center/i.test(path)) return "parent";
        if (/teacher|admin|class|member|campus|ops/i.test(path)) return "teacher";
        // Check LFCore
        if (typeof LFCore !== "undefined" && LFCore.state && LFCore.state.userRole) {
            return LFCore.state.userRole;
        }
        return null;
    }

    // ═══ NAV LINKS BY ROLE ═══
    const NAV_LINKS = {
        student: [
            { href: "/student.html", label: "主頁", icon: "🏠" },
            { href: "/docs/student-platform.html", label: "學習", icon: "📚" },
            { href: "/docs/student-practice.html", label: "練習", icon: "🎯" },
            { href: "/ai-tutor.html", label: "AI導師", icon: "🤖" },
            { href: "/docs/achievement-wall.html", label: "成就", icon: "🏆" },
        ],
        parent: [
            { href: "/parent.html", label: "主頁", icon: "🏠" },
            { href: "/parent-dashboard.html", label: "儀表板", icon: "📊" },
            { href: "/docs/parent-portal.html", label: "進度", icon: "📈" },
            { href: "/docs/parent-report-gen.html", label: "報告", icon: "📄" },
            { href: "/enroll.html", label: "報名", icon: "📝" },
        ],
        teacher: [
            { href: "/launchpad.html", label: "主頁", icon: "🏠" },
            { href: "/docs/teacher-dashboard.html", label: "儀表板", icon: "📊" },
            { href: "/docs/admin-members.html", label: "學生", icon: "👥" },
            { href: "/docs/classroom-mode.html", label: "課堂", icon: "🏫" },
            { href: "/docs/ops-dashboard.html", label: "營運", icon: "⚙️" },
        ],
        guest: [
            { href: "/", label: "首頁", icon: "🏠" },
            { href: "/docs/index.html", label: "探索", icon: "🔍" },
            { href: "/auth.html", label: "登入", icon: "🔑" },
        ]
    };

    // ═══ BUILD NAVBAR ═══
    function buildNavbar() {
        const role = detectRole();
        const links = NAV_LINKS[role] || NAV_LINKS.guest;
        const currentPath = window.location.pathname;

        // Check if navbar already exists
        if (document.getElementById("lf-navbar")) return;

        const nav = document.createElement("nav");
        nav.id = "lf-navbar";

        // Brand
        let html = '<a href="' + HOME + '" class="lf-nav-brand">';
        html += '<img src="' + LOGO + '" alt="' + BRAND + '" onerror="this.style.display=\'none\'">';
        html += '<span class="lf-nav-brand-text">' + BRAND + '</span>';
        html += '</a>';

        // Links
        html += '<div class="lf-nav-links">';
        links.forEach(function(link) {
            const isActive = currentPath === link.href || currentPath.endsWith(link.href);
            const activeClass = isActive ? ' active' : '';
            html += '<a href="' + link.href + '" class="lf-nav-link' + activeClass + '">';
            html += '<span class="lf-nav-icon">' + link.icon + '</span>';
            html += '<span class="lf-nav-label">' + link.label + '</span>';
            html += '</a>';
        });
        html += '</div>';

        // User area
        html += '<div class="lf-nav-user">';
        const user = getUserInfo();
        if (user) {
            html += '<span class="lf-nav-avatar">' + user.avatar + '</span>';
            html += '<span class="lf-nav-name">' + user.name + '</span>';
        }
        html += '<button class="lf-nav-menu-btn" onclick="document.getElementById(\'lf-navbar\').classList.toggle(\'menu-open\')" aria-label="Menu">☰</button>';
        html += '</div>';

        nav.innerHTML = html;
        document.body.insertBefore(nav, document.body.firstChild);
        document.body.style.paddingTop = "52px";

        console.log("[LF Navbar] Injected · Role: " + (role || "guest") + " · Path: " + currentPath);
    }

    function getUserInfo() {
        try {
            const session = JSON.parse(localStorage.getItem("lf_session") || "{}");
            if (session.displayName) {
                return { name: session.displayName, avatar: session.displayName.charAt(0) };
            }
        } catch(e) {}
        try {
            if (typeof LFCore !== "undefined" && LFCore.state && LFCore.state.currentUser) {
                const u = LFCore.state.currentUser;
                return { name: u.displayName || u.email || "User", avatar: "👤" };
            }
        } catch(e) {}
        return null;
    }

    // ═══ INJECT CSS ═══
    function injectCSS() {
        if (document.getElementById("lf-navbar-css")) return;
        const css = document.createElement("style");
        css.id = "lf-navbar-css";
        css.textContent = [
            "#lf-navbar{position:fixed;top:0;left:0;right:0;z-index:9999;background:rgba(255,255,255,0.97);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);display:flex;align-items:center;justify-content:space-between;padding:8px 20px;box-shadow:0 1px 4px rgba(0,0,0,0.06);font-family:'Noto Sans HK','PingFang SC','Microsoft YaHei',sans-serif;height:52px;box-sizing:border-box}",
            "#lf-navbar .lf-nav-brand{display:flex;align-items:center;gap:8px;text-decoration:none;color:#1A3C6D;font-weight:900;font-size:15px;flex-shrink:0}",
            "#lf-navbar .lf-nav-brand img{height:32px;width:auto}",
            "#lf-navbar .lf-nav-brand-text{white-space:nowrap}",
            "#lf-navbar .lf-nav-links{display:flex;align-items:center;gap:4px;flex:1;justify-content:center;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}",
            "#lf-navbar .lf-nav-links::-webkit-scrollbar{display:none}",
            "#lf-navbar .lf-nav-link{display:flex;align-items:center;gap:4px;padding:6px 12px;border-radius:10px;text-decoration:none;color:#64748B;font-size:13px;font-weight:500;transition:all 0.2s;white-space:nowrap;flex-shrink:0}",
            "#lf-navbar .lf-nav-link:hover{background:#F1F5F9;color:#1A3C6D}",
            "#lf-navbar .lf-nav-link.active{background:#DBEAFE;color:#1A3C6D;font-weight:700}",
            "#lf-navbar .lf-nav-icon{font-size:15px}",
            "#lf-navbar .lf-nav-user{display:flex;align-items:center;gap:8px;flex-shrink:0}",
            "#lf-navbar .lf-nav-avatar{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#1A3C6D,#1E4D8C);color:white;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}",
            "#lf-navbar .lf-nav-name{font-size:12px;color:#1E293B;font-weight:500;max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}",
            "#lf-navbar .lf-nav-menu-btn{display:none;background:none;border:none;font-size:22px;cursor:pointer;color:#1A3C6D;padding:4px 8px;border-radius:8px}",
            "#lf-navbar .lf-nav-menu-btn:hover{background:#F1F5F9}",
            "@media(max-width:768px){#lf-navbar{padding:6px 12px;height:48px}body{padding-top:48px!important}#lf-navbar .lf-nav-brand-text{font-size:13px}#lf-navbar .lf-nav-link{padding:5px 8px;font-size:11px}#lf-navbar .lf-nav-icon{font-size:14px}#lf-navbar .lf-nav-label{display:none}#lf-navbar .lf-nav-name{display:none}#lf-navbar .lf-nav-menu-btn{display:block}#lf-navbar.menu-open .lf-nav-links{display:flex;position:fixed;top:48px;left:0;right:0;background:white;flex-direction:column;padding:12px;box-shadow:0 4px 16px rgba(0,0,0,0.1);gap:2px}#lf-navbar .lf-nav-links{display:flex}}",
            "@media(min-width:769px){#lf-navbar .lf-nav-links{display:flex!important}}",
            "@media(max-width:400px){#lf-navbar{gap:4px}#lf-navbar .lf-nav-link{padding:4px 6px;font-size:10px}}"
        ].join("\n");
        document.head.appendChild(css);
    }

    // ═══ INIT ═══
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function() { injectCSS(); buildNavbar(); });
    } else {
        injectCSS();
        buildNavbar();
    }
})();
