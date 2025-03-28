import re
import logging
import json
from src.stlc_copilot.dto.xray_test_dto import BulkXrayTests
from src.stlc_copilot.services.xray_service import XrayService
from src.stlc_copilot.dto.jira_user_dto import User
from src.stlc_copilot.dto.github_branch_dto import Branch
from src.stlc_copilot.config import Config
from src.stlc_copilot.dto.jira_issue_dto import Issue, IssueLink, IssueLinkType, IssueToLink, BulkIssues
from src.stlc_copilot.services.jira_service import JiraService
from src.stlc_copilot.services.json_fixer import JsonFixerService
from src.stlc_copilot.services.jira_data_tranformer import JiraDataTransformer
from src.stlc_copilot.services.llm_data_transformer import LLMDataTransformer
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
        self.llm_data_transformer = LLMDataTransformer()
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
            self.jira_service.remove_label(issue.key, "Automate")

    def __handle_epic_update(self, issue: Issue):
            epic_id = issue.id
            try:
                llm_output = self.llm_data_transformer.generate_user_stories(issue)
                logger.info("LLM Generated raw output: %s", llm_output)
                json_user_stories = self.json_fixer_service.fix_json_format(llm_output)
                bulk_issues_dto:BulkIssues = self.jira_data_transformer.format_user_stories(json_user_stories, epic_id)
            except Exception as e:
                logger.error(e)
                return
            self.jira_service.create_issues_bulk(bulk_issues_dto)

    def __handle_user_story_update(self, issue: Issue):
            try:
                epic_id = issue.fields.parent.id
                user_story_summary = issue.fields.summary
                user_story_description = issue.fields.description
                if "bdd" == Config.test_generation_type:
                    llm_output = self.llm_data_transformer.generate_test_scenarios_bdd(issue)
                    logger.info(f"LLM Generated raw output: {llm_output}")
                    json_tests = self.json_fixer_service.fix_json_format(llm_output)
                    logger.info(f"Fixed json: {json_tests}")
                    # Assuming format_basic_testcases method
                    bulk_tests_dto:BulkXrayTests = self.jira_data_transformer.get_issue_bulk_dto_bdd(json_tests, epic_id)
                    xray_service = XrayService()
                    response = xray_service.create_tests_bulk(bulk_tests_dto)
                    response = xray_service.get_create_tests_bulk_status(json.loads(response.content)["jobId"])
                    self.__link_tests_to_userstory(json.loads(response.content)["result"]["issues"], issue.key)
                else:
                    llm_output = self.llm_data_transformer.generate_test_scenarios_basic(f"User Story Summary: {user_story_summary};User Story Description: {user_story_description}")
                    logger.info(f"LLM Generated raw output: {llm_output}")
                    json_tests = self.json_fixer_service.fix_json_format(llm_output)
                    logger.info(f"Fixed json: {json_tests}")
                    # Assuming format_basic_testcases method
                    bulk_issues_dto:BulkIssues = self.jira_data_transformer.get_issue_bulk_dto_basic(json_tests, epic_id)                
                    response = self.jira_service.create_issues_bulk(bulk_issues_dto)
                    self.__link_tests_to_userstory(json.loads(response.content)["issues"], issue.key)
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
                            f"{Config.github_feature_path}/{file}", 
                            branch_name, 
                            files_dict[file], 
                            f"feature file added for {linked_userstory_key}",
                            jira_user.displayName,
                            jira_user.emailAddress
                        )
                        step_definitions = self.llm_data_transformer.generate_bdd_step_definitions(files_dict[file].decode('utf-8'))
                        logger.info(f"LLM Generated step definitions : {step_definitions}")
                        step_definitions_filename = self.__get_filename_from_step_definition(step_definitions)
                        self.github_service.create_update_file_contents(
                            f"{Config.github_stepdef_path}/{step_definitions_filename}", 
                            branch_name, 
                            step_definitions.replace("'''", "").encode('utf-8'), 
                            f"step_definitions file added for feature {file}",
                            jira_user.displayName,
                            jira_user.emailAddress
                        )
                    self.github_service.create_pull_request(
                        branch_name,
                        Config.github_base_branch,
                        f"feature file for {linked_userstory_key}",
                        f"feature file for {linked_userstory_key}",
                        draft=True
                    )
                else:
                    logger.warning(f"Code generation not supported for tests type: {test_type}")             
            except Exception as err:
                logger.error(f"An unexpected error occurred: {err}")
            return None
    
    def __get_filename_from_step_definition(self, java_code:str):
        match = re.search(r"public class (\w+)", java_code)
        if match:
            class_name = match.group(1)
            # Convert the class name into a filename with a .java extension
            filename = f"{class_name}.java"
            return filename
        else:
            raise ValueError("Could not find a class name in the provided Java code.")