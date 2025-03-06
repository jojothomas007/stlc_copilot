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
            project = jira_issue_dto.Project(key=self.project_key)
            parent = jira_issue_dto.Parent(id=epic_id)
            issue_type = jira_issue_dto.IssueType(id=self.story_issue_type_id)
            fields = jira_issue_dto.Fields(
                project=project,
                summary=json_userstory["summary"],
                description=json_userstory["description"],
                issuetype=issue_type,
                parent=parent
            )
            jira_issue = jira_issue_dto.Issue(fields=fields)
            issue_dto_list.append(jira_issue)
        
        jira_issue_bulk_dto = jira_issue_dto.JiraIssueBulk(issueUpdates=issue_dto_list)
        request_body = jira_issue_bulk_dto.model_dump_json()
        return request_body

    def format_testcases(self, json_userstories, epic_id):
        issue_dto_list = []
        for json_userstory in json_userstories:
            project = jira_issue_dto.Project(key=self.project_key)
            parent = jira_issue_dto.Parent(id=epic_id)
            issue_type = jira_issue_dto.IssueType(id=self.test_issue_type_id)
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
            jira_issue = jira_issue_dto.Issue(fields=fields)
            issue_dto_list.append(jira_issue)
        jira_issue_bulk_dto = jira_issue_dto.JiraIssueBulk(issueUpdates=issue_dto_list)
        request_body = jira_issue_bulk_dto.model_dump_json()
        return request_body

    def format_basic_testcases(self, json_userstories, epicId):
            issue_dto_list = []
            for json_userstory in json_userstories:
                project = jira_issue_dto.Project(self.projectKey)
                parent = jira_issue_dto.Parent(epicId)
                issue_type = jira_issue_dto.IssueType(self.testIssueTypeId)
                fields = jira_issue_dto.Fields(project, json_userstory["summary"], json_userstory["description"], issue_type, parent)
                jira_issue = jira_issue_dto(fields)
                issue_dto_list.append(jira_issue)
            jira_issue_bulk_dto = jira_issue_dto.JiraIssueBulk(issue_dto_list)
            request_body = jira_issue_bulk_dto.model_dump_json()
            return request_body
