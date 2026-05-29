#!/usr/bin/env python3
"""LF Socratic Session Manager — Multi-turn dialogue state tracker for AI Tutor"""
import time
import uuid

# In-memory session store (persists for server lifetime)
_sessions = {}

class SocraticSession:
    """Tracks a single Socratic tutoring session with full dialogue context."""

    def __init__(self, student_name="", question_id=None, question_text="", topic="", difficulty=""):
        self.session_id = str(uuid.uuid4())[:8]
        self.student_name = student_name
        self.question_id = question_id
        self.question_text = question_text
        self.topic = topic
        self.difficulty = difficulty
        self.dialogue = []  # List of {role, content}
        self.hint_level = 0
        self.correct_answer = None
        self.start_time = time.time()
        self.misconceptions_detected = []
        self.attempts = 0
        self.resolved = False

    def add_message(self, role, content):
        """Add a message to the dialogue history."""
        self.dialogue.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        if role == "user":
            self.attempts += 1

    def get_context(self, last_n=6):
        """Get recent dialogue context for AI prompts."""
        recent = self.dialogue[-last_n:] if len(self.dialogue) > last_n else self.dialogue
        return "\n".join([f"{m['role'].upper()}: {m['content']}" for m in recent])

    def next_hint(self):
        """Increment hint level and return current level."""
        self.hint_level = min(self.hint_level + 1, 5)
        return self.hint_level

    def mark_resolved(self):
        self.resolved = True

    def elapsed(self):
        return int(time.time() - self.start_time)

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "student_name": self.student_name,
            "question_id": self.question_id,
            "topic": self.topic,
            "difficulty": self.difficulty,
            "hint_level": self.hint_level,
            "attempts": self.attempts,
            "resolved": self.resolved,
            "dialogue_length": len(self.dialogue),
            "elapsed_sec": self.elapsed(),
            "misconceptions": self.misconceptions_detected,
        }


def create_session(student_name="", question_id=None, question_text="", topic="", difficulty=""):
    """Create a new Socratic session."""
    session = SocraticSession(
        student_name=student_name,
        question_id=question_id,
        question_text=question_text,
        topic=topic,
        difficulty=difficulty
    )
    _sessions[session.session_id] = session
    return session


def get_session(session_id):
    """Retrieve an existing session by ID."""
    return _sessions.get(session_id)


def end_session(session_id):
    """Remove a session and return summary."""
    session = _sessions.pop(session_id, None)
    if session:
        return session.to_dict()
    return None


def active_sessions():
    """Return count of active sessions."""
    return len(_sessions)