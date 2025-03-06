import logging
import json
from json import JSONDecodeError

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class JsonFixerService:
    def __init__(self, jira_service, llm_service):
        self.jira_service = jira_service
        self.llm_service = llm_service

    def fix_user_story_json(self, input_str:str):
        try:
            return self.get_json(input_str.replace("```json", "").replace("```", ""))
        except JSONDecodeError as e:
            corrected_json_input = self.llm_service.get_json_corrected(input_str, None)
            corrected_json = self.get_json(corrected_json_input)
            logger.info(f"Corrected Json: {json.dumps(corrected_json, indent=2)}")
            return corrected_json

    def fix_test_case_json(self, input_str:str):
        try:
            return self.get_json(input_str.replace("```json", "").replace("```", ""))
        except JSONDecodeError as e:
            corrected_json_input = self.llm_service.get_json_corrected(input_str, None)
            corrected_json = self.get_json(corrected_json_input)
            logger.info(f"Corrected Json: {json.dumps(corrected_json, indent=2)}")
            return corrected_json

    @staticmethod
    def get_json(input_str):
        return json.loads(input_str)
