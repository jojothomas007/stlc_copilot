import base64
import json
import logging
from src.stlc_copilot.dto.github_branch_dto import Branch
from src.stlc_copilot.config import Config
from src.stlc_copilot.utils.request_sender import RequestSender
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class GithubService:
    def __init__(self):
        self.request_sender:RequestSender = RequestSender()
        self.github_api_url = Config.github_api_url
        self.github_token = Config.github_token
        self.headers:json = {
            "User-Agent": "stlc_copilot",
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.github_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            }

    def get_branch(self, branch_name:str):
        request_url = f"{self.github_api_url}/branches/{branch_name}"
        return self.request_sender.get_request(request_url, self.headers, {})
  
    def create_branch(self, branch_name:str, sha:str):
        request_url = f"{self.github_api_url}/git/refs"
        payload:json = {
            "ref":f"refs/heads/{branch_name}",
            "sha":sha
        }
        return self.request_sender.post_request_json(request_url, self.headers, payload)

    def create_update_file_contents(self, file_path:str, branch:str, file_content, commit_message:str, committer_name:str, committer_email:str):
        request_url = f"{self.github_api_url}/contents/{file_path}"
        base64_content = base64.b64encode(file_content).decode('utf-8')
        payload:json = {
            "message":commit_message,
            "committer":{
                "name":committer_name,
                "email":committer_email
                },
            "content":base64_content,
            "branch":branch
        }
        response = self.request_sender.put_request(request_url, self.headers, json.dumps(payload))
        return response

    def get_branch(self, branch_name:str) -> Branch:
        request_url = f"{self.github_api_url}/branches/{branch_name}"
        response = self.request_sender.get_request(request_url, self.headers, {})
        Branch.model_validate_json(response.text)
  
    def create_pull_request(self, branch_name:str, base_branch_name:str, pull_req_title:str, pull_req_description:str, draft:bool):
        request_url = f"{self.github_api_url}/pulls"
        payload:json = {
            "title":pull_req_title,
            "body":pull_req_description,
            "head":branch_name,
            "base":base_branch_name,
            "draft": draft
        }
        response = self.request_sender.post_request(request_url, self.headers, json.dumps(payload))
        return response

    def get_branch(self, branch_name:str) -> Branch:
        request_url = f"{self.github_api_url}/branches/{branch_name}"
        response = self.request_sender.get_request(request_url, self.headers, {})
        return Branch.model_validate_json(response.text)
    