from uuid import UUID, uuid4
from fastapi_sessions.backends.implementations import InMemoryBackend
from schemas.sessions_data import SessionData


class SessionBackendRepo:
    def __init__(self):
        self.backend = InMemoryBackend[UUID, SessionData]()

    async def delete(self, sessions_id: UUID):
        return await self.backend.delete(sessions_id)

    async def create(self, data: SessionData):
        uid = uuid4()
        return await self.backend.create(uid, data)