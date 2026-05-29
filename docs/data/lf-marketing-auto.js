// ═══════════════════════════════════════════
// 霖楓學苑 · 7-Day Auto Follow-Up Engine
// Marketing automation for parent conversion
// ═══════════════════════════════════════════

var LFMarketing = {
  // ── 7-DAY SEQUENCE ──
  sequence: [
    {
      day: 0, trigger: 'trial_signup',
      title: '🎉 歡迎加入霖楓學苑！',
      body: '你好呀！多謝你報名免費試堂～\n\n📅 試堂日期：{trial_date}\n⏰ 時間：{trial_time}\n👨‍🏫 老師：{teacher_name}\n\n💡 提提你：試堂前可以先做AI診斷，等我哋了解小朋友嘅程度：\nhttps://lfamy.github.io/docs/ai-diagnostic.html\n\n有咩問題隨時問我！😊',
      action: 'confirm_trial'
    },
    {
      day: -1, trigger: 'before_trial',
      title: '⏰ 聽日就係試堂啦！',
      body: '提提你：聽日 {trial_time} 係 {student_name} 嘅數學試堂～\n\n✅ 請確保：\n• 網絡穩定\n• 準備紙筆\n• 小朋友精神飽滿\n\n🔗 課堂連結：{class_link}\n\n聽日見！🎯',
      action: 'remind_trial'
    },
    {
      day: 0.1, trigger: 'after_trial',
      title: '🎯 試堂完成！{student_name}嘅診斷報告',
      body: '今日試堂好順利呀！{student_name}嘅表現總結：\n\n✅ 強項：{strengths}\n⚠️ 需要改善：{weaknesses}\n📊 AI診斷分數：{score}分\n\n📋 完整報告：https://lfamy.github.io/docs/ai-smart-hub.html\n\n想了解我哋嘅課程？P{grade} 係 ${price}/堂，一對三小班教學～',
      action: 'send_report'
    },
    {
      day: 1, trigger: 'day1_followup',
      title: '💡 {student_name}嘅個人化學習建議',
      body: '試堂之後，AI分析咗{student_name}嘅學習數據：\n\n🎯 最需要加強：{top_weakness}\n📖 推薦練習：{recommended_practice}\n⚔️ 挑戰Boss：{recommended_boss}\n\n全部免費㗎！試下：\nhttps://lfamy.github.io/docs/ai-smart-hub.html',
      action: 'nurture_value'
    },
    {
      day: 3, trigger: 'day3_social_proof',
      title: '🌟 其他家長嘅真實分享',
      body: '好多家長問我哋嘅成效～\n\n真實案例：\n📈 P5 小明：3個月由68分 → 89分\n📈 P6 家欣：呈分試數學攞A，入咗Band 1\n📈 P4 俊傑：由驚數學變成最鍾意數學堂\n\n🎯 佢哋都係由一堂免費試堂開始㗎！',
      action: 'social_proof'
    },
    {
      day: 5, trigger: 'day5_limited_offer',
      title: '🎁 限時優惠：首月體驗價',
      body: '為咗多謝你試堂，我哋準備咗特別優惠：\n\n✨ 首月4堂：只需 ${trial_price}\n✨ 附送：AI診斷完整報告\n✨ 附送：個人化練習包（30題）\n\n⚠️ 優惠只限試堂後7日內有效！\n\n有興趣即刻回覆我呢個訊息～',
      action: 'limited_offer'
    },
    {
      day: 7, trigger: 'day7_last_chance',
      title: '最後機會：{student_name}嘅學習唔好等',
      body: '眨下眼就過咗一個星期～\n\n{student_name}嘅數學弱項（{top_weakness}）如果唔盡快處理，可能會影響：\n• 校內考試成績\n• 升中呈分試準備\n• 數學自信心\n\n🪤 霖楓嘅陷阱教學法，專門針對呢啲問題。\n\n最後機會享用首月優惠，回覆我就得！',
      action: 'last_chance'
    }
  ],
  
  // ── TRIGGER ENGINE ──
  trigger: function(eventName, data) {
    var self = this;
    var seq = null;
    for(var i=0;i<this.sequence.length;i++){
      if(this.sequence[i].trigger === eventName){
        seq = this.sequence[i];
        break;
      }
    }
    if(!seq) return null;
    
    // Fill template
    var title = this._fillTemplate(seq.title, data);
    var body = this._fillTemplate(seq.body, data);
    
    // Save to history
    this._logSend(eventName, title, body);
    
    return {title: title, body: body, action: seq.action};
  },
  
  _fillTemplate: function(template, data) {
    var result = template;
    for(var k in data){
      result = result.replace(new RegExp('{'+k+'}','g'), data[k]||'');
    }
    return result;
  },
  
  _logSend: function(event, title, body) {
    var log = JSON.parse(localStorage.getItem('lf_marketing_log')||'[]');
    log.push({
      event: event,
      title: title,
      body: body,
      timestamp: new Date().toISOString(),
      sent: false
    });
    // Keep last 50
    if(log.length>50) log = log.slice(-50);
    localStorage.setItem('lf_marketing_log', JSON.stringify(log));
  },
  
  // ── WHATSAPP SEND ──
  sendWhatsApp: function(eventName, data, phoneNumber) {
    var msg = this.trigger(eventName, data);
    if(!msg) return;
    
    var waMsg = encodeURIComponent('*'+msg.title+'*\n\n'+msg.body);
    var phone = phoneNumber || '85294796459';
    window.open('https://wa.me/'+phone+'?text='+waMsg, '_blank');
    
    // Mark as sent
    var log = JSON.parse(localStorage.getItem('lf_marketing_log')||'[]');
    if(log.length>0) log[log.length-1].sent = true;
    localStorage.setItem('lf_marketing_log', JSON.stringify(log));
  },
  
  // ── SIMULATE SEQUENCE (for testing) ──
  simulate: function(studentData) {
    var self = this;
    var results = [];
    for(var i=0;i<this.sequence.length;i++){
      var msg = this.trigger(this.sequence[i].trigger, studentData);
      if(msg) results.push(msg);
    }
    return results;
  },
  
  // ── GET LOG ──
  getLog: function() {
    return JSON.parse(localStorage.getItem('lf_marketing_log')||'[]');
  }
};

// Auto-init
if(typeof window !== 'undefined'){
  window.LFMarketing = LFMarketing;
}
