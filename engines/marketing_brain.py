#!/usr/bin/env python3
"""
LF Marketing Brain v2.0 — Unified AI Marketing Orchestrator
===========================================================
Cross-platform intelligence for FB + IG + XHS (小紅書)
Architecture:
  Input: 172 講義 → Academic Calendar → Parent Psychology → Platform Adapter → AI Gen → Quality Gate → Publish
  MAB: Thompson Sampling content optimization across platforms
  Closed-loop: Generate → Publish → Recycle Analytics → Optimize → Repeat

用法:
  python engines/marketing_brain.py --scan             掃描所有平台狀態
  python engines/marketing_brain.py --generate week    生成一週跨平台內容
  python engines/marketing_brain.py --platform all     指定平台 (fb|ig|xhs|all)
  python engines/marketing_brain.py --dashboard         輸出儀表板數據
  python engines/marketing_brain.py --optimize          基於 MAB 優化內容策略
"""

import sys, os, io, json, hashlib, random, re, time, copy
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Set

# === SECRETS loaded from .env via _config/secrets.py ===
import os as _os, sys as _sys
_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))) if "__file__" in dir() else _os.path.dirname(_os.path.abspath("."))
for _p in [_root, _os.path.join(_root, "_config")]:
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
try:
    from _config.secrets import FRELLMAPI_KEY, FRELLMAPI_URL, DEEPSEEK_KEY, DEEPSEEK_URL
except ImportError:
    FRELLMAPI_KEY = _os.environ.get("FRELLMAPI_KEY", "")
    FRELLMAPI_URL = _os.environ.get("FRELLMAPI_URL", "http://localhost:3001")
    DEEPSEEK_KEY = _os.environ.get("DEEPSEEK_KEY", "")
    DEEPSEEK_URL = _os.environ.get("DEEPSEEK_URL", "https://api.deepseek.com/chat/completions")
# === END SECRETS ===


if not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = Path(r'G:\lam-fung-academy')
SOCIAL_DIR = BASE / 'docs' / 'social'
SOCIAL_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# PLATFORM CONFIGURATIONS
# ═══════════════════════════════════════════════════════════

PLATFORMS = {
    'fb': {
        'name': 'Facebook',
        'color': '#1877F2',
        'icon': '📘',
        'tone': '溫暖專業、有深度、適合長文',
        'audience': '香港家長 (30-50歲)',
        'content_length': 'long',       # 200-400 words
        'best_times': ['07:30', '12:00', '20:00'],
        'best_days': [0, 1, 2, 3, 4],  # Mon-Fri
        'post_freq': 1,                  # posts/day
        'hashtag_style': 'few_targeted', # 2-3 targeted hashtags
        'image_ratio': '1.91:1',         # 1200x630
        'content_mix': {
            'education': 0.25, 'social_proof': 0.20, 'engagement': 0.15,
            'urgency': 0.15, 'personality': 0.10, 'differentiation': 0.10, 'reels': 0.05,
        },
    },
    'ig': {
        'name': 'Instagram',
        'color': '#E4405F',
        'icon': '📸',
        'tone': '視覺化、簡潔有力、年輕媽媽風',
        'audience': '年輕家長 (25-40歲)',
        'content_length': 'short',       # 80-150 words
        'best_times': ['12:00', '18:00', '21:00'],
        'best_days': [0, 2, 4, 5],       # Mon, Wed, Fri, Sat
        'post_freq': 1,                   # posts/day
        'hashtag_style': 'many_branded',  # 5-10 hashtags
        'image_ratio': '1:1',             # 1080x1080
        'content_mix': {
            'reels': 0.30, 'education': 0.20, 'social_proof': 0.15,
            'engagement': 0.15, 'personality': 0.10, 'urgency': 0.05, 'differentiation': 0.05,
        },
    },
    'xhs': {
        'name': '小紅書',
        'color': '#FF2442',
        'icon': '📕',
        'tone': '真實分享、香港媽媽社群、實用攻略風',
        'audience': '香港+內地媽媽 (25-45歲)',
        'content_length': 'medium',      # 150-250 words
        'best_times': ['12:00', '17:00', '20:00', '22:00'],
        'best_days': [0, 2, 4, 6],       # Sun, Tue, Thu, Sat
        'post_freq': 1,                   # posts/day
        'hashtag_style': 'many_localized',# 5-8 localized hashtags
        'image_ratio': '3:4',            # 1080x1440
        'content_mix': {
            'education': 0.20, 'social_proof': 0.20, 'engagement': 0.15,
            'personality': 0.15, 'urgency': 0.10, 'reels': 0.10, 'differentiation': 0.10,
        },
    },
}

# ═══════════════════════════════════════════════════════════
# 7-LAYER CONTENT STRATEGY (upgraded from social_engine.py)
# ═══════════════════════════════════════════════════════════

LAYERS = {
    'education': {
        'goal': '建立專業權威',
        'weight': 25,
        'psychology': ['P1_焦慮', 'P4_困惑', 'S2_重複犯錯'],
        'journey_stages': [1, 2],
        'best_platforms': ['fb', 'xhs'],
        'ttl_days': 90,
        'icon': '📚',
        'description': '教育乾貨、陷阱解密、解題秘訣',
    },
    'social_proof': {
        'goal': '建立信任',
        'weight': 20,
        'psychology': ['P5_希望', 'P3_挫敗', 'P6_比較'],
        'journey_stages': [3, 4],
        'best_platforms': ['fb', 'ig', 'xhs'],
        'ttl_days': 60,
        'icon': '⭐',
        'description': '真實案例、家長見證、成績進步故事',
    },
    'engagement': {
        'goal': '增加互動',
        'weight': 15,
        'psychology': ['P1_焦慮', 'P4_困惑'],
        'journey_stages': [1, 2, 3],
        'best_platforms': ['fb', 'ig'],
        'ttl_days': 45,
        'icon': '🎯',
        'description': '投票、測驗、問答互動',
    },
    'urgency': {
        'goal': '驅動行動',
        'weight': 15,
        'psychology': ['P7_時間壓力', 'P1_焦慮'],
        'journey_stages': [5],
        'best_platforms': ['fb', 'xhs'],
        'ttl_days': 30,
        'icon': '⏰',
        'description': 'SSPA倒數、暑期規劃、限時優惠',
    },
    'personality': {
        'goal': '建立情感連結',
        'weight': 10,
        'psychology': ['P2_內疚', 'P5_希望', 'S1_自信崩塌'],
        'journey_stages': [1, 2, 3],
        'best_platforms': ['fb', 'ig'],
        'ttl_days': 120,
        'icon': '💬',
        'description': '創辦人故事、幕後花絮、教育理念',
    },
    'reels': {
        'goal': '觸及新受眾',
        'weight': 10,
        'psychology': ['P1_焦慮', 'S3_沉悶'],
        'journey_stages': [1],
        'best_platforms': ['ig', 'xhs'],
        'ttl_days': 60,
        'icon': '🎬',
        'description': '短影片腳本、15秒解題、動畫教學',
    },
    'differentiation': {
        'goal': '差異化定位',
        'weight': 5,
        'psychology': ['P3_挫敗', 'P5_希望'],
        'journey_stages': [3, 4],
        'best_platforms': ['fb', 'xhs'],
        'ttl_days': 90,
        'icon': '⚡',
        'description': '霖楓 vs 一般補習、陷阱診斷 vs 傳統操卷',
    },
}

