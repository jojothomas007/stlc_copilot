import json
import logging
import base64
import requests
from requests.auth import HTTPBasicAuth
from src.stlc_copilot.dto.confluence_page_content_dto import ConfluencePageContent
from src.stlc_copilot.dto.jira_user_dto import User
from src.stlc_copilot.dto.jira_issue_dto import BulkIssues, Issue, IssueLink
from src.stlc_copilot.config import Config
from src.stlc_copilot.utils.request_sender import RequestSender

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ConfluenceService:
    def __init__(self):
        self.request_sender:RequestSender = RequestSender()
        self.confluence_api_url = Config.confluence_api_url
        self.jira_api_username = Config.jira_api_username
        self.jira_api_token = Config.jira_api_token
        self.auth = HTTPBasicAuth(self.jira_api_username, self.jira_api_token)
        self.headers = {
            "Accept": "application/json"
        }

    def is_valid_link(self, url:str) -> bool:
        return url.startswith(self.confluence_api_url.split("wiki")[0])

    def get_pageId_from_url(self, url:str) -> str:
        return url.split("/pages/")[1].split("/")[0]

    def get_page_content(self, page_id:str) -> requests.Response:
        request_url = f"{self.confluence_api_url}/content/{page_id}?expand=body.view"
        response = self.request_sender.get_request(request_url, self.headers, self.auth)
        return ConfluencePageContent.model_validate_json(response.content)