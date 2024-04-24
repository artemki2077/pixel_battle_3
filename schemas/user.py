from pydantic_redis.asyncio import Model
from uuid import UUID, uuid4
import datetime as dt


class User(Model):
    _primary_key_field: str = "username"
    username: str
    password_hash: str
    password_salt: str
    last_click: dt.datetime