# ═══════════════════════════════════════════════════════════
# ACADEMIC CALENDAR (seasons drive content focus)
# ═══════════════════════════════════════════════════════════

ACADEMIC_CALENDAR = {
    1:  {'phase': '上學期尾/考試',     'mood': '考試壓力',    'focus': ['考試技巧', '最後重溫', '陷阱速攻'], 'urgency': 8},
    2:  {'phase': '農曆新年/下學期開學', 'mood': '新年新希望',  'focus': ['新年目標', '學習習慣', 'SSPA倒數'], 'urgency': 7},
    3:  {'phase': '下學期測驗',         'mood': '測驗壓力',    'focus': ['TSA準備', '呈分試策略'],          'urgency': 8},
    4:  {'phase': '復活節/期中考',      'mood': '喘息+準備',   'focus': ['假期溫習', '呈分試模擬'],          'urgency': 9},
    5:  {'phase': '呈分試/SSPA',        'mood': '終極壓力',    'focus': ['呈分試', 'SSPA衝刺', '最後提示'], 'urgency': 10},
    6:  {'phase': '考試後/暑假前',      'mood': '解脫+規劃',   'focus': ['暑假規劃', 'Summer Slide'],        'urgency': 7},
    7:  {'phase': '暑假',              'mood': '放鬆',        'focus': ['暑期活動', '升班準備', '鞏固基礎'], 'urgency': 6},
    8:  {'phase': '暑假尾/開學準備',    'mood': '開學焦慮',    'focus': ['開學準備', '升班銜接', '診斷測試'], 'urgency': 8},
    9:  {'phase': '新學年開始',         'mood': '新鮮感',      'focus': ['學習規劃', '診斷測試', '習慣建立'], 'urgency': 7},
    10: {'phase': '上學期中期',         'mood': '穩定進步',    'focus': ['測驗技巧', '弱點發現'],             'urgency': 6},
    11: {'phase': '上學期考試',         'mood': '壓力上升',    'focus': ['考試策略', '錯題分析'],             'urgency': 7},
    12: {'phase': '聖誕/學期尾',        'mood': '節日+考試',   'focus': ['聖誕溫習', '學期總結', '來年規劃'], 'urgency': 6},
}

# ═══════════════════════════════════════════════════════════
# PARENT PSYCHOLOGY FRAMEWORK
# ═══════════════════════════════════════════════════════════

PSYCHOLOGY_TRIGGERS = {
    'P1_焦慮':     {'hook': '你小朋友準備好未？', 'angle': '時間緊迫，唔可以再等'},
    'P2_內疚':     {'hook': '在職父母嘅救星',     'angle': '唔使你自己教，我哋幫你'},
    'P3_挫敗':     {'hook': '試過N間都冇用？',    'angle': '唔係你嘅錯，係方法問題'},
    'P4_困惑':     {'hook': '呢題你識唔識？',     'angle': '連家長都唔知點教'},
    'P5_希望':     {'hook': '其實佢可以做到',     'angle': '我哋見過最極限嘅進步'},
    'P6_比較':     {'hook': '人哋小朋友進步緊',   'angle': '你小朋友都可以'},
    'P7_時間壓力': {'hook': '剩低 X 日',          'angle': '每一日都影響緊派位'},
    'S1_自信崩塌': {'hook': '我數學好渣',         'angle': '唔係你蠢，係你中咗陷阱'},
    'S2_重複犯錯': {'hook': '又錯同一樣嘢',       'angle': '呢個係系統性陷阱，唔係粗心'},
    'S3_沉悶':     {'hook': '操卷操到悶',         'angle': '用遊戲化方法學數學'},
    'S6_需要小贏': {'hook': '你做得到！',         'angle': '每個小成功都值得慶祝'},
}

# ═══════════════════════════════════════════════════════════
# CONTENT FINGERPRINT DEDUP
# ═══════════════════════════════════════════════════════════

