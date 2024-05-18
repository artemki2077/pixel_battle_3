from pydantic import BaseModel
from uuid import UUID, uuid4
import datetime as dt


class Click(BaseModel):
    username: str
    x: int
    y: int
    color: str
    time: dt.datetime

