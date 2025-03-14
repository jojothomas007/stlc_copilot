from typing import Union
from fastapi import FastAPI, Request
import json
import logging
from src.stlc_copilot.dto.confluence_page_content_dto import ConfluencePageContent
from src.stlc_copilot.dto.confluence_remote_link_dto import RemoteLinkList
from src.stlc_copilot.dto.jira_issue_dto import Issue
from src.stlc_copilot.services.xray_service import XrayService
from src.stlc_copilot.dto.webhook_dto import WebhookIssue
from src.stlc_copilot.services.event_router import EventRouterService
from src.stlc_copilot.services.jira_service import JiraService
from src.stlc_copilot.services.confluence_service import ConfluenceService
from src.stlc_copilot.utils.request_sender import RequestSender

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


async def startup_event():
    print("Application startup")
    # Perform any startup tasks here (e.g., database connection)

async def shutdown_event():
    print("Application shutdown")

@app.get("/")
def isAlive():
    content= "STLC Copilot is active"
    # JiraDataTransformer().get_feature_file("SCRUM-25")
    # payload = json.load(open('src/stlc_copilot/resources/trial.json', 'r'))
    # XrayService().export_cucumber_tests(["SCRUM-261","SCRUM-271"]) 
    return content

@app.post("/webhook")
async def read_item(webhook:WebhookIssue):
    # Extract necessary information from the DTO
    issue_key = webhook.issue.key
    issue_type = webhook.issue.fields.issuetype.name
    webhook_event = webhook.webhookEvent
    logger.info(f"Webhook received for {issue_type} : {issue_key}")
    if webhook_event == "jira:issue_updated":
        # Route the event (placeholder for the actual event routing logic)
        EventRouterService().route_event(webhook.issue)
    else:
        logger.error(f"Unsupported event type : {webhook_event}")
    logger.info(f"Webhook processed for {issue_type} : {issue_key}")
    # Return a response to Jira
    return {"message": f"Webhook processing completed for {issue_type} : {issue_key}"}


@app.post("/jira_issues/{issue_key}")
async def read_item(issue_key:str):
    issue:Issue = JiraService().get_issue(issue_key)
    EventRouterService().route_event(issue)
    return {"message": f"Issue '{issue_key}' processing completed."}
