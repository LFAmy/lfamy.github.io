# LF Academy (霖楓學苑) -- Facebook 內容自動化管線

# 基於 v15.0 生產級工程模式 - API-First 設計 - 休眠引擎激活
# 從 172 講義庫自動生成 FB 內容的完整管線

import sys, io, os, json, re, hashlib, time, shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 中文輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ═══════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════

PROJECT_ROOT = Path(r"G:\lam-fung-academy")
LECTURE_ROOT = PROJECT_ROOT / "講義"
FB_OUTPUT_DIR = PROJECT_ROOT / "fb_strategy" / "output"
CONTENT_CALENDAR = PROJECT_ROOT / "fb_strategy" / "content_calendar.json"
STATE_FILE = PROJECT_ROOT / "fb_strategy" / "pipeline_state.json"

# FB 內容類型
CONTENT_TYPES = {
    "carousel":      {"format": "輪播廣告",  "platform": "page",   "ratio": "40%"},
    "reels_script":  {"format": "Reels 短影片", "platform": "page",   "ratio": "25%"},
    "poll":          {"format": "互動投票",   "platform": "group",  "ratio": "10%"},
    "freebie":       {"format": "免費資源",   "platform": "page",   "ratio": "10%"},
    "story":         {"format": "Story",      "platform": "page",   "ratio": "5%"},
    "live_outline":  {"format": "Live 流程",   "platform": "page",   "ratio": "5%"},
    "text_post":     {"format": "圖文帖",     "platform": "both",   "ratio": "5%"},
}

# 每週內容日曆模板
WEEKLY_SCHEDULE = {
    "Monday":    {"theme": "數學解題日",   "types": ["text_post", "reels_script", "story"]},
    "Tuesday":   {"theme": "呈分試攻略日", "types": ["carousel", "text_post", "story"]},
    "Wednesday": {"theme": "家長教室日",   "types": ["text_post", "poll", "story"]},
    "Thursday":  {"theme": "陷阱題診斷日", "types": ["poll", "reels_script", "freebie"]},
    "Friday":    {"theme": "社群互動日",   "types": ["text_post", "story"]},
    "Saturday":  {"theme": "成果展示日",   "types": ["carousel", "live_outline"]},
    "Sunday":    {"theme": "教育科技日",   "types": ["text_post", "story"]},
}

# ═══════════════════════════════════════════════════════════
# 核心: 內容提取器
# ═══════════════════════════════════════════════════════════

class LectureContentExtractor:
    """從講義 HTML 提取 FB 內容所需的關鍵區塊"""

    KEY_MARKERS = {
        "why_box":     ['why-box', 'WHY BOX', '核心概念', 'why'],
        "trap_example": ['陷阱', 'trap', '常見錯誤', 'misconception'],
        "sspa_tag":    ['SSPA', '呈分試', '考試'],
        "parent_summary": ['家長摘要', 'parent', '家長'],
        "learning_objective": ['學習目標', 'learning objective', '今日目標'],
        "story_context": ['故事情境', '故事', '情境'],
        "answer_key":  ['AK', '答案', 'answer'],
    }

    def __init__(self):
        self.extracted_cache = {}

    def extract(self, html_path: Path) -> Dict:
        """從講義提取所有關鍵內容區塊"""
        cache_key = str(html_path)
        if cache_key in self.extracted_cache:
            return self.extracted_cache[cache_key]

        content = html_path.read_text(encoding="utf-8")
        soup = self._parse_html(content)

        extracted = {
            "source_file": html_path.name,
            "source_path": str(html_path),
            "grade": self._extract_grade(html_path),
            "topic": self._extract_topic(content),
            "why_box": self._extract_section(soup, self.KEY_MARKERS["why_box"]),
            "trap_example": self._extract_section(soup, self.KEY_MARKERS["trap_example"]),
            "sspa_relevance": self._extract_section(soup, self.KEY_MARKERS["sspa_tag"]),
            "parent_summary": self._extract_section(soup, self.KEY_MARKERS["parent_summary"]),
            "learning_objective": self._extract_section(soup, self.KEY_MARKERS["learning_objective"]),
            "story_context": self._extract_section(soup, self.KEY_MARKERS["story_context"]),
            "key_terms": self._extract_key_terms(content),
            "extracted_at": datetime.now().isoformat(),
        }

        self.extracted_cache[cache_key] = extracted
        return extracted

    def _parse_html(self, content: str):
        """簡易 HTML 解析 (不依賴 bs4)"""
        # 移除 script 和 style
        text = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        # 移除 HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # 清理多餘空白
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_grade(self, path: Path) -> str:
        """從路徑提取年級"""
        parts = path.parts
        for p in parts:
            if p in ("P3", "P4", "P5", "P6"):
                return p
        return "Unknown"

    def _extract_topic(self, content: str) -> str:
        """從 HTML title 提取課題"""
        match = re.search(r"<title>.*?(\S+)\s*\|", content)
        if match:
            return match.group(1)
        return "Unknown Topic"

    def _extract_section(self, text: str, markers: List[str]) -> Optional[str]:
        """提取標記附近的內容段落"""
        text_lower = text.lower()
        for marker in markers:
            idx = text_lower.find(marker.lower())
            if idx >= 0:
                start = max(0, idx - 50)
                end = min(len(text), idx + 300)
                snippet = text[start:end].strip()
                return snippet
        return None

    def _extract_key_terms(self, content: str) -> List[str]:
        """提取數學關鍵詞"""
        math_terms = [
            "小數", "分數", "百分數", "面積", "體積", "周界",
            "代數", "方程", "速率", "比例", "整除", "因數",
            "倍數", "平均數", "四則運算", "圖形", "統計", "概率"
        ]
        found = []
        text_lower = content.lower()
        for term in math_terms:
            if term in text_lower or term in content:
                found.append(term)
        return found


