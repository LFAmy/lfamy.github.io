// ═══════════════════════════════════════════
// 霖楓學苑 · GBA簡體版切換系統
// 大灣區版本：繁體↔簡體自動轉換
// ═══════════════════════════════════════════

var LF_GBA = {
  enabled: false,
  currentLang: 'zh-HK', // zh-HK or zh-CN
  
  // HK→CN term mapping
  termMap: {
    '周界': '周长', '闊度': '宽度', '棒形圖': '条形图',
    '速率': '速度', '答句': '答句', '方程': '方程',
    '百分數': '百分数', '小數': '小数', '括號': '括号',
    '平方厘米': '平方厘米', '立方厘米': '立方厘米',
    '呈分試': '呈分试', '補習': '补习', '講義': '讲义',
    '嘅': '的', '咗': '了', '佢': '他', '哋': '们',
    '唔': '不', '係': '是', '咩': '什么', '點解': '为什么',
    '點樣': '怎样', '邊度': '哪里', '呢個': '这个',
    '嗰個': '那个', '佢哋': '他们', '我哋': '我们',
    '同學': '同学', '老師': '老师', '學生': '学生',
    '學校': '学校', '數學': '数学', '練習': '练习',
    '題目': '题目', '答案': '答案', '考試': '考试',
    '成績': '成绩', '進步': '进步', '學習': '学习',
    '陷阱': '陷阱', '面積': '面积', '體積': '体积',
    '分數': '分数', '折扣': '折扣', '時間': '时间',
    '公里': '千米', '米': '米', '厘米': '厘米',
    '三角形': '三角形', '梯形': '梯形', '長方形': '长方形',
    '正方形': '正方形', '平行四邊形': '平行四边形',
    '霖楓學苑': '霖枫学苑', '免費': '免费',
    '試堂': '试课', '報名': '报名', '登入': '登录'
  },
  
  // Toggle language
  toggle: function() {
    this.currentLang = (this.currentLang === 'zh-HK') ? 'zh-CN' : 'zh-HK';
    this.applyToPage();
    localStorage.setItem('lf_gba_lang', this.currentLang);
    return this.currentLang;
  },
  
  // Apply conversion to entire page
  applyToPage: function() {
    if(this.currentLang === 'zh-HK'){
      location.reload(); // Simplest: reload to restore original
      return;
    }
    
    // Walk all text nodes
    var walker = document.createTreeWalker(
      document.body, NodeFilter.SHOW_TEXT,
      {acceptNode: function(n){return n.parentElement.tagName!=='SCRIPT'&&n.parentElement.tagName!=='STYLE'?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;}}
    );
    
    var nodes = [];
    while(walker.nextNode()) nodes.push(walker.currentNode);
    
    for(var i=0;i<nodes.length;i++){
      var text = nodes[i].textContent;
      var changed = false;
      for(var hk in this.termMap){
        if(text.indexOf(hk)>=0){
          text = text.replace(new RegExp(hk,'g'), this.termMap[hk]);
          changed = true;
        }
      }
      if(changed) nodes[i].textContent = text;
    }
    
    // Update HTML lang attribute
    document.documentElement.lang = 'zh-CN';
  },
  
  // Init - check saved preference
  init: function() {
    var saved = localStorage.getItem('lf_gba_lang');
    if(saved === 'zh-CN'){
      this.currentLang = 'zh-HK'; // Reset flag so toggle works
      this.toggle();
    }
  },
  
  // Get toggle button HTML
  getToggleButton: function() {
    var isHK = this.currentLang === 'zh-HK';
    return '<button onclick="LF_GBA.toggle()" style="padding:4px 10px;border-radius:12px;border:1px solid '+(isHK?'rgba(255,255,255,0.3)':'var(--g)')+';background:'+(isHK?'transparent':'var(--g)')+';color:'+(isHK?'white':'var(--b)')+';font-size:10px;cursor:pointer;font-family:inherit;font-weight:700">'+(isHK?'繁':'简')+'</button>';
  }
};

// Auto-init
if(typeof window !== 'undefined'){
  window.LF_GBA = LF_GBA;
  document.addEventListener('DOMContentLoaded', function(){ LF_GBA.init(); });
}
