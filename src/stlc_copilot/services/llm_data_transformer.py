import json
import logging
from src.stlc_copilot.dto.jira_issue_dto import Issue
from src.stlc_copilot.services.gpt_llm_service import GPTService
from src.stlc_copilot.services.jira_data_tranformer import JiraDataTransformer

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class LLMDataTransformer:
    def __init__(self):
        self.llm_service:GPTService = GPTService()
        self.jira_data_transformer:JiraDataTransformer = JiraDataTransformer()

    def generate_user_stories(self, epic:Issue):
        epic_summary:str = epic.fields.summary
        epic_description:str = epic.fields.description
        confluence_contents:str = self.jira_data_transformer.get_confluence_page_contents(epic.key)
        attachments_contents:str = self.jira_data_transformer.get_attachment_contents(epic.key)
        user_prompt:str = f"epicSummary:{epic_summary};epicDescription:{epic_description}; Other related contents:{confluence_contents} {attachments_contents}"
        system_prompt:str = "You are a Product owner in a software project. Generate user stories from the jira epic details. Generated Output must be in the json array in the format :{\"summary\":\"User story summary in less than 100 characters\",\"description\":\"Detailed user story description\"}"
        return self.llm_service.generate_text(user_prompt, system_prompt)
    
    def generate_test_scenarios_basic(self, user_story:Issue):
        confluence_contents:str = self.jira_data_transformer.get_confluence_page_contents(user_story.key)
        attachments_contents:str = self.jira_data_transformer.get_attachment_contents(user_story.key)
        user_prompt:str = f"User Story Summary: {user_story.fields.summary};User Story Description: {user_story.fields.description}; Other related contents:{confluence_contents} {attachments_contents}"
        system_prompt:str = "Generate Test cases from the above User story details. Generated Output must be in the json array in the format :{\"summary\":\"Test case summary in less than 100 characters\",\"description\":\"Detailed testcase steps\"}"
        return self.llm_service.generate_text(user_prompt, system_prompt)
    
    def generate_test_scenarios_bdd(self, user_story:Issue):
        confluence_contents:str = self.jira_data_transformer.get_confluence_page_contents(user_story.key)
        attachments_contents:str = self.jira_data_transformer.get_attachment_contents(user_story.key)
        user_prompt:str = f"User Story Summary: {user_story.fields.summary};User Story Description: {user_story.fields.description}; Other related contents:{confluence_contents} {attachments_contents}"
        expected_json_format:json = {"feature": "Feature name and details", "scenarios": [{"scenario": "<complete executable cucumber scenario in plain text with newline and intendation. do not add additional json nodes>"}]}
        system_prompt:str = f"Generate a feature file in Gherkins format executed in Cucumber Test Framework for the below user story. Generated Output must be in the json format : {expected_json_format}."
        return self.llm_service.generate_text(user_prompt, system_prompt)
