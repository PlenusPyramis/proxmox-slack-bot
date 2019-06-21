import os
import time
from fastapi import FastAPI, Header, Body, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from typing import Dict
import logging
import json
import traceback

from slack_model import SlackEventType, SlackUrlVerificationEvent, SlackAppMentionEvent
import slack


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
app = FastAPI()


### Config

class ConfigurationException(Exception):
    pass

config = {}
required_config = ["SLACK_SIGNING_SECRET", "SLACK_TOKEN"]
try:
    for var in required_config:
        config[var] = os.environ[var]
    for name, webhook in [(k,v) for (k,v) in os.environ.items() \
                          if k.startswith("SLACK_WEBHOOK_")]:
        config[name] = webhook
        logger.info("Found slack webhook config: {webhook}".format(
            webhook=webhook))
except KeyError:
    raise ConfigurationException("Missing environment variable: {var}".format(var=var))

### Handlers

@app.post("/events/")
def receive_event(body = Body(...)):
    """
    Respond to Slack events.

    Don't do any pre-validation of the body, just get the raw string.
    This is necessary to perform signature verification via HMAC SHA256.
    """

    event_wrapper = SlackEventType(**body)
    logger.debug("Receive event type: {et}".format(et=event_wrapper))

    if event_wrapper.type == "url_verification":
        # One time event by slack to verify our endpoint
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
        logger.debug("Received app mention: {e}".format(e=event))
        user = slack.users_info(event.user)
        slack.send_message(event.channel, "Hello @{name}".format(
            name=user['profile']['display_name']))
        return {"message": "ok"}
    else:
        logger.error("Cannot handle event: {e}".format(e=event))
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Unhandled event type: {et}".format(
                                et=event_wrapper.type))

@app.middleware("http")
async def verify_slack_signature(request: Request, call_next):
    """
    Slack Webhook client verification

    https://api.slack.com/docs/verifying-requests-from-slack
    """
    version = "v0"

    # Collect the body content:
    body = await request.body()
    body = body.decode("utf-8")

    # Calling request.body "consumed" the body.
    # Recreate the original request so that it remains intact:
    request = Request()


    # Get signature in request header:
    try:
        signature = request.headers['X-Slack-Signature']
    except KeyError:
        logger.error("No X-Slack-Signature header found in request")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    # Get timestamp in request header:
    try:
        timestamp = request.headers['X-Slack-Request-Timestamp']
    except KeyError:
        logger.error("No X-Slack-Request-Timestamp header found in request")
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    ## Prevent replay attacks by ignoring any requests outside the time window:
    time_window = 5 * 60
    time_lag = abs(time.time() - float(timestamp))
    if time_lag > time_window:
        logger.error(
            "Event outside of time window by {time_lag} seconds".format(
                time_lag=time_lag))
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    # Verify signature:
    try:
        verified = slack.verify_signature(
            signature,
            timestamp,
            body,
            config['SLACK_SIGNING_SECRET'],
            version)
        if not verified:
            raise slack.InvalidSlackSignatureException("slack.verify_signature returned False")
    except Exception as e:
        logger.error(type(e))
        logger.error(e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


    logger.info("Slack signature verified")
    # Process the request and await response:
    response = await call_next(request)
    return response
