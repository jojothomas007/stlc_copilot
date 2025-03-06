from pydantic import BaseModel
from src.stlc_copilot.dto.jira_issue_dto import Issue

class WebhookIssue(BaseModel):
    webhookEvent: str
    issue: Issue
