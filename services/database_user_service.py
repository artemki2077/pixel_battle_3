from repositories.database_user_repo import DataBaseUserRepo
from schemas.user import User


class DataBaseUserService:
    def __init__(self, repo: DataBaseUserRepo):
        self.repo = repo

    async def get_user_by_username(self, username: str):
        return await self.repo.get_user_by_username(username)

    async def add_user(self, user: User):
        await self.repo.add_user(user)

    async def add_users(self, user: list[User]):
        await self.repo.add_users(user)

    def hash_pass(self, value: str, salt: str):
        return self.repo.hash_pass(value, salt)
