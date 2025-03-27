import json
import logging
import base64
from typing import List
import requests
from requests.auth import HTTPBasicAuth
from src.stlc_copilot.dto.zephyr_test_steps_dto import InlineItem, Item, TestStepsPayload, TestStepsResponse
from src.stlc_copilot.dto.zephyr_folder_dto import Folder, Folders
from src.stlc_copilot.dto.zephyr_test_dto import TestCase
from src.stlc_copilot.dto.confluence_remote_link_dto import RemoteLinkList
from src.stlc_copilot.dto.jira_user_dto import User
from src.stlc_copilot.dto.jira_issue_dto import BulkIssues, Issue, IssueLink
from src.stlc_copilot.config import Config
from src.stlc_copilot.utils.request_sender import RequestSender
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class ZephyrService:
    def __init__(self):
        self.request_sender:RequestSender = RequestSender()
        self.jira_projectkey = Config.jira_projectkey
        self.zephyr_test_folder_id = None
        self.zephyr_api_url = Config.zephyr_api_url
        self.zephyr_test_folder_path = Config.zephyr_test_folder_path
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.zephyr_api_token}"
        }

    def get_folders(self, folderType, max_results:int, start_at:int) -> Folders:
        request_url = f"{self.zephyr_api_url}/folders"
        params = {
            "projectKey": self.jira_projectkey,
            "folderType": folderType,
            "maxResults": max_results,
            "startAt": start_at
        }
        response = self.request_sender.get_request(request_url, self.headers, params)
        return Folders.model_validate_json(response.text)

    def get_test_folders(self) -> List[Folder]:
        max_results = 10
        start_at = 0
        isLast = False
        folder_list:List[Folder] = []
        while(not isLast):
            folders:Folders = self.get_folders("TEST_CASE", max_results, start_at)
            folder_list.extend(folders.values)
            start_at += max_results
            isLast = folders.isLast
        return folder_list
    
    def get_test_folder_id(self):
        if self.zephyr_test_folder_id != None:
            return self.zephyr_test_folder_id
        path_parts = Config.zephyr_test_folder_path.split("/")
        folder_list:List[Folder] = self.get_test_folders()
        current_parent_id = None
        for part in path_parts:
            found = False
            for folder in folder_list:
                if folder.name == part and (folder.parentId == current_parent_id):
                    current_parent_id = folder.id
                    found = True
                    break
            if not found:
                logger.info(f"Folder '{part}' not found in the hierarchy.")
        self.zephyr_test_folder_id = current_parent_id
        return current_parent_id
    
    def create_test_case(self, payload):
        request_url = f"{self.zephyr_api_url}/testcases"
        response = self.request_sender.post_request_json(request_url, self.headers, payload, None)
        return response

    def create_test_steps(self, testCaseKey:str, teststeps_payload:TestStepsPayload):
        request_url = f"{self.zephyr_api_url}/testcases/{testCaseKey}/teststeps"
        payload = teststeps_payload.model_dump_json(exclude_none=True)
        response = self.request_sender.post_request(request_url, self.headers, payload)
        return response
        
    def create_issue_links(self, testCaseKey:str, issueId:int):
        request_url = f"{self.zephyr_api_url}/testcases/{testCaseKey}/links/issues"
        payload = {"issueId": issueId}
        response = self.request_sender.post_request_json(request_url, self.headers, payload)
        return response
    
    def get_linked_testcases(self, issue_key:str) -> requests.Response:
        request_url = f"{self.zephyr_api_url}/issuelinks/{issue_key}/testcases"
        response = self.request_sender.get_request(request_url, self.headers, {})
        return response
    
    def get_testcase(self, test_key:str) -> TestCase:
        request_url = f"{self.zephyr_api_url}/testcases/{test_key}"
        response = self.request_sender.get_request(request_url, self.headers, {})
        return TestCase.model_validate_json(response.content)
    
    def get_teststeps(self, test_key:str) -> TestStepsResponse:
        request_url = f"{self.zephyr_api_url}/testcases/{test_key}/teststeps"
        response = self.request_sender.get_request(request_url, self.headers, {})
        return TestStepsResponse.model_validate_json(response.content)