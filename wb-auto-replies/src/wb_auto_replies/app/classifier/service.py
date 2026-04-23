from __future__ import annotations

from wb_auto_replies.app.db.models import Feedback


class FeedbackClassifier:
    def classify(self, feedback: Feedback) -> str:
        has_text = bool(feedback.text and feedback.text.strip())
        has_pros = bool(feedback.pros and feedback.pros.strip())
        has_cons = bool(feedback.cons and feedback.cons.strip())
        has_stars = feedback.stars is not None

        if has_stars and not has_text and not has_pros and not has_cons:
            return "karmic"
        if has_text or has_pros or has_cons:
            return "real"
        return "unknown"
