import logging
import base64
import requests
from requests.auth import HTTPBasicAuth
from fastapi import Depends
from src.stlc_copilot.config import Config

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class JiraService:
    def __init__(self):
        self.jira_api_url = Config.jira_api_url
        self.jira_username = Config.jira_api_username
        self.jira_api_token = Config.jira_api_token
        # self.auth = HTTPBasicAuth(jira_username, jira_api_token)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + base64.b64encode(f"{self.jira_username}:{self.jira_api_token}".encode()).decode()
        }

    def create_issues_bulk(self, payload):
        logger.info("Payload: %s", payload)
        response = requests.post(
            f"{self.jira_api_url}/issue/bulk",
            headers=self.headers,
            # auth=self.auth,
            json=payload
        )
        response.raise_for_status()
        return response.json()
