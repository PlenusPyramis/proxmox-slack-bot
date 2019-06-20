import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Dict
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("fastapi").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.warning("This should be a warning on startup")

class SlackEventType(BaseModel):
    type: str
    token: str = None
    team_id: str = None
    api_app_id: str = None
    event: dict = None

class SlackUrlVerificationEvent(SlackEventType):
    challenge: str

class SlackAppMentionEvent(BaseModel):
    user: str
    text: str
    ts: str
    channel: str

app = FastAPI()

@app.post("/events/")
def receive_event(event_wrapper: dict):
    """
    Respond to Slack events
    """
    event_wrapper = SlackEventType(**event_wrapper)
    logging.info("Receive event type: {et}".format(et=event_wrapper))
    logging.info("type of event_wrapper: {}".format(type(event_wrapper)))

    # TODO : verify slack signature
    if event_wrapper.type == "url_verification":
        event = SlackUrlVerificationEvent(**event_wrapper.event)
        # Respond to initial URL verification:
        # See: https://api.slack.com/events-api#events_api_request_urls
        return {"challenge": event.challenge}

    elif event_wrapper.type == "event_callback":
        return handle_event_callback(event_wrapper.event)

    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Unhandled event type: {et}".format(
                                et=event_wrapper.type))

def handle_event_callback(event: dict):
    try:
        event_type = event['type']
    except KeyError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Missing event type")

    if event_type == "app_mention":
        event = SlackAppMentionEvent(**event)
        logging.info("Received app mention: {e}".format(e=event))
        user = slack_users_info(event.user)
        send_message(event.channel, "Hello @{name}".format(name=user['profile']['display_name']))
        return {"message": "ok"}
    else:
        logging.error("Cannot handle event: {e}".format(e=event))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Unhandled event type: {et}".format(
                                et=event_wrapper.type))

def send_message(channel, message):
    try:
        webhook_url = os.environ["SLACK_WEBHOOK_{channel}".format(channel=channel)]
    except KeyError:
        logging.error("No known webhook for channel: {channel} - "
                      "must provide SLACK_CHANNEL_{channel} environment variable.".format(channel=channel))
        raise
    requests.post(webhook_url, json={"text": message})

def slack_api(method, data):
    token = os.environ["SLACK_TOKEN"]
    url = "https://slack.com/api/{method}".format(method=method)
    headers = {"Authorization": "Bearer {t}".format(t=token)}
    logging.debug("headers: {h}".format(h=headers))
    res = requests.post(url, headers=headers, data=data)
    if res.status_code != 200:
        logging.error("Slack API returned status: {status}".format(status=res.status))
        logging.error(res.content)
    return json.loads(res.content)

def slack_users_info(user):
    logging.debug("asking for info for user: {}".format(user))
    return slack_api("users.info", {"user": user, "include_locale": "false"})['user']

# @app.middleware("http")
# async def logmy422(request, call_next):
#     response = await call_next(request)
#     if response.status_code == 422:
#         logging.debug("that failed")
#         logging.debug([i async for i in response.body_iterator])
#     return response
