from __future__ import annotations

from wb_auto_replies.app.db.models import Feedback


KARMIC_STATES = {"wbRu", "reviewRequired", "rejected"}


class FeedbackClassifier:
    def classify(self, feedback: Feedback) -> str:
        if feedback.source_api == "archive":
            return "karmic"
        if feedback.answer_state_current in KARMIC_STATES and (feedback.text is None or feedback.text.strip() == ""):
            return "karmic"
        if feedback.text and feedback.text.strip():
            return "real"
        return "unknown"
