from pydantic import BaseModel

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
