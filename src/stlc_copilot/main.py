from typing import Union
from fastapi import FastAPI, Request
import json
import logging
from src.stlc_copilot.services.jira_data_tranformer import JiraDataTransformer
from src.stlc_copilot.dto.webhook_dto import WebhookIssue
from src.stlc_copilot.services.event_router import EventRouterService

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
    payload = json.load(open('src/stlc_copilot/resources/trial.json', 'r'))
    JiraDataTransformer().format_testcases_bdd(payload, "10004") 
    return "STLC Copilot is active"

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
    return {"message": f"Webhook processed successfully for {issue_type} : {issue_key}"}


@app.get("/read_items")
def read_items(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
