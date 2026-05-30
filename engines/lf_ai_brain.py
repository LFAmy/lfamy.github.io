#!/usr/bin/env python3
"""
LF AI Brain Core v1.0 — frellmapi 驅動的 AI 引擎中樞
為所有 LF Academy 引擎提供統一 AI 接口
特點: 多模型、快取、fallback、成本 $0
"""
import json
import urllib.request
import urllib.error
import time
import sys
import io
from pathlib import Path
from functools import lru_cache
from datetime import datetime, timedelta

try:
    if not isinstance(sys.stdout, io.TextIOWrapper) and hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

FRELLMAPI_KEY = "sk-e422da39eb9840e387134c823609995e"
FRELLMAPI_URL = "http://localhost:3001/v1"
TIMEOUT = 30
CACHE_TTL = 3600  # 1 hour

# 模型角色分配 (99 models, $0)

_system_prompts = {
    "math_checker": 'You are a math grading expert. Compare student answer with model answer. Return JSON: {"status": "CORRECT|PARTIAL|WRONG", "confidence": 0.0-1.0, "reason": "short reason"}. Only JSON.',
    "tutor_socratic": 'You are a math tutor. Ask ONE guiding question to help the student discover the answer. Do NOT give the answer. Chinese.',
    "analyst_deep": 'You are an education analyst. Analyze student data. Return JSON.',
    "creative_gen": 'You are a math question creator. Generate HK DSE format questions. Return JSON. Chinese.',
    "fast_summary": 'You generate parent reports. Summarize student progress. Chinese, under 100 chars.',
    "nvidia_nim": 'You are an AI assistant running on NVIDIA NIM. Be concise and accurate.',
    "cloudflare_ai": 'You are an AI assistant running on Cloudflare Workers AI. Be helpful.',
}

MODEL_ROLES = {
    # Tier 1: NVIDIA NIM (fastest free tier)
    "math_checker": "nvidia/nemotron-3-super-120b-a12b:free",
    "tutor_socratic": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "analyst_deep": "nvidia/nemotron-3-super-120b-a12b:free",
    # Tier 2: Cloudflare Workers AI
    "creative_gen": "@cf/qwen/qwen3-30b-a3b-fp8",
    "fast_summary": "@cf/meta/llama-4-scout-17b-16e-instruct",
    # Tier 3: DeepSeek (main brain, fallback)
    "ensemble_backup": "deepseek-ai/deepseek-v4-pro",
}
# Fallback chain per role (NIM -> CF -> DeepSeek -> auto)
FALLBACK_CHAIN = {
    "math_checker": [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
        "deepseek-ai/deepseek-v4-pro",
        "auto"
    ],
    "tutor_socratic": [
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "@cf/moonshotai/kimi-k2.6",
        "deepseek-ai/deepseek-v4-pro",
        "auto"
    ],
    "analyst_deep": [
        "nvidia/nemotron-3-super-120b-a12b:free",
        "deepseek-ai/deepseek-v4-pro",
        "auto"
    ],
    "creative_gen": [
        "@cf/qwen/qwen3-30b-a3b-fp8",
        "qwen/qwen3-coder:free",
        "auto"
    ],
    "fast_summary": [
        "@cf/meta/llama-4-scout-17b-16e-instruct",
        "@cf/google/gemma-4-26b-a4b-it",
        "mistralai/mistral-large-3-675b-instruct-2512",
        "auto"
    ],
}

_cache = {}
_cache_timestamps = {}


# === OllamaFreeAPI Provider (free public Ollama servers — slow but free) ===
_OLLAMA_API = None
_OLLAMA_AVAILABLE = False
try:
    from ollamafreeapi import OllamaFreeAPI
    _OLLAMA_API = OllamaFreeAPI()
    _OLLAMA_MODELS = {
        "math_checker": ["deepseek-r1:latest", "llama3:latest", "llama3.2:3b"],
        "tutor_socratic": ["llama3:latest", "mistral:latest", "llama3.2:3b"],
        "analyst_deep": ["deepseek-r1:latest", "llama3:latest"],
        "creative_gen": ["llama3:latest", "mistral:latest"],
        "fast_summary": ["llama3.2:3b", "smollm2:135m"],
    }
    _OLLAMA_AVAILABLE = True
    print("[AI Brain] OllamaFreeAPI loaded: 16 models, 3 families", file=sys.stderr)
except Exception as e:
    print(f"[AI Brain] OllamaFreeAPI not available: {e}", file=sys.stderr)

