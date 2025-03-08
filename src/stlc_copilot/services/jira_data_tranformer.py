import json
import logging
from pydantic import BaseModel
from typing import List
from src.stlc_copilot.dto import jira_issue_dto
from src.stlc_copilot.config import Config

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
            project = jira_issue_dto.Project(id=None, key=self.project_key)
            parent = jira_issue_dto.Parent(id=epic_id)
            issue_type = jira_issue_dto.IssueType(id=self.story_issue_type_id, name=None)
            fields = jira_issue_dto.Fields(
                project=project,
                summary=json_userstory["summary"],
                description=json_userstory["description"],
                issuetype=issue_type,
                parent=parent
            )
            bulk_issue_fields = jira_issue_dto.BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        jira_issue_bulk_dto = jira_issue_dto.BulkIssues(issueUpdates=issue_dto_list)
        request_body = jira_issue_bulk_dto.model_dump_json()
        return request_body

    def format_testcases_with_tables(self, json_userstories, epic_id):
        issue_dto_list = []
        for json_userstory in json_userstories:
            project = jira_issue_dto.Project(id=None, key=self.project_key)
            parent = jira_issue_dto.Parent(id=epic_id)
            issue_type = jira_issue_dto.IssueType(id=self.test_issue_type_id, name=None)
            testcase_steps = json_userstory["description"]
            description = f"Precondition: {testcase_steps['precondition']} \n||*Step No*||*Test Steps*||*Expected*||"
            for testcase_step in testcase_steps["steps"]:
                description += f"\n|{testcase_step['Step No']}|{testcase_step['Test Step']}|{testcase_step['Expected']}|"
            fields = jira_issue_dto.Fields(
                project=project,
                summary=json_userstory["summary"],
                description=description,
                issuetype=issue_type,
                parent=parent
            )
            bulk_issue_fields = jira_issue_dto.BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        jira_issue_bulk_dto = jira_issue_dto.BulkIssues(issueUpdates=issue_dto_list)
        request_body = jira_issue_bulk_dto.model_dump_json()
        return request_body

    def format_testcases_basic(self, json_testcases, epic_id):
            issue_dto_list = []
            for json_testcase in json_testcases:
                project = jira_issue_dto.Project(id=None, key=self.project_key)
                parent = jira_issue_dto.Parent(id=epic_id)
                issue_type = jira_issue_dto.IssueType(id=self.test_issue_type_id, name=None)
                fields = jira_issue_dto.Fields(
                    project=project, 
                    summary=json_testcase["summary"], 
                    description=json_testcase["description"], 
                    issuetype=issue_type,
                    parent=parent
                )
                bulk_issue_fields = jira_issue_dto.BulkIssueFields(fields=fields)
                issue_dto_list.append(bulk_issue_fields)
            jira_issue_bulk_dto = jira_issue_dto.BulkIssues(issueUpdates=issue_dto_list)
            request_body = jira_issue_bulk_dto.model_dump_json()
            return request_body
    
    def format_testcases_bdd(self, json_scenarios, epic_id):
            issue_dto_list = []
            for json_scenario in json_scenarios["scenarios"]:
                project = jira_issue_dto.Project(id=None, key=self.project_key)
                parent = jira_issue_dto.Parent(id=epic_id)
                issue_type = jira_issue_dto.IssueType(id=self.test_issue_type_id, name=None)
                fields = jira_issue_dto.Fields(
                    project=project, 
                    summary=json_scenario["name"],
                    description=f"{json_scenario["description"]}\n{json_scenario["steps"]}",
                    issuetype=issue_type,
                    parent=parent
                )
                bulk_issue_fields = jira_issue_dto.BulkIssueFields(fields=fields)
                issue_dto_list.append(bulk_issue_fields)
            jira_issue_bulk_dto = jira_issue_dto.BulkIssues(issueUpdates=issue_dto_list)
            request_body = jira_issue_bulk_dto.model_dump_json()
            return request_body

