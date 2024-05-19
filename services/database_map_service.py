from repositories.database_map_repo import DataBaseMapRepo
from schemas.cell import Cell
from schemas.click import Click


class DataBaseMapService:
    def __init__(self, repo: DataBaseMapRepo):
        self.repo = repo

    async def get_all_map(self):
        return await self.repo.get_all_map()

    async def update_cell(self, cell: Cell):
        await self.repo.update_cell(cell)

    async def get_new_click(self):
        return await self.repo.get_new_click()

    async def add_new_click(self, click: Click):
        return await self.repo.add_new_click(click)

    async def get_count_clicks(self):
        return await self.repo.get_count_clicks()

    async def get_by_key(self, key: str):
        return await self.repo.get_by_key(key)

    async def set_by_key(self, key: str, value: str):
        return await self.repo.set_by_key(key, value)