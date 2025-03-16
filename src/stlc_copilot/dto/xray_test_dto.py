from pydantic import BaseModel, RootModel
from typing import List
from src.stlc_copilot.dto.jira_issue_dto import Fields

class XrayTest(BaseModel):
    testtype: str
    fields: Fields
    gherkin_def: str
    xray_test_sets: List[str]

class BulkXrayTests(RootModel):
    root: list[XrayTest]