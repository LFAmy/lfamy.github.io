# -*- coding: utf-8 -*-
"""Feedback engine for AI marking."""

class FeedbackResult:
    """Result object with attribute access for mark_engine compatibility."""
    def __init__(self, status="ok", score=10, message="", hint=None, related_topics=None, suggested_practice=None):
        self.status = status
        self.score = score
        self.message = message
        self.hint = hint
        self.related_topics = related_topics or []
        self.suggested_practice = suggested_practice or []

class FeedbackEngine:
    def __init__(self):
        pass

    def generate(self, result, question_id, student_answer):
        """Called by mark_engine - returns FeedbackResult with .status etc."""
        score = getattr(result, 'score', 0) if not isinstance(result, dict) else result.get('score', 5)
        max_score = getattr(result, 'max_score', 10) if not isinstance(result, dict) else result.get('max_score', 10)
        correct = score >= max_score * 0.8

        if correct:
            return FeedbackResult(
                status="correct",
                score=score,
                message="Excellent! Your answer is correct.",
                hint=None
            )
        return FeedbackResult(
            status="incorrect",
            score=score,
            message="Keep practicing! Review the steps.",
            hint="Try reviewing the key concepts for this topic.",
            related_topics=["algebra", "equations"],
            suggested_practice=["practice_basic", "practice_intermediate"]
        )

    def generate_feedback(self, student_answer, model_answer, question="", max_score=None):
        sa = (student_answer or "").strip().lower()
        ma = (model_answer or "").strip().lower()
        if sa == ma:
            return FeedbackResult(status="correct", score=max_score or 10, message="Excellent!")
        return FeedbackResult(status="incorrect", score=1, message="Not quite.", hint="Try again.")

    def batch_mark(self, answers_list):
        return [self.generate_feedback(a.get("student_answer",""), a.get("model_answer","")) for a in answers_list]

    def close(self):
        pass
