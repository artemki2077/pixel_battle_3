from pydantic import BaseModel
from uuid import UUID, uuid4
import datetime as dt


class Click(BaseModel):
    x: int
    y: int
    color: str
    time: dt.datetime