class ContentFingerprinter:
    """Cross-platform content deduplication with LRU cache."""

    def __init__(self, db_path=None):
        self.db_path = db_path or (SOCIAL_DIR / '.content_fingerprints.json')
        self.fingerprints: Set[str] = self._load()
        self.recent = OrderedDict()  # LRU for fast lookup

    def _load(self) -> Set[str]:
        if self.db_path.exists():
            try:
                return set(json.loads(self.db_path.read_text(encoding='utf-8')))
            except Exception:
                return set()
        return set()

    def save(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(json.dumps(list(self.fingerprints)), encoding='utf-8')

    def fingerprint(self, text: str) -> str:
        normalized = ''.join(text.lower().split())[:300]
        return hashlib.sha256(normalized.encode()).hexdigest()[:20]

    def is_duplicate(self, text: str) -> bool:
        fp = self.fingerprint(text)
        if fp in self.fingerprints:
            return True
        if fp in self.recent:
            return True
        self.recent[fp] = True
        if len(self.recent) > 500:
            self.recent.popitem(last=False)
        return False

    def register(self, text: str):
        fp = self.fingerprint(text)
        self.fingerprints.add(fp)
        self.recent[fp] = True
        if len(self.fingerprints) % 50 == 0:
            self.save()

    def count(self) -> int:
        return len(self.fingerprints)


# ═══════════════════════════════════════════════════════════
# MAB CONTENT OPTIMIZER (Thompson Sampling)
# ═══════════════════════════════════════════════════════════

class MABContentOptimizer:
    """Multi-Armed Bandit for content strategy optimization across platforms."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.arms = {}  # {platform_layer: {alpha, beta, trials, rewards}}
        self.prior_alpha = 2.0
        self.prior_beta = 2.0

    def _key(self, platform: str, layer: str) -> str:
        return f"{platform}:{layer}"

    def update(self, platform: str, layer: str, reward: float):
        """Update arm with engagement reward (0-1 scale)."""
        key = self._key(platform, layer)
        if key not in self.arms:
            self.arms[key] = {
                'alpha': self.prior_alpha, 'beta': self.prior_beta,
                'trials': 0, 'total_reward': 0.0,
            }
        arm = self.arms[key]
        arm['trials'] += 1
        arm['total_reward'] += reward
        # Beta update: reward is success probability
        arm['alpha'] += reward
        arm['beta'] += (1.0 - reward)

    def sample(self, platform: str, layer: str) -> float:
        """Thompson sample from Beta distribution."""
        key = self._key(platform, layer)
        if key not in self.arms:
            a, b = self.prior_alpha, self.prior_beta
        else:
            a, b = self.arms[key]['alpha'], self.arms[key]['beta']
        return random.betavariate(max(a, 1.0), max(b, 1.0))

    def get_optimal_mix(self, platform: str, top_n: int = 3) -> List[Dict]:
        """Get top-N best performing content layers for a platform."""
        scores = []
        for layer_key, arm in self.arms.items():
            plat, layer = layer_key.split(':', 1)
            if plat == platform:
                est = arm['alpha'] / (arm['alpha'] + arm['beta']) if (arm['alpha'] + arm['beta']) > 0 else 0.5
                scores.append({
                    'layer': layer,
                    'estimated_ctr': round(est, 3),
                    'trials': arm['trials'],
                    'total_reward': round(arm['total_reward'], 2),
                    'ucb': round(self.sample(platform, layer), 3),
                })
        scores.sort(key=lambda x: x['ucb'], reverse=True)
        return scores[:top_n]

    def get_cross_platform_insights(self) -> Dict:
        """Cross-platform performance comparison."""
        by_platform = defaultdict(list)
        for key, arm in self.arms.items():
            plat, layer = key.split(':', 1)
            est = arm['alpha'] / (arm['alpha'] + arm['beta']) if (arm['alpha'] + arm['beta']) > 0 else 0.5
            by_platform[plat].append({'layer': layer, 'est': est, 'trials': arm['trials']})

        insights = {}
        for plat, arms in by_platform.items():
            if arms:
                avg = sum(a['est'] for a in arms) / len(arms)
                best = max(arms, key=lambda a: a['est'])
                insights[plat] = {
                    'avg_engagement': round(avg, 3),
                    'total_trials': sum(a['trials'] for a in arms),
                    'best_layer': best['layer'],
                    'best_layer_score': round(best['est'], 3),
                }
        return insights

    def to_dict(self) -> Dict:
        return {'arms': self.arms}

    @classmethod
    def from_dict(cls, data: Dict):
        mab = cls()
        mab.arms = data.get('arms', {})
        return mab


# ═══════════════════════════════════════════════════════════
# AI CONTENT GENERATION ENGINE
# ═══════════════════════════════════════════════════════════

class AIContentGenerator:
    """AI-powered content generation via DeepSeek with platform awareness."""

    DEEPSEEK_KEY = DEEPSEEK_KEY
    DEEPSEEK_URL = 'https://api.deepseek.com/chat/completions'

    SYSTEM_PROMPT = """你是霖楓學苑 (LF Academy) 的首席 AI 內容策略師。
背景：香港小學數學補習平台，專注 P3-P6，核心理念是「陷阱診斷教學法」—— 不教數學，教小朋友避開自己的陷阱。

品牌聲音檔案：
- 語調：溫暖專業，香港家長語氣，中英夾雜自然
- 節奏：短句、直接、有重點、情感先行
- 禁止：空泛形容詞、假裝興奮、教育術語堆砌、硬銷
- 特色：用「阿仔」「阿女」「媽咪」「爹哋」等親切稱呼
- 數據：永遠用具體數字而非「很多」「大量」
- CTA：自然引導互動，不做壓力推銷

核心差異化：
- 一般補習 = 亂槍打鳥式操卷
- 霖楓 = 先診斷陷阱指紋 → 針對性操練 → 口訣記憶 → 進度追蹤

請根據以下要求生成內容。"""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.cache = OrderedDict()
        self.cache_max = 50
        self._check_ai()

    def _check_ai(self):
        """Test DeepSeek connectivity."""
        try:
            import urllib.request
            req = urllib.request.Request(
                self.DEEPSEEK_URL,
                data=json.dumps({
                    'model': 'deepseek-v4-flash',
                    'messages': [{'role': 'user', 'content': 'ping'}],
                    'max_tokens': 5,
                }).encode(),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.DEEPSEEK_KEY}',
                },
            )
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception:
            return False

    def generate(self, platform: str, layer: str, topic: str,
                 context: Dict, fingerprint_set: ContentFingerprinter,
                 max_retries: int = 2) -> Dict:
        """Generate a platform-optimized post using AI."""

        plat_cfg = PLATFORMS.get(platform, PLATFORMS['fb'])
        layer_cfg = LAYERS.get(layer, LAYERS['education'])

        # Build prompt with platform-specific instructions
        prompt = self._build_prompt(platform, layer, topic, context, plat_cfg, layer_cfg)

        for attempt in range(max_retries + 1):
            content = self._call_deepseek(prompt)

            if not content:
                return self._fallback_template(platform, layer, topic, context)

            parsed = self._parse_response(content)
            if not parsed.get('body'):
                continue

            # Check duplicate
            if fingerprint_set.is_duplicate(parsed['body']):
                prompt += '\n\n⚠️ 注意：請確保內容同之前完全不同，換一個角度切入。'
                continue

            fingerprint_set.register(parsed['body'])
            parsed['generation_method'] = 'deepseek-ai'
            parsed['platform'] = platform
            parsed['layer'] = layer
            parsed['psychology'] = layer_cfg['psychology']
            return parsed

        return self._fallback_template(platform, layer, topic, context)

    def _build_prompt(self, platform: str, layer: str, topic: str,
                      context: Dict, plat_cfg: Dict, layer_cfg: Dict) -> str:
        """Build a detailed generation prompt."""

        length_map = {'long': '250-350字', 'medium': '150-250字', 'short': '80-150字'}
        hashtag_guide = {
            'few_targeted': '2-3個精準hashtag',
            'many_branded': '5-8個品牌hashtag',
            'many_localized': '5-8個本地化hashtag（混合香港+內地用語）',
        }

        psych = layer_cfg['psychology']
        triggers = [PSYCHOLOGY_TRIGGERS.get(p, {}) for p in psych[:3]]
        trigger_text = '\n'.join([
            f"  - {t.get('hook', '')}: {t.get('angle', '')}" for t in triggers if t
        ])

        return f"""請為 {plat_cfg['name']} 創作一篇 {layer_cfg['icon']} {layer} 類型的貼文。

平台要求：
- 風格：{plat_cfg['tone']}
- 目標受眾：{plat_cfg['audience']}
- 長度：{length_map.get(plat_cfg['content_length'], '150-250字')}
- Hashtag：{hashtag_guide.get(plat_cfg['hashtag_style'], '3-5個')}
- 主題：{topic}

時間背景：
- 月份階段：{context.get('phase', '一般')}
- 氣氛：{context.get('mood', '一般')}
- 距離SSPA：{context.get('days_to_sspa', '?')}日
- 緊急程度：{context.get('urgency', 5)}/10

心理觸發點（請自然融入，不要生硬）：
{trigger_text}

內容層目標：{layer_cfg['goal']}

寫作要求：
1. 從家長真實痛點出發（不是補習社廣告角度）
2. 包含至少一個具體的數學例子或陷阱
3. 用數據/研究支持觀點（如果有）
4. 結尾有自然、不做作的行動召喚
5. 使用香港繁體中文 + 自然廣東話口語
6. 加入指定數量的hashtag

回覆格式（嚴格遵守，不要添加其他文字）：
[TITLE]: 標題（必須吸引點擊）
[BODY]: 內文（符合平台長度要求）
[CTA]: 行動召喚（自然引導留言互動）
[HASHTAGS]: #hashtag1 #hashtag2 #hashtag3"""

    def _call_deepseek(self, prompt: str, max_tokens: int = 800) -> str:
        """Call DeepSeek API."""
        import urllib.request

        cache_key = hashlib.md5(prompt.encode()).hexdigest()[:16]
        if cache_key in self.cache:
            self.cache.move_to_end(cache_key)
            return self.cache[cache_key]

        try:
            req = urllib.request.Request(
                self.DEEPSEEK_URL,
                data=json.dumps({
                    'model': 'deepseek-v4-flash',
                    'messages': [
                        {'role': 'system', 'content': self.SYSTEM_PROMPT},
                        {'role': 'user', 'content': prompt},
                    ],
                    'max_tokens': max_tokens,
                    'temperature': 0.85,
                }).encode(),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.DEEPSEEK_KEY}',
                },
            )
            resp = urllib.request.urlopen(req, timeout=30)
            data = json.loads(resp.read())
            result = data['choices'][0]['message']['content']

            if len(self.cache) >= self.cache_max:
                self.cache.popitem(last=False)
            self.cache[cache_key] = result
            return result
        except Exception as e:
            print(f'  [AI] DeepSeek error: {e}', file=sys.stderr)
            return ''

    def _parse_response(self, content: str) -> Dict:
        """Parse structured AI response."""
        result = {'title': '', 'body': '', 'cta': '', 'hashtags': ''}
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('[TITLE]:'):
                result['title'] = line.replace('[TITLE]:', '').strip()
            elif line.startswith('[BODY]:'):
                result['body'] = line.replace('[BODY]:', '').strip()
            elif line.startswith('[CTA]:'):
                result['cta'] = line.replace('[CTA]:', '').strip()
            elif line.startswith('[HASHTAGS]:'):
                result['hashtags'] = line.replace('[HASHTAGS]:', '').strip()
        return result

    def _fallback_template(self, platform: str, layer: str, topic: str,
                           context: Dict) -> Dict:
        """Template-based fallback when AI fails."""
        month_phase = context.get('phase', '一般時期')
        urgency = context.get('urgency', 5)

        templates = {
            'education': {
                'title': f'【{topic}】9成學生都中嘅數學陷阱',
                'body': f'【唔係你小朋友蠢，係佢中咗系統性陷阱】\n\n每年{month_phase}，我哋都會見到大量學生喺{topic}呢個課題出錯。\n\n唔係佢哋蠢，係佢哋中咗系統性嘅「陷阱盲點」— 大腦自動跳過睇落唔重要嘅步驟。\n\n想知你小朋友中咗邊種陷阱？留言「診斷」免費幫佢測試 👇',
                'cta': '留言「診斷」免費攞陷阱指紋測試 👇',
                'hashtags': '#呈分試 #小學數學 #陷阱解密 #霖楓學苑',
            },
            'social_proof': {
                'title': f'由唔合格到8字頭 — {topic}真實進步故事',
                'body': f'「最大改變唔係分數，係佢肯主動拎練習出嚟做。」\n\n我哋其中一位學生，原本{topic}長期唔合格。做咗陷阱診斷之後，發現佢有系統性盲點。針對操練8堂之後，最近考試攞咗85分。\n\n你小朋友嘅陷阱指紋係咩？留言「測試」免費診斷 👇',
                'cta': '留言「測試」免費為小朋友做陷阱診斷 👇',
                'hashtags': '#真實案例 #數學進步 #呈分試 #霖楓學苑',
            },
            'engagement': {
                'title': f'【快問快答】{topic} — 你小朋友識唔識？',
                'body': f'俾你3秒回答：\n\n408 ÷ 2 = ?\n\nA) 24\nB) 204\nC) 240\n\n.\n.\n.\n答案係 B — 204！\n\n如果你小朋友答咗 A（24），佢中咗我哋講嘅「T4陷阱：漏寫0」。呢個陷阱嘅恐怖之處係：小朋友覺得自己識，但每次都錯。\n\n留言你嘅答案同「診斷」，免費幫小朋友測試 \U0001f447',
                'cta': '留言你嘅答案 +「診斷」免費測試 \U0001f447',
                'hashtags': '#數學挑戰 #親子互動 #小學數學 #陷阱解密',
            },
            'urgency': {
                'title': f'⏰ SSPA倒數：{topic}準備好未？',
                'body': f'距離SSPA仲有{context.get("days_to_sspa", "?")}日。\n\n如果你小朋友而家P6，冇時間「慢慢溫」喇。每個星期都應該有針對性嘅操練。\n\n我哋嘅SSPA衝刺計劃：10份模擬卷 + 個人化診斷 + 操完即改。\n\n留言「SSPA」免費做個診斷先 👇',
                'cta': '留言「SSPA」免費診斷 👇',
                'hashtags': '#SSPA #呈分試 #P6 #升中 #霖楓學苑',
            },
            'personality': {
                'title': '點解我開咗一間「唔教數學」嘅補習社',
                'body': f'因為我細個都係數學渣。\n\n唔係蠢，係永遠唔知錯喺邊。直到有個老師話：「你係不停中同一類陷阱。」\n\n幫我分析盲點 → 針對操練 → 數學全級頭20%\n\n呢個就係陷阱診斷教學法嘅起源。\n\n留言「我的故事」分享你小朋友嘅情況 🤍',
                'cta': '留言「我的故事」分享你小朋友嘅情況 🤍',
                'hashtags': '#教育理念 #創業故事 #數學補習 #呈分試',
            },
            'reels': {
                'title': f'15秒學懂{topic}',
                'body': f'【Reels 短影片腳本】\n\n主題：{topic}\n\n[0-3秒] Hook: 「你小朋友識唔識呢條數？\U0001f447」\n[3-10秒] 教學動畫展示核心概念\n[10-13秒] 結果展示 + 陷阱提醒\n[13-15秒] CTA: Follow我哋睇更多教學！\n\n建議配樂：輕快節奏\n字幕：大字體繁體中文\n目標觀眾：香港P3-P6家長',
                'cta': 'Follow我哋睇更多教學！',
                'hashtags': '#數學教學 #Reels #小學數學 #15秒學數學',
            },
            'differentiation': {
                'title': '一般補習 vs 陷阱診斷教學法',
                'body': f'一般補習：❌ 亂槍打鳥式操卷 ❌ 錯咩就做多啲 ❌ 冇分析「點解」會錯\n\n我哋：✅ 先診斷 → 鎖定陷阱指紋 ✅ 針對性操練 ✅ 口訣記憶 + 進度追蹤\n\n做20題 = 人哋做100題。\n\n留言「比較」免費體驗 🤍',
                'cta': '留言「比較」免費體驗 🤍',
                'hashtags': '#香港補習 #數學補習 #教育方法 #霖楓學苑',
            },
        }

        tmpl = templates.get(layer, templates['education'])
        return {
            'title': tmpl['title'],
            'body': tmpl['body'],
            'cta': tmpl['cta'],
            'hashtags': tmpl['hashtags'],
            'generation_method': 'template-fallback',
            'platform': platform,
            'layer': layer,
            'psychology': LAYERS.get(layer, {}).get('psychology', []),
        }