# ═══════════════════════════════════════════════════════════
# AI 內容生成器 (調用 lf_ai_brain)
# ═══════════════════════════════════════════════════════════

class FBContentGenerator:
    """AI 驅動的 FB 內容生成"""

    VOICE_PROFILE = """
    LF Academy 品牌聲音檔案:
    - 語調: 溫暖專業 - 香港家長語氣 - 中英夾雜自然
    - 節奏: 短句 - 直接 - 有重點
    - 禁止: 空泛形容詞 - 假裝興奮 - 教育術語堆砌
    - 特色: 「阿仔」「阿女」「媽咪」「爹哋」等親切稱呼
    - 數據: 永遠用具體數字而非「很多」「大量」
    - CTA: 自然引導，不做壓力推銷
    """

    def __init__(self):
        self.generator_available = self._check_ai_engine()

    def _check_ai_engine(self) -> bool:
        """檢查 lf_ai_brain 是否可用"""
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            from engines.lf_ai_brain import ai_tutor_chat
            self.brain_chat = ai_tutor_chat
            return True
        except Exception as e:
            print(f"⚠️ lf_ai_brain 不可用: {e}")
            print("  使用模板模式 (template-only)")
            return False

    def generate(self, extracted: Dict, content_type: str) -> Dict:
        """生成特定類型的 FB 內容"""
        if self.generator_available:
            return self._generate_with_ai(extracted, content_type)
        else:
            return self._generate_from_template(extracted, content_type)

    def _generate_with_ai(self, extracted: Dict, content_type: str) -> Dict:
        """使用 AI 引擎生成"""
        prompt = self._build_prompt(extracted, content_type)
        try:
            result = self.brain_chat(prompt, mode="content_writer")
            return {
                "type": content_type,
                "source": extracted["source_file"],
                "prompt": prompt,
                "content": result,
                "generated_at": datetime.now().isoformat(),
                "method": "ai",
            }
        except Exception as e:
            print(f"AI 生成失敗: {e}，改用模板")
            return self._generate_from_template(extracted, content_type)

    def _generate_from_template(self, extracted: Dict, content_type: str) -> Dict:
        """使用模板生成"""
        templates = {
            "text_post": self._tpl_text_post,
            "carousel": self._tpl_carousel,
            "reels_script": self._tpl_reels,
            "poll": self._tpl_poll,
            "freebie": self._tpl_freebie,
            "story": self._tpl_story,
            "live_outline": self._tpl_live,
        }

        tpl_func = templates.get(content_type, self._tpl_text_post)
        content = tpl_func(extracted)

        return {
            "type": content_type,
            "source": extracted["source_file"],
            "content": content,
            "generated_at": datetime.now().isoformat(),
            "method": "template",
        }

    def _build_prompt(self, extracted: Dict, content_type: str) -> str:
        """構建 AI prompt"""
        config = CONTENT_TYPES.get(content_type, {})
        return f"""
你是 LF Academy (霖楓學苑) 的 FB 內容編輯。品牌聲音：{self.VOICE_PROFILE}

請根據以下講義內容，生成一個 {config.get('format', content_type)} 格式的 FB 帖文：

講義資料:
- 年級: {extracted.get('grade', '')}
- 課題: {extracted.get('topic', '')}
- 核心概念: {extracted.get('why_box', '')}
- 陷阱例題: {extracted.get('trap_example', '')}
- 家長摘要: {extracted.get('parent_summary', '')}
- 關鍵詞: {', '.join(extracted.get('key_terms', []))}

要求:
- 使用香港繁體中文
- 適合香港小學家長閱讀
- 包含具體數字/例子
- 自然引導互動 (非硬銷)
- 加入相關 hashtag (#呈分試 #小學數學 #{extracted.get('grade', '')} #霖楓學苑)

請直接輸出帖文內容，不要加說明。
"""

    # -- 模板函數 --

    def _tpl_text_post(self, e: Dict) -> str:
        topic = e.get("topic", "數學")
        grade = e.get("grade", "P6")
        why = e.get("why_box", "")
        return f"""📐 【{grade} {topic}】核心概念一覽

{self._truncate(why, 200) if why else f"今日同大家拆解 {topic} 嘅核心概念，幫小朋友打好基礎！"}

💡 家長貼士：
教小朋友呢個課題時，最緊要係理解背後嘅原理，而唔係死記公式。試下用生活化嘅例子解釋，小朋友會更容易明白！

想攞相關練習？留言「+1」我 PM 你 👇

#呈分試 #{grade}數學 #{topic} #小學數學 #霖楓學苑"""

    def _tpl_carousel(self, e: Dict) -> Dict:
        topic = e.get("topic", "數學課題")
        return {
            "title": f"📊 {e.get('grade', 'P6')} {topic} -- 5分鐘速成",
            "cards": [
                {"title": "🤔 常見誤解", "body": "90% 學生都理解錯嘅概念..."},
                {"title": "🔍 正確理解", "body": "其實正確嘅諗法係..."},
                {"title": "📝 例題示範", "body": "一齊睇吓呢條例題..."},
                {"title": "⚠️ 陷阱提醒", "body": "考試最常出錯嘅位..."},
                {"title": "✅ 即時測試", "body": "試下做呢題，留言答案！"},
            ],
        }

    def _tpl_reels(self, e: Dict) -> str:
        topic = e.get("topic", "數學")
        return f"""🎬 Reels 腳本: {e.get('grade', 'P6')} {topic} 15秒解題

[0-3秒 - Hook]
「你小朋友識唔識呢條數？👇」

[3-10秒 - 教學]
「只需要記住呢個步驟...」

[10-13秒 - 結果]
「咁就搞掂！簡單過你諗嘅！」

[13-15秒 - CTA]
「想攞更多練習？Follow 我哋！」

字幕: 全程繁體中文
配樂: 輕快節奏
字幕大小: 大字體，手機友善"""

    def _tpl_poll(self, e: Dict) -> str:
        topic = e.get("topic", "數學課題")
        return f"""📊 【家長投票】

你覺得 {topic} 對小朋友嚟講難唔難？

🟢 好易，一學就識
🟡 中等，要多少少練習
🔴 好難，成日都搞唔清楚

投票話我知！之後我會針對最難嘅部分做詳細講解 💪

#小學數學 #家長心聲"""

    def _tpl_freebie(self, e: Dict) -> str:
        topic = e.get("topic", "數學")
        grade = e.get("grade", "P6")
        return f"""🎁 【免費下載】{grade} {topic} -- 精選練習紙

✅ 5 題精選練習 (由淺入深)
✅ 詳細解題步驟
✅ 常見陷阱標記
✅ A4 打印即用

👉 立即下載: [連結]
⏰ 限時開放至 { (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d') }

Tag 一位家長朋友，一齊攞！👨‍👩‍👧

#免費練習 #{grade}數學 #呈分試 #霖楓學苑"""

    def _tpl_story(self, e: Dict) -> str:
        return f"""📸 Story 素材建議:
- 背景: {e.get('topic', '數學')} 相關圖解
- 文字: 「聽日教你呢個課題！」
- 貼圖: 倒數貼圖
- CTA: 「向上滑睇更多」"""

    def _tpl_live(self, e: Dict) -> str:
        topic = e.get("topic", "數學")
        return f"""🔴 Live 流程: {topic} 親子工作坊

⏱ 總時長: 20-25 分鐘

[0-3分] 開場
- 歡迎大家
- 今日主題介紹
- 呼籲留言互動

[3-12分] 核心教學
- 概念講解 (用實物/動畫)
- 例題示範
- 常見錯誤展示

[12-18分] 互動環節
- 即時出題，觀眾留言答案
- 選出最佳答案
- 解答觀眾問題

[18-20分] 總結+CTA
- 今日重點回顧
- 免費資源介紹
- 下次 Live 預告"""

    def _truncate(self, text: str, max_len: int) -> str:
        if not text:
            return ""
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= max_len:
            return text
        return text[:max_len] + "..."

