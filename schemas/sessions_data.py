from pydantic import BaseModel
import datetime as dt


class SessionData(BaseModel):
    username: str
    last_click: dt.datetime