# ═══════════════════════════════════════════════════════════
# CROSS-PLATFORM CONTENT ADAPTER
# ═══════════════════════════════════════════════════════════

class CrossPlatformAdapter:
    """Adapts core content across platforms with platform-native formatting."""

    @staticmethod
    def adapt_post(post: Dict, target_platform: str) -> Dict:
        """Adapt a post for a specific platform."""
        adapted = copy.deepcopy(post)
        plat = PLATFORMS.get(target_platform, PLATFORMS['fb'])

        # Adjust body length
        adapted['platform'] = target_platform
        adapted['platform_name'] = plat['name']
        adapted['platform_color'] = plat['color']

        # Adjust hashtags per platform
        if plat['hashtag_style'] == 'many_branded':
            if '#霖楓學苑' not in adapted.get('hashtags', ''):
                adapted['hashtags'] = adapted.get('hashtags', '') + ' #霖楓學苑 #香港補習'
        elif plat['hashtag_style'] == 'many_localized':
            if '香港媽媽' not in adapted.get('hashtags', ''):
                adapted['hashtags'] = adapted.get('hashtags', '') + ' #香港媽媽 #育兒 #教育'

        return adapted


# ═══════════════════════════════════════════════════════════
# QUALITY GATE
# ═══════════════════════════════════════════════════════════

