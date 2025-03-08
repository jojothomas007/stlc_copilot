import logging

from src.stlc_copilot.config import Config
from src.stlc_copilot.dto.jira_issue_dto import Issue
from src.stlc_copilot.services.jira_service import JiraService
from src.stlc_copilot.services.json_fixer import JsonFixerService
from src.stlc_copilot.services.jira_data_tranformer import JiraDataTransformer
from src.stlc_copilot.services.gpt_llm_service import GPTService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventRouterService:
    def __init__(self):
        self.jira_service = JiraService()
        self.llm_service = GPTService()
        self.json_fixer_service = JsonFixerService(self.jira_service, self.llm_service)
        self.jira_data_transformer = JiraDataTransformer()
    
    def route_event(self, issue: Issue):
            issue_type = issue.fields.issuetype.id
            if issue_type == Config.jira_epic_issuetypeid:
                self.__handle_epic_update(issue)
            elif issue_type == Config.jira_story_issuetypeid:
                self.__handle_user_story_update(issue)
            elif issue_type == Config.jira_test_issuetypeid:
                self.__handle_test_update(issue)
            else:
                logger.error(f"Unsupported issue type: {issue_type}")

    def __handle_epic_update(self, issue: Issue):
            epic_id = issue.id
            epic_summary = issue.fields.summary
            epic_description = issue.fields.description
            user_stories_payloads = None
            try:
                llm_output = self.llm_service.generate_user_stories(f"epicSummary:{epic_summary};epicDescription:{epic_description}")
                logger.info("LLM Generated raw output: %s", llm_output)
                json_user_stories = self.json_fixer_service.fix_json_format(llm_output)
                user_stories_payloads = self.jira_data_transformer.format_user_stories(json_user_stories, epic_id)
            except Exception as e:
                logger.error(e)
                return
            self.jira_service.create_issues_bulk(user_stories_payloads)

    def __handle_user_story_update(self, issue: Issue):
            try:
                epic_id = issue.fields.parent.id
                user_story_summary = issue.fields.summary
                user_story_description = issue.fields.description
                if "bdd" == Config.test_generation_type:
                    llm_output = self.llm_service.generate_test_scenarios_bdd(f"User Story Summary: {user_story_summary};User Story Description: {user_story_description}")
                    logger.info(f"LLM Generated raw output: {llm_output}")
                    json_tests = self.json_fixer_service.fix_json_format(llm_output)
                    logger.info(f"Fixed json: {json_tests}")
                    # Assuming format_basic_testcases method
                    tests_payloads = self.jira_data_transformer.format_testcases_bdd(json_tests, epic_id)
                else:
                    llm_output = self.llm_service.generate_test_scenarios_basic(f"User Story Summary: {user_story_summary};User Story Description: {user_story_description}")
                    logger.info(f"LLM Generated raw output: {llm_output}")
                    json_tests = self.json_fixer_service.fix_json_format(llm_output)
                    logger.info(f"Fixed json: {json_tests}")
                    # Assuming format_basic_testcases method
                    tests_payloads = self.jira_data_transformer.format_testcases_basic(json_tests, epic_id)                
            except Exception as e:
                logger.error(e)
                return
            self.jira_service.create_issues_bulk(tests_payloads)

    def __handle_test_update(self, issue: Issue):
            try:
                epic_id = issue.fields.parent.id
                user_story_summary = issue.fields.summary
                user_story_description = issue.fields.description
                if "bdd" == Config.test_generation_type:
                    llm_output = self.llm_service.generate_test_scenarios_bdd(f"User Story Summary: {user_story_summary};User Story Description: {user_story_description}")
                    logger.info(f"LLM Generated raw output: {llm_output}")
                    json_tests = self.json_fixer_service.fix_json_format(llm_output)
                    logger.info(f"Fixed json: {json_tests}")
                    # Assuming format_basic_testcases method
                    tests_payloads = self.jira_data_transformer.format_testcases_bdd(json_tests, epic_id)
                else:
                    llm_output = self.llm_service.generate_test_scenarios_basic(f"User Story Summary: {user_story_summary};User Story Description: {user_story_description}")
                    logger.info(f"LLM Generated raw output: {llm_output}")
                    json_tests = self.json_fixer_service.fix_json_format(llm_output)
                    logger.info(f"Fixed json: {json_tests}")
                    # Assuming format_basic_testcases method
                    tests_payloads = self.jira_data_transformer.format_testcases_basic(json_tests, epic_id)                
            except Exception as e:
                logger.error(e)
                return
            self.jira_service.create_issues_bulk(tests_payloads)