from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    gpt_api_url: str = os.environ["gpt_api_url"]
    gpt_api_key: str = os.environ["gpt_api_key"]
    gpt_model: str = os.environ["gpt_model"]
    jira_api_url: str = os.environ["jira_api_url"]
    jira_api_username: str = os.environ["jira_api_username"]
    jira_api_token: str = os.environ["jira_api_token"]
    jira_projectkey: str = os.environ["jira_projectkey"]
    jira_epic_issuetypeid: int = os.environ["jira_epic_issuetypeid"]
    jira_story_issuetypeid: int = os.environ["jira_story_issuetypeid"]
    jira_test_issuetypeid: int = os.environ["jira_test_issuetypeid"]
    test_generation_type: int = os.environ["test_generation_type"]

