import json
import logging
from typing import List
from src.stlc_copilot.utils.content_util import ContentManager
from src.stlc_copilot.dto.confluence_page_content_dto import ConfluencePageContent
from src.stlc_copilot.dto.confluence_remote_link_dto import RemoteLinkList
from src.stlc_copilot.services.confluence_service import ConfluenceService
from src.stlc_copilot.dto.jira_issue_dto import Issue, Project, Parent, IssueType, Fields, BulkIssues, BulkIssueFields
from src.stlc_copilot.config import Config
from src.stlc_copilot.services.jira_service import JiraService
from src.stlc_copilot.services.xray_service import XrayService
from src.stlc_copilot.services.gpt_llm_service import GPTService
from src.stlc_copilot.utils.zip_util import ZipUtil

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class JiraDataTransformer:
    def __init__(self):
        self.project_key = Config.jira_projectkey
        self.story_issue_type_id = Config.jira_story_issuetypeid
        self.test_issue_type_id = Config.jira_test_issuetypeid

    def format_user_stories(self, json_userstories:json, epic_id:str) -> BulkIssues:
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
                parent=parent,
                attachment=[],
                creator=None,
                issuelinks=None
            )
            bulk_issue_fields = BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        return BulkIssues(issueUpdates=issue_dto_list)

    def format_testcases_with_tables(self, json_userstories, epic_id) -> BulkIssues:
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
                parent=parent,
                attachment=[],
                creator=None,
                issuelinks=None
            )
            bulk_issue_fields = BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        return BulkIssues(issueUpdates=issue_dto_list)

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
                parent=parent,
                attachment=[],
                creator=None,
                issuelinks=None
            )
            bulk_issue_fields = BulkIssueFields(fields=fields)
            issue_dto_list.append(bulk_issue_fields)
        return BulkIssues(issueUpdates=issue_dto_list)
    
    def get_issue_bulk_dto_bdd(self, json_scenarios, epic_id) -> BulkIssues:
        issue_dto_list = []
        for json_scenario in json_scenarios:
            project = Project(id=None, key=self.project_key)
            parent = Parent(id=epic_id)
            issue_type = IssueType(id=self.test_issue_type_id, name=None)
            fields = Fields(
                project=project, 
                summary=json_scenario["scenario"],
                description=json_scenario["steps"],
                issuetype=issue_type,
                parent=parent,
                attachment=[],
                creator=None,
                issuelinks=None
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
        files_dict = self.__update_file_name(files_dict)
        return files_dict
    
    def __update_file_name(self, files_dict:dict) -> dict:
        new_file_dict = {}
        for file in files_dict:
            file_content = files_dict.get(file)            
            filename:str = GPTService().generate_filename_from_content(file_content.decode('utf-8'))
            new_file_dict[filename] = file_content
        return new_file_dict

    def get_confluence_page_contents(self, issue_id_or_key:str) -> str:
        content = " "
        jira_service:JiraService = JiraService()
        remoteLinkList:RemoteLinkList = jira_service.get_remote_link(issue_id_or_key)
        confluenceService:ConfluenceService = ConfluenceService()
        for remoteLink in remoteLinkList.root:
            website_link = remoteLink.object.url
            if confluenceService.is_valid_link(website_link):
                pageId = confluenceService.get_pageId_from_url(website_link)
                confluence_page_content:ConfluencePageContent = confluenceService.get_page_content(pageId) 
                content += confluence_page_content.body.view.value + "\n"
            else:
                logger.warning("External link found - %s; data not fetched", website_link)
        return content
    
    def get_attachment_contents(self, issue_id_or_key:str) -> str:
        content = " "
        jira_service:JiraService = JiraService()
        issue:Issue = jira_service.get_issue(issue_id_or_key)
        content = " " 
        for attachment in issue.fields.attachment :
            response = jira_service.get_attachment_content(attachment.id)
            content += ContentManager().extract_from_bytes(response.headers.get("Content-Type"), response.content) + "\n"
        return content