class QualityGate:
    """Content quality validation for all platforms."""

    CHECKS = {
        'has_chinese':     lambda c: bool(re.search('[\u4e00-\u9fff]', str(c))),
        'has_cta':         lambda body, cta='': any(w in str(body).lower() or w in str(cta).lower() for w in
                            ['留言', 'follow', '下載', 'dm', 'pm', '👇', '🤍']),
        'min_length':      lambda c, plat: len(str(c)) >= {'long': 100, 'medium': 60, 'short': 30}.get(
                            PLATFORMS.get(plat, {}).get('content_length', 'medium'), 50),
        'no_banned':       lambda c: not any(w in str(c) for w in
                            ['revolutionary', 'game-changer', 'guaranteed results']),
        'has_layer_match': lambda c, layer: layer in LAYERS,
    }

    @classmethod
    def validate(cls, post: Dict) -> Tuple[bool, Dict]:
        """Run all quality checks on a post."""
        import re
        results = {}
        body = post.get('body', '')
        platform = post.get('platform', 'fb')
        layer = post.get('layer', 'education')

        try:
            results['has_chinese'] = cls.CHECKS['has_chinese'](body)
        except Exception:
            results['has_chinese'] = False
        try:
            results['has_cta'] = cls.CHECKS['has_cta'](body, post.get('cta', ''))
        except Exception:
            results['has_cta'] = False
        try:
            results['min_length'] = cls.CHECKS['min_length'](body, platform)
        except Exception:
            results['min_length'] = False
        try:
            results['no_banned'] = cls.CHECKS['no_banned'](body)
        except Exception:
            results['no_banned'] = False
        try:
            results['has_layer_match'] = cls.CHECKS['has_layer_match'](body, layer)
        except Exception:
            results['has_layer_match'] = True  # Don't fail on this

        passed = all(results.values())
        return passed, results

    @classmethod
    def validate_batch(cls, posts: List[Dict]) -> Dict:
        """Validate a batch and return report."""
        report = {'total': len(posts), 'passed': 0, 'failed': 0, 'by_platform': {}, 'details': []}
        for p in posts:
            passed, checks = cls.validate(p)
            plat = p.get('platform', 'unknown')
            if plat not in report['by_platform']:
                report['by_platform'][plat] = {'total': 0, 'passed': 0}
            report['by_platform'][plat]['total'] += 1

            if passed:
                report['passed'] += 1
                report['by_platform'][plat]['passed'] += 1
            else:
                report['failed'] += 1

            report['details'].append({
                'title': p.get('title', '')[:50],
                'platform': plat,
                'layer': p.get('layer', ''),
                'passed': passed,
                'checks': checks,
            })
        return report


# ═══════════════════════════════════════════════════════════
# MAIN: MARKETING BRAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════

