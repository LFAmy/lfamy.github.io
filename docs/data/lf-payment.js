/**
 * LF Payment Client v1.0
 * 前端支付 API 客戶端 — Stripe Checkout + PayMe + FPS
 * Include: <script src="/docs/data/lf-payment.js"></script>
 */
var LFPayment = {
    apiBase: "/api/payment",

    /**
     * 獲取所有方案
     * @returns {Promise<Array>} plans array
     */
    async getPlans() {
        try {
            var res = await fetch(this.apiBase + "/plans");
            if (!res.ok) throw new Error("HTTP " + res.status);
            return await res.json();
        } catch(e) {
            console.warn("[LFPayment] Plans API failed, using defaults:", e.message);
            return this._defaultPlans();
        }
    },

    /**
     * 建立 Stripe Checkout
     * @param {string} planKey - e.g. "P5_monthly"
     * @param {string} email
     * @param {string} name
     * @returns {Promise<Object>} {url, session_id}
     */
    async createCheckout(planKey, email, name) {
        try {
            var res = await fetch(this.apiBase + "/checkout", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    plan_key: planKey,
                    email: email,
                    name: name,
                    success_url: window.location.origin + "/docs/payment-success.html",
                    cancel_url: window.location.origin + "/docs/pay.html"
                })
            });
            if (!res.ok) throw new Error("HTTP " + res.status);
            return await res.json();
        } catch(e) {
            console.warn("[LFPayment] Checkout API failed:", e.message);
            return {error: e.message, _offline: true};
        }
    },

    /**
     * 檢查會員狀態
     * @param {string} email
     * @returns {Promise<Object>} membership status
     */
    async checkMembership(email) {
        try {
            var res = await fetch(this.apiBase + "/membership/status", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({email: email})
            });
            if (!res.ok) throw new Error("HTTP " + res.status);
            return await res.json();
        } catch(e) {
            console.warn("[LFPayment] Membership check failed:", e.message);
            return this._localMembership(email);
        }
    },

    /**
     * 記錄離線付款 (PayMe/FPS/銀行轉帳)
     * 儲存到 localStorage，等待 sync
     */
    recordOfflinePayment(data) {
        var payments = [];
        try {
            payments = JSON.parse(localStorage.getItem("lf_offline_payments") || "[]");
        } catch(e) {}
        payments.push({
            id: "off_" + Date.now(),
            method: data.method,
            plan: data.plan,
            amount: data.amount,
            email: data.email,
            name: data.name,
            phone: data.phone,
            reference: data.reference,
            status: "pending",
            created_at: new Date().toISOString()
        });
        localStorage.setItem("lf_offline_payments", JSON.stringify(payments));
        console.log("[LFPayment] Offline payment recorded:", payments[payments.length-1].id);
        return payments[payments.length-1];
    },

    /**
     * Get pending offline payments for sync
     */
    getPendingPayments() {
        try {
            return JSON.parse(localStorage.getItem("lf_offline_payments") || "[]");
        } catch(e) { return []; }
    },

    /**
     * Mark offline payment as synced
     */
    markSynced(paymentId) {
        var payments = this.getPendingPayments();
        payments = payments.map(function(p) {
            if (p.id === paymentId) p.status = "synced";
            return p;
        });
        localStorage.setItem("lf_offline_payments", JSON.stringify(payments));
    },

    // Default plans fallback
    _defaultPlans() {
        return [
            {key:"trial", name:"免費試堂", amount:0, currency:"hkd", grade:"any", sessions:1, interval:"once"},
            {key:"P3_monthly", name:"小三 P3 · 月付", amount:250, currency:"hkd", grade:"P3", sessions:4, interval:"month"},
            {key:"P4_monthly", name:"小四 P4 · 月付", amount:280, currency:"hkd", grade:"P4", sessions:4, interval:"month"},
            {key:"P5_monthly", name:"小五 P5 · 月付", amount:330, currency:"hkd", grade:"P5", sessions:4, interval:"month"},
            {key:"P6_monthly", name:"小六 P6 · 月付", amount:330, currency:"hkd", grade:"P6", sessions:4, interval:"month"},
            {key:"P3_annual", name:"小三 P3 · 年繳(8折)", amount:2400, currency:"hkd", grade:"P3", sessions:4, interval:"year"},
            {key:"P4_annual", name:"小四 P4 · 年繳(8折)", amount:2688, currency:"hkd", grade:"P4", sessions:4, interval:"year"},
            {key:"P5_annual", name:"小五 P5 · 年繳(8折)", amount:3168, currency:"hkd", grade:"P5", sessions:4, interval:"year"},
            {key:"P6_annual", name:"小六 P6 · 年繳(8折)", amount:3168, currency:"hkd", grade:"P6", sessions:4, interval:"year"}
        ];
    },

    // Local membership check
    _localMembership(email) {
        try {
            var members = JSON.parse(localStorage.getItem("lf_memberships") || "{}");
            var m = members[email];
            if (m && m.expires_at && new Date(m.expires_at) > new Date()) {
                return {active: true, plan: m.plan, expires_at: m.expires_at};
            }
        } catch(e) {}
        return {active: false};
    }
};

console.log("[LFPayment] Client initialized · API: " + LFPayment.apiBase);
