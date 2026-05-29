/**
 * 霖楓學苑 LF AI API Client v1.0
 * 連接前端頁面到 Python lf_ai_brain.py 引擎
 * 使用方式: <script src="/docs/data/lf-api-client.js"></script>
 * 
 * API 伺服器: http://localhost:5000 (開發) / http://localhost:3001 (生產)
 */

const LF_API = (() => {
    // Auto-detect environment
    const DEV = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'http://localhost:3001/v1'
    
    // Cache for repeated calls (same input within 5 minutes)
    const _cache = new Map();
    const _cacheTTL = 5 * 60 * 1000; // 5 minutes
    
    function _getCacheKey(endpoint, data) {
        return endpoint + '::' + JSON.stringify(data);
    }
    
    function _fromCache(key) {
        const hit = _cache.get(key);
        if (hit && Date.now() - hit.time < _cacheTTL) {
            console.log('[LF-API] ⚡ Cache hit:', key.substring(0, 60));
            return hit.data;
        }
        return null;
    }
    
    function _toCache(key, data) {
        _cache.set(key, { data, time: Date.now() });
        // Trim cache if > 100 items
        if (_cache.size > 100) {
            const oldest = [..._cache.entries()].sort((a, b) => a[1].time - b[1].time)[0];
            _cache.delete(oldest[0]);
        }
    }
    
    async function _call(endpoint, data, options = {}) {
        const cacheKey = _getCacheKey(endpoint, data);
        
        // Check cache (skip for non-idempotent operations)
        if (!options.noCache) {
            const cached = _fromCache(cacheKey);
            if (cached) return cached;
        }
        
        const url = `${BASE_URL}${endpoint}`;
        console.log(`[LF-API] 📡 ${endpoint}`, data ? Object.keys(data) : '');
        
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), options.timeout || 15000);
            
            const response = await fetch(url, {
                method: data ? 'POST' : 'GET',
                headers: data ? { 'Content-Type': 'application/json' } : {},
                body: data ? JSON.stringify(data) : undefined,
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (result.status === 'ok') {
                if (!options.noCache) _toCache(cacheKey, result);
                return result;
            } else {
                console.warn('[LF-API] ⚠️ API returned error:', result.error || result.message);
                return result;
            }
        } catch (err) {
            if (err.name === 'AbortError') {
                console.warn('[LF-API] ⏱️ Timeout:', endpoint);
            } else {
                console.warn('[LF-API] ❌ Error:', err.message);
            }
            // Return fallback (the function will handle gracefully)
            return null;
        }
    }
    
        async function _callDeepSeek(prompt, systemPrompt, maxTokens) {
        const key = 'sk-e422da39eb9840e387134c823609995e';
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 30000);
            const response = await fetch('https://api.deepseek.com/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key },
                body: JSON.stringify({
                    model: 'deepseek-chat',
                    messages: [
                        { role: 'system', content: systemPrompt || 'You are a helpful math tutor.' },
                        { role: 'user', content: prompt }
                    ],
                    max_tokens: maxTokens || 200
                }),
                signal: controller.signal
            });
            clearTimeout(timeout);
            if (!response.ok) return null;
            const result = await response.json();
            return result.choices?.[0]?.message?.content || null;
        } catch(e) { return null; }
    }

// ═════════════════// ═══════════════════════════════════
    // PUBLIC API
        async function _callDeepSeek(prompt, systemPrompt, maxTokens) {
        const key = 'sk-e422da39eb9840e387134c823609995e';
        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 30000);
            const response = await fetch('https://api.deepseek.com/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key },
                body: JSON.stringify({
                    model: 'deepseek-chat',
                    messages: [
                        { role: 'system', content: systemPrompt || 'You are a helpful math tutor.' },
                        { role: 'user', content: prompt }
                    ],
                    max_tokens: maxTokens || 200
                }),
                signal: controller.signal
            });
            clearTimeout(timeout);
            if (!response.ok) return null;
            const result = await response.json();
            return result.choices?.[0]?.message?.content || null;
        } catch(e) { return null; }
    }

