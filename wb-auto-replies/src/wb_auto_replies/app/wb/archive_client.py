from wb_auto_replies.app.wb.client import BaseWbFeedbackClient


class ArchiveFeedbacksClient(BaseWbFeedbackClient):
    source_api = "archive"
    endpoint = "/api/v1/feedbacks/archive"
