/**
 * LF Academy Core v2.0
 * Unified backend: Firebase (when available) + localStorage fallback
 * Auth · Data · Sync · Real-time
 */
const LFCore = {
    // ==========================================
    // CONFIG
    // ==========================================
    config: {
        appName: '霖楓學苑',
        useFirebase: false, // Set true when Firebase keys configured
        firebase: {
            apiKey: "YOUR_API_KEY",
            authDomain: "lam-fung-academy.firebaseapp.com",
            projectId: "lam-fung-academy",
            storageBucket: "lam-fung-academy.appspot.com",
            messagingSenderId: "YOUR_SENDER_ID",
            appId: "YOUR_APP_ID"
        }
    },

    // ==========================================
    // STATE
    // ==========================================
    state: {
        isLoggedIn: false,
        currentUser: null,
        userRole: null, // 'student' | 'teacher' | 'parent' | 'admin'
        userData: null,
        isDemo: true,
    },

    // ==========================================
    // INIT
    // ==========================================
    init() {
        // Try Firebase
        if (this.config.useFirebase && typeof firebase !== 'undefined') {
            try {
                firebase.initializeApp(this.config.firebase);
                this.db = firebase.firestore();
                this.auth = firebase.auth();
                console.log('[LF Core] Firebase initialized');
            } catch(e) {
                console.warn('[LF Core] Firebase unavailable, using local mode');
            }
        }

        // Load saved session
        this.loadSession();

        // Set up auth listener
        if (this.auth) {
            this.auth.onAuthStateChanged(user => {
                if (user) this.onLogin(user);
                else this.onLogout();
            });
        }

        this._initCrossTab();
        console.log('[LF Core] Initialized. Logged in:', this.state.isLoggedIn, 'Role:', this.state.userRole);
        window.dispatchEvent(new CustomEvent('lf:ready', { detail: this.state }));
    },

    // ==========================================
    // AUTH - LOCAL MODE (no Firebase needed)
    // ==========================================
    loadSession() {
        try {
            const session = JSON.parse(localStorage.getItem('lf_session') || 'null');
            if (session && session.email) {
                this.state.isLoggedIn = true;
                this.state.currentUser = { email: session.email, uid: session.uid };
                this.state.userRole = session.role;
                this.state.userData = session;
                this.state.isDemo = false;
            }
        } catch(e) {}
    },

    saveSession() {
        localStorage.setItem('lf_session', JSON.stringify({
            email: this.state.currentUser?.email || '',
            uid: this.state.currentUser?.uid || 'local-' + Date.now(),
            role: this.state.userRole,
            displayName: this.state.userData?.displayName || '',
            lastLogin: Date.now(),
        }));
        localStorage.setItem('lf_has_data', 'true');
        this.state.isDemo = false;
    },

    async signUp(email, password, role, displayName) {
        role = role || 'student';
        displayName = displayName || email.split('@')[0];

        if (this.auth) {
            const cred = await this.auth.createUserWithEmailAndPassword(email, password);
            await this.db.collection('users').doc(cred.user.uid).set({
                email, role, displayName,
                createdAt: new Date().toISOString(),
                status: 'active',
                points: 0, badges: [],
            });
            return cred.user;
        }

        // Local mode
        const uid = 'local-' + Date.now();
        this.state.currentUser = { email, uid };
        this.state.userRole = role;
        this.state.userData = { email, role, displayName, points: 0, badges: [], status: 'active' };
        this.state.isLoggedIn = true;
        this.saveSession();

        // Store user in local DB
        const users = JSON.parse(localStorage.getItem('lf_users') || '{}');
        users[uid] = this.state.userData;
        localStorage.setItem('lf_users', JSON.stringify(users));

        window.dispatchEvent(new CustomEvent('lf:auth:login', { detail: this.state.userData }));
        return this.state.currentUser;
    },

    async signIn(email, password) {
        if (this.auth) {
            return await this.auth.signInWithEmailAndPassword(email, password);
        }

        // Local mode - check stored users
        const users = JSON.parse(localStorage.getItem('lf_users') || '{}');
        const user = Object.values(users).find(u => u.email === email);
        if (!user) throw new Error('用戶不存在');

        this.state.currentUser = { email, uid: Object.keys(users).find(k => users[k].email === email) };
        this.state.userRole = user.role;
        this.state.userData = user;
        this.state.isLoggedIn = true;
        this.saveSession();
        window.dispatchEvent(new CustomEvent('lf:auth:login', { detail: user }));
        return this.state.currentUser;
    },

    signOut() {
        if (this.auth) return this.auth.signOut();
        localStorage.removeItem('lf_session');
        this.state.isLoggedIn = false;
        this.state.currentUser = null;
        this.state.userRole = null;
        this.state.userData = null;
        window.dispatchEvent(new CustomEvent('lf:auth:logout'));
    },

    onLogin(user) {
        this.state.currentUser = user;
        this.state.isLoggedIn = true;
        if (this.db) {
            this.db.collection('users').doc(user.uid).get().then(doc => {
                if (doc.exists) {
                    this.state.userData = doc.data();
                    this.state.userRole = this.state.userData.role;
                    this.saveSession();
                    window.dispatchEvent(new CustomEvent('lf:auth:login', { detail: this.state.userData }));
                }
            });
        }
    },

    onLogout() {
        localStorage.removeItem('lf_session');
        this.state.isLoggedIn = false;
        this.state.currentUser = null;
        this.state.userRole = null;
        this.state.userData = null;
        window.dispatchEvent(new CustomEvent('lf:auth:logout'));
    },

    // ==========================================
    // DATA - Local fallback
    // ==========================================
    getData(key, fallback) {
        try {
            const val = localStorage.getItem('lf_' + key);
            return val ? JSON.parse(val) : fallback;
        } catch(e) { return fallback; }
    },

    setData(key, value) {
        localStorage.setItem('lf_' + key, JSON.stringify(value));
    },

        // ==========================================
    // DATA BUS v2.1 - Cross-page reactive data
    // ==========================================
    _watchers: {},
    _events: {},

    watchData(key, callback) {
        if (!this._watchers[key]) this._watchers[key] = [];
        this._watchers[key].push(callback);
        // Return unsubscribe function
        return () => {
            this._watchers[key] = this._watchers[key].filter(cb => cb !== callback);
        };
    },

    setData(key, value) {
        localStorage.setItem("lf_" + key, JSON.stringify(value));
        // Notify watchers
        if (this._watchers[key]) {
            this._watchers[key].forEach(cb => {
                try { cb(value, key); } catch(e) {}
            });
        }
        // Emit cross-tab event
        this.emit("data:" + key, value);
    },

    // ==========================================
    // EVENT BUS - Cross-role notification
    // ==========================================
    on(event, callback) {
        if (!this._events[event]) this._events[event] = [];
        this._events[event].push(callback);
        return () => {
            this._events[event] = this._events[event].filter(cb => cb !== callback);
        };
    },

    emit(event, data) {
        // Local listeners
        if (this._events[event]) {
            this._events[event].forEach(cb => {
                try { cb(data, event); } catch(e) {}
            });
        }
        // Cross-tab broadcast via localStorage
        try {
            localStorage.setItem("lf_event:" + event, JSON.stringify({
                event, data, ts: Date.now()
            }));
            // Clean up immediately to avoid polluting
            setTimeout(() => localStorage.removeItem("lf_event:" + event), 100);
        } catch(e) {}
    },

    // Listen for cross-tab events
    _initCrossTab() {
        window.addEventListener("storage", (e) => {
            if (e.key && e.key.startsWith("lf_event:")) {
                try {
                    const { event, data } = JSON.parse(e.newValue);
                    if (this._events[event]) {
                        this._events[event].forEach(cb => {
                            try { cb(data, event); } catch(e) {}
                        });
                    }
                } catch(e) {}
            }
        });
    },

    // ==========================================
    // NOTIFICATION SYSTEM - Cross-role alerts
    // ==========================================
    notify(role, title, message, action) {
        const notification = {
            id: "notif_" + Date.now(),
            role: role, // "student" | "teacher" | "parent" | "admin"
            title: title,
            message: message,
            action: action || null, // { url: "...", label: "..." }
            read: false,
            ts: Date.now()
        };
        // Store in notifications list
        const notifs = this.getData("notifications_" + role, []);
        notifs.unshift(notification);
        if (notifs.length > 50) notifs.length = 50; // Cap
        this.setData("notifications_" + role, notifs);
        // Emit event
        this.emit("notification:" + role, notification);
        return notification.id;
    },

    getNotifications(role) {
        return this.getData("notifications_" + (role || this.state.userRole), []);
    },

    markNotificationRead(role, notifId) {
        const notifs = this.getData("notifications_" + role, []);
        const n = notifs.find(x => x.id === notifId);
        if (n) n.read = true;
        this.setData("notifications_" + role, notifs);
    },

    // ==========================================
    // ONBOARDING - New user wizard state
    // ==========================================
    isOnboarded(role) {
        const r = role || this.state.userRole;
        return this.getData("onboarded_" + r, false);
    },

    completeOnboarding(role) {
        const r = role || this.state.userRole;
        this.setData("onboarded_" + r, true);
        this.emit("onboarding:complete", { role: r });
    },

    getOnboardingStep(role) {
        const r = role || this.state.userRole;
        return this.getData("onboarding_step_" + r, 1);
    },

    setOnboardingStep(role, step) {
        const r = role || this.state.userRole;
        this.setData("onboarding_step_" + r, step);
    },

    // ==========================================
    // SYNC - Cross-page data integrity
    // ==========================================
    syncAll() {
        const keys = [];
        for (let i = 0; i < localStorage.length; i++) {
            const k = localStorage.key(i);
            if (k.startsWith("lf_")) keys.push(k);
        }
        this.emit("sync:complete", { keys, ts: Date.now() });
        return keys;
    },

// ==========================================
    // STUDENT DATA
    // ==========================================
    getStudentProgress() {
        return this.getData('student_progress', {
            totalScore: 847, streak: 12, accuracy: 72,
            trapsFound: 3, trapsOk: 7,
            badges: ['陷阱獵人', '連續7日', '速度之星'],
            recentActivity: [],
        });
    },

    saveStudentProgress(progress) {
        this.setData('student_progress', progress);
    },

    // ==========================================
    // TEACHER DATA
    // ==========================================
    getTeacherClasses() {
        return this.getData('teacher_classes', [
            { id: 'P5-A', grade: 'P5', students: 3, day: '週三', time: '16:30' },
            { id: 'P5-B', grade: 'P5', students: 3, day: '週四', time: '17:00' },
        ]);
    },

    // ==========================================
    // PARENT DATA
    // ==========================================
    getParentView() {
        return this.getData('parent_view', {
            childName: '未設定',
            monthlyProgress: [],
            teacherNote: '未有導師評語',
        });
    },

    // ==========================================
    // UTILS
    // ==========================================
    isLoggedIn() { return this.state.isLoggedIn; },
    getRole() { return this.state.userRole; },
    getUser() { return this.state.userData; },
    isDemo() { return this.state.isDemo && !this.state.isLoggedIn; },
};

// Auto-init
document.addEventListener('DOMContentLoaded', () => LFCore.init());
console.log('[LF Core v2.0] Ready - Local-first with Firebase optional');
