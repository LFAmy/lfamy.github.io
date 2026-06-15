#!/usr/bin/env python3
"""LF Academy MAB Flow-Zone Engine v1.0 — Multi-Armed Bandit Adaptive Learning
Maintains optimal difficulty (85% success rate = flow zone) using Thompson Sampling.
Balances Exploration (new topics) vs Exploitation (weak topics)."""

import sys, os, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class MABFlowZone:
    """Multi-Armed Bandit for topic selection in the flow zone."""
    
    def __init__(self, alpha_prior=2.0, beta_prior=2.0):
        self.topics = {}  # {topic: {alpha, beta, last_seen}}
        self.alpha_prior = alpha_prior
        self.beta_prior = beta_prior
        self.flow_target = 0.85  # Target success rate for flow
    
    def update(self, topic, success):
        """Update topic statistics after an attempt."""
        if topic not in self.topics:
            self.topics[topic] = {
                "alpha": self.alpha_prior,
                "beta": self.beta_prior,
                "attempts": 0,
                "successes": 0,
            }
        
        t = self.topics[topic]
        t["attempts"] += 1
        if success:
            t["successes"] += 1
            t["alpha"] += 1
        else:
            t["beta"] += 1
    
    def thompson_sample(self, topic):
        """Sample from Beta distribution for a topic."""
        if topic not in self.topics:
            t = {"alpha": self.alpha_prior, "beta": self.beta_prior}
        else:
            t = self.topics[topic]
        return random.betavariate(t["alpha"], t["beta"])
    
    def select_topic(self, available_topics, top_n=3):
        """Select best topic using Thompson Sampling.
        Returns: [(topic, score, reason), ...]"""
        if not available_topics:
            return []
        
        # Sample each topic
        samples = []
        for topic in available_topics:
            score = self.thompson_sample(topic)
            # Distance from flow zone target
            flow_distance = abs(0.85 - score)
            # Prioritize topics close to but below flow target (sweet spot for learning)
            if score < 0.6:
                priority = "critical"  # Needs work
            elif score < 0.8:
                priority = "learning"  # In learning zone
            elif score < 0.9:
                priority = "flow"      # Flow zone!
            else:
                priority = "mastered"  # Move on
            
            samples.append((topic, score, flow_distance, priority))
        
        # Sort: prioritize learning zone first, then critical, then flow, then mastered
        priority_order = {"learning": 0, "critical": 1, "flow": 2, "mastered": 3}
        samples.sort(key=lambda x: (priority_order.get(x[3], 99), x[2]))
        
        result = []
        for topic, score, dist, priority in samples[:top_n]:
            result.append({
                "topic": topic,
                "estimated_mastery": round(score, 3),
                "flow_distance": round(dist, 3),
                "priority": priority,
                "recommendation": self._recommend_action(priority, score),
            })
        
        return result
    
    def _recommend_action(self, priority, score):
        if priority == "critical":
            return "重點複習 + 陷阱題診斷"
        elif priority == "learning":
            return "漸進練習 + 提示輔助"
        elif priority == "flow":
            return "挑戰題 + 計時作答"
        else:
            return "進階應用題 + 綜合測驗"
    
    def get_flow_report(self):
        """Generate flow zone analysis report."""
        if not self.topics:
            return {"status": "no_data", "message": "No topics practiced yet"}
        
        topics_list = []
        for topic, t in self.topics.items():
            if t["attempts"] > 0:
                mastery = t["successes"] / t["attempts"]
                topics_list.append({
                    "topic": topic,
                    "mastery": round(mastery, 3),
                    "attempts": t["attempts"],
                    "in_flow": 0.75 <= mastery <= 0.90,
                })
        
        topics_list.sort(key=lambda x: x["mastery"])
        
        flow_count = sum(1 for t in topics_list if t["in_flow"])
        critical = sum(1 for t in topics_list if t["mastery"] < 0.6)
        mastered = sum(1 for t in topics_list if t["mastery"] >= 0.9)
        
        return {
            "total_topics": len(topics_list),
            "flow_zone_topics": flow_count,
            "critical_topics": critical,
            "mastered_topics": mastered,
            "flow_zone_pct": round(flow_count / len(topics_list) * 100, 1) if topics_list else 0,
            "topics": topics_list,
        }

    def to_dict(self):
        """Serialize state for storage."""
        return {
            "topics": self.topics,
            "flow_target": self.flow_target,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Deserialize from stored state."""
        mab = cls()
        mab.topics = data.get("topics", {})
        mab.flow_target = data.get("flow_target", 0.85)
        return mab


def get_flowzone_recommendation(student_name, conn):
    """API-friendly: Get flow-zone topic recommendations for a student."""
    cur = conn.cursor()
    cur.execute("""
        SELECT q.topic,
               COUNT(*) FILTER (WHERE sp.status='CORRECT') as correct,
               COUNT(*) as total
        FROM student_progress sp
        JOIN questions q ON sp.question_id = q.id
        WHERE sp.student_name = %s
        GROUP BY q.topic
        ORDER BY q.topic
    """, (student_name,))
    rows = cur.fetchall()
    cur.close()
    
    mab = MABFlowZone()
    available_topics = set()
    
    for topic, correct, total in rows:
        available_topics.add(topic)
        successes = correct or 0
        failures = (total - correct) if total > correct else 0
        # Seed MAB from historical data
        for _ in range(successes):
            mab.update(topic, True)
        for _ in range(failures):
            mab.update(topic, False)
    
    if not available_topics:
        return {"status": "no_data", "message": "No practice history yet"}
    
    # Get recommendations
    recommendations = mab.select_topic(list(available_topics), top_n=5)
    flow_report = mab.get_flow_report()
    
    return {
        "student": student_name,
        "recommendations": recommendations,
        "flow_report": flow_report,
        "strategy": "Thompson Sampling (Beta-Bernoulli MAB)",
        "flow_target": 0.85,
    }


if __name__ == "__main__":
    # Quick simulation test
    mab = MABFlowZone()
    topics = ["分數加法", "小數乘法", "面積計算", "方程入門", "體積概念"]
    
    # Simulate some practice
    import random
    random.seed(42)
    
    print("=== MAB Flow-Zone Simulation ===")
    for _ in range(30):
        topic = random.choice(topics)
        # Simulate different mastery levels per topic
        true_mastery = {"分數加法": 0.9, "小數乘法": 0.5, "面積計算": 0.75, "方程入門": 0.3, "體積概念": 0.95}
        success = random.random() < true_mastery[topic]
        mab.update(topic, success)
    
    recs = mab.select_topic(topics, top_n=5)
    for r in recs:
        print(f"  {r['topic']}: mastery={r['estimated_mastery']}, priority={r['priority']}, action={r['recommendation']}")
    
    report = mab.get_flow_report()
    print(f"\nFlow Report: {report['flow_zone_topics']}/{report['total_topics']} in flow zone ({report['flow_zone_pct']}%)")