# ═══════════════════════════════════════════════════════════
# 內容排程器
# ═══════════════════════════════════════════════════════════

class ContentScheduler:
    """管理內容日曆和排程"""

    def __init__(self):
        self.calendar = self._load_calendar()

    def _load_calendar(self) -> Dict:
        if CONTENT_CALENDAR.exists():
            return json.loads(CONTENT_CALENDAR.read_text(encoding="utf-8"))
        return {"weeks": {}, "generated_at": None}

    def generate_weekly_plan(self, lectures: List[Path], week_start: datetime) -> Dict:
        """根據可用講義生成一週內容計劃"""
        week_key = week_start.strftime("%Y-W%W")
        plan = {
            "week": week_key,
            "start_date": week_start.isoformat(),
            "days": {},
        }

        lectures_iter = iter(lectures)
        for day_name, schedule in WEEKLY_SCHEDULE.items():
            day_plan = {
                "theme": schedule["theme"],
                "posts": [],
            }
            for content_type in schedule["types"]:
                try:
                    lecture_path = next(lectures_iter)
                    day_plan["posts"].append({
                        "type": content_type,
                        "source_lecture": str(lecture_path.relative_to(LECTURE_ROOT)),
                        "scheduled_time": self._get_post_time(day_name),
                    })
                except StopIteration:
                    break
            plan["days"][day_name] = day_plan

        self.calendar["weeks"][week_key] = plan
        self._save_calendar()
        return plan

    def _get_post_time(self, day: str) -> str:
        """根據日期返回最佳發布時間"""
        times = {
            "Monday": "07:30",
            "Tuesday": "07:30",
            "Wednesday": "07:30",
            "Thursday": "07:30",
            "Friday": "07:30",
            "Saturday": "10:00",
            "Sunday": "10:00",
        }
        return times.get(day, "08:00")

    def _save_calendar(self):
        CONTENT_CALENDAR.parent.mkdir(parents=True, exist_ok=True)
        CONTENT_CALENDAR.write_text(
            json.dumps(self.calendar, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

# ═══════════════════════════════════════════════════════════
# 品質閘道
# ═══════════════════════════════════════════════════════════

class QualityGate:
    """內容品質檢查"""

    CHECKS = {
        "has_chinese": lambda c: bool(re.search(r'[\u4e00-\u9fff]', str(c))),
        "has_hashtag": lambda c: '#' in str(c),
        "no_empty_claims": lambda c: len(str(c)) > 20,
        "has_cta": lambda c: any(w in str(c).lower() for w in ['留言', '下載', 'follow', '了解更多', 'pm', 'dm', '👇']),
        "no_banned_words": lambda c: not any(w in str(c) for w in [
            'revolutionary', 'game-changer', 'revolutionize', 'cutting-edge'
        ]),
    }

    @classmethod
    def validate(cls, content: Dict) -> Tuple[bool, Dict]:
        """檢查內容品質"""
        results = {}
        content_str = str(content.get("content", ""))

        for check_name, check_fn in cls.CHECKS.items():
            try:
                results[check_name] = check_fn(content_str)
            except Exception:
                results[check_name] = False

        passed = all(results.values())
        return passed, results

    @classmethod
    def validate_batch(cls, contents: List[Dict]) -> Dict:
        """批量驗證"""
        report = {"total": len(contents), "passed": 0, "failed": 0, "details": []}
        for c in contents:
            passed, checks = cls.validate(c)
            if passed:
                report["passed"] += 1
            else:
                report["failed"] += 1
            report["details"].append({
                "source": c.get("source", "unknown"),
                "type": c.get("type", "unknown"),
                "passed": passed,
                "checks": checks,
            })
        return report

# ═══════════════════════════════════════════════════════════
# 增量同步引擎 (避免重複生成)
# ═══════════════════════════════════════════════════════════

class IncrementalSyncEngine:
    """Hash-based 變更檢測，只處理新增/修改的講義"""

    def __init__(self):
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {"processed": {}, "last_sync": None}

    def _save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def get_pending_lectures(self, lecture_dir: Path) -> List[Path]:
        """獲取未處理或已修改的講義"""
        pending = []
        for html_file in lecture_dir.rglob("*.html"):
            # 跳過非講義檔案
            if any(skip in html_file.parts for skip in ["_svg", "assets", "backup"]):
                continue

            file_hash = self._hash_file(html_file)
            file_key = str(html_file.relative_to(LECTURE_ROOT))

            if file_key not in self.state["processed"]:
                pending.append(html_file)
            elif self.state["processed"][file_key] != file_hash:
                pending.append(html_file)

        return pending

    def mark_processed(self, file_path: Path):
        """標記已處理"""
        file_key = str(file_path.relative_to(PROJECT_ROOT))
        self.state["processed"][file_key] = self._hash_file(file_path)
        self.state["last_sync"] = datetime.now().isoformat()
        self._save_state()

    def _hash_file(self, path: Path) -> str:
        """計算檔案 hash"""
        return hashlib.md5(path.read_bytes()).hexdigest()

# ═══════════════════════════════════════════════════════════
# 主管線
# ═══════════════════════════════════════════════════════════

class FBContentPipeline:
    """
    LF Academy Facebook 內容自動化管線

    用法:
        pipeline = FBContentPipeline()
        
        # 掃描待處理講義
        pipeline.scan()
        
        # 生成一週內容
        pipeline.generate_week()
        
        # 只生成特定內容類型
        pipeline.generate_type("reels_script", count=5)
        
        # 導出內容日曆
        pipeline.export_calendar()
    """

    def __init__(self):
        self.extractor = LectureContentExtractor()
        self.generator = FBContentGenerator()
        self.scheduler = ContentScheduler()
        self.sync = IncrementalSyncEngine()
        self.quality = QualityGate()

    def scan(self) -> Dict:
        """掃描講義庫，回報待處理狀態"""
        pending = self.sync.get_pending_lectures(LECTURE_ROOT)
        return {
            "total_lectures": len(list(LECTURE_ROOT.rglob("*.html"))),
            "pending": len(pending),
            "last_sync": self.sync.state.get("last_sync"),
            "pending_files": [str(p.relative_to(PROJECT_ROOT)) for p in pending[:10]],
        }

    def generate_week(self, week_start: Optional[datetime] = None) -> Dict:
        """生成一週的完整內容"""
        if week_start is None:
            week_start = datetime.now()

        # 獲取待處理講義
        pending = self.sync.get_pending_lectures(LECTURE_ROOT)
        if not pending:
            return {"error": "沒有待處理的講義", "status": "up_to_date"}

        # 生成一週計劃
        plan = self.scheduler.generate_weekly_plan(pending, week_start)

        # 提取並生成內容
        generated = []
        for day_name, day_plan in plan.get("days", {}).items():
            for post in day_plan.get("posts", []):
                lecture_path = LECTURE_ROOT / post["source_lecture"]
                if lecture_path.exists():
                    extracted = self.extractor.extract(lecture_path)
                    content = self.generator.generate(extracted, post["type"])
                    generated.append(content)

        # 品質閘道
        qc_report = self.quality.validate_batch(generated)

        # 保存輸出
        output = {
            "plan": plan,
            "contents": generated,
            "quality_report": qc_report,
            "generated_at": datetime.now().isoformat(),
        }

        self._save_output(output)
        return output

    def generate_type(self, content_type: str, count: int = 5) -> List[Dict]:
        """生成指定類型的內容"""
        if content_type not in CONTENT_TYPES:
            return [{"error": f"未知內容類型: {content_type}"}]

        pending = self.sync.get_pending_lectures(LECTURE_ROOT)
        results = []

        for lecture_path in pending[:count]:
            extracted = self.extractor.extract(lecture_path)
            content = self.generator.generate(extracted, content_type)
            passed, checks = self.quality.validate(content)
            content["quality_passed"] = passed
            content["quality_checks"] = checks
            results.append(content)

        return results


    def publish_week(self, week_data: Dict = None) -> Dict:
        """發布一週內容到 FB (使用 Meta API)"""
        try:
            from fb_api_client import MetaAPIClient, AutoPublisher
        except ImportError:
            return {"error": "fb_api_client.py 未找到，請確保在同目錄下"}

        api = MetaAPIClient()
        if not api.cred.is_configured():
            return {"error": "FB 憑證未設定，請先執行: python fb_strategy/fb_api_client.py setup"}

        # 健康檢查
        health = api.health_check()
        if health["status"] != "healthy":
            return {"error": "API 未就緒", "health": health}

        publisher = AutoPublisher(api)

        if week_data is None:
            # 從最新生成中讀取
            output_dir = FB_OUTPUT_DIR
            batches = sorted(output_dir.glob("batch_*.json"), reverse=True)
            if not batches:
                return {"error": "沒有已生成的內容，先執行 generate"}
            week_data = json.loads(batches[0].read_text(encoding="utf-8"))

        contents = week_data.get("contents", [])
        plan = week_data.get("plan", {})

        # 建立排程對應
        schedule_map = {}
        for day_name, day_plan in plan.get("days", {}).items():
            for post in day_plan.get("posts", []):
                source = post.get("source_lecture")
                time_str = post.get("scheduled_time")
                if source and time_str:
                    # 計算實際發布日期
                    day_offset = list(plan["days"].keys()).index(day_name)
                    publish_date = datetime.now() + timedelta(days=day_offset)
                    hour, minute = map(int, time_str.split(":"))
                    publish_datetime = publish_date.replace(
                        hour=hour, minute=minute, second=0, microsecond=0
                    )
                    schedule_map[source] = publish_datetime

        result = publisher.publish_batch(contents, schedule_map)
        return result

    def export_calendar(self, weeks: int = 4) -> Path:
        """導出內容日曆為 Markdown"""
        md = ["# LF Academy Facebook 內容日曆\n"]
        md.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

        for week_key, week_data in self.scheduler.calendar.get("weeks", {}).items():
            md.append(f"## {week_key} ({week_data.get('start_date', '')})\n")
            md.append("| 日期 | 主題 | 內容類型 | 來源講義 |")
            md.append("|------|------|----------|----------|")
            for day_name, day_plan in week_data.get("days", {}).items():
                for post in day_plan.get("posts", []):
                    md.append(
                        f"| {day_name} | {day_plan['theme']} | "
                        f"{post['type']} | {post['source_lecture']} |"
                    )
            md.append("")

        output_path = FB_OUTPUT_DIR / f"calendar_{datetime.now().strftime('%Y%m%d')}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(md), encoding="utf-8")
        return output_path

    def _save_output(self, output: Dict):
        """保存生成結果"""
        FB_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = FB_OUTPUT_DIR / f"batch_{timestamp}.json"
        output_path.write_text(
            json.dumps(output, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"✅ 輸出已保存: {output_path}")

# ═══════════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LF Academy FB 內容自動化管線")
    parser.add_argument("action", choices=["scan", "generate", "export", "status", "publish"],
                        help="動作: scan(掃描) / generate(生成一週) / export(導出日曆) / status(狀態)")
    parser.add_argument("--type", help="內容類型 (僅 generate 時可用)")
    parser.add_argument("--count", type=int, default=5, help="生成數量")
    
    args = parser.parse_args()
    pipeline = FBContentPipeline()

    if args.action == "scan":
        result = pipeline.scan()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.action == "generate":
        if args.type:
            results = pipeline.generate_type(args.type, args.count)
            print(f"生成 {len(results)} 件 {args.type} 內容")
            for r in results:
                qc = "✅" if r.get("quality_passed") else "❌"
                print(f"  {qc} {r['source']}")
        else:
            result = pipeline.generate_week()
            qc = result.get("quality_report", {})
            print(f"一週內容已生成: {qc.get('passed', 0)}/{qc.get('total', 0)} 通過品質檢查")

    elif args.action == "export":
        path = pipeline.export_calendar()
        print(f"內容日曆已導出: {path}")

    elif args.action == "publish":
        result = pipeline.publish_week()
        if result.get("error"):
            sys.stderr.write(f"[ERROR] Publish failed: {result['error']}\n")
        else:
            sys.stderr.write(f"[OK] Published {result['total']} items\n")
            for r in result.get("results", []):
                status = "OK" if r.get("success") else "FAIL"
                sys.stderr.write(f"  [{status}] {r['source']} ({r['type']})\n")

    elif args.action == "status":
        scan = pipeline.scan()
        print(f"📊 LF Academy FB 管線狀態")
        print(f"  總講義數: {scan['total_lectures']}")
        print(f"  待處理: {scan['pending']}")
        print(f"  最後同步: {scan['last_sync']}")
        print(f"\n🔧 AI 引擎: {'✅ 可用' if pipeline.generator.generator_available else '⚠️ 模板模式'}")
        print(f"📅 已計劃週數: {len(pipeline.scheduler.calendar.get('weeks', {}))}")
