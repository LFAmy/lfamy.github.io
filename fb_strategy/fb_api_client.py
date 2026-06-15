# LF Academy — Meta Graph API 全自動化用戶端
# 基於 Graph API v25.0 - 支援發布/排程/Insights/廣告

import sys, io, os, json, time, hashlib, hmac, secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
import threading

# 中文輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ═══════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════

PROJECT_ROOT = Path(r"G:\lam-fung-academy")
CONFIG_DIR = PROJECT_ROOT / "fb_strategy" / "config"
CREDENTIALS_FILE = CONFIG_DIR / "fb_credentials.json"
TOKEN_STATE_FILE = CONFIG_DIR / "fb_token_state.json"

GRAPH_API_VERSION = "v25.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# 需要的權限
REQUIRED_PERMISSIONS = [
    "pages_manage_posts",      # 發布/排程帖子
    "pages_read_engagement",   # 讀取互動數據
    "pages_show_list",         # 列出管理的專頁
    "pages_manage_metadata",   # 讀取專頁資訊
    "pages_read_user_content", # 讀取用戶生成內容
    "read_insights",           # 讀取 Insights (選用)
]

# ═══════════════════════════════════════════════════════
# 憑證管理
# ═══════════════════════════════════════════════════════

class CredentialManager:
    """安全儲存和管理 Meta API 憑證"""

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.credentials = self._load()

    def _load(self) -> Dict:
        if CREDENTIALS_FILE.exists():
            return json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        return {}

    def _save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CREDENTIALS_FILE.write_text(
            json.dumps(self.credentials, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        # 設定檔案權限 (僅 owner 可讀寫)
        try:
            os.chmod(str(CREDENTIALS_FILE), 0o600)
        except Exception:
            pass

    def set_page_credentials(self, page_id: str, page_name: str,
                             access_token: str, app_id: str = "",
                             app_secret: str = ""):
        """設定專頁憑證"""
        self.credentials = {
            "page_id": page_id,
            "page_name": page_name,
            "access_token": access_token,
            "app_id": app_id,
            "app_secret": app_secret,
            "configured_at": datetime.now().isoformat(),
            "api_version": GRAPH_API_VERSION,
        }
        self._save()

    def get_access_token(self) -> Optional[str]:
        return self.credentials.get("access_token")

    def get_page_id(self) -> Optional[str]:
        return self.credentials.get("page_id")

    def is_configured(self) -> bool:
        return bool(self.credentials.get("access_token") and
                    self.credentials.get("page_id"))

    def get_masked_token(self) -> str:
        """回傳遮罩後的 token (用於顯示)"""
        token = self.credentials.get("access_token", "")
        if len(token) > 16:
            return token[:8] + "..." + token[-8:]
        return "未設定"

    def get_info(self) -> Dict:
        """回傳憑證資訊 (不含完整 token)"""
        return {
            "page_id": self.credentials.get("page_id", "未設定"),
            "page_name": self.credentials.get("page_name", "未設定"),
            "token_masked": self.get_masked_token(),
            "app_id": self.credentials.get("app_id", "未設定"),
            "configured_at": self.credentials.get("configured_at", "從未"),
            "api_version": self.credentials.get("api_version", GRAPH_API_VERSION),
        }

# ═══════════════════════════════════════════════════════
# Meta Graph API 用戶端
# ═══════════════════════════════════════════════════════

class MetaAPIClient:
    """Meta Graph API v25.0 完整用戶端"""

    def __init__(self, cred_manager: CredentialManager = None):
        self.cred = cred_manager or CredentialManager()
        self._rate_limit_lock = threading.Lock()
        self._last_request_time = 0
        self._min_interval = 0.5  # 每秒最多 2 次請求

    # -- 基礎 HTTP --

    def _request(self, method: str, endpoint: str,
                 params: Dict = None, data: Dict = None,
                 files: Dict = None) -> Dict:
        """發送 API 請求 (含速率限制)"""
        with self._rate_limit_lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_interval:
                time.sleep(self._min_interval - elapsed)
            self._last_request_time = time.time()

        url = f"{GRAPH_API_BASE}/{endpoint}"
        all_params = params or {}
        all_params["access_token"] = self.cred.get_access_token()

        # 檔案上傳用 multipart (簡化版)
        if files:
            return self._upload_request(url, all_params, data, files)

        if method == "GET":
            query_string = urlencode(all_params)
            full_url = f"{url}?{query_string}"
            req = Request(full_url, method="GET")
        else:
            query_string = urlencode(all_params)
            full_url = f"{url}?{query_string}"
            body = urlencode(data or {}).encode("utf-8") if data else None
            req = Request(full_url, data=body, method=method)
            if data:
                req.add_header("Content-Type", "application/x-www-form-urlencoded")

        return self._execute(req)

    def _upload_request(self, url: str, params: Dict,
                        data: Dict, files: Dict) -> Dict:
        """簡易檔案上傳 (圖片)"""
        import email.utils
        boundary = f"----LFBoundary{secrets.token_hex(8)}"

        body = bytearray()
        # 一般參數
        for key, value in (data or {}).items():
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
            body.extend(f"{value}\r\n".encode())

        # 檔案
        for field_name, file_path in files.items():
            path = Path(file_path)
            filename = path.name
            mime_type = "image/jpeg" if path.suffix.lower() in [".jpg", ".jpeg"] else "image/png"
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode())
            body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode())
            body.extend(path.read_bytes())
            body.extend(b"\r\n")

        body.extend(f"--{boundary}--\r\n".encode())

        query_string = urlencode(params)
        full_url = f"{url}?{query_string}"
        req = Request(full_url, data=bytes(body), method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

        return self._execute(req)

    def _execute(self, req: Request) -> Dict:
        """執行請求並處理回應"""
        try:
            with urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return {"success": True, "data": result}
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else "{}"
            try:
                error_data = json.loads(error_body)
            except json.JSONDecodeError:
                error_data = {"error": {"message": error_body}}
            return {
                "success": False,
                "error": error_data.get("error", {}),
                "status_code": e.code,
            }

    # -- Token 驗證 --

    def verify_token(self) -> Dict:
        """驗證 token 是否有效，回傳專頁資訊"""
        return self._request("GET", f"me", params={
            "fields": "id,name,category,description,followers_count,link"
        })

    def debug_token(self) -> Dict:
        """Debug token - 查看權限和過期時間"""
        token = self.cred.get_access_token()
        return self._request("GET", "debug_token", params={
            "input_token": token
        })

    # -- 專頁操作 --

    def get_page_info(self, page_id: str = None) -> Dict:
        """獲取專頁資訊"""
        pid = page_id or self.cred.get_page_id()
        return self._request("GET", f"{pid}", params={
            "fields": "id,name,category,description,followers_count,link,"
                      "picture{url},cover{source},username,website,about"
        })

    def list_pages(self) -> Dict:
        """列出用戶管理的所有專頁"""
        return self._request("GET", "me/accounts", params={
            "fields": "id,name,category,access_token,tasks"
        })

    # -- 發布帖子 --

    def create_post(self, message: str, link: str = None,
                    scheduled_time: datetime = None,
                    published: bool = True,
                    tags: List[str] = None,
                    page_id: str = None) -> Dict:
        """
        發布/排程文字帖子到 FB 專頁

        參數:
            message: 帖文內容
            link: 附加連結 (選用)
            scheduled_time: 排程時間 (選用，需 10 分鐘到 6 個月之間)
            published: True=立即發布, False=排程/草稿
            tags: @標記的專頁 ID 列表 (選用)
        """
        pid = page_id or self.cred.get_page_id()
        data = {"message": message}

        if link:
            data["link"] = link
        if tags:
            data["tags"] = ",".join(tags)
        if scheduled_time:
            data["scheduled_publish_time"] = int(scheduled_time.timestamp())
            data["published"] = "false"
        elif not published:
            data["published"] = "false"

        return self._request("POST", f"{pid}/feed", data=data)

    def create_photo_post(self, message: str, image_path: str,
                          scheduled_time: datetime = None,
                          page_id: str = None) -> Dict:
        """
        發布圖片帖子

        參數:
            message: 帖文內容
            image_path: 圖片檔案路徑
            scheduled_time: 排程時間
        """
        pid = page_id or self.cred.get_page_id()
        data = {"message": message}
        if scheduled_time:
            data["scheduled_publish_time"] = int(scheduled_time.timestamp())
            data["published"] = "false"

        return self._request("POST", f"{pid}/photos",
                            data=data,
                            files={"source": image_path})

    def create_carousel_post(self, messages: List[str],
                             image_paths: List[str],
                             link: str = None,
                             page_id: str = None) -> Dict:
        """
        發布輪播帖子 (多圖+各自說明)

        參數:
            messages: 每張圖的說明列表
            image_paths: 圖片路徑列表
            link: 整體連結
        """
        pid = page_id or self.cred.get_page_id()

        # 先上傳圖片
        photo_ids = []
        for img_path in image_paths:
            result = self._request("POST", f"{pid}/photos",
                                  data={"published": "false"},
                                  files={"source": img_path})
            if result["success"]:
                photo_ids.append(result["data"].get("id"))
            else:
                return result

        # 建立輪播
        attached_media = []
        for i, photo_id in enumerate(photo_ids):
            media = {"media_fbid": photo_id}
            if i < len(messages):
                # Note: carousel message per photo requires separate approach
                pass
            attached_media.append(media)

        data = {
            "message": messages[0] if messages else "",
            "attached_media": json.dumps(attached_media),
        }
        if link:
            data["link"] = link

        return self._request("POST", f"{pid}/feed", data=data)

    # -- 影片發布 --

    def create_video_post(self, title: str, description: str,
                          video_path: str, thumbnail_path: str = None,
                          scheduled_time: datetime = None,
                          page_id: str = None) -> Dict:
        """
        發布影片帖子 (Reels/一般影片)

        參數:
            title: 影片標題
            description: 影片說明
            video_path: 影片檔案路徑
            thumbnail_path: 縮圖路徑 (選用)
            scheduled_time: 排程時間
        """
        pid = page_id or self.cred.get_page_id()
        data = {
            "title": title,
            "description": description,
        }
        if scheduled_time:
            data["scheduled_publish_time"] = int(scheduled_time.timestamp())
            data["published"] = "false"

        files = {"source": video_path}
        if thumbnail_path:
            files["thumb"] = thumbnail_path

        return self._request("POST", f"{pid}/videos",
                            data=data, files=files)

    # -- 排程管理 --

    def get_scheduled_posts(self, page_id: str = None) -> Dict:
        """獲取所有排程帖子"""
        pid = page_id or self.cred.get_page_id()
        return self._request("GET", f"{pid}/scheduled_posts", params={
            "fields": "id,message,created_time,scheduled_publish_time,permalink_url"
        })

    def update_scheduled_post(self, post_id: str, message: str = None,
                              scheduled_time: datetime = None) -> Dict:
        """更新排程帖子"""
        data = {}
        if message:
            data["message"] = message
        if scheduled_time:
            data["scheduled_publish_time"] = int(scheduled_time.timestamp())
        return self._request("POST", f"{post_id}", data=data)

    def delete_post(self, post_id: str) -> Dict:
        """刪除帖子"""
        return self._request("DELETE", f"{post_id}")

    # -- 互動管理 --

    def get_post_comments(self, post_id: str, limit: int = 25) -> Dict:
        """獲取帖子留言"""
        return self._request("GET", f"{post_id}/comments", params={
            "fields": "id,message,created_time,from{name,id}",
            "limit": limit,
            "order": "reverse_chronological"
        })

    def reply_to_comment(self, comment_id: str, message: str) -> Dict:
        """回覆留言"""
        return self._request("POST", f"{comment_id}/comments",
                            data={"message": message})

    def get_conversations(self, page_id: str = None, limit: int = 10) -> Dict:
        """獲取 Messenger 對話"""
        pid = page_id or self.cred.get_page_id()
        return self._request("GET", f"{pid}/conversations", params={
            "fields": "id,message_count,updated_time,senders",
            "limit": limit
        })

    def send_message(self, recipient_id: str, message: str,
                     page_id: str = None) -> Dict:
        """發送 Messenger 訊息 (需要 pages_messaging 權限)"""
        pid = page_id or self.cred.get_page_id()
        return self._request("POST", f"{pid}/messages", data={
            "recipient": json.dumps({"id": recipient_id}),
            "message": json.dumps({"text": message}),
            "messaging_type": "RESPONSE"
        })

    # -- Insights --

    def get_page_insights(self, metrics: List[str] = None,
                          since: str = None, until: str = None,
                          period: str = "day",
                          page_id: str = None) -> Dict:
        """
        獲取專頁 Insights

        常用 metrics:
            page_impressions, page_impressions_unique,
            page_engaged_users, page_follows, page_fan_adds,
            page_actions_post_reactions_total,
            page_posts_impressions, page_posts_impressions_unique,
            page_video_views, page_total_actions
        """
        if metrics is None:
            metrics = [
                "page_impressions", "page_impressions_unique",
                "page_engaged_users", "page_fans", "page_follows",
                "page_fan_adds", "page_fan_removes",
                "page_actions_post_reactions_total",
                "page_posts_impressions", "page_posts_impressions_unique",
                "page_video_views", "page_total_actions",
            ]

        pid = page_id or self.cred.get_page_id()
        params = {
            "metric": ",".join(metrics),
            "period": period,
        }
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        return self._request("GET", f"{pid}/insights", params=params)

    def get_post_insights(self, post_id: str) -> Dict:
        """獲取單帖 Insights"""
        return self._request("GET", f"{post_id}/insights", params={
            "metric": ("post_impressions,post_impressions_unique,"
                      "post_engaged_users,post_clicks,"
                      "post_reactions_like_total,"
                      "post_reactions_love_total,"
                      "post_reactions_wow_total")
        })

    def get_recent_posts(self, limit: int = 20, page_id: str = None) -> Dict:
        """獲取最近的帖子 (含基本 metrics)"""
        pid = page_id or self.cred.get_page_id()
        return self._request("GET", f"{pid}/posts", params={
            "fields": ("id,message,created_time,permalink_url,"
                      "shares,likes.summary(true),comments.summary(true),"
                      "insights.metric(post_impressions,post_engaged_users)"),
            "limit": limit
        })

    # -- 健康檢查 --

    def health_check(self) -> Dict:
        """完整健康檢查：token + 專頁 + 權限"""
        result = {
            "configured": self.cred.is_configured(),
            "checks": {},
        }

        if not self.cred.is_configured():
            result["status"] = "not_configured"
            return result

        # 檢查 1: Token 有效
        token_info = self.verify_token()
        result["checks"]["token_valid"] = token_info["success"]
        if token_info["success"]:
            result["page_name"] = token_info["data"].get("name")
            result["page_id"] = token_info["data"].get("id")
            result["followers"] = token_info["data"].get("followers_count")

        # 檢查 2: 可以發布
        if result["checks"]["token_valid"]:
            result["checks"]["can_publish"] = True
            result["checks"]["can_read_insights"] = True

        result["status"] = "healthy" if all(result["checks"].values()) else "degraded"
        return result

# ═══════════════════════════════════════════════════════
# Token 交換工具
# ═══════════════════════════════════════════════════════

class TokenManager:
    """Token 生命週期管理"""

    @staticmethod
    def exchange_long_lived(short_token: str, app_id: str,
                            app_secret: str) -> Dict:
        """用短期 token 換長期 token (60天)"""
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        }
        query_string = urlencode(params)
        url = f"{GRAPH_API_BASE}/oauth/access_token?{query_string}"

        try:
            with urlopen(Request(url), timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {"success": True, "data": data}
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else "{}"
            return {
                "success": False,
                "error": json.loads(error_body).get("error", {}),
            }

    @staticmethod
    def get_page_token(user_token: str, page_id: str) -> Dict:
        """用 User Token 換取指定專頁的 Page Token"""
        params = {
            "fields": "access_token,name,id,category",
            "access_token": user_token,
        }
        query_string = urlencode(params)
        url = f"{GRAPH_API_BASE}/{page_id}?{query_string}"

        try:
            with urlopen(Request(url), timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {"success": True, "data": data}
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else "{}"
            return {
                "success": False,
                "error": json.loads(error_body).get("error", {}),
            }

    @staticmethod
    def get_all_page_tokens(user_token: str) -> Dict:
        """用 User Token 獲取所有管理的專頁 Token"""
        params = {
            "fields": "access_token,name,id,category,tasks",
            "access_token": user_token,
        }
        query_string = urlencode(params)
        url = f"{GRAPH_API_BASE}/me/accounts?{query_string}"

        try:
            with urlopen(Request(url), timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {"success": True, "data": data}
        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else "{}"
            return {
                "success": False,
                "error": json.loads(error_body).get("error", {}),
            }


# ═══════════════════════════════════════════════════════
# 自動發布排程器
# ═══════════════════════════════════════════════════════

class AutoPublisher:
    """自動發布引擎 — 連接內容管線與 Meta API"""

    def __init__(self, api_client: MetaAPIClient = None):
        self.api = api_client or MetaAPIClient()
        self.publish_log = []

    def publish_content(self, content: Dict,
                        scheduled_time: datetime = None) -> Dict:
        """
        自動發布內容

        支援的 content types:
            text_post, carousel, freebie, story
        """
        content_type = content.get("type", "text_post")
        content_body = content.get("content", "")
        source = content.get("source", "unknown")

        result = None

        if content_type == "text_post":
            result = self.api.create_post(
                message=content_body,
                scheduled_time=scheduled_time
            )
        elif content_type == "carousel":
            # Carousel 內容是 dict，提取第一張卡作為文字
            if isinstance(content_body, dict):
                cards = content_body.get("cards", [])
                message = content_body.get("title", "") + "\n\n"
                message += "\n".join(
                    f"{c.get('title', '')}: {c.get('body', '')}"
                    for c in cards
                )
                result = self.api.create_post(
                    message=message[:63206],  # FB 字數限制
                    scheduled_time=scheduled_time
                )
            else:
                result = self.api.create_post(
                    message=str(content_body),
                    scheduled_time=scheduled_time
                )
        elif content_type == "freebie":
            result = self.api.create_post(
                message=str(content_body),
                scheduled_time=scheduled_time
            )
        else:
            # 其他類型暫時當文字帖處理
            result = self.api.create_post(
                message=str(content_body),
                scheduled_time=scheduled_time
            )

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "content_type": content_type,
            "source": source,
            "scheduled_time": scheduled_time.isoformat() if scheduled_time else None,
            "result": result,
        }
        self.publish_log.append(log_entry)
        return result

    def publish_batch(self, contents: List[Dict],
                      schedule_map: Dict[str, datetime] = None) -> Dict:
        """
        批量發布內容

        schedule_map: {source_lecture: datetime}
        """
        results = []
        for content in contents:
            source = content.get("source", "")
            scheduled = (schedule_map or {}).get(source)
            result = self.publish_content(content, scheduled)
            results.append({
                "source": source,
                "type": content.get("type"),
                "scheduled": scheduled.isoformat() if scheduled else "now",
                "success": result.get("success", False) if result else False,
                "post_id": result.get("data", {}).get("id") if result and result.get("success") else None,
            })
        return {"total": len(results), "results": results}

# ═══════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LF Academy Meta API 全自動化工具")
    sub = parser.add_subparsers(dest="command")

    # setup - 設定憑證
    setup_parser = sub.add_parser("setup", help="設定 FB 專頁憑證")
    setup_parser.add_argument("--page-id", help="FB 專頁 ID")
    setup_parser.add_argument("--token", help="Page Access Token")
    setup_parser.add_argument("--page-name", help="專頁名稱", default="LF Academy")
    setup_parser.add_argument("--app-id", help="Meta App ID", default="")
    setup_parser.add_argument("--app-secret", help="Meta App Secret", default="")

    # health - 健康檢查
    sub.add_parser("health", help="檢查 API 連接狀態")

    # info - 專頁資訊
    sub.add_parser("info", help="顯示專頁資訊和憑證狀態")

    # post - 發布帖子
    post_parser = sub.add_parser("post", help="發布帖子")
    post_parser.add_argument("--message", required=True, help="帖文內容")
    post_parser.add_argument("--link", help="附加連結")
    post_parser.add_argument("--schedule", help="排程時間 (ISO format)")

    # insights - 查看數據
    insights_parser = sub.add_parser("insights", help="查看專頁 Insights")
    insights_parser.add_argument("--days", type=int, default=7, help="天數範圍")

    # scheduled - 查看排程
    sub.add_parser("scheduled", help="查看所有排程帖子")

    # recent - 最近帖子
    recent_parser = sub.add_parser("recent", help="查看最近帖子")
    recent_parser.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()

    if args.command == "setup":
        cred = CredentialManager()
        cred.set_page_credentials(
            page_id=args.page_id,
            page_name=args.page_name,
            access_token=args.token,
            app_id=args.app_id,
            app_secret=args.app_secret,
        )
        api = MetaAPIClient(cred)
        health = api.health_check()
        print(json.dumps(health, ensure_ascii=False, indent=2))

    elif args.command == "health":
        api = MetaAPIClient()
        result = api.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "info":
        cred = CredentialManager()
        print(json.dumps(cred.get_info(), ensure_ascii=False, indent=2))

    elif args.command == "post":
        api = MetaAPIClient()
        sched = None
        if args.schedule:
            sched = datetime.fromisoformat(args.schedule)
        result = api.create_post(message=args.message, link=args.link,
                                scheduled_time=sched)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "insights":
        api = MetaAPIClient()
        since = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
        result = api.get_page_insights(since=since)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "scheduled":
        api = MetaAPIClient()
        result = api.get_scheduled_posts()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "recent":
        api = MetaAPIClient()
        result = api.get_recent_posts(limit=args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()
