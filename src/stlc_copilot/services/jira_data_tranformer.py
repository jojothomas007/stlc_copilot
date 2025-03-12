import json
import logging
from pydantic import BaseModel
from typing import List
from src.stlc_copilot.dto.jira_issue_dto import Issue, Project, Parent, IssueType, Fields, BulkIssues, BulkIssueFields
from src.stlc_copilot.config import Config
from src.stlc_copilot.services.jira_service import JiraService
from src.stlc_copilot.services.xray_service import XrayService
from src.stlc_copilot.utils.zip_util import ZipUtil

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class JiraDataTransformer:
    def __init__(self):
        self.project_key = Config.jira_projectkey
        self.story_issue_type_id = Config.jira_story_issuetypeid
        self.test_issue_type_id = Config.jira_test_issuetypeid

    def format_user_stories(self, json_userstories:json, epic_id:str):
        issue_dto_list = []
        for json_userstory in json_userstories:
            project = Project(id=None, key=self.project_key)
            parent = Parent(id=epic_id)
            issue_type = IssueType(id=self.story_issue_type_id, name=None)
            fields = Fields(
                project=project,
                summary=json_userstory["summary"],
                description=json_userstory["description"],
                issuetype=issue_type,
                parent=parent
            )
            bulk_issue_fields = BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        jira_issue_bulk_dto = BulkIssues(issueUpdates=issue_dto_list)
        request_body = jira_issue_bulk_dto.model_dump_json()
        return request_body

    def format_testcases_with_tables(self, json_userstories, epic_id):
        issue_dto_list = []
        for json_userstory in json_userstories:
            project = Project(id=None, key=self.project_key)
            parent = Parent(id=epic_id)
            issue_type = IssueType(id=self.test_issue_type_id, name=None)
            testcase_steps = json_userstory["description"]
            description = f"Precondition: {testcase_steps['precondition']} \n||*Step No*||*Test Steps*||*Expected*||"
            for testcase_step in testcase_steps["steps"]:
                description += f"\n|{testcase_step['Step No']}|{testcase_step['Test Step']}|{testcase_step['Expected']}|"
            fields = Fields(
                project=project,
                summary=json_userstory["summary"],
                description=description,
                issuetype=issue_type,
                parent=parent
            )
            bulk_issue_fields = BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        jira_issue_bulk_dto = BulkIssues(issueUpdates=issue_dto_list)
        request_body = jira_issue_bulk_dto.model_dump_json()
        return request_body

    def get_issue_bulk_dto_basic(self, json_testcases, epic_id) -> BulkIssues:
        issue_dto_list = []
        for json_testcase in json_testcases:
            project = Project(id=None, key=self.project_key)
            parent = Parent(id=epic_id)
            issue_type = IssueType(id=self.test_issue_type_id, name=None)
            fields = Fields(
                project=project, 
                summary=json_testcase["summary"], 
                description=json_testcase["description"], 
                issuetype=issue_type,
                parent=parent
            )
            bulk_issue_fields = BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        return BulkIssues(issueUpdates=issue_dto_list)
    
    def get_issue_bulk_dto_bdd(self, json_scenarios, epic_id) -> BulkIssues:
        issue_dto_list = []
        for json_scenario in json_scenarios["scenarios"]:
            project = Project(id=None, key=self.project_key)
            parent = Parent(id=epic_id)
            issue_type = IssueType(id=self.test_issue_type_id, name=None)
            fields = Fields(
                project=project, 
                summary=f"{json_scenario["scenario"]}".split("\n")[0],
                description=json_scenario["scenario"],
                issuetype=issue_type,
                parent=parent
            )
            bulk_issue_fields = BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        return BulkIssues(issueUpdates=issue_dto_list)
    
    def get_linked_userstory_key(self, issue:Issue):
        for issue_link in issue.fields.issuelinks:
            if issue_link.type.name == Config.jira_test_linktype_name:
                return issue_link.outwardIssue.key
        return None
    
    def get_feature_file(self, key:str) -> dict:
        issue:Issue = JiraService().get_issue(key)
        issue_key_list:List = []
        for issue_link in issue.fields.issuelinks:
            if issue_link.type.name == "Test" and issue_link.inwardIssue != None :
                issue_key_list.append(issue_link.inwardIssue.key)
        feature_file_zip = XrayService().export_cucumber_tests(issue_key_list)
        files_dict = ZipUtil().unzip(feature_file_zip)
        return files_dict
    