class MarketingBrain:
    """
    LF Academy Unified Marketing Brain v2.0

    Orchestrates content generation, scheduling, optimization across
    Facebook, Instagram, and Xiaohongshu (小紅書).

    Usage:
        brain = MarketingBrain()
        brain.scan()                    # Health check all platforms
        posts = brain.generate_week()   # Generate 1 week cross-platform
        brain.optimize()                # MAB-based strategy optimization
        brain.dashboard()               # Export dashboard data
    """

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.fingerprinter = ContentFingerprinter()
        self.generator = AIContentGenerator()
        self.adapter = CrossPlatformAdapter()
        self.mab = MABContentOptimizer()
        self._load_state()

        # Stats
        self.stats = {
            'total_generated': 0,
            'total_published': 0,
            'by_platform': {'fb': 0, 'ig': 0, 'xhs': 0},
            'by_layer': defaultdict(int),
            'sessions': 0,
        }

    def _load_state(self):
        """Load persisted state."""
        state_file = SOCIAL_DIR / '.marketing_brain_state.json'
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text(encoding='utf-8'))
                self.mab = MABContentOptimizer.from_dict(data.get('mab', {}))
                self.stats = data.get('stats', self.stats)
            except Exception:
                pass

    def _save_state(self):
        """Persist state."""
        state_file = SOCIAL_DIR / '.marketing_brain_state.json'
        state_file.write_text(json.dumps({
            'mab': self.mab.to_dict(),
            'stats': self.stats,
            'updated_at': datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2), encoding='utf-8')

    def get_time_context(self, target_date: datetime = None) -> Dict:
        """Get full temporal context for content generation."""
        if target_date is None:
            target_date = datetime.now()

        month = target_date.month
        cal = ACADEMIC_CALENDAR.get(month, ACADEMIC_CALENDAR[9])

        # SSPA countdown
        sspa_date = datetime(target_date.year, 5, 25)
        if target_date > sspa_date:
            sspa_date = datetime(target_date.year + 1, 5, 25)
        days_to_sspa = (sspa_date - target_date).days

        return {
            'date': target_date.isoformat(),
            'month': month,
            'phase': cal['phase'],
            'mood': cal['mood'],
            'focus': cal['focus'],
            'urgency': cal['urgency'],
            'days_to_sspa': days_to_sspa,
            'weekday': target_date.strftime('%A'),
            'weekday_cn': ['一', '二', '三', '四', '五', '六', '日'][target_date.weekday()],
        }

    def scan(self) -> Dict:
        """Health check all platforms and engines."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'fingerprints': self.fingerprinter.count(),
            'mab_arms': len(self.mab.arms),
            'platforms': {},
            'engines': {},
        }

        # Check platforms
        for plat_id, plat_cfg in PLATFORMS.items():
            report['platforms'][plat_id] = {
                'name': plat_cfg['name'],
                'status': 'configured',
                'best_times': plat_cfg['best_times'],
                'content_mix': plat_cfg['content_mix'],
            }

        # Check AI engine
        report['engines']['deepseek'] = 'available' if self.generator._check_ai() else 'unavailable'

        # Check existing engines
        engine_checks = {
            'social_engine': BASE / 'scripts' / 'social_engine.py',
            'fb_pipeline': BASE / 'fb_strategy' / 'fb_content_pipeline.py',
            'xhs_autopilot': BASE / 'scripts' / 'xhs_autopilot.py',
            'content_brain': BASE / 'scripts' / 'lf_content_brain_v4.py',
            'content_engine': BASE / 'scripts' / 'lf_ai_content_engine.py',
        }
        for name, path in engine_checks.items():
            report['engines'][name] = 'available' if path.exists() else 'missing'

        # Cross-platform insights
        report['mab_insights'] = self.mab.get_cross_platform_insights()

        return report

    def generate_calendar(self, platforms: List[str] = None, days: int = 7,
                          start_date: datetime = None, use_ai: bool = True) -> Dict:
        """Generate a content calendar for specified platforms."""
        if platforms is None:
            platforms = ['fb', 'ig', 'xhs']
        if start_date is None:
            start_date = datetime.now()

        context = self.get_time_context(start_date)
        all_posts = []
        layer_cycle = ['education', 'engagement', 'social_proof', 'urgency',
                       'personality', 'reels', 'differentiation']

        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            day_context = self.get_time_context(date)

            # Determine best layer for this day
            layer_idx = day_offset % len(layer_cycle)
            layer = layer_cycle[layer_idx]

            # Skip if layer not good for this platform
            for plat in platforms:
                plat_cfg = PLATFORMS.get(plat, PLATFORMS['fb'])

                # Pick topic from calendar focus
                topic = day_context['focus'][day_offset % len(day_context['focus'])]

                # Generate content (with error recovery)
                try:
                    if use_ai:
                        post = self.generator.generate(
                            platform=plat, layer=layer, topic=topic,
                            context=day_context, fingerprint_set=self.fingerprinter,
                        )
                    else:
                        post = self.generator._fallback_template(plat, layer, topic, day_context)
                except Exception as e:
                    post = self.generator._fallback_template(plat, layer, topic, day_context)
                    post['_generation_error'] = str(e)[:100]

                # Add metadata
                # Cross-platform adaptation
                post = self.adapter.adapt_post(post, plat)
                post['date'] = date.strftime('%Y-%m-%d')
                post['weekday'] = day_context['weekday_cn']
                post['scheduled_time'] = plat_cfg['best_times'][day_offset % len(plat_cfg['best_times'])]

                # Quality gate
                passed, checks = QualityGate.validate(post)
                post['quality_passed'] = passed
                post['quality_checks'] = checks

                all_posts.append(post)

                # Update stats
                self.stats['total_generated'] += 1
                self.stats['by_platform'][plat] = self.stats['by_platform'].get(plat, 0) + 1
                self.stats['by_layer'][layer] += 1

        self.stats['sessions'] += 1
        self._save_state()
        self.fingerprinter.save()

        # Quality summary
        qc_report = QualityGate.validate_batch(all_posts)

        return {
            'generated_at': datetime.now().isoformat(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'days': days,
            'platforms': platforms,
            'context': context,
            'total_posts': len(all_posts),
            'quality': qc_report,
            'posts': all_posts,
        }

    def optimize(self) -> Dict:
        """Run MAB optimization and return strategy recommendations."""
        insights = self.mab.get_cross_platform_insights()

        recommendations = {}
        for plat in PLATFORMS:
            optimal = self.mab.get_optimal_mix(plat, top_n=5)
            suggestions = []
            for opt in optimal:
                suggestions.append({
                    'layer': opt['layer'],
                    'performance': opt['estimated_ctr'],
                    'trials': opt['trials'],
                    'action': f"增加 {opt['layer']} 類型內容比例" if opt['estimated_ctr'] > 0.5
                    else f"檢討或替換 {opt['layer']} 類型內容",
                })
            recommendations[plat] = {
                'platform': PLATFORMS[plat]['name'],
                'current_mix': PLATFORMS[plat]['content_mix'],
                'optimal_mix': {s['layer']: s['performance'] for s in suggestions},
                'suggestions': suggestions,
            }

        return {
            'timestamp': datetime.now().isoformat(),
            'cross_platform_insights': insights,
            'recommendations': recommendations,
        }

    def record_engagement(self, platform: str, layer: str, impressions: int,
                          engagements: int):
        """Record real engagement data for MAB learning."""
        if impressions > 0:
            reward = min(engagements / impressions, 1.0)
            self.mab.update(platform, layer, reward)
        self._save_state()

    def dashboard(self) -> Dict:
        """Export complete dashboard data."""
        scan = self.scan()
        optimize = self.optimize()

        return {
            'timestamp': datetime.now().isoformat(),
            'health': scan,
            'optimization': optimize,
            'stats': dict(self.stats),
            'fingerprints': {
                'total': self.fingerprinter.count(),
                'db_path': str(self.fingerprinter.db_path),
            },
            'platforms': {
                pid: {
                    'name': cfg['name'],
                    'color': cfg['color'],
                    'icon': cfg['icon'],
                    'audience': cfg['audience'],
                    'best_times': cfg['best_times'],
                    'content_mix': cfg['content_mix'],
                }
                for pid, cfg in PLATFORMS.items()
            },
            'layers': {
                lid: {
                    'goal': cfg['goal'],
                    'icon': cfg['icon'],
                    'description': cfg['description'],
                    'best_platforms': cfg['best_platforms'],
                }
                for lid, cfg in LAYERS.items()
            },
        }

    def export_html(self, calendar_data: Dict, output_path: Path = None) -> Path:
        """Export generated content as an interactive HTML calendar."""
        if output_path is None:
            output_path = SOCIAL_DIR / f'marketing_calendar_{datetime.now().strftime("%Y%m%d")}.html'

        posts = calendar_data.get('posts', [])

        # Build HTML sections
        platform_sections = ''
        for plat_id, plat_cfg in PLATFORMS.items():
            plat_posts = [p for p in posts if p.get('platform') == plat_id]
            if not plat_posts:
                continue

            cards = ''
            for p in plat_posts:
                qc_icon = '✅' if p.get('quality_passed') else '❌'
                layer_icon = LAYERS.get(p.get('layer', ''), {}).get('icon', '📝')
                nl = chr(10)
                body_escaped = p.get('body', '').replace(nl, '\\n')
                data_text = body_escaped + nl + p.get('cta', '')
                cards += f'''
                <div class="post-card" style="border-left:4px solid {plat_cfg['color']}">
                  <div class="post-date">{p.get('date', '')} ({p.get('weekday', '')})
                    <span class="layer-tag">{layer_icon} {p.get('layer', '')}</span>
                    <span class="qc-tag">{qc_icon}</span>
                  </div>
                  <div class="post-tag">{p.get('layer', '')} · {p.get('generation_method', '')}</div>
                  <div class="post-title">{p.get('title', '')}</div>
                  <div class="post-body">{p.get('body', '').replace(chr(10), '<br>')}</div>
                  <div class="post-cta">💬 {p.get('cta', '')}</div>
                  <div class="post-hashtags">{p.get('hashtags', '')}</div>
                  <button class="btn-copy" onclick="copyText(this)" data-text="{data_text}">📋 複製</button>
                </div>'''

            platform_sections += f'''
            <div class="platform-section" id="section-{plat_id}">
              <h2 style="color:{plat_cfg['color']}">{plat_cfg['icon']} {plat_cfg['name']} · {len(plat_posts)} 篇</h2>
              <div class="post-grid">{cards}</div>
            </div>'''

        html = f'''<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>霖楓學苑 · AI 營銷日曆 v2.0</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@400;500;700;900&family=Noto+Serif+HK:wght@600;700;900&display=swap');
:root{{--fb:#1877F2;--ig:#E4405F;--xhs:#FF2442;--bg:#F8F9FA;--card:#FFFFFF;--text:#1A1A1A;--muted:#6B7280;--accent:#1A3C6D;--success:#10B981;--fail:#EF4444}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans HK',sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.7;padding:24px}}
.container{{max-width:1600px;margin:0 auto}}
.header{{text-align:center;margin-bottom:32px}}
.header h1{{font-family:'Noto Serif HK',serif;font-size:32px;color:var(--accent);margin-bottom:4px}}
.header .subtitle{{color:var(--muted);font-size:14px}}
.top-bar{{display:flex;gap:12px;margin-bottom:24px;justify-content:center;flex-wrap:wrap}}
.top-bar button{{padding:12px 28px;border-radius:25px;border:2px solid #E5E7EB;background:white;cursor:pointer;font-weight:700;font-size:14px;transition:all .2s}}
.top-bar button:hover,.top-bar button.active{{border-color:var(--accent);background:var(--accent);color:white}}
.stats-bar{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:32px}}
.stat-card{{background:white;border-radius:12px;padding:16px 20px;box-shadow:0 1px 3px rgba(0,0,0,0.04);text-align:center}}
.stat-value{{font-size:28px;font-weight:900;color:var(--accent)}}
.stat-label{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px}}
.platform-section{{margin-bottom:40px}}
.platform-section h2{{font-size:20px;margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid #E5E7EB}}
.post-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}}
.post-card{{background:white;border-radius:12px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,0.04);transition:transform .15s}}
.post-card:hover{{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.08)}}
.post-date{{font-size:11px;color:var(--muted);margin-bottom:6px;font-weight:700;display:flex;align-items:center;gap:8px}}
.layer-tag{{background:#F3F4F6;padding:2px 8px;border-radius:4px;font-size:10px}}
.qc-tag{{margin-left:auto}}
.post-tag{{display:inline-block;background:var(--accent);color:white;padding:2px 10px;border-radius:4px;font-size:10px;font-weight:700;margin-bottom:8px}}
.post-title{{font-size:16px;font-weight:900;margin-bottom:10px;line-height:1.4}}
.post-body{{font-size:13px;color:#374151;line-height:1.8;margin-bottom:8px}}
.post-cta{{font-size:12px;color:var(--fail);font-weight:700;margin-bottom:6px}}
.post-hashtags{{font-size:11px;color:#8B5CF6;margin-bottom:8px}}
.btn-copy{{background:var(--accent);color:white;border:none;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:700;transition:background .15s}}
.btn-copy:hover{{background:#1E4D8C}}
.insights-panel{{background:white;border-radius:12px;padding:24px;margin-bottom:32px;box-shadow:0 1px 3px rgba(0,0,0,0.04)}}
.insights-panel h3{{font-size:16px;margin-bottom:12px;color:var(--accent)}}
.insights-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}}
.insight-item{{padding:12px;background:var(--bg);border-radius:8px}}
.insight-item .label{{font-size:11px;color:var(--muted);margin-bottom:4px}}
.insight-item .value{{font-size:14px;font-weight:700}}
@media(max-width:768px){{.post-grid{{grid-template-columns:1fr}}.stats-bar{{grid-template-columns:repeat(2,1fr)}}}}
</style>
</head><body><div class="container">
<div class="header">
  <h1>🤖 霖楓學苑 · AI 智能營銷系統 v2.0</h1>
  <div class="subtitle">7層內容策略 · 跨平台智能排程 · MAB優化 · 心理學驅動</div>
</div>

<div class="stats-bar">
  <div class="stat-card"><div class="stat-value">{calendar_data.get('total_posts', 0)}</div><div class="stat-label">本週內容</div></div>
  <div class="stat-card"><div class="stat-value">{calendar_data.get('quality', {}).get('passed', 0)}</div><div class="stat-label">品質通過</div></div>
  <div class="stat-card"><div class="stat-value">{len(PLATFORMS)}</div><div class="stat-label">平台覆蓋</div></div>
  <div class="stat-card"><div class="stat-value">{len(LAYERS)}</div><div class="stat-label">內容層次</div></div>
  <div class="stat-card"><div class="stat-value">{self.fingerprinter.count()}</div><div class="stat-label">去重指紋</div></div>
  <div class="stat-card"><div class="stat-value">{len(self.mab.arms)}</div><div class="stat-label">MAB學習臂</div></div>
</div>

<div class="insights-panel">
  <h3>📊 跨平台策略洞察</h3>
  <div class="insights-grid">
    {''.join(f'<div class="insight-item"><div class="label">{PLATFORMS.get(pid, {}).get("icon", "")} {PLATFORMS.get(pid, {}).get("name", pid)}</div><div class="value">最佳內容層: {insight.get("best_layer", "N/A")} · 平均互動: {insight.get("avg_engagement", "N/A")}</div></div>' for pid, insight in self.mab.get_cross_platform_insights().items())}
  </div>
</div>

<div class="top-bar">
  <button class="active" onclick="filter('all')">🌐 全部</button>
  <button onclick="filter('fb')" style="border-color:var(--fb)">📘 Facebook</button>
  <button onclick="filter('ig')" style="border-color:var(--ig)">📸 Instagram</button>
  <button onclick="filter('xhs')" style="border-color:var(--xhs)">📕 小紅書</button>
</div>

<div id="calendar">{platform_sections}</div>
</div>

<script>
function filter(p) {{
  document.querySelectorAll('.platform-section').forEach(s => {{
    s.style.display = (p === 'all' || s.id === 'section-' + p) ? 'block' : 'none';
  }});
  document.querySelectorAll('.top-bar button').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
}}
function copyText(b) {{
  var t = b.getAttribute('data-text').replace(/\\\\n/g, '\\n');
  navigator.clipboard.writeText(t).then(() => {{
    b.textContent = '✓ 已複製';
    setTimeout(() => {{ b.textContent = '📋 複製' }}, 2000);
  }});
}}
</script></body></html>'''

        output_path.write_text(html, encoding='utf-8')
        return output_path


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LF Marketing Brain v2.0')
    parser.add_argument('--scan', action='store_true', help='掃描所有平台狀態')
    parser.add_argument('--generate', choices=['day', 'week', 'month'], default='week',
                        help='生成內容日曆')
    parser.add_argument('--platform', default='all',
                        help='目標平台 (fb|ig|xhs|all)')
    parser.add_argument('--days', type=int, default=7, help='生成天數')
    parser.add_argument('--no-ai', action='store_true', help='使用模板模式（不用AI）')
    parser.add_argument('--dashboard', action='store_true', help='輸出儀表板數據')
    parser.add_argument('--optimize', action='store_true', help='MAB優化建議')
    parser.add_argument('--record', nargs=4, metavar=('PLATFORM', 'LAYER', 'IMPRESSIONS', 'ENGAGEMENTS'),
                        help='記錄互動數據')
    parser.add_argument('--output', help='輸出路徑')

    args = parser.parse_args()
    brain = MarketingBrain()

    if args.scan:
        report = brain.scan()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif args.record:
        plat, layer, imp, eng = args.record
        brain.record_engagement(plat, layer, int(imp), int(eng))
        print(f'✅ 已記錄: {plat}/{layer} — {imp}曝光, {eng}互動')

    elif args.optimize:
        result = brain.optimize()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.dashboard:
        data = brain.dashboard()
        if args.output:
            Path(args.output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'✅ 儀表板已輸出: {args.output}')
        else:
            print(json.dumps(data, ensure_ascii=False, indent=2))

    elif args.generate:
        platforms = ['fb', 'ig', 'xhs'] if args.platform == 'all' else [args.platform]
        days = args.days if args.generate == 'day' else (7 if args.generate == 'week' else 30)

        print(f'🤖 LF Marketing Brain v2.0')
        print(f'   平台: {", ".join(PLATFORMS[p]["name"] for p in platforms)}')
        print(f'   天數: {days}')
        print(f'   模式: {"模板" if args.no_ai else "AI (DeepSeek)"}')
        print()

        calendar = brain.generate_calendar(platforms=platforms, days=days, use_ai=not args.no_ai)

        qc = calendar['quality']
        print(f'✅ 生成完成: {calendar["total_posts"]} 篇')
        print(f'   品質通過: {qc["passed"]}/{qc["total"]}')
        if qc['by_platform']:
            for plat, pqc in qc['by_platform'].items():
                print(f'   {PLATFORMS.get(plat, {}).get("name", plat)}: {pqc["passed"]}/{pqc["total"]}')

        # Export HTML
        html_path = brain.export_html(calendar,
            output_path=Path(args.output) if args.output else None)
        print(f'\n📄 HTML日曆: {html_path}')

        # Save JSON
        json_path = SOCIAL_DIR / f'marketing_calendar_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        json_path.write_text(json.dumps(calendar, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'📦 JSON備份: {json_path}')

    else:
        # Default: show status
        report = brain.scan()
        print('🤖 LF Marketing Brain v2.0')
        print('=' * 50)
        print(f'指紋庫: {report["fingerprints"]} 條')
        print(f'MAB學習臂: {report["mab_arms"]} 個')
        print(f'DeepSeek: {report["engines"].get("deepseek", "?")}')
        print()
        print('命令:')
        print('  --scan           掃描狀態')
        print('  --generate week  生成一週內容')
        print('  --optimize       MAB優化建議')
        print('  --dashboard      完整儀表板')
        print('  --record PLAT LAYER IMP ENG  記錄互動')
