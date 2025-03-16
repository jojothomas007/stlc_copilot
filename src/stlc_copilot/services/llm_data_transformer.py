import json
import logging
from src.stlc_copilot.config import Config
from src.stlc_copilot.dto.jira_issue_dto import Issue
from src.stlc_copilot.services.gpt_llm_service import GPTService
from src.stlc_copilot.services.jira_data_tranformer import JiraDataTransformer
from src.stlc_copilot.services.search_service import SearchService

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMDataTransformer:
    def __init__(self):
        self.llm_service:GPTService = GPTService()
        self.jira_data_transformer:JiraDataTransformer = JiraDataTransformer()
        self.search_service:SearchService = SearchService()

    def generate_user_stories(self, epic:Issue):
        epic_summary:str = epic.fields.summary
        epic_description:str = epic.fields.description
        userstory_desc_format:str = Config.prompts["userstory_desc_format"]
        confluence_contents:str = self.jira_data_transformer.get_confluence_page_contents(epic.key)
        attachments_contents:str = self.jira_data_transformer.get_attachment_contents(epic.key)
        related_contents:str = self.search_service.search_text(f"{confluence_contents}{attachments_contents}", f"{epic_summary}{epic_description}")
        user_prompt:str = f"epicSummary:{epic_summary};epicDescription:{epic_description}; Other related contents:{related_contents}"
        expected_json_format:json = {"summary":"User story summary in less than 80 characters","description":"Detailed user story description"}
        system_prompt:str = f"You are a Product owner in a software project. Generate user stories from the jira epic details. Userstory description format : {userstory_desc_format}. Generated Output must be in the json array in the format : {expected_json_format}"
        return self.llm_service.generate_text(user_prompt, system_prompt)
    
    def generate_test_scenarios_basic(self, user_story:Issue):
        testcase_desc_format:str = Config.prompts["testcase_desc_format"]
        confluence_contents:str = self.jira_data_transformer.get_confluence_page_contents(user_story.key)
        attachments_contents:str = self.jira_data_transformer.get_attachment_contents(user_story.key)
        user_prompt:str = f"User Story Summary: {user_story.fields.summary};User Story Description: {user_story.fields.description}; Other related contents:{confluence_contents} {attachments_contents}"
        expected_json_format:json = {"summary":"Test case summary in less than 80 characters","description":f"Detailed testcase steps. Testcase description format : {testcase_desc_format}"}
        system_prompt:str = f"Generate Test cases from the above User story details. Generated Output must be in the json array in the format : {expected_json_format}"
        return self.llm_service.generate_text(user_prompt, system_prompt)
    
    def generate_test_scenarios_bdd(self, user_story:Issue):
        user_story_summary = user_story.fields.summary
        user_story_description = user_story.fields.description
        confluence_contents:str = self.jira_data_transformer.get_confluence_page_contents(user_story.key)
        attachments_contents:str = self.jira_data_transformer.get_attachment_contents(user_story.key)
        related_contents:str = self.search_service.search_text(f"{confluence_contents}{attachments_contents}", f"{user_story_summary}{user_story_description}")
        user_prompt:str = f"User Story Summary: {user_story_summary};User Story Description: {user_story_description}; Other related contents:{related_contents}"
        expected_json_format:json = [{"scenario": "<scenario name>", "steps": "<complete executable cucumber steps in plain text with newline and intendation. do not add additional json nodes>"}]
        system_prompt:str = f"You are a bdd expert. Generate a bdd scenario in Gherkins format executable in Cucumber Test Framework for the below user story. Generated Output must be in the json format : {expected_json_format}."
        return self.llm_service.generate_text(user_prompt, system_prompt)
    
    def generate_bdd_step_definitions(self, scenarios):
        user_prompt:str = f"BDD gherkins scenario steps: {scenarios}"
        system_prompt:str = f"You are a bdd expert. Generate bdd cucumber java step definition file for the bdd gherkins scenario steps. Do not any other description other than the compilable java file content."
        return self.llm_service.generate_text(user_prompt, system_prompt)
