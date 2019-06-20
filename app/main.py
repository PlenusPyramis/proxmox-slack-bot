from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

class SlackEventModel(BaseModel):
    type: str
    event_ts: str

class SlackEventTypeModel(BaseModel):
    type: str
    token: str = None
    team_id: str = None
    api_app_id: str = None
    event: SlackEventModel = None
    challenge: str = None

app = FastAPI()

@app.post("/events/")
def receive_event(event: SlackEventTypeModel):
    """
    Respond to Slack events
    """
    # TODO : verify slack signature

    if event.type == "url_verification":
        # Respond to initial URL verification:
        # See: https://api.slack.com/events-api#events_api_request_urls
        return {"challenge": event.challenge}
    else:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="Unhandled event type")
