
# LF Academy - Meta OAuth One-Click Authorization
import sys, json, time, webbrowser, secrets, urllib.parse, threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).parent))

APP_ID = "4465664880321550"
APP_SECRET = "cc16171491c307d7f9dfac24e5261f04"
REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/callback"
GRAPH_API = "https://graph.facebook.com/v25.0"

SCOPES = ["pages_manage_posts", "pages_read_engagement", "pages_show_list", "pages_manage_metadata"]

class OAuthHandler(BaseHTTPRequestHandler):
    auth_code = None
    error_msg = None
    done = threading.Event()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/callback":
            if "code" in params:
                OAuthHandler.auth_code = params["code"][0]
                self._respond("OK - Authorization Success", "You may close this window.")
            elif "error" in params:
                OAuthHandler.error_msg = params.get("error_description", ["Unknown"])[0]
                self._respond("FAIL - Authorization Failed", OAuthHandler.error_msg)
            OAuthHandler.done.set()
        else:
            self.send_response(404); self.end_headers()

    def _respond(self, title, msg):
        html = f"<html><body style='font-family:sans-serif;text-align:center;padding-top:100px;'><h2>{title}</h2><p>{msg}</p></body></html>"
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args): pass

def api_get(url):
    try:
        with urlopen(Request(url), timeout=15) as resp:
            return {"ok": True, "data": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        return {"ok": False, "error": json.loads(e.read().decode("utf-8"))}

def main():
    print("=" * 55)
    print("  LF Academy - Meta OAuth One-Click Setup")
    print("  Browser will open. Click Allow to authorize.")
    print("=" * 55)
    print()

    # Step 1: Start server
    print("[1/4] Starting local server...")
    server = HTTPServer(("localhost", REDIRECT_PORT), OAuthHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"      Server started on port {REDIRECT_PORT}")

    # Step 2: Open browser
    state = secrets.token_hex(16)
    scope_str = ",".join(SCOPES)
    auth_url = (
        f"https://www.facebook.com/v25.0/dialog/oauth?"
        f"client_id={APP_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={scope_str}"
        f"&state={state}"
    )
    print(f"\n[2/4] Opening browser for authorization...")
    time.sleep(1)
    webbrowser.open(auth_url)

    # Step 3: Wait for callback
    print(f"\n[3/4] Waiting for authorization... (click Allow in browser)")
    OAuthHandler.done.wait(timeout=120)
    server.shutdown()

    if OAuthHandler.error_msg:
        print(f"\nFAILED: {OAuthHandler.error_msg}")
        return
    if not OAuthHandler.auth_code:
        print("\nFAILED: No authorization code received")
        return

    print("      Authorization code received!")

    # Step 4: Exchange code for tokens
    print(f"\n[4/4] Exchanging tokens...")

    # 4a: code -> short token
    url = (f"{GRAPH_API}/oauth/access_token?"
           f"client_id={APP_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
           f"&client_secret={APP_SECRET}&code={OAuthHandler.auth_code}")
    r = api_get(url)
    if not r["ok"]:
        print(f"      FAILED: {r.get('error', {})}")
        return
    short_token = r["data"]["access_token"]
    print("      Short token obtained")

    # 4b: short -> long token (60 days)
    url = (f"{GRAPH_API}/oauth/access_token?"
           f"grant_type=fb_exchange_token&client_id={APP_ID}"
           f"&client_secret={APP_SECRET}&fb_exchange_token={short_token}")
    r = api_get(url)
    if not r["ok"]:
        print(f"      FAILED: {r.get('error', {})}")
        return
    long_token = r["data"]["access_token"]
    days = r["data"].get("expires_in", 5184000) // 86400
    print(f"      Long token obtained (valid: {days} days)")

    # 4c: get page token
    url = f"{GRAPH_API}/me/accounts?access_token={long_token}"
    r = api_get(url)
    if not r["ok"]:
        print(f"      FAILED: {r.get('error', {})}")
        return
    pages = r["data"].get("data", [])
    if not pages:
        print("      FAILED: No pages found")
        return
    print(f"      Found {len(pages)} page(s)")

    # Select page
    if len(pages) == 1:
        selected = pages[0]
    else:
        for i, p in enumerate(pages):
            pname = p.get("name", "?")
            pid = p.get("id", "?")
            print(f"  [{i+1}] {pname} (ID: {pid})")
        idx = int(input(f"Select [1-{len(pages)}]: ")) - 1
        selected = pages[idx]

    # Save credentials
    from fb_api_client import CredentialManager, MetaAPIClient
    cred = CredentialManager()
    cred.set_page_credentials(
        page_id=selected["id"],
        page_name=selected["name"],
        access_token=selected.get("access_token", long_token),
        app_id=APP_ID,
        app_secret=APP_SECRET,
    )

    # Verify
    api = MetaAPIClient(cred)
    health = api.health_check()

    print()
    print("=" * 55)
    print("  SUCCESS! Authorization Complete!")
    print(f"  Page: {selected['name']}")
    print(f"  ID:   {selected['id']}")
    print(f"  Status: {'HEALTHY' if health['status'] == 'healthy' else 'CHECK NEEDED'}")
    print("=" * 55)
    print()
    print("Next commands:")
    print("  python fb_strategy/fb_content_pipeline.py generate")
    print("  python fb_strategy/fb_content_pipeline.py publish")

if __name__ == "__main__":
    main()
