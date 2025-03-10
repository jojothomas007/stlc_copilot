import logging
import json
import requests
from pydantic import BaseModel
from fastapi import Depends
from src.stlc_copilot.config import Config

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GPTService:
    def __init__(self):
        self.gpt_api_url = Config.gpt_api_url
        self.gpt_api_key = Config.gpt_api_key
        self.gpt_model = Config.gpt_model
        self.headers = {
            "Authorization": f"Bearer {self.gpt_api_key}",
            "Content-Type": "application/json"
        }

    def generate_user_stories(self, epic_details):
        return self.generate_text(epic_details, "You are a Product owner in a software project. Generate user stories from the jira epic details. Generated Output must be in the json array in the format :{\"summary\":\"User story summary in less than 100 characters\",\"description\":\"Detailed user story description\"}")

    def generate_test_scenarios_basic(self, user_story_details):
        return self.generate_text(user_story_details, "Generate bdd Test cases from the above User story details. Generated Output must be in the json array in the format :{\"feature\":\"Feature name in less than 80 characters\",\"scenario\":\"Detailed testcase steps\"}")
    
    def generate_test_scenarios_bdd(self, user_story_details):
        expected_json_format:json={
        "feature": "Feature name in less than 50 characters",
        "scenarios": [
        {
            "name": "Scenario name in less than 80 characters",
            "description": "Scenario description in less than 200 characters",
            "steps": "All Scenario steps formatted and each in new line"
        }]}
        return self.generate_text(user_story_details, f"Generate bdd testcases from below userstory description. Generated Output must be in the json format : {expected_json_format}")

    def generate_text(self, user_prompt, system_prompt):
        logger.info(f"Generating text for prompt: {system_prompt} {user_prompt}")
        try:
            request_body = {
                "model": self.gpt_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 900,
                "store": True
            }
            response = requests.post(
                f"{self.gpt_api_url}/v1/chat/completions",
                headers=self.headers,
                json=request_body
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(e)
            return "Error generating text."

    def get_json_corrected(self, json_str:str, json_schema:json):
        # formatting with schema to be added later
        return self.generate_text(json_str, "Can you correct the format of the json input? If truncated, correct it by removing last element.")
