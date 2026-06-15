#!/usr/bin/env python3
"""
frellmapi Bridge v1.0 — OpenAI-compatible proxy for LF Academy
Bridges http://localhost:3001/v1 → DeepSeek API
Drop-in replacement for the Node.js frellmapi server
"""
import json
from _config.secrets import FRELLMAPI_KEY, urllib.request, urllib.error, sys, io, os
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DEEPSEEK_KEY = "sk-86ee7fd32bd347a4a8e67e965a7fe50d"
DEEPSEEK_URL = "https://api.deepseek.com/v1"
PORT = 3001

MODELS = [
    {"id": "deepseek-v4-flash", "object": "model", "owned_by": "deepseek"},
    {"id": "deepseek-reasoner", "object": "model", "owned_by": "deepseek"},
    {"id": "nvidia/nemotron-3-super-120b-a12b:free", "object": "model", "owned_by": "nvidia"},
    {"id": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free", "object": "model", "owned_by": "nvidia"},
    {"id": "@cf/qwen/qwen3-30b-a3b-fp8", "object": "model", "owned_by": "cloudflare"},
    {"id": "@cf/meta/llama-4-scout-17b-16e-instruct", "object": "model", "owned_by": "cloudflare"},
    {"id": "deepseek-ai/deepseek-v4-pro", "object": "model", "owned_by": "deepseek"},
    {"id": "auto", "object": "model", "owned_by": "frellmapi"},
]

class FrellmAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silent
    
    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/v1/models':
            self._send_json({"object": "list", "data": MODELS})
        elif self.path == '/api/health' or self.path == '/health':
            self._send_json({"status": "ok", "bridge": "deepseek", "models": len(MODELS)})
        elif self.path == '/api/settings/api-key':
            self._send_json({"apiKey": FRELLMAPI_KEY})
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
        except:
            self._send_json({"error": "Invalid JSON"}, 400)
            return
        
        if self.path == '/v1/chat/completions':
            self._proxy_chat(data)
        elif self.path == '/api/settings/api-key/regenerate':
            self._send_json({"apiKey": FRELLMAPI_KEY})
        else:
            self._send_json({"error": f"Not found: {self.path}"}, 404)
    
    def _proxy_chat(self, data):
        model = data.get("model", "deepseek-v4-flash")
        messages = data.get("messages", [])
        max_tokens = data.get("max_tokens", 500)
        temperature = data.get("temperature", 0.7)
        
        # Map frellmapi model names to DeepSeek
        deepseek_model = "deepseek-v4-flash"
        if "reasoning" in model or "reasoner" in model:
            deepseek_model = "deepseek-reasoner"
        
        req_body = json.dumps({
            "model": deepseek_model,
            "messages": messages,
            "max_tokens": min(max_tokens, 4000),
            "temperature": temperature
        }).encode()
        
        req = urllib.request.Request(
            f"{DEEPSEEK_URL}/chat/completions",
            data=req_body,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                result = json.loads(resp.read())
            
            # Add model info that frellmapi expects
            result["model"] = model
            self._send_json(result)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            self._send_json({"error": f"DeepSeek error: {error_body[:200]}"}, e.code)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', PORT), FrellmAPIHandler)
    print(f"frellmapi Bridge v1.0 → DeepSeek API")
    print(f"Listening on http://0.0.0.0:{PORT}/v1")
    print(f"Models: {len(MODELS)} registered")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        print("Shutdown.")
