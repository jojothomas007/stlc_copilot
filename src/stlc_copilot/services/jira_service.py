import json
import logging
import base64
import requests
from requests.auth import HTTPBasicAuth
from src.stlc_copilot.dto.confluence_remote_link_dto import RemoteLinkList
from src.stlc_copilot.dto.jira_user_dto import User
from src.stlc_copilot.dto.jira_issue_dto import BulkIssues, Issue, IssueLink
from src.stlc_copilot.config import Config
from src.stlc_copilot.utils.request_sender import RequestSender

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class JiraService:
    def __init__(self):
        self.request_sender:RequestSender = RequestSender()
        self.jira_api_url = Config.jira_api_url
        self.jira_api_username = Config.jira_api_username
        self.jira_api_token = Config.jira_api_token
        self.auth = HTTPBasicAuth(self.jira_api_username, self.jira_api_token)
        self.headers = {
            "Content-Type": "application/json"
        }

    def create_issues_bulk(self, jira_issue_bulk_dto:BulkIssues) -> requests.Response:
        request_url = f"{self.jira_api_url}/issue/bulk"
        payload = jira_issue_bulk_dto.model_dump_json(exclude_none=True)
        return self.request_sender.post_request(request_url, self.headers, payload, self.auth)
    
    def create_issue_link(self, payload:IssueLink):
        request_url = f"{self.jira_api_url}/issueLink"
        self.request_sender.post_request(request_url, self.headers, payload.model_dump_json(), self.auth)

    def get_issue(self, issue_id_or_key:str) -> Issue:
        request_url = f"{self.jira_api_url}/issue/{issue_id_or_key}"
        response = self.request_sender.get_request(request_url, self.headers, self.auth)
        return Issue.model_validate_json(response.text)

    def get_current_user(self) -> User:
        request_url = f"{self.jira_api_url}/myself"
        response = self.request_sender.get_request(request_url, self.headers, self.auth)
        return User.model_validate_json(response.text)
    
    def get_attachment_content(self, attachment_id:str) -> requests.Response:
        request_url = f"{self.jira_api_url}/attachment/content/{attachment_id}"
        response = self.request_sender.get_request(request_url, self.headers, self.auth)
        return response

    def get_remote_link(self, issue_id_or_key:str) -> RemoteLinkList:
        request_url = f"{self.jira_api_url}/issue/{issue_id_or_key}/remotelink"
        response = self.request_sender.get_request(request_url, self.headers, self.auth)
        return RemoteLinkList.model_validate_json(response.content)