import logging

import json
from src.stlc_copilot.dto.jira_user_dto import User
from src.stlc_copilot.dto.github_branch_dto import Branch
from src.stlc_copilot.config import Config
from src.stlc_copilot.dto.jira_issue_dto import Issue, IssueLink, IssueLinkType, IssueToLink, BulkIssues
from src.stlc_copilot.services.jira_service import JiraService
from src.stlc_copilot.services.json_fixer import JsonFixerService
from src.stlc_copilot.services.jira_data_tranformer import JiraDataTransformer
from src.stlc_copilot.services.gpt_llm_service import GPTService
from src.stlc_copilot.services.github_service import GithubService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventRouterService:
    def __init__(self):
        self.jira_service = JiraService()
        self.llm_service = GPTService()
        self.json_fixer_service = JsonFixerService(self.jira_service, self.llm_service)
        self.jira_data_transformer = JiraDataTransformer()
        self.github_service = GithubService()
    
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
                    bulk_issues_dto:BulkIssues = self.jira_data_transformer.get_issue_bulk_dto_bdd(json_tests, epic_id)
                else:
                    llm_output = self.llm_service.generate_test_scenarios_basic(f"User Story Summary: {user_story_summary};User Story Description: {user_story_description}")
                    logger.info(f"LLM Generated raw output: {llm_output}")
                    json_tests = self.json_fixer_service.fix_json_format(llm_output)
                    logger.info(f"Fixed json: {json_tests}")
                    # Assuming format_basic_testcases method
                    bulk_issues_dto:BulkIssues = self.jira_data_transformer.get_issue_bulk_dto_basic(json_tests, epic_id)                
                response = self.jira_service.create_issues_bulk(bulk_issues_dto)
                self.__link_tests_to_userstory(response["issues"], issue.key)
            except Exception as err:
                logger.error(f"An unexpected error occurred: {err}")
            return None           
           
    def __link_tests_to_userstory(self, issues: json, user_story_key:str):
        for issue in issues:
            issue_link = IssueLink(
                inwardIssue=IssueToLink(key=issue["key"]),
                outwardIssue=IssueToLink(key=user_story_key),
                type=IssueLinkType(name=Config.jira_test_linktype_name)
            )
            self.jira_service.create_issue_link(issue_link)
    
    def __handle_test_update(self, issue: Issue):
            try:
                epic_id = issue.fields.parent.id
                test_summary = issue.fields.summary
                test_description = issue.fields.description
                test_type:str = Config.test_generation_type
                if "bdd" == test_type:
                    linked_userstory_key = self.jira_data_transformer.get_linked_userstory_key(issue)
                    files_dict:dict = self.jira_data_transformer.get_feature_file(linked_userstory_key)
                    branch_name = f"{linked_userstory_key}_tests"
                    base_branch:Branch = self.github_service.get_branch(Config.github_base_branch)
                    self.github_service.create_branch(branch_name, base_branch.commit.sha)
                    jira_user:User = self.jira_service.get_current_user()
                    for file in files_dict:
                        self.github_service.create_update_file_contents(
                            f"{Config.github_target_path}/{file}", 
                            branch_name, 
                            files_dict[file], 
                            f"feature file added for {linked_userstory_key}",
                            jira_user.displayName,
                            jira_user.emailAddress
                        )
                    self.github_service.create_pull_request(
                        branch_name,
                        Config.github_base_branch,
                        f"feature file for {linked_userstory_key}",
                        f"feature file for {linked_userstory_key}"
                    )
                else:
                    logger.warning(f"Code generation not supported for tests type: {test_type}")             
            except Exception as err:
                logger.error(f"An unexpected error occurred: {err}")
            return None