# LF Academy — Meta API Token 設定精靈
# 引導用戶逐步獲取 Facebook Page Access Token

import sys, io, os, json, webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from fb_api_client import CredentialManager, MetaAPIClient, TokenManager

# ═══════════════════════════════════════════════════════

BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║      LF Academy — Meta API 全自動化設定精靈              ║
║      連接你的 Facebook 專頁，實現全自動發布              ║
╚══════════════════════════════════════════════════════════╝
"""

def print_step(num: int, title: str):
    print(f"\n{'='*60}")
    print(f" 步驟 {num}: {title}")
    print(f"{'='*60}")

def main():
    print(BANNER)
    
    cred = CredentialManager()
    
    # ── 步驟 0: 檢查現有設定 ──
    if cred.is_configured():
        info = cred.get_info()
        print("\n📍 發現現有設定:")
        print(f"   專頁: {info['page_name']} (ID: {info['page_id']})")
        print(f"   Token: {info['token_masked']}")
        print(f"   設定時間: {info['configured_at']}")
        
        api = MetaAPIClient(cred)
        health = api.health_check()
        
        if health.get("status") == "healthy":
            print(f"\n✅ API 連接正常！專頁「{health.get('page_name')}」- {health.get('followers', '?')} 位粉絲")
            print("\n如需重新設定，請刪除 fb_strategy/config/fb_credentials.json 後再執行")
            return
        
        print(f"\n⚠️ Token 可能已過期，將重新設定...")
    
    # ── 步驟 1: 說明所需準備 ──
    print_step(1, "前置準備")
    print("""
你需要以下其中一種方式獲取 Page Access Token：

【方式 A: Meta Business Suite (推薦 - 最簡單)】
  1. 打開 https://business.facebook.com/settings/system-users
  2. 點擊「新增」→ 建立「系統用戶」
  3. 分配「管理專頁」權限
  4. 在「產生存取憑證」中選擇你的專頁
  5. 複製產生的 Page Access Token
  
  所需權限: pages_manage_posts, pages_read_engagement, 
            pages_show_list, pages_manage_metadata

【方式 B: Graph API Explorer (快速測試)】
  1. 打開 https://developers.facebook.com/tools/explorer/
  2. 選擇你的 Meta App
  3. 在「權限」中添加: pages_manage_posts, pages_read_engagement
  4. 點擊「Generate Access Token」
  5. 在右側選擇你的專頁，獲取 Page Access Token
  ⚠️ 注意: 此 Token 有效期較短

【方式 C: 長期 Token (我幫你交換)】
  如果你有短期 User Token + App ID + App Secret，
  我可以用 TokenManager 自動交換為 60 天長期 Token。
""")
    
    # ── 步驟 2: 選擇方式 ──
    print_step(2, "選擇設定方式")
    print("""
  [1] 我已有 Page Access Token (直接輸入)
  [2] 我有 User Token + App ID + App Secret (自動交換長期Token)
  [3] 我有 User Token，幫我列出所有專頁
  [4] 打開 Meta Business Suite 設定頁面
  [5] 打開 Graph API Explorer
