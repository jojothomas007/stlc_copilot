import logging
import json
import requests
from pydantic import BaseModel
from fastapi import Depends
from src.stlc_copilot.config import Config
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

class GPTService:
    def __init__(self):
        self.gpt_api_url = Config.gpt_api_url
        self.gpt_api_key = Config.gpt_api_key
        self.gpt_model = Config.gpt_model
        self.headers = {
            "Authorization": f"Bearer {self.gpt_api_key}",
            "Content-Type": "application/json"
        }

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
    
    def generate_filename_from_content(self, file_content, length:int=40):
        system_prompt:str = f"Generate feature file name from the provided BDD scenario details in the format <filename>.feature specifically. The filename length should be between 10 and {length}. The filename should not have spaces; use _ instead. The response must not contain anything other than the filename."
        return self.generate_text(file_content, system_prompt)
    
    def generate_filename_for_playwright_script(self, file_content, length:int=20):
        system_prompt:str = f"Generate file name for the playwright script written in typescript. Generate File name without any extension. The filename length should be between 10 and {length}. The filename should not have spaces; use _ instead. The response must not contain anything other than the filename."
        return self.generate_text(file_content, system_prompt) + ".ts"

