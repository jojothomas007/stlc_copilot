import json
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    gpt_api_url: str = os.environ["gpt_api_url"]
    gpt_api_key: str = os.environ["gpt_api_key"]
    gpt_model: str = os.environ["gpt_model"]
    confluence_api_url: str = os.environ["confluence_api_url"]
    jira_api_url: str = os.environ["jira_api_url"]
    jira_api_username: str = os.environ["jira_api_username"]
    jira_api_token: str = os.environ["jira_api_token"]
    jira_projectkey: str = os.environ["jira_projectkey"]
    jira_epic_issuetypeid: int = os.environ["jira_epic_issuetypeid"]
    jira_story_issuetypeid: int = os.environ["jira_story_issuetypeid"]
    jira_test_issuetypeid: int = os.environ["jira_test_issuetypeid"]
    jira_test_linktype_name: int = os.environ["jira_test_linktype_name"]
    test_generation_type: int = os.environ["test_generation_type"]
    xray_api_url: str = os.environ["xray_api_url"]
    xray_client_id: str = os.environ["xray_client_id"]
    xray_client_secret: str = os.environ["xray_client_secret"]
    xray_token: str = os.environ["xray_token"]
    github_api_url: str = os.environ["github_api_url"]
    github_token: str = os.environ["github_token"]
    github_target_path: str = os.environ["github_target_path"]
    github_base_branch: str = os.environ["github_base_branch"]


    # Construct the path relative to the project root
    __json_path = Path(__file__).resolve().parent / 'resources' / 'prompt.json'
    prompts:json = json.load(open(__json_path, 'r'))
