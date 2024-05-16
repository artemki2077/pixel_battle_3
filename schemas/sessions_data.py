from pydantic import BaseModel
import datetime as dt


class SessionData(BaseModel):
    username: str