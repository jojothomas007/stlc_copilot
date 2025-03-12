import json
import os
import logging
import base64
from typing import List
import requests
from requests.auth import HTTPBasicAuth
from src.stlc_copilot.config import Config
from src.stlc_copilot.utils.request_sender import RequestSender
from requests.exceptions import HTTPError, RequestException

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
