// ═══════════════════════════════════════════
// 霖楓學苑 · WhatsApp AI Fox Webhook
// Deploy to: Cloudflare Workers / Vercel Edge
// Twilio WhatsApp Sandbox Webhook
// ═══════════════════════════════════════════

// KNOWLEDGE BASE (same as client-side AI Fox)
const KNOWLEDGE = {
  triangle_area: {
    keywords: ['三角形','面積','triangle'],
    reply: `📐 *三角形面積公式：底 × 高 ÷ 2*

例如：底10cm，高6cm
→ 10×6÷2 = *30cm²*

⚠️ 最常見陷阱：記得÷2！唔寫就直接錯！

🪄 口訣：「底乘高，除以二；唔除二，就玩完！」

想練習多啲？→ https://lfamy.github.io/docs/trap-quiz.html`
  },
  trapezoid_area: {
    keywords: ['梯形','面積','trapezoid'],
    reply: `🔷 *梯形面積公式：(上底+下底) × 高 ÷ 2*

例如：上底5cm，下底9cm，高4cm
→ (5+9)×4÷2 = *28cm²*

⚠️ 陷阱：記得加括號！先加咗上底同下底先乘高！

想睇更多例子？→ https://lfamy.github.io/docs/ai-study-buddy.html`
  },
  fraction_add: {
    keywords: ['分數','加法','通分','fraction','add'],
    reply: `🍕 *分數加法要先通分！*

例如：1/3 + 1/4
→ LCM of 3,4 = 12
→ 4/12 + 3/12 = *7/12*

⚠️ 陷阱：唔可以就咁分子加分子分母加分母！
1/3+1/4 ≠ 2/7`
  },
  fraction_multiply: {
    keywords: ['分數','乘法','multiply'],
    reply: `✖️ *分數乘法：分子×分子，分母×分母*

例如：2/3 × 3/4
→ 6/12 = *1/2*

記得約簡！做完練習睇下自己明唔明：
→ https://lfamy.github.io/docs/trap-quiz.html`
  },
  equation: {
    keywords: ['方程','代數','equation','x','algebra'],
    reply: `🔣 *解方程：目標係搵出x！*

例如：3x + 5 = 20
① 移項：3x = 20-5 = 15
② ÷3：x = *5*

⚠️ 陷阱：移項要變符號！+5移去右邊變-5！

試下AI診斷測下你嘅方程能力：
→ https://lfamy.github.io/docs/ai-diagnostic.html`
  },
  decimal: {
    keywords: ['小數','decimal','點'],
    reply: `0️⃣ *小數乘法三步：*
① 先當整數乘（唔理小數點）
② 數下有幾多個小數位
③ 答案度數返咁多位加點

例如：1.2×0.5
→ 12×5=60，2個小數位
→ *0.60 = 0.6*`
  },
  percentage: {
    keywords: ['百分','折扣','discount','%','折'],
    reply: `💯 *折扣計算：*
• 八折 = ×0.8
• 九折 = ×0.9
• 七折 = ×0.7

⚠️ 陷阱①：八折再九折 ≠ 七折！
→ ×0.8×0.9 = ×0.72

⚠️ 陷阱②：加20%再減20% ≠ 原價！

想知更多？做AI診斷 →
https://lfamy.github.io/docs/ai-diagnostic.html`
  },
  speed: {
    keywords: ['速率','速度','speed','km'],
    reply: `🚗 *速率 = 距離 ÷ 時間*

例如：150公里÷2.5小時
= *60 km/h*

P6先會分「速率」同「速度」～
小學一般用「速率」呢個詞。`
  },
  volume: {
    keywords: ['體積','volume','立方'],
    reply: `📦 *長方體體積 = 長×闊×高*

例如：8×5×3 = *120cm³*

⚠️ 陷阱：單位係cm³（立方厘米）
面積先係cm²（平方厘米）！
唔好搞錯！`
  },
  perimeter: {
    keywords: ['周界','周長','perimeter'],
    reply: `📏 *周界 = 所有邊長加埋*

香港叫「周界」，唔係「周長」！

長方形周界：(長+闊)×2
正方形周界：邊長×4`
  }
};

// ── MAIN HANDLER ──
async function handleRequest(request) {
  // Only accept POST from Twilio
  if (request.method !== 'POST') {
    return new Response('LF WhatsApp AI Fox Webhook - POST only', { status: 200 });
  }

  const formData = await request.formData();
  const body = formData.get('Body') || '';
  const from = formData.get('From') || '';
  
  // Find matching knowledge
  let reply = findReply(body);
  
  // Build Twilio response
  const twiml = `<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Message>${escapeXml(reply)}</Message>
</Response>`;

  return new Response(twiml, {
    headers: { 'Content-Type': 'text/xml' }
  });
}

function findReply(msg) {
  const lower = msg.toLowerCase();
  
  // Check greetings
  if (lower.match(/^(hi|hello|你好|喂|嗨|早晨|午安)/)) {
    return `👋 你好！我係啊狐🦊 霖楓學苑嘅AI數學助手！

有咩數學問題想問我？
📐 三角形面積點計？
🍕 分數點通分？
🔣 方程點解？
💯 八折即係幾多？

直接打字問我就得～`;
  }

  // Check thanks
  if (lower.match(/(多謝|唔該|thank|thx)/)) {
    return `😊 唔使客氣！記住啊：數學唔係背，係明！明咗一世都記得。

想做練習？→ https://lfamy.github.io/docs/ai-smart-hub.html`;
  }

  // Check knowledge base
  for (const [key, entry] of Object.entries(KNOWLEDGE)) {
    for (const kw of entry.keywords) {
      if (lower.includes(kw.toLowerCase())) {
        return entry.reply;
      }
    }
  }

  // Topic detection
  if (lower.includes('面積')) return KNOWLEDGE.triangle_area.reply;
  if (lower.includes('分數') && lower.includes('加')) return KNOWLEDGE.fraction_add.reply;
  if (lower.includes('分數') && lower.includes('乘')) return KNOWLEDGE.fraction_multiply.reply;
  if (lower.includes('折扣') || lower.includes('%')) return KNOWLEDGE.percentage.reply;

  // Fallback
  return `我暫時未識答呢個問題 🙈

你可以試下問：
📐 三角形面積點計？
🍕 分數點通分？
🔣 方程點解？
💯 八折即係幾多？

或者上網站做AI診斷：
https://lfamy.github.io/docs/ai-diagnostic.html

或者同真人老師傾計：
https://wa.me/85294796459`;
}

function escapeXml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Cloudflare Workers entry
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