// ═════════════════// ═══════════════════════════════════
    
    return {
        /** Check API server health */
        async health() {
            // First try local, then Render
            try {
                const r = await fetch('http://localhost:5000/health', { signal: AbortSignal.timeout(3000) });
                const j = await r.json();
                return j.status === 'ok' ? 'local' : 'remote';
            } catch {
                try {
                    const r = await fetch(BASE_URL + '/health', { signal: AbortSignal.timeout(5000) });
                    const j = await r.json();
                    return j.status === 'ok' ? 'remote' : 'offline';
                } catch {
                    return 'offline';
                }
            }
        },
        
        /** AI 語意批改 */
        async mark(studentAnswer, modelAnswer, question, maxScore = 5) {
            // DeepSeek first
            try {
                const r = await _callDeepSeek(`題目: ${question}\n標準答案: ${modelAnswer}\n學生答案: ${studentAnswer}\n滿分: ${maxScore}\n\n只回傳JSON: {"status":"CORRECT|PARTIAL|WRONG","confidence":0.0-1.0,"score":分數,"reason":"用廣東話解釋"}`, '你是香港小學數學老師，只輸出JSON。', 200);
                if (r) { try { return JSON.parse(r); } catch(e) {} }
            } catch(e) {}
            // Fallback: Flask
            const r2 = await _call('/api/mark', { student_answer: studentAnswer, model_answer: modelAnswer, question: question, max_score: maxScore }, { noCache: true });
            return r2?.result || { status: 'UNCERTAIN', confidence: 0, reason: '無法自動評分' };
        },
        },
        
        /** AI 蘇格拉底提示 */
        async hints(question, modelAnswer = '') {
            // DeepSeek first
            try {
                const r = await _callDeepSeek(`題目: ${question}\n答案: ${modelAnswer}\n\n生成3個由淺入深的提示引導學生(繁體中文)，不直接給答案。`, '你是香港數學補習老師，用蘇格拉底提問法。', 300);
                if (r) {
                    const hints = r.split('\n').filter(h => h.trim().length > 5).slice(0, 3);
                    return hints.length > 0 ? hints : ['請嘗試思考這道題目涉及什麼概念。'];
                }
            } catch(e) {}
            // Fallback: Flask
            const r2 = await _call('/api/hints', { question, model_answer: modelAnswer });
            return r2?.hints || ['請嘗試思考這道題目涉及什麼概念。'];
        },
        },
        
        /** AI 學生分析 */
        async analyze(studentName, progressData = []) {
            const r = await _call('/api/analyze', {
                student_name: studentName,
                progress_data: progressData
            });
            if (r?.analysis) return r.analysis;
            return { weak_concepts: [], strength_concepts: [], learning_style: '待分析', next_best_action: '繼續練習' };
        },
        
        /** AI 家長日報 */
        async report(studentName, todayData = {}) {
            try {
                const r = await _callDeepSeek(`學生: ${studentName}\n今日數據: ${JSON.stringify(todayData)}\n\n用廣東話寫一段簡短溫暖的家長日報(100字內)，包含進度、亮點和建議。`, '你是補習班老師，語氣親切。', 300);
                if (r) return r;
            } catch(e) {}
            const r2 = await _call('/api/report', { student_name: studentName, today_data: todayData });
            return r2?.summary || `${studentName} 今天努力學習了！繼續保持。`;
        },
        },
        
        /** AI 錯誤模式分析 */
        async misconceptions(studentName, errors = []) {
            const r = await _call('/api/misconceptions', {
                student_name: studentName,
                errors: errors
            }, { noCache: true });
            if (r?.result) return r.result;
            return { patterns: [], root_cause: '分析暫時不可用', fix_suggestions: ['回顧錯題涉及的基礎概念'] };
        },
        
        /** AI 智能出題 */
        async generate(topic, difficulty = 3) {
            try {
                const r = await _callDeepSeek(`生成一道香港小學${topic}題目，難度${difficulty}/5。包含題目、答案和陷阱說明。只用JSON格式: {"question":"題目","answer":"答案","trap":"陷阱說明"}`, '你是香港數學出題專家，只輸出JSON。', 300);
                if (r) { try { return JSON.parse(r); } catch(e) {} }
            } catch(e) {}
            const r2 = await _call('/api/generate', { topic, difficulty });
            return r2?.question || { question: `請練習 ${topic} 相關題目`, answer: '請參考筆記', difficulty, topic };
        },
            return { question: `請練習 ${topic} 相關題目`, answer: '請參考筆記', difficulty, topic, marks: 3 };
        },
        
        /** 批量提示（課堂副駕駛） */
        async batchHints(questions = []) {
            const r = await _call('/api/batch-hints', { questions });
            return r?.results || [];
        },
        
        /** 清除快取 */
        clearCache() {
            _cache.clear();
            console.log('[LF-API] 🧹 Cache cleared');
        }
    };
})();

console.log('[LF-API] 🍁 LF AI API Client v1.0 loaded');
console.log('[LF-API] 📡 API server:', window.location.hostname === 'localhost' ? 'http://localhost:5000' : 'http://localhost:3001');