""")
    
    choice = input("請選擇 [1-5]: ").strip()
    
    if choice == "4":
        print("\n正在打開 Meta Business Suite...")
        webbrowser.open("https://business.facebook.com/settings/system-users")
        input("\n完成後按 Enter 繼續...")
        choice = "1"
    
    if choice == "5":
        print("\n正在打開 Graph API Explorer...")
        webbrowser.open("https://developers.facebook.com/tools/explorer/")
        input("\n完成後按 Enter 繼續...")
        choice = "1"
    
    # ── 步驟 3: 輸入憑證 ──
    if choice in ["1", "2", "3"]:
        print_step(3, "輸入憑證")
        
        if choice == "1":
            page_id = input("FB 專頁 ID (數字): ").strip()
            token = input("Page Access Token: ").strip()
            page_name = input("專頁名稱 (可選): ").strip() or "LF Academy"
            
            cred.set_page_credentials(
                page_id=page_id,
                page_name=page_name,
                access_token=token,
            )
        
        elif choice == "2":
            user_token = input("User Access Token: ").strip()
            app_id = input("App ID: ").strip()
            app_secret = input("App Secret: ").strip()
            
            print("\n🔄 正在交換長期 Token...")
            result = TokenManager.exchange_long_lived(user_token, app_id, app_secret)
            
            if result["success"]:
                long_token = result["data"]["access_token"]
                expires = result["data"].get("expires_in", "unknown")
                print(f"✅ 長期 Token 獲取成功 (有效期: {expires} 秒)")
                
                # 用長期 token 獲取專頁
                print("\n🔄 正在獲取專頁列表...")
                pages = TokenManager.get_all_page_tokens(long_token)
                
                if pages["success"]:
                    page_list = pages["data"].get("data", [])
                    if not page_list:
                        print("❌ 未找到任何管理的專頁")
                        return
                    
                    print("\n📋 找到以下專頁:")
                    for i, page in enumerate(page_list):
                        print(f"  [{i+1}] {page.get('name')} (ID: {page.get('id')}) - {page.get('category', '')}")
                    
                    idx = int(input(f"\n選擇專頁 [1-{len(page_list)}]: ")) - 1
                    selected = page_list[idx]
                    
                    cred.set_page_credentials(
                        page_id=selected["id"],
                        page_name=selected["name"],
                        access_token=selected.get("access_token", long_token),
                        app_id=app_id,
                        app_secret=app_secret,
                    )
        
        elif choice == "3":
            user_token = input("User Access Token: ").strip()
            
            print("\n🔄 正在獲取專頁列表...")
            pages = TokenManager.get_all_page_tokens(user_token)
            
            if pages["success"]:
                page_list = pages["data"].get("data", [])
                if not page_list:
                    print("❌ 未找到任何管理的專頁")
                    return
                
                print("\n📋 找到以下專頁:")
                for i, page in enumerate(page_list):
                    print(f"  [{i+1}] {page.get('name')} (ID: {page.get('id')}) - {page.get('category', '')}")
                
                idx = int(input(f"\n選擇專頁 [1-{len(page_list)}]: ")) - 1
                selected = page_list[idx]
                
                cred.set_page_credentials(
                    page_id=selected["id"],
                    page_name=selected["name"],
                    access_token=selected.get("access_token", user_token),
                )
    
    else:
        print("無效選擇")
        return
    
    # ── 步驟 4: 驗證 ──
    print_step(4, "驗證連接")
    
    api = MetaAPIClient(cred)
    health = api.health_check()
    
    print(f"\n健康檢查結果:")
    print(json.dumps(health, ensure_ascii=False, indent=2))
    
    if health.get("status") == "healthy":
        print(f"""
╔══════════════════════════════════════════════════════════╗
║  ✅ 設定成功！                                          ║
║                                                        ║
║  專頁: {health.get('page_name', 'N/A')}
║  粉絲: {health.get('followers', 'N/A')}
║                                                        ║
║  接下來可以:                                            ║
║  1. 產生內容: python fb_strategy/fb_content_pipeline.py generate  ║
║  2. 自動發布: python fb_strategy/fb_content_pipeline.py publish   ║
║  3. 查看數據: python fb_strategy/fb_api_client.py insights       ║
║  4. 手動發帖: python fb_strategy/fb_api_client.py post --message "測試"  ║
╚══════════════════════════════════════════════════════════╝
""")
    else:
        print("""
❌ 驗證失敗。可能原因:
  1. Token 無效或已過期
  2. 權限不足 (需要 pages_manage_posts, pages_read_engagement)
  3. Page ID 錯誤
  4. 專頁類型不支援 (需為「一般」或「企業」專頁)

請重新執行此設定精靈。
""")

if __name__ == "__main__":
    main()
