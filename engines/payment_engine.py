#!/usr/bin/env python3
"""
LF Payment Engine — Stripe 支付整合 + 會員管理
支援：Stripe Checkout、Webhook、Firebase 記錄同步
"""
import os
import json
import time
import hmac
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# ═══ Stripe 配置 ═══
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_API = "https://api.stripe.com/v1"
TIMEOUT = 30

# ═══ Idempotency Store (event ID dedup) ═══
_processed_events = set()  # In production, use DB/Redis with TTL

# ═══ 產品定價 ═══
PRICING = {
    "P3_monthly": {"name": "小三 P3 · 月付", "amount": 25000, "currency": "hkd", "interval": "month", "grade": "P3", "sessions_per_month": 4},
    "P4_monthly": {"name": "小四 P4 · 月付", "amount": 28000, "currency": "hkd", "interval": "month", "grade": "P4", "sessions_per_month": 4},
    "P5_monthly": {"name": "小五 P5 · 月付", "amount": 33000, "currency": "hkd", "interval": "month", "grade": "P5", "sessions_per_month": 4},
    "P6_monthly": {"name": "小六 P6 · 月付", "amount": 33000, "currency": "hkd", "interval": "month", "grade": "P6", "sessions_per_month": 4},
    "P3_annual":  {"name": "小三 P3 · 年繳(8折)", "amount": 240000, "currency": "hkd", "interval": "year", "grade": "P3", "sessions_per_month": 4},
    "P4_annual":  {"name": "小四 P4 · 年繳(8折)", "amount": 268800, "currency": "hkd", "interval": "year", "grade": "P4", "sessions_per_month": 4},
    "P5_annual":  {"name": "小五 P5 · 年繳(8折)", "amount": 316800, "currency": "hkd", "interval": "year", "grade": "P5", "sessions_per_month": 4},
    "P6_annual":  {"name": "小六 P6 · 年繳(8折)", "amount": 316800, "currency": "hkd", "interval": "year", "grade": "P6", "sessions_per_month": 4},
    "trial":      {"name": "免費試堂 · 1堂", "amount": 0, "currency": "hkd", "interval": "once", "grade": "any", "sessions_per_month": 1},
}


def _stripe_request(method: str, path: str, data: dict = None) -> dict:
    """呼叫 Stripe API"""
    if not STRIPE_SECRET_KEY:
        return {"error": "Stripe not configured", "_mock": True}

    url = f"{STRIPE_API}/{path}"
    body = urllib.parse.urlencode(data).encode("utf-8") if data else None

    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {STRIPE_SECRET_KEY}")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            return json.loads(error_body)
        except:
            return {"error": str(e), "body": error_body}


def create_checkout_session(plan_id: str, student_email: str = "", student_name: str = "",
                            success_url: str = "", cancel_url: str = "") -> dict:
    """
    建立 Stripe Checkout Session。
    前段 redirect 到 session.url 即可完成付款。
    """
    plan = PRICING.get(plan_id)
    if not plan:
        return {"error": f"Unknown plan: {plan_id}", "available_plans": list(PRICING.keys())}

    price_data = {
        "line_items[0][price_data][currency]": plan["currency"],
        "line_items[0][price_data][product_data][name]": f"霖楓學苑 · {plan['name']}",
        "line_items[0][price_data][unit_amount]": plan["amount"],
        "line_items[0][quantity]": "1",
        "mode": "subscription" if plan["interval"] in ("month", "year") else "payment",
        "metadata[plan_id]": plan_id,
        "metadata[grade]": plan["grade"],
        "metadata[student_name]": student_name,
    }

    if plan["interval"] in ("month", "year"):
        price_data["line_items[0][price_data][recurring][interval]"] = plan["interval"]

    if success_url:
        price_data["success_url"] = success_url
    else:
        price_data["success_url"] = "https://lfacademyhk.com/docs/payment-success.html"

    if cancel_url:
        price_data["cancel_url"] = cancel_url
    else:
        price_data["cancel_url"] = "https://lfacademyhk.com/docs/pricing.html"

    if student_email:
        price_data["customer_email"] = student_email

    if not STRIPE_SECRET_KEY:
        # Mock mode for development
        return {
            "mock": True,
            "mock_url": f"https://buy.stripe.com/test_mock_{plan_id}",
            "plan": plan,
            "message": "Stripe not configured. Set STRIPE_SECRET_KEY env var.",
        }

    return _stripe_request("POST", "checkout/sessions", price_data)


def get_checkout_session(session_id: str) -> dict:
    """查詢 checkout session 狀態"""
    if not STRIPE_SECRET_KEY:
        return {"mock": True, "status": "complete", "payment_status": "paid"}
    return _stripe_request("GET", f"checkout/sessions/{session_id}")


