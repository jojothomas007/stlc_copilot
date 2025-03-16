import time
import json
import os
import logging
import base64
from typing import List
import requests
from requests.auth import HTTPBasicAuth
from src.stlc_copilot.dto.xray_test_dto import BulkXrayTests
from src.stlc_copilot.config import Config
from src.stlc_copilot.utils.request_sender import RequestSender
from requests.exceptions import HTTPError, RequestException
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class XrayService:
    def __init__(self):
        self.request_sender:RequestSender = RequestSender()
        self.xray_api_url = Config.xray_api_url
        self.xray_client_id = Config.xray_client_id
        self.xray_client_secret = Config.xray_client_secret
        self.token:str = Config.xray_token
        self.headers:json = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
            }

    def __authenticate_xray(self):
        if self.token != "":
            return
        request_url = f"{self.xray_api_url}/authenticate"
        headers:json = {
            "Content-Type": "application/json"
        }
        payload:json={ "client_id": self.xray_client_id,
                      "client_secret": self.xray_client_secret
                      }
        response = self.request_sender.post_request_json(request_url, headers, payload, None)
        Config.xray_token = os.environ['xray_token'] = self.token = response.text.replace('"','')
        self.headers:json = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
            }

    def export_cucumber_tests(self, test_key_list:List[str]):
        self.__authenticate_xray()
        story_keys=';'.join(test_key_list)
        request_url = f"{self.xray_api_url}/export/cucumber?keys={story_keys}"
        response = self.request_sender.get_request(request_url, self.headers, None)
        return response.content
    
    def create_tests_bulk(self, payload:BulkXrayTests) -> requests.Response:
        self.__authenticate_xray()
        request_url = f"{self.xray_api_url}/import/test/bulk"
        payload = payload.model_dump_json(exclude_none=True)
        response = self.request_sender.post_request(request_url, self.headers, payload, None)
        return response
    
    def get_create_tests_bulk_status(self, jobId:str) -> requests.Response:
        self.__authenticate_xray()
        response = None
        status = ""
        attempts = 0
        max_attempts = 5
        poll_interval = 10
        while(status != "successful" and attempts < max_attempts):
            try:
                request_url = f"{self.xray_api_url}/import/test/bulk/{jobId}/status"
                response = self.request_sender.get_request(request_url, self.headers, None)
                status = json.loads(response.content)["status"]
            except Exception as err:
                logger.error(f"An unexpected error occurred; retrying. Error: {err}")
                status = ""
            attempts += 1
            time.sleep(poll_interval)
        return response
