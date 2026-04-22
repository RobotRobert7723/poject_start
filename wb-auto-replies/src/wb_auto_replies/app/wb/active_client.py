from wb_auto_replies.app.wb.client import BaseWbFeedbackClient


class ActiveFeedbacksClient(BaseWbFeedbackClient):
    source_api = "active"
    endpoint = "/api/v1/feedbacks"
