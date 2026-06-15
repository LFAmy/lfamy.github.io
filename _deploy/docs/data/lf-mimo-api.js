/* ═══════════════════════════════════════════════════════
   霖楓學苑 · MiMo API Client v2.5
   2026-06-05 · Xiaomi MiMo v2.5 · 1M context window
   API: https://token-plan-sgp.xiaomimimo.com/v1
   ═══════════════════════════════════════════════════════ */

const MIMO = {
  endpoint: 'https://token-plan-sgp.xiaomimimo.com/v1/chat/completions',
  apiKey: 'tp-snhe8xafawoier045vqcybvjivmwdrj4cm4z62jg1jglfvds',
  model: 'mimo-v2.5-pro',
  maxTokens: 1200,
  temperature: 0.5,

  /* ── System Prompts ── */
  prompts: {
    tutor: '你係霖楓學苑（LF Academy）AI數學導師。身份：香港小學數學陷阱診斷專家。風格：用繁體中文+廣東話，蘇格拉底式引導，唔直接俾答案。逐步引導學生思考。每個步驟都要解釋點解。遇到陷阱題要標記T1-T10陷阱類型。最後俾答案時要驗算。',
    solver: '你係霖楓學苑AI數學解題專家。逐步解答數學題目。每題：1)列出題目 2)逐步解答（每步解釋） 3)標記陷阱類型(T1-T10) 4)驗算 5)最終答案。用繁體中文+廣東話。',
    vision: '你係MiMo Vision v2.5數學影像分析系統。從圖片中提取數學題目。如果圖片包含數學公式、圖表或文字，將其轉換為可讀文本。對於分數用 a/b 表示，對於幾何圖形描述其形狀和尺寸。用繁體中文輸出。',
    grader: '你係霖楓學苑AI批改專家。批改學生答案：1)判斷對錯 2)如果錯，指出錯在哪裡 3)分析可能踩中的陷阱 4)給出正確解法。用繁體中文+廣東話，友善鼓勵。'
  },

  /* ── Core API Call ── */
  async ask(messages, options = {}) {
    const opts = {
      model: options.model || this.model,
      messages: messages,
      max_tokens: options.maxTokens || this.maxTokens,
      temperature: options.temperature || this.temperature
    };

    try {
      const ctrl = new AbortController();
      const timeout = setTimeout(() => ctrl.abort(), options.timeout || 20000);
      
      const r = await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + this.apiKey,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(opts),
        signal: ctrl.signal
      });
      
      clearTimeout(timeout);
      
      if (!r.ok) {
        console.warn('[MiMo] API error:', r.status);
        return null;
      }
      
      const data = await r.json();
      return {
        content: data.choices?.[0]?.message?.content || null,
        model: data.model,
        usage: data.usage,
        raw: data
      };
    } catch(e) {
      console.warn('[MiMo] Request failed:', e.message);
      return null;
    }
  },

  /* ── Convenience Methods ── */
  async tutorAsk(question, context = '') {
    const messages = [
      { role: 'system', content: this.prompts.tutor },
      { role: 'user', content: context ? context + '\n\n' + question : question }
    ];
    return this.ask(messages, { maxTokens: 1500, temperature: 0.5 });
  },

  async solveMath(problem) {
    const messages = [
      { role: 'system', content: this.prompts.solver },
      { role: 'user', content: problem }
    ];
    return this.ask(messages, { maxTokens: 2000, temperature: 0.3 });
  },

  async analyzeImage(base64Image) {
    const messages = [
      { role: 'system', content: this.prompts.vision },
      { role: 'user', content: [
        { type: 'text', text: '請分析以下圖片中的數學題目，提取所有文字、數字和圖表信息：' },
        { type: 'image_url', image_url: { url: base64Image } }
      ]}
    ];
    return this.ask(messages, { maxTokens: 1200, temperature: 0.2 });
  },

  async gradeAnswer(question, studentAnswer, correctAnswer) {
    const messages = [
      { role: 'system', content: this.prompts.grader },
      { role: 'user', content: `題目：${question}\n學生答案：${studentAnswer}\n正確答案：${correctAnswer}\n\n請批改。` }
    ];
    return this.ask(messages, { maxTokens: 800, temperature: 0.3 });
  },

  /* ── Streaming (for real-time typing effect) ── */
  async askStream(messages, onChunk, options = {}) {
    const opts = {
      model: options.model || this.model,
      messages: messages,
      max_tokens: options.maxTokens || this.maxTokens,
      temperature: options.temperature || this.temperature,
      stream: true
    };

    try {
      const r = await fetch(this.endpoint, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer ' + this.apiKey,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(opts)
      });

      if (!r.ok) return null;

      const reader = r.body.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(l => l.startsWith('data: '));
        
        for (const line of lines) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;
          try {
            const json = JSON.parse(data);
            const content = json.choices?.[0]?.delta?.content || '';
            if (content) {
              fullContent += content;
              if (onChunk) onChunk(content, fullContent);
            }
          } catch(e) {}
        }
      }

      return { content: fullContent };
    } catch(e) {
      console.warn('[MiMo] Stream failed:', e.message);
      return null;
    }
  }
};

console.log('[MiMo v2.5] API client ready. Endpoint:', MIMO.endpoint);
