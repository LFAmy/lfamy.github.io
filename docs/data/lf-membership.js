// ═══════════════════════════════════════════════════
// 霖楓學苑 · 會員系統 (Membership System)
// Firebase Auth + Firestore 使用追蹤
// ═══════════════════════════════════════════════════
try { firebase.initializeApp(LF_FIREBASE_CONFIG); } catch(e) {}
const auth = firebase.auth();
const db = firebase.firestore();

const MEMBERSHIP = {
  free:    { name:"免費體驗", aiDaily:10, practiceDaily:5,  diagReport:false, price:"$0" },
  basic:   { name:"基本會員", aiDaily:50, practiceDaily:999, diagReport:true,  price:"$88/月" },
  pro:     { name:"專業會員", aiDaily:999, practiceDaily:9999, diagReport:true,  price:"$168/月" }
};

let currentUser = null;
let userMembership = "free";
let todayUsage = { ai:0, practice:0, date:"" };

auth.onAuthStateChanged(async function(user) {
  currentUser = user;
  if (user) {
    try {
      const doc = await db.collection("users").doc(user.uid).get();
      if (doc.exists && doc.data().membership) userMembership = doc.data().membership;
    } catch(e) {}
    await loadTodayUsage();
  } else {
    userMembership = "free";
    todayUsage = { ai:0, practice:0, date:"" };
  }
  if (typeof updateMembershipUI === "function") updateMembershipUI();
});

async function loadTodayUsage() {
  if (!currentUser) return;
  const today = new Date().toISOString().slice(0,10);
  try {
    const doc = await db.collection("users").doc(currentUser.uid).collection("usage").doc(today).get();
    if (doc.exists) { todayUsage = doc.data(); todayUsage.date = today; }
    else { todayUsage = { ai:0, practice:0, date:today }; }
  } catch(e) {
    const saved = localStorage.getItem("lf_usage_"+today);
    if (saved) { try { todayUsage = JSON.parse(saved); } catch(e2) {} }
    todayUsage.date = today;
  }
}

async function incrementUsage(type) {
  const today = new Date().toISOString().slice(0,10);
  if (todayUsage.date !== today) { todayUsage = { ai:0, practice:0, date:today }; }
  todayUsage[type] = (todayUsage[type] || 0) + 1;
  if (currentUser) {
    try { await db.collection("users").doc(currentUser.uid).collection("usage").doc(today).set(todayUsage, {merge:true}); } catch(e) {}
  }
  localStorage.setItem("lf_usage_"+today, JSON.stringify(todayUsage));
  if (typeof updateMembershipUI === "function") updateMembershipUI();
}

function checkLimit(type) {
  const tier = MEMBERSHIP[userMembership];
  const limit = type === "ai" ? tier.aiDaily : tier.practiceDaily;
  return todayUsage[type] < limit;
}

function showUpgradePrompt(type) {
  const tierName = MEMBERSHIP[userMembership].name;
  const limit = type === "ai" ? MEMBERSHIP[userMembership].aiDaily : MEMBERSHIP[userMembership].practiceDaily;
  typeof addMsg === "function" && addMsg("⚠️ **" + tierName + "今日" + (type==="ai"?"AI問答":"練習") + "限額 (" + limit + "次) 已用完！**", "system");
  typeof addMsg === "function" && addMsg("🔓 **升級解鎖更多：**\n\n⭐ 基本會員 ($88/月)：每日50次AI問答 + 無限練習 + 弱項診斷報告\n💎 專業會員 ($168/月)：無限AI + 每週診斷 + 專屬學習計劃\n\n👉 留言「升級」或 inbox 查詢優惠！", "ai");
}

function updateMembershipUI() {
  const badge = document.getElementById("memberBadge");
  const loginBtn = document.getElementById("loginBtn");
  const usageDisplay = document.getElementById("usageDisplay");
  if (!badge) return;
  if (currentUser) {
    const tier = MEMBERSHIP[userMembership];
    badge.textContent = tier.name;
    badge.style.display = "inline-block";
    badge.style.background = userMembership === "pro" ? "#7C3AED" : userMembership === "basic" ? "#16A34A" : "#64748b";
    if (loginBtn) { loginBtn.textContent = (currentUser.displayName || currentUser.email || "已登入").substring(0,12); loginBtn.style.background = "#16A34A"; loginBtn.onclick = function() { if (confirm("要登出嗎？")) auth.signOut(); }; }
  } else {
    badge.style.display = "none";
    if (loginBtn) { loginBtn.textContent = "🔑 登入"; loginBtn.style.background = "#1A3C6D"; loginBtn.onclick = showAuthModal; }
  }
  if (usageDisplay) {
    const tier = MEMBERSHIP[userMembership];
    usageDisplay.textContent = "AI:" + (tier.aiDaily - todayUsage.ai) + "/" + tier.aiDaily + " | 練習:" + (tier.practiceDaily - todayUsage.practice);
  }
}

function showAuthModal() {
  const email = prompt("📧 輸入電郵註冊/登入（或用Google一鍵登入）:\n\n留空 = Google登入");
  if (email === null) return;
  if (email.trim() === "") {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider).catch(function(e) { alert("Google登入失敗: " + e.message); });
  } else {
    auth.signInWithEmailAndPassword(email.trim(), "lfmember2026").catch(function() {
      auth.createUserWithEmailAndPassword(email.trim(), "lfmember2026").then(function() {
        db.collection("users").doc(auth.currentUser.uid).set({
          email: email.trim(), membership: "free",
          createdAt: firebase.firestore.FieldValue.serverTimestamp()
        }, {merge:true});
      }).catch(function(e) { alert("註冊失敗: " + e.message); });
    });
  }
}
