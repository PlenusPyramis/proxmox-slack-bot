from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Dict
import requests
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("fastapi").setLevel(logging.DEBUG)

class SlackEvent(BaseModel):
    type: str
    event_ts: str

class SlackEventType(BaseModel):
    type: str
    token: str = None
    team_id: str = None
    api_app_id: str = None
    event: Dict[str, str] = None

class SlackUrlVerificationEvent(SlackEventType):
    challenge: str

class SlackAppMentionEvent(SlackEvent):
    user: str
    text: str
    ts: str
    channel: str

app = FastAPI()

@app.post("/events/")
def receive_event(event_wrapper: Dict [str, str]):
    """
    Respond to Slack events
    """
    # TODO : verify slack signature
    logging.info("Receive event type: {et}".format(et=event_wrapper))
    if event_wrapper.type == "url_verification":
        event = SlackUrlVerificationEvent.parse_obj(event_wrapper)
        # Respond to initial URL verification:
        # See: https://api.slack.com/events-api#events_api_request_urls
        return {"challenge": event.challenge}

    elif event_wrapper.type == "event_callback":
        event = event_wrapper.event
        return handle_event_callback(event)

    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Unhandled event type")

def handle_event_callback(event: Dict[str, str]):
    if event.type == "app_mention":
        logging.info(event)
        event = SlackAppMentionEvent.parse_obj(event)
        logging.info("Received app mention: {e}".format(e=event))
        send_message(event.channel, "Hello @{user}".format(user=event.user))
        return
    else:
        logging.error("Cannot handle event: {e}".format(e=event))

def send_message(channel, message):
    try:
        webhook_url = os.environ("SLACK_WEBHOOK_{channel}".format(channel=channel))
    except KeyError:
        logging.error("No known webhook for channel: {channel} - "
                      "must provide SLACK_CHANNEL_{channel} environment variable.".format(channel=channel))
        raise
    requests.post(webhook_url, json={"text": message})
