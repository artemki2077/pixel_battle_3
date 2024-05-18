from pydantic_redis.asyncio import Model, Store, RedisConfig
from typing import Optional, Dict, Any
from schemas.user import User
import hashlib


class DataBaseUserRepo:
    def __init__(self, name: str = "user_store", redis_config: Optional[RedisConfig] = None):
        self.store = Store(
            name=name,
            redis_config=redis_config if redis_config is not None else RedisConfig()
        )
        self.store.register_model(User)
        self.User_model = User

    @staticmethod
    def sha256(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def hash_pass(self, value: str, salt: str) -> str:
        return self.sha256(f'{value}:{salt}')

    async def get_user_by_username(self, username: str) -> User | dict[str, Any] | None:
        return await self.User_model.select(ids=[username], limit=1)

    async def add_user(self, user: User):
        await self.User_model.insert(user)

    async def add_users(self, user: list[User]):
        await self.User_model.insert(user)