def _verify_stripe_signature(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature (HMAC-SHA256, constant-time compare, 300s tolerance).
    Reference: Stripe Webhooks End-to-End (2026) + Hookdeck Best Practices.
    """
    if not STRIPE_WEBHOOK_SECRET:
        return True  # Dev mode: no secret configured, allow all
    if not signature:
        return False

    try:
        parts = {}
        for part in signature.split(","):
            k, v = part.strip().split("=", 1)
            parts[k] = v
        timestamp = parts.get("t", "")
        sig_v1 = parts.get("v1", "")
        if not timestamp or not sig_v1:
            return False
        # Timestamp tolerance: 300 seconds
        if abs(int(time.time()) - int(timestamp)) > 300:
            return False
        # Recompute HMAC-SHA256
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
        expected = hmac.new(
            STRIPE_WEBHOOK_SECRET.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        # Constant-time comparison
        return hmac.compare_digest(expected, sig_v1)
    except Exception:
        return False


def handle_webhook(payload: bytes, signature: str) -> dict:
    """
    Process Stripe Webhook events.
    Step 1: Verify signature (CRITICAL security gate)
    Step 2: Parse event JSON
    Step 3: Idempotency check (event ID dedup)
    Step 4: Process by event type
    Step 5: Mark as processed
    Reference: Stripe Webhooks End-to-End (2026), Hookdeck Best Practices
    """
    # Step 1: Verify signature
    if STRIPE_WEBHOOK_SECRET and not _verify_stripe_signature(payload, signature):
        return {"error": "Invalid signature", "verified": False}

    # Step 2: Parse event
    try:
        event = json.loads(payload.decode("utf-8"))
    except Exception:
        return {"error": "Invalid JSON payload"}

    event_id = event.get("id", "")
    event_type = event.get("type", "")

    # Step 3: Idempotency check
    if event_id in _processed_events:
        return {"event": event_type, "processed": False, "reason": "duplicate_event", "event_id": event_id}

    obj = event.get("data", {}).get("object", {})
    result = {"event": event_type, "processed": False, "event_id": event_id}

    # Step 4: Process by event type
    if event_type == "checkout.session.completed":
        customer_email = obj.get("customer_details", {}).get("email", "") or obj.get("customer_email", "")
        metadata = obj.get("metadata", {})
        plan_id = metadata.get("plan_id", "")
        grade = metadata.get("grade", "")
        student_name = metadata.get("student_name", "")

        membership = {
            "email": customer_email,
            "plan": plan_id,
            "grade": grade,
            "student_name": student_name,
            "status": "active",
            "stripe_session_id": obj.get("id", ""),
            "stripe_customer_id": obj.get("customer", ""),
            "amount": obj.get("amount_total", 0) / 100,
            "currency": obj.get("currency", "hkd"),
            "created_at": datetime.now().isoformat(),
            "expiry": (datetime.now() + timedelta(days=30 if "monthly" in plan_id else 365)).isoformat(),
            "sessions_remaining": PRICING.get(plan_id, {}).get("sessions_per_month", 4),
        }

        result["membership"] = membership
        result["processed"] = True

    elif event_type == "customer.subscription.deleted":
        result["processed"] = True
        result["action"] = "cancel_membership"

    elif event_type == "invoice.payment_failed":
        result["processed"] = True
        result["action"] = "payment_failed_alert"

    # Step 5: Mark as processed (idempotency)
    if result["processed"]:
        _processed_events.add(event_id)
        # Keep set bounded (in production, use DB with TTL/auto-cleanup)
        if len(_processed_events) > 10000:
            _processed_events.clear()

    return result


def get_plans() -> list:
    """獲取所有方案清單（含試堂）"""
    plans = []
    for pid, plan in PRICING.items():
        plans.append({
            "id": pid,
            "name": plan["name"],
            "amount_hkd": plan["amount"] / 100,
            "interval": plan["interval"],
            "grade": plan["grade"],
            "sessions_per_month": plan["sessions_per_month"],
            "is_trial": pid == "trial",
        })
    return plans


def get_plan_by_grade(grade: str) -> list:
    """按年級篩選方案"""
    return [p for p in get_plans() if p["grade"] == grade or p["grade"] == "any"]


# ═══ 會員管理 (本地記錄，Firebase 同步) ═══
def create_trial_membership(student_email: str, student_name: str = "", grade: str = "") -> dict:
    """建立免費試堂會員"""
    trial = PRICING["trial"]
    return {
        "email": student_email,
        "student_name": student_name,
        "grade": grade,
        "plan": "trial",
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "expiry": (datetime.now() + timedelta(days=7)).isoformat(),
        "sessions_remaining": 1,
        "total_sessions": 1,
        "is_trial": True,
    }


def check_membership_status(membership: dict) -> dict:
    """檢查會員狀態並返回可用資訊"""
    if not membership:
        return {"status": "none", "message": "尚未成為會員", "can_trial": True}

    expiry_str = membership.get("expiry", "")
    sessions_left = membership.get("sessions_remaining", 0)

    try:
        expiry = datetime.fromisoformat(expiry_str)
        expired = expiry < datetime.now()
    except:
        expired = True

    if membership.get("status") != "active" or expired:
        return {
            "status": "expired",
            "message": "會員已過期" if expired else "會員已停用",
            "expired_on": expiry_str,
            "can_renew": True,
        }

    return {
        "status": "active",
        "plan": membership.get("plan", ""),
        "sessions_remaining": sessions_left,
        "expiry": expiry_str,
        "days_left": max(0, (expiry - datetime.now()).days) if not expired else 0,
        "message": f"會員有效，剩餘{sessions_left}堂",
    }