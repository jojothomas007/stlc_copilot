import json
import logging

from requests import Response
from src.stlc_copilot.dto.zephyr_test_dto import TestCase
from src.stlc_copilot.services.zephyr_service import ZephyrService
from src.stlc_copilot.config import Config
from src.stlc_copilot.dto.zephyr_test_steps_dto import InlineItem, Item, TestStepsPayload, TestStepsResponse
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class ZephyrDataTransformer:
    def __init__(self):
        self.zephyr_service:ZephyrService = ZephyrService()

    def create_tests(self, testcase_list:json):
        testcase_key_list:list = []
        for testcase in testcase_list:
            testcase_payload:json = {
                "projectKey": Config.jira_projectkey,
                "name": testcase["test_name"],
                "folderId": self.zephyr_service.get_test_folder_id(),
            }
            reponse = self.zephyr_service.create_test_case(testcase_payload)
            testcase_key = json.loads(reponse.content)["key"]
            testcase_key_list.append(testcase_key)
            self.create_the_test_steps(testcase_key, testcase["steps"])
        return testcase_key_list

    def create_the_test_steps(self, testcase_key:str, test_steps:json):
        items = []
        for test_step in test_steps:
            item = Item(
                inline=InlineItem(
                description=test_step["step"],
                testData=test_step["test_data"],
                expectedResult=test_step["expected_result"],
                )
            )
            items.append(item)
        teststeps_payload:TestStepsPayload = TestStepsPayload(
                mode="OVERWRITE",
                items=items
            )
        self.zephyr_service.create_test_steps(testcase_key, teststeps_payload)

    def get_linked_testcases_details(self, issue_key):
        response:Response = self.zephyr_service.get_linked_testcases(issue_key)
        test_details:str = ""
        for test in json.loads(response.content):
            test_key = test["key"]
            testcase:TestCase = self.zephyr_service.get_testcase(test_key)
            test_details = f"{test_details} \nTestcase Name : {testcase.name}\n  Testcase Steps :\n"
            teststeps:TestStepsResponse = self.zephyr_service.get_teststeps(test_key)
            for step in teststeps.values:
                test_details = f"{test_details} step: {step.inline.description}\n"
                # test_details = f"{test_details} step description: {step.inline.description}\n testData: {step.inline.testData}\n expectedResult: {step.inline.expectedResult}\n"
        logger.info("Linked Test details :%s", test_details)
        return test_details
