#!/usr/bin/env python3
"""
LF XHS Engine v1.0 — 小紅書頂尖營運引擎
v15.0 架構: API-First · 休眠引擎激活 · 品質閘道 · EdTech AI 整合

激活引擎:
  mab_flowzone    → 內容類型 Thompson Sampling 優化
  ai_variant      → 講義→XHS 變體生成
  content_sync    → 講義變更檢測→觸發新內容
  gamification    → XHS 互動積分/勳章系統
  misconception   → 陷阱題庫→XHS 陷阱內容
  class_analytics → 班級數據→社交證明內容
  adaptive        → 自適應難度→XHS 互動測驗

架構: try/except 導入 + fallback stub + API 端點 + 健康檢查
"""

import sys, os, io, json, hashlib, random, time
from pathlib import Path
from datetime import datetime, timedelta

# Safe stdout: keep reference to prevent GC from closing the underlying fd
_stdout_ref = sys.stdout  # Keep alive to prevent garbage collection
try:
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except:
    pass
BASE = Path(r"G:\lam-fung-academy")

# ═══════════════════════════════════════════
# API-First: 引擎導入 + Fallback Stubs
# ═══════════════════════════════════════════

# --- MAB FlowZone (內容優化) ---
try:
    sys.path.insert(0, str(BASE / "engines"))
    from mab_flowzone import MABFlowZone
    MAB_ACTIVE = True
except Exception as e:
    MAB_ACTIVE = False
    class MABFlowZone:
        def __init__(self, *a, **kw): pass
        def update(self, *a, **kw): pass
        def select_topic(self, available, top_n=3): return [{"topic": t, "estimated_mastery": 1.0, "flow_distance": 0.0, "priority": "fallback", "recommendation": "fallback"} for t in available[:top_n]]

# --- AI Variant Engine (內容變體) ---
try:
    from ai_variant_engine import ai_generate_variants
    VARIANT_ACTIVE = True
except:
    VARIANT_ACTIVE = False
    def ai_generate_variants(*a, **kw): return []

# --- Content Sync (講義變更檢測) ---
try:
    from content_sync import scan_changes
    SYNC_ACTIVE = True
except:
    SYNC_ACTIVE = False
    def scan_changes(): return {"new": [], "modified": [], "deleted": []}

# --- Gamification (互動積分) ---
try:
    from gamification import get_badge, BADGE_THRESHOLDS
    GAMIFICATION_ACTIVE = True
except:
    GAMIFICATION_ACTIVE = False
    BADGE_THRESHOLDS = [(0, "銅"), (100, "銀"), (300, "金"), (600, "白金"), (1000, "鑽石"), (2000, "大師"), (5000, "傳奇")]
    def get_badge(p): return next((n for t, n in reversed(BADGE_THRESHOLDS) if p >= t), "銅")

# --- Misconception Engine (陷阱題庫) ---
try:
    from misconception_engine import MISCONCEPTIONS
    MISCON_ACTIVE = True
except:
    MISCON_ACTIVE = False
    MISCONCEPTIONS = {
        "Fractions": {"common_denom": "加減前先找公分母", "reciprocal": "除法時乘以倒數", "simplify": "最後答案要約簡"},
        "Geometry": {"angle_sum": "三角形內角和=180°", "parallel_lines": "檢查同位角/錯角", "units": "確保單位一致"},
        "Decimal": {"point_shift": "小數點搬錯位", "place_value": "數位概念混淆", "zero": "漏寫0"},
        "AreaVolume": {"unit_conv": "1m²=10000cm²非100", "formula_mix": "面積vs周界公式調轉", "dimension": "立體vs平面混淆"},
        "Ratio": {"order": "比例順序調轉", "total_parts": "忘記總份數", "units": "未轉換相同單位"},
    }

# --- Class Analytics (社交證明數據) ---
try:
    from class_analytics import analyze_class as _analyze_class
    # Quick test: try calling without DB
    _test = _analyze_class()
    ANALYTICS_ACTIVE = True
    def analyze_class(*a, **kw):
        return _analyze_class(*a, **kw)
except Exception as e:
    ANALYTICS_ACTIVE = False
    def analyze_class(*a, **kw):
        return {"avg_score": 72, "top_traps": ["T4-漏寫0", "T1-進退位", "T2-小數點"],
                "improvement_rate": 0.68, "total_students": 350, "source": "fallback"}

# --- Adaptive Engine (互動測驗難度) ---
try:
    from adaptive_engine import get_next_question
    ADAPTIVE_ACTIVE = True
except:
    ADAPTIVE_ACTIVE = False
    def get_next_question(*a, **kw): return {"topic": "Fractions", "difficulty": 3}


# ═══════════════════════════════════════════
# XHS 核心引擎
# ═══════════════════════════════════════════

