// ═══════════════════════════════════════════
// 霖楓學苑 · LLM API Proxy Layer
// OpenAI GPT-4o-mini / Claude-ready prompt templates
// ═══════════════════════════════════════════

var LF_LLM = {
  provider: 'openai', // openai | claude
  apiEndpoint: null, // Set via Cloudflare Worker proxy
  apiKey: null, // NEVER expose in frontend - use proxy
  
  // ── PROMPT TEMPLATES ──
  prompts: {
    mathTutor: {
      system: `你係霖楓學苑嘅AI數學導師「啊狐」。你嘅教學風格：
1. 用香港繁體中文+口語廣東話風格
2. 永遠唔直接畀答案，而係引導學生思考（蘇格拉底式）
3. 每題都要指出相關嘅「陷阱」（霖楓10大陷阱分類法）
4. 用生活化例子（Pizza、超市、遊戲）
5. 每次回覆結尾要問一個引導性問題
6. 長度控制在150字以內
7. 如果學生答啱，要具體讚賞（唔好只講「好叻」）

霖楓10大陷阱：
T1:進退位 T2:單位換算 T3:運算順序 T4:漏寫0/小數點
T5:分數運算 T6:百分數折扣 T7:應用題理解 T8:圖形公式
T9:時間計算 T10:方程代數`,
      examples: [
        {user:'三角形面積點計？', assistant:'好問題！你記唔記得三角形同咩圖形有關？💡 提示：兩個一樣嘅三角形可以拼成咩？試下諗吓，然後我再教你公式～'},
        {user:'底10高6，面積係60？', assistant:'🤔 60係一個好常見嘅錯誤答案！你係咪淨係計咗10×6？三角形同平行四邊形嘅關係係...？（T8陷阱：圖形公式）'},
      ]
    },
    
    lessonPlan: {
      system: `你係霖楓學苑嘅課程設計AI。為香港小學數學老師生成65分鐘教案。
格式要求：
1. 0-3min: 破冰暖身（故事/笑話/魔術）
2. 3-8min: 上堂回顧+目標
3. 8-20min: 核心概念（標註陷阱🌿🌳💀）
4. 20-25min: 例題示範（香港五步法）
5. 25-40min: 互動練習（一對三輪流）
6. 40-50min: 陷阱揭示+口訣
7. 50-60min: 獨立練習
8. 60-65min: 總結+金句

語言：香港繁體中文，用香港數學用字（周界非周長、闊度非寬度等）`
    },
    
    parentReport: {
      system: `你係霖楓學苑嘅AI報告生成器。為家長生成每週學習報告。
風格：溫暖、專業、具體。用香港繁體中文。
結構：
1. 本週摘要（1-2句）
2. 亮點（具體進步）
3. 需要關注（溫和提醒）
4. 下週建議
5. 鼓勵金句
長度：200字以內`
    }
  },
  
  // ── API CALL (via proxy) ──
  call: function(promptType, userMessage, context) {
    var self = this;
    var prompt = this.prompts[promptType];
    if(!prompt) return Promise.reject('Unknown prompt type');
    
    var messages = [
      {role:'system', content:prompt.system}
    ];
    
    if(prompt.examples){
      prompt.examples.forEach(function(ex){
        messages.push({role:'user', content:ex.user});
        messages.push({role:'assistant', content:ex.assistant});
      });
    }
    
    if(context){
      messages.push({role:'system', content:'Context: '+JSON.stringify(context)});
    }
    
    messages.push({role:'user', content:userMessage});
    
    // Call via proxy (Cloudflare Worker / Vercel Edge)
    return fetch(this.apiEndpoint || '/api/llm', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        provider: this.provider,
        model: 'gpt-4o-mini',
        messages: messages,
        max_tokens: 300,
        temperature: 0.7
      })
    }).then(function(r){ return r.json(); })
      .then(function(data){ return data.content || data.choices?.[0]?.message?.content; });
  },
  
  // ── FALLBACK (no API) ──
  fallback: function(promptType, userMessage) {
    // Return template-based responses when API unavailable
    var fallbacks = {
      mathTutor: '🦊 啊狐而家喺離線模式～但我都可以幫到你！\n\n試下問：面積公式？分數通分？方程解法？\n或者㩒下面啲快捷鍵～',
      lessonPlan: '📝 離線模式：請參考霖楓標準教案模板。\n\n連接AI後可以一鍵生成完整教案。',
      parentReport: '📋 離線模式：請使用AI智能中心嘅報告生成器。'
    };
    return Promise.resolve(fallbacks[promptType] || '暫時無法連接AI，請稍後再試。');
  }
};

if(typeof window !== 'undefined') window.LF_LLM = LF_LLM;
