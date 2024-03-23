from pydantic import BaseModel
import datetime as dt


class SessionData(BaseModel):
    id: int
    username: str
    last_click: dt.datetime