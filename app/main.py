from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from typing import Dict
import logging

from slack import send_message, slack_users_info
from slack_model import SlackEventType, SlackUrlVerificationEvent, SlackAppMentionEvent


logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.post("/events/")
def receive_event(event_wrapper: dict):
    """
    Respond to Slack events
    """
    event_wrapper = SlackEventType(**event_wrapper)
    logging.debug("Receive event type: {et}".format(et=event_wrapper))

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
        logging.debug("Received app mention: {e}".format(e=event))
        user = slack_users_info(event.user)
        send_message(event.channel, "Hello @{name}".format(
            name=user['profile']['display_name']))
        return {"message": "ok"}
    else:
        logging.error("Cannot handle event: {e}".format(e=event))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Unhandled event type: {et}".format(
                                et=event_wrapper.type))

