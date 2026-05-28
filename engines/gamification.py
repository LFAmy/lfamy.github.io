#!/usr/bin/env python3
"""LF AI Gamification Engine v2.0 — AI 動態難度調整 + 心流激勵"""
from datetime import date
import sys

sys.path.insert(0, r"G:\lam-fung-academy")
try:
    from lf_ai_brain import ai_analyze_student
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

BADGE_THRESHOLDS = [
    (0, "🥉 銅章"), (100, "🥈 銀章"), (300, "🥇 金章"),
    (600, "💎 白金"), (1000, "👑 鑽石"), (2000, "🌟 大師"),
    (5000, "🏆 傳奇"),
]

STREAK_MILESTONE = 5
STREAK_BONUS = 10
DAILY_BONUS = 25
DAILY_TARGET = 5

def get_badge(points: int) -> str:
    badge = "🥉 銅章"
    for threshold, name in BADGE_THRESHOLDS:
        if points >= threshold:
            badge = name
    return badge

def ai_dynamic_bonus(student_name: str, conn) -> dict:
    """AI 動態獎勵 — 根據學生狀態調整激勵強度"""
    if not AI_AVAILABLE:
        return {"dynamic_bonus": 0, "reason": "使用標準獎勵"}
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT q.topic, sp.score, sp.max_score, sp.status
            FROM student_progress sp
            JOIN questions q ON sp.question_id = q.id
            WHERE sp.student_name = %s
            ORDER BY sp.created_at DESC LIMIT 20
        """, (student_name,))
        rows = cur.fetchall()
        cur.close()
        
        if len(rows) < 5:
            return {"dynamic_bonus": 5, "reason": "新手鼓勵加成"}
        
        # Check recent performance trend
        recent_scores = [float(r[1] or 0) / max(float(r[2] or 1), 1) for r in rows[:5]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        if avg_recent < 0.4:
            return {"dynamic_bonus": 0, "reason": "建議先複習基礎"}
        elif avg_recent < 0.6:
            return {"dynamic_bonus": 8, "reason": "穩步進步中，額外鼓勵"}
        elif avg_recent < 0.8:
            return {"dynamic_bonus": 3, "reason": "表現良好，保持節奏"}
        else:
            return {"dynamic_bonus": 5, "reason": "優秀表現！挑戰更高難度"}
    except:
        return {"dynamic_bonus": 0, "reason": "使用標準獎勵"}

def update_gamification(student_name: str, is_correct: bool, conn):
    cur = conn.cursor()
    today = date.today()

    cur.execute(
        "SELECT points, streak, badge, last_played, daily_date, daily_correct, daily_bonus_claimed FROM gamification WHERE student_name = %s",
        (student_name,),
    )
    row = cur.fetchone()

    if row:
        points, streak, badge, last_played, daily_date, daily_correct, daily_bonus_claimed = row
    else:
        points = streak = 0
        last_played = daily_date = None
        daily_correct = 0
        daily_bonus_claimed = False

    is_daily = daily_date == today
    if not is_daily:
        daily_correct = 0
        daily_bonus_claimed = False
        daily_date = today

    # Base points
    earned = 10 if is_correct else 2
    
    # Streak
    if is_correct:
        if last_played and (today - last_played).days == 1:
            streak += 1
        elif not last_played or (today - last_played).days > 1:
            streak = 1
    else:
        streak = 0
    
    bonus = 0
    if streak > 0 and streak % STREAK_MILESTONE == 0:
        bonus += STREAK_BONUS
    
    if is_correct:
        daily_correct += 1
    
    if is_daily and daily_correct >= DAILY_TARGET and not daily_bonus_claimed:
        bonus += DAILY_BONUS
        daily_bonus_claimed = True
    
    # AI dynamic bonus
    ai_bonus_info = ai_dynamic_bonus(student_name, conn) if AI_AVAILABLE else {"dynamic_bonus": 0}
    bonus += ai_bonus_info.get("dynamic_bonus", 0)
    
    points += earned + bonus
    badge = get_badge(points)

    cur.execute(
        """INSERT INTO gamification
               (student_name, points, streak, badge, last_played,
                daily_date, daily_correct, daily_bonus_claimed)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (student_name) DO UPDATE SET
               points = EXCLUDED.points,
               streak = EXCLUDED.streak,
               badge = EXCLUDED.badge,
               last_played = EXCLUDED.last_played,
               daily_date = EXCLUDED.daily_date,
               daily_correct = EXCLUDED.daily_correct,
               daily_bonus_claimed = EXCLUDED.daily_bonus_claimed""",
        (student_name, points, streak, badge, today,
         daily_date, daily_correct, daily_bonus_claimed),
    )
    conn.commit()
    cur.close()

    return {
        "student_name": student_name,
        "points": points,
        "streak": streak,
        "badge": badge,
        "earned": earned,
        "bonus": bonus,
        "daily_correct": daily_correct,
        "daily_target": DAILY_TARGET,
        "daily_bonus_claimed": daily_bonus_claimed,
        "ai_boost": ai_bonus_info,
    }

def get_leaderboard(conn, limit: int = 10) -> list:
    cur = conn.cursor()
    cur.execute(
        "SELECT student_name, points, streak, badge FROM gamification ORDER BY points DESC LIMIT %s",
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    return [
        {"rank": i + 1, "student_name": r[0], "points": r[1],
         "streak": r[2], "badge": r[3]}
        for i, r in enumerate(rows)
    ]
