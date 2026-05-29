// ============================================================
// 霖楓學苑 - WhatsApp 自動化引擎 v2.0
// 功能: 診斷報告 | 課堂提醒 | 付款確認 | 每週報告 | 自動跟進
// ============================================================

const LFWhatsApp = {
  PHONE: "85294796459",
  BASE: "https://wa.me/85294796459",

  // ── 1. 診斷報告推送 ──
  sendDiagnosticReport(name, grade, score, weakTraps, strongTraps) {
    var msg = encodeURIComponent(
      "🪤 *霖楓學苑 · 陷阱診斷報告*\n\n" +
      "👦 學生：" + name + " (" + grade + ")\n" +
      "📊 完成題數：10題\n" +
      "✅ 正確率：" + score + "%\n\n" +
      "💪 強項：" + (strongTraps.join("、") || "無") + "\n" +
      "⚠️ 弱項：" + (weakTraps.join("、") || "無") + "\n\n" +
      "🎯 建議：針對弱項陷阱進行專項訓練\n\n" +
      "📱 回覆「試堂」預約免費體驗！"
    );
    window.open(this.BASE + "?text=" + msg, "_blank");
    this._log("diagnostic", { name: name, grade: grade, score: score });
  },

  // ── 2. 試堂確認推送 ──
  sendTrialConfirmation(name, grade, date, time) {
    var msg = encodeURIComponent(
      "✅ *霖楓學苑 · 試堂確認*\n\n" +
      "👦 學生：" + name + "\n" +
      "📚 年級：" + grade + "\n" +
      "📅 日期：" + date + "\n" +
      "⏰ 時間：" + time + "\n" +
      "🖥 上課連結：請用ClassIn加入\n\n" +
      "📌 請提前5分鐘登入測試設備！\n" +
      "💬 有問題隨時WhatsApp我哋！"
    );
    window.open(this.BASE + "?text=" + msg, "_blank");
    this._log("trial_confirmed", { name: name, date: date });
  },

  // ── 3. 付款確認推送 ──
  sendPaymentConfirmation(name, amount, plan) {
    var msg = encodeURIComponent(
      "💰 *霖楓學苑 · 付款確認*\n\n" +
      "👦 學生：" + name + "\n" +
      "💳 金額：HK$" + amount + "\n" +
      "📋 計劃：" + plan + "\n" +
      "✅ 狀態：已確認收款\n\n" +
      "📅 首堂日期將由老師WhatsApp確認\n" +
      "🎉 歡迎加入霖楓學苑！"
    );
    window.open(this.BASE + "?text=" + msg, "_blank");
    this._log("payment", { name: name, amount: amount });
  },

  // ── 4. 課堂提醒（給家長） ──
  sendClassReminder(name, subject, date, time, link) {
    var msg = encodeURIComponent(
      "⏰ *霖楓學苑 · 課堂提醒*\n\n" +
      "👦 " + name + " 今日有堂！\n" +
      "📚 課題：" + subject + "\n" +
      "📅 " + date + " " + time + "\n" +
      "🖥 連結：" + (link || "ClassIn 課室") + "\n\n" +
      "📌 記得準備：講義 + 白紙 + 筆！"
    );
    window.open(this.BASE + "?text=" + msg, "_blank");
    this._log("reminder", { name: name, subject: subject });
  },

  // ── 5. 每週進度報告 ──
  sendWeeklyReport(name, weekData) {
    var msg = encodeURIComponent(
      "📊 *霖楓學苑 · 本週學習報告*\n\n" +
      "👦 " + name + "\n" +
      "📅 本週練習：" + weekData.days + "/5 天\n" +
      "📈 掌握度：" + weekData.mastery + "%\n" +
      "🏆 進步課題：" + (weekData.improved || "—") + "\n" +
      "⚠️ 需加強：" + (weekData.weak || "—") + "\n\n" +
      "💬 老師評語：" + (weekData.teacherNote || "繼續努力！") + "\n\n" +
      "📱 回覆了解詳情！"
    );
    window.open(this.BASE + "?text=" + msg, "_blank");
    this._log("weekly_report", { name: name });
  },

  // ── 6. 自動跟進（48小時未回覆） ──
  sendFollowUp(name, lastAction) {
    var msg = encodeURIComponent(
      "👋 *霖楓學苑 · 溫馨跟進*\n\n" +
      "你好呀！見到你上次" + lastAction + "之後就冇咗下文。\n\n" +
      "想提提你，我哋嘅免費試堂名額有限㗎！\n" +
      "小朋友嘅數學陷阱問題，早啲解決早啲安心～\n\n" +
      "📱 回覆「試堂」即刻安排！"
    );
    window.open(this.BASE + "?text=" + msg, "_blank");
    this._log("followup", { name: name });
  },

  // ── 7. 通用訊息發送 ──
  sendCustom(phone, template) {
    var msg = encodeURIComponent(template);
    var target = phone ? "https://wa.me/" + phone : this.BASE;
    window.open(target + "?text=" + msg, "_blank");
  },

  // ── 內部：記錄發送日誌 ──
  _log(type, data) {
    var logs = JSON.parse(localStorage.getItem("lf_wa_logs") || "[]");
    logs.push({
      type: type,
      data: data,
      time: new Date().toISOString()
    });
    // Keep only last 100 logs
    if (logs.length > 100) logs = logs.slice(-100);
    localStorage.setItem("lf_wa_logs", JSON.stringify(logs));
    
    // If Firebase available, also log to Firestore
    if (typeof db !== "undefined" && typeof firebase !== "undefined") {
      try {
        db.collection("wa_logs").add({
          type: type,
          data: data,
          time: firebase.firestore.FieldValue.serverTimestamp()
        }).catch(function() {});
      } catch(e) {}
    }
  },

  // ── 獲取發送歷史 ──
  getLogs(type) {
    var logs = JSON.parse(localStorage.getItem("lf_wa_logs") || "[]");
    if (type) return logs.filter(function(l) { return l.type === type; });
    return logs;
  },

  // ── 排程提醒（儲存到localStorage，頁面載入時檢查） ──
  scheduleReminder(name, subject, dateTime, link) {
    var reminders = JSON.parse(localStorage.getItem("lf_reminders") || "[]");
    reminders.push({
      name: name,
      subject: subject,
      datetime: dateTime,
      link: link,
      created: new Date().toISOString()
    });
    localStorage.setItem("lf_reminders", JSON.stringify(reminders));
  },

  // ── 檢查並觸發到期提醒 ──
  checkReminders() {
    var reminders = JSON.parse(localStorage.getItem("lf_reminders") || "[]");
    var now = new Date();
    var triggered = [];
    var remaining = [];
    
    reminders.forEach(function(r) {
      var remindTime = new Date(r.datetime);
      var diffMin = (remindTime - now) / 60000;
      
      if (diffMin <= 60 && diffMin > 0) {
        // Within 1 hour - trigger reminder
        this.sendClassReminder(r.name, r.subject, 
          remindTime.toLocaleDateString("zh-HK"),
          remindTime.toLocaleTimeString("zh-HK", {hour:"2-digit",minute:"2-digit"}),
          r.link);
        triggered.push(r);
      } else if (diffMin > 0) {
        remaining.push(r);
      }
    }.bind(this));
    
    localStorage.setItem("lf_reminders", JSON.stringify(remaining));
    return triggered.length;
  }
};

// Auto-check reminders every 5 minutes
setInterval(function() {
  LFWhatsApp.checkReminders();
}, 300000);

// Check on page load
if (document.readyState === "complete") {
  LFWhatsApp.checkReminders();
} else {
  window.addEventListener("load", function() {
    LFWhatsApp.checkReminders();
  });
}

console.log("LFWhatsApp v2.0 loaded | Phone: " + LFWhatsApp.PHONE);
