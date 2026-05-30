# -*- coding: utf-8 -*-
"""Topic knowledge base for Socratic tutoring - stub module."""
import json, os

SOCRATIC_STRATEGIES = {
    "default": ["引導思考", "回歸基本概念", "逐步拆解", "驗證答案"],
    "equations": ["先理解等式意義", "思考逆向運算", "逐項化簡", "代入驗證"],
    "fractions": ["畫圖輔助理解", "找出公分母", "通分後計算", "約簡至最簡"],
    "geometry": ["畫圖標註已知", "回想相關公式", "代入計算", "檢查單位"],
    "percentages": ["確認基準值(100%)", "判斷增減方向", "計算變化量", "用原值驗證"],
}

COMMON_MISTAKES = {
    "equations": ["移項忘記變號", "只解一半", "忘記驗證"],
    "fractions": ["忘記通分", "分子分母搞亂", "答案未約簡"],
    "geometry": ["公式記錯", "單位不統一", "忘記平方"],
    "percentages": ["基準值搞錯", "增減方向錯誤", "連續變化基準不同"],
}

KEY_CONCEPTS = {
    "equations": ["等式兩邊平衡", "逆向運算", "代入驗證"],
    "fractions": ["等值分數", "通分", "約簡"],
    "geometry": ["面積公式", "體積公式", "周界公式"],
    "percentages": ["百分數=分數/100", "基準值", "變化率"],
}

def get_topic_knowledge(topic: str) -> dict:
    """Get knowledge base for a topic."""
    topic_lower = topic.lower() if topic else ""
    
    strategy_key = "default"
    for key in SOCRATIC_STRATEGIES:
        if key in topic_lower:
            strategy_key = key
            break
    
    return {
        "socratic": SOCRATIC_STRATEGIES.get(strategy_key, SOCRATIC_STRATEGIES["default"]),
        "common_mistakes": COMMON_MISTAKES.get(strategy_key, []),
        "key_concepts": KEY_CONCEPTS.get(strategy_key, []),
    }

def get_socratic_strategy(topic: str) -> list:
    """Get Socratic questioning strategy for a topic."""
    tk = get_topic_knowledge(topic)
    return tk.get("socratic", SOCRATIC_STRATEGIES["default"])

print("[topic_knowledge] Module loaded")
