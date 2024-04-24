from pydantic_redis.asyncio import Model
from uuid import UUID, uuid4
import datetime as dt


class Click(Model):
    _primary_key_field: str = "id"
    id: int
    x: int
    y: int
    color: str
    time: dt.datetime
