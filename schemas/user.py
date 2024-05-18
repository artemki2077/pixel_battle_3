from pydantic_redis.asyncio import Model
from uuid import UUID, uuid4
import datetime as dt
from enum import Enum


class UserRole(Enum):
    user = "User"
    admin = "Admin"


class UserStatus(Enum):
    at_registration = "registration"
    activated = "activated"


class User(Model):
    _primary_key_field: str = "username"
    username: str
    password_hash: str | None = None
    password_salt: str | None = None
    role: UserRole = UserRole.user
    status: UserStatus = UserStatus.at_registration
    last_click: dt.datetime
    count_click: int = 0