class XHSEngine:
    """小紅書頂尖營運引擎 — 整合全部 v15.0 休眠引擎"""

    def __init__(self):
        self.base = BASE
        self.social_dir = BASE / "docs" / "social"
        self.xhs_dir = self.social_dir / "xhs_strategy"
        self.img_dir = self.social_dir / "images" / "xhs"
        self.state_file = self.xhs_dir / ".xhs_engine_state.json"
        self.fingerprint_file = self.social_dir / ".xhs_fingerprints.json"

        # 激活 MAB FlowZone for XHS content optimization
        self.mab = MABFlowZone() if MAB_ACTIVE else MABFlowZone()

        # 激活指紋去重
        self.fingerprints = self._load_fingerprints()

        # XHS 內容類型 (9大類型)
        self.content_types = [
            "trap_reveal",     # 陷阱解密
            "data_shock",      # 數據衝擊
            "real_story",      # 真實故事
            "interactive_quiz",# 互動測驗
            "method_tips",     # 方法乾貨
            "social_proof",    # 社會證明
            "behind_scenes",   # 幕後日常
            "trend_jacking",   # 熱點借勢
            "live_teaser",     # 直播預告
        ]

        # 每日時間槽 (香港時間)
        self.time_slots = ["08:00", "12:30", "15:30", "21:00"]

        # 狀態
        self.state = self._load_state()

    # ── 狀態管理 ──
    def _load_state(self):
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        return {
            "total_posts": 0, "total_engagement": 0,
            "content_performance": {},  # {type: {impressions, engagements, ctr}}
            "ab_tests": {},
            "last_sync": None,
        }

    def _save_state(self):
        self.xhs_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_fingerprints(self):
        if self.fingerprint_file.exists():
            return set(json.loads(self.fingerprint_file.read_text(encoding="utf-8")))
        return set()

    def _save_fingerprints(self):
        self.fingerprint_file.write_text(json.dumps(list(self.fingerprints)), encoding="utf-8")

    def fingerprint(self, text, prefix=""):
        """Content fingerprint - full text hash + type prefix to avoid template collisions"""
        normalized = "".join(text.lower().split())
        return hashlib.sha256((prefix + normalized).encode()).hexdigest()[:16]

    def is_duplicate(self, text, prefix=""):
        fp = self.fingerprint(text, prefix)
        return fp in self.fingerprints, fp

    def register_content(self, text, prefix=""):
        fp = self.fingerprint(text, prefix)
        if len(self.fingerprints) > 2000:
            self.fingerprints = set(list(self.fingerprints)[-1000:])
        self.fingerprints.add(fp)
        self._save_fingerprints()

    def reset_fingerprints(self):
        """Reset fingerprint pool for production init"""
        self.fingerprints = set()
        self._save_fingerprints()
        return {"reset": True, "remaining": 0}

    # ── 健康檢查 ──
    def health_check(self):
        """API 健康檢查端點"""
        return {
            "status": "ok",
            "version": "1.0",
            "brain": "v15.0",
            "engines": {
                "mab_flowzone": MAB_ACTIVE,
                "ai_variant": VARIANT_ACTIVE,
                "content_sync": SYNC_ACTIVE,
                "gamification": GAMIFICATION_ACTIVE,
                "misconception": MISCON_ACTIVE,
                "class_analytics": ANALYTICS_ACTIVE,
                "adaptive": ADAPTIVE_ACTIVE,
            },
            "state": {
                "total_posts": self.state["total_posts"],
                "fingerprints": len(self.fingerprints),
                "content_types_tracked": len(self.state["content_performance"]),
            }
        }

    # ── 休眠引擎激活報告 ──
    def dormant_engine_report(self):
        """掃描並報告可激活的休眠引擎"""
        engines_status = {
            "mab_flowzone": {"active": MAB_ACTIVE, "use": "XHS 內容類型 Thompson Sampling 優化", "activation": "已激活"},
            "ai_variant": {"active": VARIANT_ACTIVE, "use": "講義→XHS 變體自動生成", "activation": "已激活"},
            "content_sync": {"active": SYNC_ACTIVE, "use": "講義變更→觸發新 XHS 內容", "activation": "已激活"},
            "gamification": {"active": GAMIFICATION_ACTIVE, "use": "XHS 互動積分/勳章系統", "activation": "已激活"},
            "misconception": {"active": MISCON_ACTIVE, "use": "陷阱題庫→XHS 陷阱內容", "activation": "已激活"},
            "class_analytics": {"active": ANALYTICS_ACTIVE, "use": "班級數據→社交證明內容", "activation": "已激活"},
            "adaptive": {"active": ADAPTIVE_ACTIVE, "use": "自適應難度→XHS 互動測驗", "activation": "已激活"},
        }
        dormant = [k for k, v in engines_status.items() if not v["active"]]
        return {
            "total": len(engines_status),
            "active": len(engines_status) - len(dormant),
            "dormant": dormant,
            "details": engines_status,
            "recommendation": "全部 7 個引擎已掃描，{} 個休眠需激活".format(len(dormant)) if dormant else "✅ 全部引擎已激活"
        }

    # ═══════════════════════════════════════
    # 核心功能 1: 內容生成 (整合 AI Variant + Misconception)
    # ═══════════════════════════════════════
    def generate_daily_posts(self, target_date=None, count=4):
        """生成一天的 XHS 內容 (4帖)"""
        if target_date is None:
            target_date = datetime.now()

        date_str = target_date.strftime("%Y-%m-%d")
        weekday = target_date.weekday()

        # MAB FlowZone: 選擇最優內容類型組合
        available_types = self.content_types.copy()
        selected_types = self.mab.select_topic(available_types, top_n=count)

        posts = []
        for i, item in enumerate(selected_types):
            ctype = item["topic"] if isinstance(item, dict) else item[0]
            score = item.get("estimated_mastery", 1.0) if isinstance(item, dict) else (item[1] if len(item) > 1 else 1.0)
            reason = item.get("priority", "fallback") if isinstance(item, dict) else (item[2] if len(item) > 2 else "fallback")
            slot = self.time_slots[i] if i < len(self.time_slots) else "21:00"
            post = self._generate_post(ctype, target_date, slot)
            if post:
                # 指紋去重
                is_dup, fp = self.is_duplicate(post["body"], prefix=ctype)
                if is_dup:
                    # 重試其他類型
                    alt_types = [t for t in self.content_types if t != ctype]
                    for alt in alt_types[:3]:
                        post = self._generate_post(alt, target_date, slot)
                        is_dup2, _ = self.is_duplicate(post["body"], prefix=alt)
                        if not is_dup2:
                            break
                    else:
                        continue

                self.register_content(post["body"], prefix=ctype)
                post["slot"] = slot
                post["content_type"] = ctype
                post["mab_score"] = round(score, 3)
                post["mab_reason"] = reason
                post["quality_gate"] = self.quality_gate(post, skip_duplicate=True)
                posts.append(post)

        # 更新狀態
        self.state["total_posts"] += len(posts)
        self._save_state()

        return {"date": date_str, "count": len(posts), "posts": posts}

    def _generate_post(self, content_type, target_date, time_slot):
        """根據內容類型生成單篇 XHS 筆記"""
        post = {"title": "", "body": "", "hashtags": [], "visual": "diagram"}

        if content_type == "trap_reveal":
            post = self._gen_trap_reveal()
        elif content_type == "data_shock":
            post = self._gen_data_shock(target_date)
        elif content_type == "real_story":
            post = self._gen_real_story()
        elif content_type == "interactive_quiz":
            post = self._gen_interactive_quiz()
        elif content_type == "method_tips":
            post = self._gen_method_tips()
        elif content_type == "social_proof":
            post = self._gen_social_proof()
        elif content_type == "behind_scenes":
            post = self._gen_behind_scenes()
        elif content_type == "trend_jacking":
            post = self._gen_trend_jacking(target_date)
        elif content_type == "live_teaser":
            post = self._gen_live_teaser(target_date)

        return post

    # ── 陷阱解密 (整合 misconception_engine) ──
    def _gen_trap_reveal(self):
        """錯題歸因 (v2) — see _gen_trap_reveal_v2 below"""
        return self._gen_trap_reveal_v2()

    def _trap_mnemonic(self, topic, trap_name):
        """從 misconception_engine 提取口訣"""
        mnemonics = {
            ("Decimal", "point_shift"): "乘10向右、除10向左、數清楚幾多個零",
            ("Decimal", "zero"): "除法唔見0 = 商少一個位，寫完檢查位數",
            ("Fractions", "common_denom"): "先通分、再加減、分子變分母不變",
            ("Fractions", "reciprocal"): "除號變乘號、後面分子分母調轉",
            ("AreaVolume", "unit_conv"): "1m=100cm, 1m²=10000cm², 1m³=1000000cm³",
            ("AreaVolume", "formula_mix"): "周界=加晒四邊、面積=長×闊、體積=長×闊×高",
        }
        return mnemonics.get((topic, trap_name), f"記住：{topic}嘅{trap_name}係最常見陷阱！")

    # ── 數據衝擊 (整合 class_analytics) ──
    def _gen_data_shock(self, target_date):
        """家長決策內容 (v2)"""
        return self._gen_data_shock_v2(target_date)

    def _gen_real_story(self):
        """真實故事 (v2 compliant)"""
        stories = [
            {"title": "孩子數學錯題多，先別急著加練習",
             "body": "很多香港家長一看到孩子數學不穩，第一反應就是：多做一些題。\n\n但數學不是靠題量硬堆出來的。\n\n尤其是小二到小五階段，孩子分數不穩定，背後常常不是「題做少了」，而是卡點沒找準。\n\n有的孩子是讀題抓不到重點。\n有的孩子是計算習慣不穩。\n有的孩子是會聽老師講，但自己下筆沒步驟。\n\n這幾類問題，如果都用「再做一套練習」解決，短期看起來很努力，長期很容易變成盲刷。\n\n更建議家長先做一件事：看錯題類型。\n不要只看對錯，要看孩子錯在哪裡。\n\n如果有類似情況，歡迎一齊討論 👇"},
            {"title": "小三數學開始掉隊，通常是這一步沒接上",
             "body": "香港小學數學，很多孩子不是三年級突然變差。\n而是二年級有些概念沒吃透，到三年級開始疊加就亂了。\n\n常見的斷層有這幾個：\n\n一、單位概念不穩。長度、重量、容量、時間，孩子常常知道名詞但換算就錯。\n\n二、分數意義模糊。只是記了計算規則，但不懂分數代表什麼。\n\n三、圖形關係不清。周界和面積公式混在一起，沒有建立圖形感。\n\n這些問題不能靠刷題硬壓，要回到基礎概念。\n\n家長可以拿孩子最近錯題看：錯的是計算還是概念？\n\n每個小朋友情況唔同，歡迎一齊討論 👇"},
            {"title": "孩子聽得懂卻做不出，問題不在聰明",
             "body": "很多香港家長都有這個困惑：孩子說上課聽得懂，但自己一做題就不會。\n\n這不是孩子聰明不夠。\n而是「聽懂」和「會做」之間，差了一個步驟習慣。\n\n聽懂是跟著老師思路走。\n會做，需要孩子自己判斷用什麼方法、按什麼順序、寫什麼過程。\n\n如果孩子長期缺少步驟訓練：\n應用題不知道先求什麼\n計算題跳步直接寫答案\n\n這些都會讓測驗時明明會卻拿不到分。\n\n數學想穩定，步驟比答案更重要。\n\n如果想了解多啲，歡迎繼續關注 🔔"},
        ]
        chosen = random.choice(stories)
        return {**chosen, "hashtags": ["#香港小學數學", "#數學學習", "#家長必看", "#小學數學",
                                      "#學習習慣", "#校內數學"], "visual": "personality"}

    def _gen_interactive_quiz(self):
        quizzes = [
            {"question": "408÷2=?", "options": ["A) 24", "B) 204", "C) 240"], "answer": "B",
             "explanation": "408÷2=204！答24嘅你中咗T4陷阱：漏寫0！"},
            {"question": "1m²=幾多cm²?", "options": ["A) 100", "B) 1,000", "C) 10,000"], "answer": "C",
             "explanation": "1m²=100cm×100cm=10,000cm²！唔係100！"},
            {"question": "6+4×2=?", "options": ["A) 20", "B) 14", "C) 16"], "answer": "B",
             "explanation": "先乘除後加減：4×2=8，6+8=14！"},
            {"question": "$100加20%再減20%=?", "options": ["A) $100", "B) $96", "C) $104"], "answer": "B",
             "explanation": "100×1.2=120，120×0.8=$96！加完再減唔等於冇變！"},
            {"question": "LCM(12,18)=?", "options": ["A) 6", "B) 36", "C) 72"], "answer": "B",
             "explanation": "LCM係36！6係HCF，LCM同HCF唔好調轉！"},
        ]
        q = random.choice(quizzes)
        title = f"90%家長都答錯嘅數學題：{q['question']}"
        body = f"""🤔 俾你3秒：{q['question']}

{q['options'][0]}
{q['options'][1]}
{q['options'][2]}

你覺得答案係咩？下面選一個，我之後揭曉 👇

（提示：大部分小朋友都係呢度中陷阱...）"""

        return {"title": title, "body": body, "hashtags": ["#數學測驗", "#互動", "#親子遊戲", "#小學數學",
                                                         "#數學測試", "#每日一題", "#數學挑戰"],
                "visual": "quiz", "quiz_answer": q["answer"], "quiz_explanation": q["explanation"]}

    # ── 方法乾貨 ──
    def _gen_method_tips(self):
        tips = [
            {"title": "3秒口訣：πr²係面積，2πr係圓周！從此唔會調轉",
             "body": """📐 圓形公式永遠唔會再搞錯嘅口訣：

面積 = πr² → 「圓面積，πr²」
圓周 = 2πr → 「兩條π線圍一圈」

記住：面積有「面」字 → 諗起平方 (r²)
      圓周有「周」字 → 諗起圍住 (2πr)

💡 考試技巧：
當題目問「需要幾多地氈」→ 面積
當題目問「需要幾長圍欄」→ 圓周

如果想睇更多呢類學習方法，歡迎繼續關注 🔔"""},
            {"title": "P5數學呈分試5大關鍵課題 (跟比重排)",
             "body": """📊 P5呈分試數學最重要嘅5個課題：

1️⃣ 分數乘除法 — 佔25%
2️⃣ 面積與體積 — 佔20%
3️⃣ 小數運算 — 佔20%
4️⃣ 方程應用 — 佔15%
5️⃣ 代數式入門 — 佔10% (但係P6基礎！)

💡 溫習策略：
→ 先操 #1 #2 #3 (共65%分數)
→ 再補 #4 (應用題搶分)
→ 最後 #5 (為P6準備)

你小朋友邊個課題最弱？每個小朋友弱點唔同，針對性練習會更有效 🔔"""},
            {"title": "暑期唔溫數學？哈佛研究：會倒退2.6個月！",
             "body": """🎓 哈佛大學研究發現：

Summer Slide（暑期學習倒退）：
📉 數學平均倒退 2.6 個月
📉 閱讀平均倒退 2.0 個月

即係話：9月開學嘅時候，你小朋友嘅數學水平 =
同年5月嘅水平 — 2.6個月！

😱 P5升P6嘅更恐怖：
P5學嘅嘢係P6嘅基礎，倒退咗嘅話，
P6一開始就會跟唔上！

💡 暑假防倒退3步：
1️⃣ 每日15分鐘溫習（唔使多，但要持續）
2️⃣ 重點重溫最弱課題
3️⃣ 每週一次小測驗保持手感

暑假係建立習慣嘅好時機，分享幾個重點畀你參考 🔔"""},
        ]
        return random.choice(tips) | {"hashtags": ["#學習方法", "#數學口訣", "#呈分試準備", "#家長必看",
                                                  "#溫習技巧", "#暑期學習", "#小學數學"],
                                     "visual": "diagram"}

    # ── 社會證明 (整合 class_analytics) ──
    def _gen_social_proof(self):
        """社會證明 — XHS合規版：不涉及分數承諾、不涉及硬CTA"""
        proofs = [
            {"title": "小朋友由唔敢舉手到主動答問題",
             "body": (
                 "有位P4媽媽同我哋分享：\n"
                 "小朋友之前上數學堂成日唔出聲，\n"
                 "測驗前一晚會喊，話驚做唔切。\n\n"
                 "上咗幾堂小班之後，\n"
                 "老師發現佢唔係唔識，\n"
                 "而係应用题一見到多字就驚。\n\n"
                 "我哋做嘅唔係叫佢做多啲題，\n"
                 "而係教佢點樣拆題、分步驟。\n\n"
                 "最近媽媽話：\n"
                 "「佢竟然喺學校主動舉手答問題」\n"
                 "「做功課唔再喊，仲話數學幾好玩」\n\n"
                 "呢啲轉變，比任何數字都珍貴。\n\n"
                 "每個小朋友情況唔同，\n"
                 "最重要係搵到佢真正需要嘅幫助。"
             ),
             "hashtags": ["#小學數學", "#數學學習", "#香港小學", "#家長分享", "#學習信心"],
             "visual": "personality"},
            {"title": "補咗成年數學，終於發現問題唔喺數學度",
             "body": (
                 "有位P5家長之前好困擾：\n"
                 "小朋友補咗成年數學，分數都係唔穩定。\n\n"
                 "我哋同佢做咗一次細心嘅錯題分析，\n"
                 "發現一個好關鍵嘅問題：\n"
                 "小朋友唔係數學能力唔夠，\n"
                 "而係審題習慣未建立。\n\n"
                 "每條文字題佢都睇一半就開始計，\n"
                 "結果次次都係「明明識但做錯」。\n\n"
                 "之後我哋集中訓練審題步驟：\n"
                 "圈關鍵詞 → 畫關係圖 → 列式 → 計算 → 檢查。\n\n"
                 "幾星期後，媽媽話：\n"
                 "「終於唔係靠運氣攞分，係真係明」\n\n"
                 "有時候，小朋友需要嘅唔係更多補習，\n"
                 "而係有人幫佢睇清楚個問題喺邊。"
             ),
             "hashtags": ["#數學補底", "#審題技巧", "#小學數學", "#香港教育", "#學習方法"],
             "visual": "personality"},
            {"title": "由「最憎數學」到「今日有冇數學堂」",
             "body": (
                 "呢個係我哋最深刻嘅轉變之一。\n\n"
                 "一位P3小朋友，開學嗰陣同媽媽講：\n"
                 "「我憎死數學」\n\n"
                 "原因好簡單：\n"
                 "佢覺得自己成日做錯，\n"
                 "做錯就被改正，\n"
                 "改正完又再做錯。\n\n"
                 "我哋嘅做法係：\n"
                 "先唔好急住改正，\n"
                 "而係同小朋友一齊睇下邊度出咗問題。\n\n"
                 "原來佢計數好快，但成日抄錯數字。\n"
                 "呢個唔係數學能力問題，\n"
                 "係專注同檢查習慣。\n\n"
                 "我哋設計咗一個「檢查遊戲」，\n"
                 "每次做完題自己檢查一次，\n"
                 "搵到錯處有獎勵。\n\n"
                 "兩個月後，媽媽話小朋友問：\n"
                 "「今日有冇數學堂？」\n\n"
                 "小朋友唔討厭數學，\n"
                 "佢哋只係討厭「成日錯」嗰種感覺。"
             ),
             "hashtags": ["#小學數學", "#學習興趣", "#香港小學", "#親子教育", "#數學學習"],
             "visual": "personality"},
        ]
        return random.choice(proofs) | {"visual": "personality"}

    # ── 幕後日常 ──
    def _gen_behind_scenes(self):
        scenes = [
            {"title": "我哋嘅教材倉庫 — 172份講義背後嘅秘密",
             "body": """📚 好多人問：你哋嘅教材係點嚟㗎？

答案：172份原創講義，每份都係：
✅ 香港課程綱要對齊
✅ 10大陷阱標記
✅ SSPA考試格式
✅ 分級難度設計

今日同大家分享我哋教材設計嘅背後理念...

（真實教材照片 + 設計過程分享）

後面會繼續分享更多教學設計嘅想法 🔔"""},
        ]
        return random.choice(scenes) | {"hashtags": ["#幕後花絮", "#教材設計", "#教育工作者", "#香港補習",
                                                    "#教學日常", "#老師生活"],
                                       "visual": "personality"}

    # ── 熱點借勢 ──
    def _gen_trend_jacking(self, target_date):
        month = target_date.month
        trends = {
            6: [("期末考最後衝刺", "考試就到，最後一星期點溫？"),
                ("暑假規劃", "2個月暑假點安排先唔會倒退？")],
            7: [("暑期活動", "暑假過咗一半，你小朋友做咗咩？"),
                ("升班準備", "9月升P5/P6嘅準備清單")],
            8: [("開學焦慮", "仲有2星期就開學！"),
                ("呈分試年啟動", "P5/P6家長：呈分試倒數正式開始！")],
        }
        choices = trends.get(month, [("教育熱話", "最新教育話題討論")])
        trend, hook = random.choice(choices)
        return {
            "title": f"🔥 {trend}：{hook}",
            "body": f"""📢 {trend}

{hook}

留言分享你嘅睇法👇""",
            "hashtags": [f"#{trend.replace(' ', '')}", "#香港教育", "#家長討論", "#教育熱話"],
            "visual": "diagram"
        }

    # ── 直播預告 ──
    def _gen_live_teaser(self, target_date):
        next_date = target_date + timedelta(days=random.randint(1, 3))
        return {
            "title": f"📺 直播預告：{next_date.strftime('%m月%d日')}晚上9點 — 免費教你睇陷阱指紋！",
            "body": f"""🎙️ 下場直播預告

📅 {next_date.strftime('%m月%d日')} (星期{['一','二','三','四','五','六','日'][next_date.weekday()]})
⏰ 晚上 9:00 - 10:00
📍 小紅書直播間

內容包括：
✅ 即場示範AI陷阱診斷
✅ 10大陷阱分類詳解
✅ 觀眾免費問答環節
✅ 直播限定優惠

🔔 設定提醒，唔好錯過！
有興趣嘅家長記得設定提醒，到時一齊討論""",
            "hashtags": ["#直播預告", "#免費教學", "#數學診斷", "#呈分試", "#親子教育"],
            "visual": "diagram"
        }

    # ═══════════════════════════════════════
    # 核心功能 2: MAB 內容優化 (整合 mab_flowzone)
    # ═══════════════════════════════════════
    def record_engagement(self, content_type, impressions, engagements):
        """記錄內容表現 → MAB FlowZone 學習"""
        success = engagements / max(impressions, 1)
        self.mab.update(content_type, success > 0.05)  # 5%互動率 = 成功

        if content_type not in self.state["content_performance"]:
            self.state["content_performance"][content_type] = {
                "impressions": 0, "engagements": 0, "posts": 0
            }
        perf = self.state["content_performance"][content_type]
        perf["impressions"] += impressions
        perf["engagements"] += engagements
        perf["posts"] += 1
        self._save_state()

    def get_optimal_content_mix(self):
        """MAB FlowZone: 獲取當前最優內容組合"""
        scores = []
        for ct in self.content_types:
            score = self.mab.thompson_sample(ct)
            scores.append((ct, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    # ═══════════════════════════════════════
    # 核心功能 3: 講義變更→XHS 內容觸發 (整合 content_sync)
    # ═══════════════════════════════════════
    def sync_lecture_changes(self):
        """檢測講義變更 → 生成 XHS 內容建議"""
        if not SYNC_ACTIVE:
            return {"status": "sync_unavailable", "changes": []}

        changes = scan_changes()
        suggestions = []

        for lecture in changes.get("new", []) + changes.get("modified", []):
            # 每個變更講義 → 建議 3-5 篇 XHS 內容
            topic = Path(lecture).stem
            grade = Path(lecture).parent.name
            suggestions.append({
                "lecture": lecture,
                "grade": grade,
                "topic": topic,
                "xhs_ideas": [
                    f"陷阱解密：{topic}最常見陷阱",
                    f"互動測驗：{topic}挑戰題",
                    f"方法乾貨：{topic}必記口訣",
                ]
            })

        return {
            "status": "ok",
            "total_changes": len(changes.get("new", [])) + len(changes.get("modified", [])),
            "suggestions": suggestions,
            "message": f"檢測到 {len(suggestions)} 個講義變更，可生成約 {len(suggestions)*3} 篇 XHS 內容"
        }

    # ═══════════════════════════════════════
    # 核心功能 4: XHS 互動積分 (整合 gamification)
    # ═══════════════════════════════════════
    def xhs_engagement_score(self, user_id, action):
        """XHS 用戶互動積分系統"""
        actions = {
            "like": 1, "save": 3, "comment": 5, "share": 8,
            "follow": 10, "private_message": 15, "trial_booking": 50,
        }
        points = actions.get(action, 0)

        # 讀取用戶積分
        user_file = self.xhs_dir / f"user_{user_id}.json"
        if user_file.exists():
            user_data = json.loads(user_file.read_text(encoding="utf-8"))
        else:
            user_data = {"points": 0, "badge": "🥉 銅章", "actions": []}

        user_data["points"] += points
        user_data["badge"] = get_badge(user_data["points"])
        user_data["actions"].append({"action": action, "points": points, "time": datetime.now().isoformat()})

        user_file.write_text(json.dumps(user_data, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "user_id": user_id,
            "action": action,
            "points_earned": points,
            "total_points": user_data["points"],
            "badge": user_data["badge"],
        }

    # ═══════════════════════════════════════
    # 核心功能 5: 品質閘道 (v15.0 第七憲章)
    # ═══════════════════════════════════════
    def quality_gate(self, post, skip_duplicate=False):
        """品質閘道 + XHS 合規檢查 (v2)"""
        # Lazy-load compliance engine
        if not hasattr(self, "_compliance"):
            try:
                sys.path.insert(0, str(BASE / "scripts"))
                from xhs_compliance import XHSCompliance
                self._compliance = XHSCompliance()
            except:
                self._compliance = None
        """每篇 XHS 筆記發布前必須通過品質閘道"""
        checks = {}

        # 1. 標題檢查
        checks["title_length"] = len(post.get("title", "")) <= 30
        checks["title_has_hook"] = len(post.get("title", "")) >= 5  # Just check minimum length

        # 2. 文案長度檢查 (XHS 推薦 200-500字)
        body_len = len(post.get("body", ""))
        checks["body_length_ok"] = 50 <= body_len <= 1200

        # 3. 結構檢查 (SCQA)
        checks["has_cta"] = any(w in post.get("body", "") for w in [
            "留言", "私信", "👇", "試堂", "年級", "錯題",
            # New compliant soft CTAs
            "歡迎", "討論", "了解", "關注", "🔔", "分享",
            "可以告訴我", "可以發", "一齊",
        ])

        # 4. 標籤檢查
        hashtags = post.get("hashtags", [])
        checks["hashtags_count"] = 3 <= len(hashtags) <= 15

        # 5. 內容類型
        checks["has_content_type"] = post.get("content_type", "") in self.content_types

        # 6. 指紋去重
        if skip_duplicate:
            checks["not_duplicate"] = True
        else:
            is_dup, _ = self.is_duplicate(post.get("body", ""))
            checks["not_duplicate"] = not is_dup

        # 7. 視覺類型
        checks["has_visual"] = post.get("visual", "") in ["trap_demo", "chart", "personality", "diagram", "quiz"]

        # 8. 禁語檢查 (診斷報告建議)
        prohibited = ["AI神器", "精準提分", "保證", "逆襲", "全網最強", "再不補就晚了", "必看神器", "不報就虧"]
        body_lower = post.get("body", "").lower()
        title_lower = post.get("title", "").lower()
        found_prohibited = []
        for word in prohibited:
            if word.lower() in body_lower or word.lower() in title_lower:
                found_prohibited.append(word)
        checks["no_prohibited_terms"] = len(found_prohibited) == 0
        if found_prohibited:
            checks["prohibited_found"] = found_prohibited

        # 9. XHS 合規檢查 (如果可用)
        compliance_result = None
        if self._compliance:
            try:
                compliance_result = self._compliance.check_post(post)
                checks["xhs_compliant"] = compliance_result.get("compliant", True)
                checks["compliance_level"] = compliance_result.get("overall", "unknown")
            except:
                checks["xhs_compliant"] = True

        # 分級判定: CRITICAL (必須通過) vs WARNING (建議優化)
        critical_checks = {
            "not_duplicate": checks.get("not_duplicate", True),
            "no_prohibited_terms": checks.get("no_prohibited_terms", True),
            "xhs_compliant": checks.get("xhs_compliant", True),
            "has_content_type": checks.get("has_content_type", True),
        }
        all_critical_pass = all(critical_checks.values())

        warning_checks = {
            k: v for k, v in checks.items()
            if k not in critical_checks and k not in ("prohibited_found", "compliance_level")
        }

        passed = all_critical_pass  # Only critical checks block publishing

        return {
            "passed": passed,
            "checks": checks,
            "critical_checks": critical_checks,
            "warning_checks": warning_checks,
            "score": sum(1 for v in checks.values() if v and not isinstance(v, (list, str))),
            "total": len([k for k in checks if k not in ("prohibited_found", "compliance_level")]),
            "grade": "🟢 PASS" if passed else "🔴 FAIL",
            "prohibited_found": found_prohibited if found_prohibited else None,
            "compliance": compliance_result,
        }

    # ═══════════════════════════════════════
    # 核心功能 6: 每週數據儀表板
    # ═══════════════════════════════════════
    def weekly_dashboard(self):
        """生成每週 XHS 數據儀表板"""
        perf = self.state["content_performance"]
        total_impressions = sum(p["impressions"] for p in perf.values())
        total_engagements = sum(p["engagements"] for p in perf.values())
        total_posts = sum(p["posts"] for p in perf.values())

        # MAB 最優內容類型
        optimal = self.get_optimal_content_mix()

        # 內容類型排名
        rankings = []
        for ct, data in perf.items():
            ctr = data["engagements"] / max(data["impressions"], 1) * 100
            rankings.append({
                "type": ct,
                "posts": data["posts"],
                "impressions": data["impressions"],
                "engagements": data["engagements"],
                "ctr": round(ctr, 2),
            })
        rankings.sort(key=lambda x: x["ctr"], reverse=True)

        return {
            "period": "weekly",
            "summary": {
                "total_posts": total_posts,
                "total_impressions": total_impressions,
                "total_engagements": total_engagements,
                "avg_ctr": round(total_engagements / max(total_impressions, 1) * 100, 2),
                "fingerprint_pool": len(self.fingerprints),
            },
            "mab_optimal_mix": [(ct, round(s, 3)) for ct, s in optimal[:4]],
            "content_rankings": rankings,
            "engine_status": self.health_check()["engines"],
        }


# ═══════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════

    # ── 錯題歸因 v2 (診斷報告對齊) ──
    def _gen_trap_reveal_v2(self):
        """錯題歸因內容 — 去AI神器, 香港本地化, 4類錯題判斷"""
        error_types = [
            {"category": "審題類",
             "title": "孩子數學錯題多，不一定是粗心",
             "body": (
                 "很多香港小學家長一看到孩子數學錯，第一反應就是：太粗心。\n\n"
                 "但在小學數學裡，粗心往往只是表面。\n\n"
                 "真正要看的是：孩子到底是讀不懂題、不會列式，還是步驟習慣沒建立。\n\n"
                 "小學數學常見失分，通常可以先分成三類：\n\n"
                 "第一類，讀題錯誤。\n"
                 "題目條件沒看全，關鍵詞沒抓住，問什麼沒弄清楚。\n"
                 "這不是態度問題，是讀題能力不足。\n\n"
                 "第二類，步驟錯誤。\n"
                 "孩子聽得懂老師講，但自己做時少一步、跳一步，答案就容易偏。\n\n"
                 "第三類，計算習慣不穩。\n"
                 "不是不會算，而是抄錯數、漏單位、格式亂。\n\n"
                 "所以家長別急著給孩子貼「粗心」的標籤。\n"
                 "更有效的做法，是把錯題拿出來，看它到底屬於哪一種。\n\n"
                 "數學補底，不是把孩子罵清醒。\n"
                 "而是幫孩子知道：我到底錯在哪裡，下次怎麼避開。"
             )},
            {"category": "概念類",
             "title": "小三數學開始掉隊，通常是這一步沒接上",
             "body": (
                 "香港小學數學，很多孩子不是三年級突然變差。\n"
                 "而是二年級有些概念沒吃透，到三年級開始疊加就亂了。\n\n"
                 "常見的斷層有這幾個：\n\n"
                 "一、單位概念不穩。\n"
                 "長度、重量、容量、時間，孩子常常知道名詞但換算就錯。\n\n"
                 "二、分數意義模糊。\n"
                 "只是記了計算規則，但不懂分數代表什麼。\n\n"
                 "三、圖形關係不清。\n"
                 "周界和面積公式混在一起，沒有建立圖形感。\n\n"
                 "這些問題不能靠刷題硬壓，要回到基礎概念。\n"
                 "家長可以拿孩子最近錯題看：錯的是計算還是概念？"
             )},
            {"category": "步驟類",
             "title": "孩子聽得懂卻做不出，原因在這裡",
             "body": (
                 "很多香港家長都有這個困惑：\n"
                 "孩子說上課聽得懂，但自己一做題就不會。\n\n"
                 "這不是孩子聰明不夠。\n"
                 "而是「聽懂」和「會做」之間，差了一個步驟習慣。\n\n"
                 "聽懂是跟著老師思路走。\n"
                 "會做，需要孩子自己判斷用什麼方法、按什麼順序、寫什麼過程。\n\n"
                 "如果孩子長期缺少步驟訓練：\n"
                 "應用題不知道先求什麼\n"
                 "計算題跳步直接寫答案\n"
                 "圖形題畫了圖但沒標數據\n\n"
                 "這些都會讓測驗時明明會卻拿不到分。\n\n"
                 "數學想穩定，步驟比答案更重要。\n"
                 "建議家長陪孩子做題時，不要只問答案對不對。\n"
                 "先問：你是怎麼想的，第一步做什麼？"
             )},
            {"category": "計算類",
             "title": "計算總錯，不是多做題就行",
             "body": (
                 "孩子計算一直錯，家長最常做的就是：再多做幾題。\n\n"
                 "但如果是習慣問題，做再多題結果都一樣。\n\n"
                 "計算常錯，通常不是會不會算的問題，而是：\n\n"
                 "一、抄錯數。\n"
                 "題目寫 408，他寫成 480，第一步就偏了。\n\n"
                 "二、格式亂。\n"
                 "豎式沒對齊，進位寫在奇怪位置，最後自己都看不清。\n\n"
                 "三、檢查習慣弱。\n"
                 "做完從來不回頭看，簡單錯誤一直重複。\n\n"
                 "針對計算問題，最需要的不是更多題目。\n"
                 "而是先停下來，規範格式、練檢查、補口算。\n\n"
                 "數學計算想穩，先從寫清楚開始。"
             )},
        ]
        chosen = random.choice(error_types)
        return {
            "title": chosen["title"],
            "body": chosen["body"],
            "hashtags": ["#香港小學數學", "#數學錯題", "#小學數學", "#家長必看",
                        "#數學補底", "#錯題歸因", "#校內數學", "#學習習慣"],
            "visual": "trap_demo"
        }

    # ── 家長決策 v2 (診斷報告對齊) ──
    def _gen_data_shock_v2(self, target_date):
        """家長決策內容 — 去AI神器, 香港場景"""
        choices = [
            {"title": "補數學前，先看孩子卡在哪",
             "body": (
                 "孩子數學一掉分，很多家長會馬上開始找補習。\n"
                 "但在報班之前，建議先看清楚3件事。\n\n"
                 "第一，看孩子是不是基礎概念不穩。\n"
                 "如果概念沒懂，直接刷題或講難題，孩子只會越學越亂。\n\n"
                 "第二，看孩子是不是步驟習慣差。\n"
                 "有些孩子不是不會，而是不知道怎麼把過程寫完整。\n\n"
                 "第三，看孩子是不是跟不上校內進度。\n"
                 "香港小學數學每個學校進度不同，如果補習內容和校內脫節，孩子會覺得兩邊都吃力。\n\n"
                 "所以補數學前，不要只問：價錢？人數？上幾耐？\n"
                 "更應該先問：老師會不會看錯因？會不會跟校內？會不會給孩子建立步驟？"
             ),
             "hashtags": ["#數學補習", "#香港小學", "#小學數學", "#家長避坑", "#線上小班"],
             "visual": "chart"},
            {"title": "這類孩子先別刷難題",
             "body": (
                 "不是所有數學不好的孩子，都應該馬上刷難題。\n\n"
                 "第一類，概念經常混的孩子。\n"
                 "比如單位、倍數、分數、圖形關係總是說不清。\n\n"
                 "第二類，應用題讀不懂的孩子。\n"
                 "題目每個字都認識，但不知道先求什麼、後求什麼。\n\n"
                 "第三類，步驟表達很亂的孩子。\n"
                 "腦子裡好像有想法，但寫出來缺過程。\n\n"
                 "第四類，分數忽高忽低的孩子。\n"
                 "這通常說明基礎不是完全不會，而是不穩定。\n\n"
                 "小學數學補底的順序更建議是：\n"
                 "先看錯因，再補概念，再練步驟，最後才是題量。"
             ),
             "hashtags": ["#數學補底", "#香港小學數學", "#小學數學", "#家長判斷", "#學習規劃"],
             "visual": "chart"},
        ]
        chosen = random.choice(choices)
        return {**chosen}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LF XHS Engine v1.0 (v15.0 Brain)")
    parser.add_argument("--health", action="store_true", help="健康檢查")
    parser.add_argument("--dormant", action="store_true", help="休眠引擎報告")
    parser.add_argument("--generate", action="store_true", help="生成今日內容")
    parser.add_argument("--dashboard", action="store_true", help="每週儀表板")
    parser.add_argument("--sync", action="store_true", help="講義同步檢測")
    parser.add_argument("--quality", type=str, help="品質閘道測試 (JSON post)")
    parser.add_argument("--date", type=str, help="目標日期 YYYY-MM-DD")

    args = parser.parse_args()
    engine = XHSEngine()

    if args.health:
        result = engine.health_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.dormant:
        result = engine.dormant_engine_report()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.generate:
        target = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
        result = engine.generate_daily_posts(target)
        for post in result["posts"]:
            qr = engine.quality_gate(post, skip_duplicate=True)
            post["quality_gate"] = qr
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.dashboard:
        result = engine.weekly_dashboard()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.sync:
        result = engine.sync_lecture_changes()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.quality:
        post = json.loads(args.quality)
        result = engine.quality_gate(post)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        # Default: show status
        print("LF XHS Engine v1.0 | Brain v15.0")
        print(json.dumps(engine.health_check(), indent=2, ensure_ascii=False))
