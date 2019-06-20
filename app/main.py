from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
import logging

class SlackEventType(BaseModel):
    type: str
    token: str = None
    team_id: str = None
    api_app_id: str = None
    event: SlackEvent = None

class SlackUrlVerificationEvent(SlackEventType):
    challenge: str

class SlackEvent(BaseModel):
    type: str
    event_ts: str

class SlackAppMentionEvent(SlackEvent)
    user: str
    text: str
    ts: str
    channel: str

app = FastAPI()

@app.post("/events/")
def receive_event(event_wrapper: SlackEventType):
    """
    Respond to Slack events
    """
    # TODO : verify slack signature

    if event_wrapper.type == "url_verification":
        event = SlackUrlVerificationEvent(event_wrapper)
        # Respond to initial URL verification:
        # See: https://api.slack.com/events-api#events_api_request_urls
        return {"challenge": event.challenge}

    elif event_wrapper.type == "event_callback":
        event = event_wrapper.event
        return handle_event_callback(event)

    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Unhandled event type")

def handle_event_callback(event: SlackEvent):
    if event.type == "app_mention":
        event = SlackAppMentionEvent(event)
        logging.info("Received app mention: {e}".format(e=event))
        return
