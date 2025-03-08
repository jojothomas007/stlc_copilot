import json
import logging
import base64
import requests
from requests.auth import HTTPBasicAuth
from src.stlc_copilot.config import Config
from requests.exceptions import HTTPError, RequestException

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class JiraService:
    def __init__(self):
        self.jira_api_url = Config.jira_api_url
        self.jira_api_username = Config.jira_api_username
        self.jira_api_token = Config.jira_api_token
        self.auth = HTTPBasicAuth(self.jira_api_username, self.jira_api_token)
        self.headers = {
            "Content-Type": "application/json"
        }

    def create_issues_bulk(self, payload:json):
        request_url = f"{self.jira_api_url}/issue/bulk"
        logger.info("Request URL: %s", request_url)
        logger.info("Request Headers: %s", self.headers)
        logger.info("Request Payload: %s", payload)
        try:
            response = requests.post(
                request_url,
                headers=self.headers,
                auth=self.auth,
                data=payload 
            )
            response.raise_for_status()
            logger.info("Response : %s", response.content)
            return response.json()
        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err} - {response}")
        except RequestException as req_err:
            logger.error(f"Request error occurred: {req_err} - {response}")
        except Exception as err:
            logger.error(f"An unexpected error occurred: {err} - {response}")
        return None
