import logging
import json
from json import JSONDecodeError
from src.stlc_copilot.services.gpt_llm_service import GPTService
from src.stlc_copilot.services.jira_service import JiraService
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class JsonFixerService:
    def __init__(self, jira_service:JiraService, llm_service:GPTService):
        self.jira_service = jira_service
        self.llm_service = llm_service

    def fix_json_format(self, input_str:str, json_schema:json=None) -> json:
        try:
            return self.get_json(input_str.replace("```json", "").replace("```", ""))
        except JSONDecodeError as e:
            corrected_json_input = self.llm_service.get_json_corrected(input_str, json_schema)
            corrected_json = self.get_json(corrected_json_input)
            logger.info(f"Corrected Json: {json.dumps(corrected_json, indent=2)}")
            return corrected_json
        
    @staticmethod
    def get_json(input_str) -> json:
        return json.loads(input_str)