def _call_ollamafree(prompt: str, role: str = "math_checker", max_tokens: int = 200, timeout: int = 12) -> str:
    """Call ollamafreeapi public servers — slower but free, no rate limit"""
    if not _OLLAMA_AVAILABLE:
        return ""
    
    model_list = _OLLAMA_MODELS.get(role, ["llama3.2:3b"])
    
    for model in model_list:
        try:
            system_prompt = _system_prompts.get(role, "")
            sep = chr(10) + chr(10)
            full_prompt = system_prompt + sep + "User: " + prompt if system_prompt else prompt
            
            import threading as _th, queue as _q
            q = _q.Queue()
            def _do():
                try:
                    resp = _OLLAMA_API.chat(full_prompt, model=model)
                    q.put(resp)
                except Exception as e:
                    q.put(e)
            
            t = _th.Thread(target=_do, daemon=True)
            t.start()
            t.join(timeout=timeout)
            
            if t.is_alive():
                continue  # try next model
            
            result = q.get_nowait()
            if isinstance(result, Exception):
                continue
            
            return str(result).strip()[:max_tokens * 4]  # rough char limit
        except:
            continue
    
    return ""  # all models failed


def _call_frellmapi(prompt: str, role: str = "math_checker", max_tokens: int = 500, model_override: str = None) -> str:
    """呼叫 frellmapi — 自動模型選擇 + fallback"""
    model = model_override if model_override else MODEL_ROLES.get(role, MODEL_ROLES["math_checker"])
    
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": get_system_prompt(role)},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.1 if "check" in role or "analyst" in role else 0.7
    }).encode("utf-8")
    
    req = urllib.request.Request(
        f"{FRELLMAPI_URL}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {FRELLMAPI_KEY}",
            "Content-Type": "application/json"
        }
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        result = json.loads(resp.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[AI Brain] frellmapi {role} failed: {e}", file=sys.stderr)
        # Fallback to ensemble model
        try:
            body_dict = json.loads(body.decode("utf-8"))
            body_dict["model"] = MODEL_ROLES["ensemble_backup"]
            req2 = urllib.request.Request(
                f"{FRELLMAPI_URL}/chat/completions",
                data=json.dumps(body_dict).encode("utf-8"),
                headers={"Authorization": f"Bearer {FRELLMAPI_KEY}", "Content-Type": "application/json"}
            )
            resp2 = urllib.request.urlopen(req2, timeout=TIMEOUT)
            result2 = json.loads(resp2.read().decode("utf-8"))
            return result2["choices"][0]["message"]["content"].strip()
        except Exception as e2:
            print(f"[AI Brain] Fallback also failed: {e2}", file=sys.stderr)
            return ""

def get_system_prompt(role: str) -> str:
    prompts = {
        "math_checker": """你是香港數學批改專家。比較學生答案與標準答案。
答案格式嚴格為JSON: {"status": "CORRECT|PARTIAL|WRONG", "confidence": 0.0-1.0, "reason": "簡短原因"}
- CORRECT: 學生答案在數學上完全等價
- PARTIAL: 方法正確但有小錯誤
- WRONG: 答案明顯錯誤
注意: x=3 與 3 在代數意義上等價。只回傳JSON，不要其他文字。""",
        
        "tutor_socratic": """你是香港數學導師，用蘇格拉底式提問引導學生自己發現答案。
絕對不直接給答案。每次回覆只問一個引導性問題。
根據題目和學生目前進度，提出下一個引導問題。
用繁體中文。只回傳問題本身，不附加解釋。""",
        
        "analyst_deep": """你是教育數據分析師。分析學生答題歷史，找出深層學習模式。
回傳JSON: {"weak_concepts": [...], "strength_concepts": [...], "learning_style": "...", "next_best_action": "..."}
用繁體中文描述概念名稱。""",
        
        "creative_gen": """你是香港數學出題專家。根據指定主題和難度生成新題目。
回傳JSON: {"question": "題目文字", "answer": "標準答案", "difficulty": 1-5, "topic": "主題", "marks": 分數}
題目須符合香港DSE/校內考試格式。用繁體中文。""",
        
        "fast_summary": """你是教育報告生成器。根據學生數據生成簡潔的家長摘要。
用繁體中文，100字以內，溫暖專業的語氣。包含：今日進度、強項、建議。""",
    }
    return prompts.get(role, prompts["math_checker"])


def _quick_call(prompt: str, role: str = "math_checker", max_tokens: int = 300, timeout: int = 10) -> str:
    """Fast frellmapi call with short timeout — returns '' on any failure"""
    try:
        import threading, queue
        q = queue.Queue()
        def _do():
            try:
                q.put(_call_frellmapi(prompt, role, max_tokens))
            except:
                q.put("")
        t = threading.Thread(target=_do, daemon=True)
        t.start()
        t.join(timeout=timeout)
        if t.is_alive():
            return ""
        return q.get_nowait() if not q.empty() else ""
    except:
        return ""



import threading, time as _time, queue as _queue
from collections import OrderedDict

# === Rate Limit Protection ===
_MIN_REQUEST_INTERVAL = 2.0  # 最少間隔2秒
_last_request_time = 0.0
_request_lock = threading.Lock()

def _rate_limit_wait():
    """Ensure minimum interval between API calls"""
    global _last_request_time
    with _request_lock:
        elapsed = _time.time() - _last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            _time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
        _last_request_time = _time.time()

# === Smart Cache (LRU, TTL-aware) ===
_cache = OrderedDict()
_cache_max = 200

def _cached_call(prompt: str, role: str = "math_checker", max_tokens: int = 300, ttl: int = 1800) -> str:
    """Cached frellmapi call with rate limiting, retry, and fallback"""
    cache_key = f"{role}:{hash(prompt)}:{max_tokens}"
    now = _time.time()
    
    # Check cache
    if cache_key in _cache:
        entry = _cache[cache_key]
        if now - entry["ts"] < ttl:
            _cache.move_to_end(cache_key)
            return entry["val"]
        del _cache[cache_key]
    
    _rate_limit_wait()
    
    # Use provider rotation for load balancing
    global _rotation_index
    models_to_try = [MODEL_ROLES.get(role, "auto")] + PROVIDER_ROTATION
    # Rotate starting point
    start_idx = _rotation_index % len(models_to_try)
    _rotation_index += 1
    rotated = models_to_try[start_idx:] + models_to_try[:start_idx]
    
    # Try frellmapi with rotated providers
    for attempt, model in enumerate(rotated[:5]):  # max 5 attempts  # reduced from 3 to save time
        try:
            result = _call_frellmapi(prompt, role, max_tokens, model_override=model)
            if result and "rate" not in result.lower() and "limit" not in result.lower():
                if len(_cache) >= _cache_max:
                    _cache.popitem(last=False)
                _cache[cache_key] = {"val": result, "ts": now}
                return result
        except Exception as e:
            err = str(e)
            if "429" in err or "rate" in err.lower() or "401" in err:
                break  # don't retry auth/rate errors, go to fallback
            elif attempt < 1:
                _time.sleep(1)
    
    # Fallback 1: OllamaFreeAPI (free public servers)
    if _OLLAMA_AVAILABLE:
        print(f"[AI Brain] frellmapi failed, trying OllamaFreeAPI...", file=sys.stderr)
        ollama_result = _call_ollamafree(prompt, role, max_tokens)
        if ollama_result and len(ollama_result) > 5:
            if len(_cache) >= _cache_max:
                _cache.popitem(last=False)
            _cache[cache_key] = {"val": ollama_result, "ts": now}
            return ollama_result
    
    # All providers exhausted
    return ""



# ═══════ DeepSeek Direct API (primary AI backend) ═══════
DEEPSEEK_API_KEY = "sk-e422da39eb9840e387134c823609995e"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def _call_deepseek(prompt, system_prompt="", max_tokens=200, timeout=15):
    """Call DeepSeek API directly — primary AI backend"""
    import urllib.request, json
    
    payload = {
        "model": "deepseek-chat",
        "messages": [],
        "max_tokens": max_tokens
    }
    if system_prompt:
        payload["messages"].append({"role": "system", "content": system_prompt})
    payload["messages"].append({"role": "user", "content": prompt})
    
    try:
        req = urllib.request.Request(
            DEEPSEEK_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[DeepSeek] Error: {e}", file=sys.stderr)
        return None

def ai_semantic_mark(student_answer: str, model_answer: str, question_text: str = "", max_marks: int = 5, student_history: dict = None) -> dict:
    """AI 語意批改 — 優先使用 DeepSeek"""
    prompt = f"""題目: {question_text}
標準答案: {model_answer}
學生答案: {student_answer}
滿分: {max_marks}

請評估學生答案。回傳JSON（不要其他文字）:
{{"status": "CORRECT|PARTIAL|WRONG", "confidence": 0.0-1.0, "score": 分數, "reason": "用廣東話寫原因, 指出的陷阱"}}"""
    
    # Try DeepSeek first
    try:
        result = _call_deepseek(prompt, "你是香港小學數學老師，擅長分析學生錯誤。只回傳JSON。", 200, 15)
        if result:
            try:
                return json.loads(result)
            except:
                pass
    except:
        pass
    
    # Fallback — exact match
    if student_answer.strip() == model_answer.strip():
        return {"status": "CORRECT", "confidence": 0.9, "score": max_marks, "reason": "答案完全正確。"}
    
    # Try frellmapi
    try:
        raw = _cached_call(prompt, role="math_checker", max_tokens=300)
        if raw:
            return json.loads(raw)
    except:
        pass
    return {"status": "UNCERTAIN", "confidence": 0.3, "score": 0, "reason": "無法自動評分，請老師人工檢查。"}
def ai_generate_hints(question: str, model_answer: str = "", student_history: dict = None) -> list:
    """AI 蘇格拉底式提示 — 優先使用 DeepSeek"""
    prompt = f"""題目: {question}
答案: {model_answer}

學生需要引導性提示來解決這道題。生成 3 個由淺入深的提示（繁體中文），用蘇格拉底式提問引導，不直接給答案。"""
    
    # Try DeepSeek first
    try:
        result = _call_deepseek(prompt, "你是香港數學補習老師，擅長用蘇格拉底提問法引導學生。", 300, 15)
        if result:
            hints = [h.strip() for h in result.replace('\n\n', '\n').split('\n') if h.strip()]
            if hints:
                return hints[:3]
    except:
        pass
    
    # Fallback
    try:
        raw = _cached_call(prompt, role="tutor_socratic", max_tokens=300)
        if raw:
            result = json.loads(raw)
            return result.get("hints", ["請嘗試思考這道題目涉及什麼概念。"])
    except:
        pass
    return ["請嘗試思考這道題目涉及什麼概念。"]
def ai_analyze_student(student_name: str, progress_data: list) -> dict:
    """AI 深度分析學生認知模型"""
    if not progress_data:
        return {"weak_concepts": [], "strength_concepts": [], "learning_style": "未知", "next_best_action": "開始練習"}
    
    summary = "\n".join([
        f"- 主題: {p.get('topic','?')}, 分數: {p.get('score',0)}/{p.get('max_score',5)}, 狀態: {p.get('status','?')}"
        for p in progress_data[-30:]  # last 30
    ])
    
    prompt = f"""學生: {student_name}
最近30題記錄:
{summary}

分析此學生的學習模式，找出：最弱概念、最強概念、學習風格、最佳下一步行動。
回傳JSON。"""
    
    try:
        raw = _cached_call(prompt, role="analyst_deep", max_tokens=400)
        if not raw:
            raise Exception("cached empty")
        return json.loads(raw)
    except:
        return {"weak_concepts": ["需要更多數據"], "strength_concepts": [], "learning_style": "待分析", "next_best_action": "繼續練習"}

def ai_daily_summary(student_name: str, today_total=0, today_correct=0, weak_areas=None) -> str:
    # Support both old (student_name, today_data) and new (student_name, total, correct, weak_areas) signatures
    if isinstance(today_total, dict):
        today_data = today_total
    else:
        today_data = {"total": today_total, "correct": today_correct, "weak_areas": weak_areas or []}
    """AI 生成家長日報"""
    prompt = f"""學生: {student_name}
今日數據: {json.dumps(today_data, ensure_ascii=False)}

生成一段簡潔溫暖的家長摘要（繁體中文，100字內）。包含：今日進度、表現亮點、溫和建議。"""
    
    try:
        raw = _cached_call(prompt, role="fast_summary", max_tokens=200)
        return raw if raw else f"{student_name} 今天努力學習了！繼續保持。"
    except:
        return f"{student_name} 今天努力學習了！繼續保持。"

def ai_detect_misconceptions(student_name: str, errors: list) -> dict:
    """AI 深度錯誤模式分析"""
    if not errors:
        return {"patterns": [], "root_cause": "無錯誤記錄", "fix_suggestions": []}
    
    error_text = "\n".join([
        f"主題: {e.get('topic','?')}, 題目: {e.get('question','')[:100]}, 正確答案: {e.get('correct_answer','')}"
        for e in errors[:10]
    ])
    
    prompt = f"""分析以下學生的錯誤模式，找出根本原因和修正建議：
{error_text}

回傳JSON: {{"patterns": ["錯誤模式1",...], "root_cause": "根本原因", "fix_suggestions": ["建議1",...]}}"""
    
    try:
        raw = _cached_call(prompt, role="analyst_deep", max_tokens=400)
        if not raw:
            raise Exception("cached empty")
        return json.loads(raw)
    except:
        return {"patterns": [], "root_cause": "分析暫時不可用", "fix_suggestions": ["回顧錯題涉及的基礎概念"]}

def ai_generate_question(topic: str, difficulty: int = 3, avoid_ids: list = None, student_history: dict = None) -> dict:
    """AI 智能出題 — 根據主題和難度生成全新題目"""
    prompt = f"""生成一道香港中學數學題目：
主題: {topic}
難度: {difficulty}/5
格式: 香港DSE/校內考試格式

回傳JSON: {{"question": "題目", "answer": "答案", "difficulty": {difficulty}, "topic": "{topic}", "marks": 分數}}"""
    
    try:
        raw = _cached_call(prompt, role="creative_gen", max_tokens=500, ttl=7200)
        if not raw:
            raise Exception("cached empty")
        return json.loads(raw)
    except:
        return {"question": f"請練習 {topic} 相關題目", "answer": "請參考筆記", "difficulty": difficulty, "topic": topic, "marks": 3}

def check_health() -> dict:
    """健康檢查"""
    try:
        req = urllib.request.Request(
            f"{FRELLMAPI_URL}/models",
            headers={"Authorization": f"Bearer {FRELLMAPI_KEY}"}
        )
        urllib.request.urlopen(req, timeout=5)
        return {"frellmapi": "online", "models_available": 99, "cost": "$0"}
    except:
        return {"frellmapi": "offline", "fallback": "rule_based"}

if __name__ == "__main__":
    print("=" * 50)
    print("🧠 LF AI Brain Core v1.0 — 健康檢查")
    print("=" * 50)
    health = check_health()
    for k, v in health.items():
        print(f"  {k}: {v}")
    
    # Quick test
    print("\n📝 語意批改測試:")
    result = ai_semantic_mark("x=3", "3", "Solve for x: 2x+1=7", 5)
    print(f"  'x=3' vs '3' → {result}")
    
    print("\n💡 提示生成測試:")
    hints = ai_generate_hints("解方程: 2x + 5 = 13", "x = 4")
    for i, h in enumerate(hints):
        print(f"  L{i+1}: {h}")
    
    print("\n✅ LF AI Brain Core 就緒")

# ═══ Tutor Chat (Free Ask) ═══
def ai_tutor_chat(message: str, conversation_history: str = "", mode: str = "math_tutor") -> str:
    """Free-form Socratic math tutor chat with conversation context."""
    system = '''你是霖楓學苑的 AI 數學導師。以蘇格拉底式對話引導學生思考，不要直接給答案。
規則：
1. 每次只問一個引導性問題
2. 如果學生答對，給予正面鼓勵再問下一步
3. 如果學生答錯，不要說「錯」，說「讓我們再想想」
4. 用學生年級適合的語言（香港小學 P3-P6）
5. 全程使用繁體中文
6. 如果學生明顯困惑，給一個小提示而不是答案'''
    
    context_block = ""
    if conversation_history:
        context_block = f"\n\n對話歷史：\n{conversation_history}\n\n請根據以上對話歷史繼續引導。"
    
    full_prompt = f"{system}{context_block}\n\n學生說：{message}\n\n你的引導回應："
    
    try:
        return _call_frellmapi(full_prompt, "tutor_socratic", max_tokens=400)
    except:
        return "讓我幫你一起思考這道題目。你可以先告訴我，題目中給了哪些已知條件？"


def ai_tutor_solve(question: str) -> str:
    """Generate a step-by-step solution for a math problem."""
    prompt = f'''你是香港小學數學老師。請逐步解答以下題目，每一步都要清楚解釋。

題目：{question}

請按以下格式回答：
第1步：[步驟說明]
第2步：[步驟說明]
...
最終答案：[答案]

使用繁體中文。適合小學 P3-P6 學生理解。'''

    try:
        return _call_frellmapi(prompt, "math_checker", max_tokens=600)
    except:
        # Rule-based fallback
        import re
        numbers = re.findall(r'\d+', question)
        if numbers:
            return f"這道題目的關鍵數字是：{', '.join(numbers[:5])}。請嘗試自己逐步推理，找出它們之間的關係。"
        return "請嘗試從題目中找出已知條件，一步一步推理。"