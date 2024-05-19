import redis
from pydantic_redis import RedisConfig
from pydantic_redis.asyncio import Store
from redis import asyncio as aioredis
from schemas.cell import Cell
from typing import Optional

from schemas.click import Click


class DataBaseMapRepo:
    def __init__(self, host: str = "localhost", port: int = 6379, decode_responses: bool = True, password: Optional[str] = None, store_cell_name: str = "cell_store"):
        self.host = host
        self.port = port
        self.size = 100
        self.redis = aioredis.StrictRedis(
            host=host,
            port=port,
            decode_responses=decode_responses,
            password=password,
            health_check_interval=10,
            socket_timeout=10,
            socket_keepalive=True,
            socket_connect_timeout=10,
            retry_on_timeout=True
        )
        self.stream_click_name = "stream_clicks"
        self.redisConfig = RedisConfig(
            host=host,
            port=port,
            password=password
        )
        self.store = Store(
            name=store_cell_name,
            redis_config=self.redisConfig
        )
        self.store_cell_name = store_cell_name
        self.store.register_model(Cell)
        self.Cell = Cell

    async def get_all_map(self):
        return await self.Cell.select()

    async def update_cell(self, cell: Cell):
        await self.Cell.insert(cell)

    async def get_count_clicks(self):
        return await self.redis.xlen(self.stream_click_name)

    async def get_by_key(self, key: str):
        return await self.redis.get(key)

    async def set_by_key(self, key: str, value: str):
        return await self.redis.set(key, value)

    async def get_new_click(self) -> list[Click] | None:
        try:
            res = await self.redis.xread({self.stream_click_name: "$"}, block=0)
            if res:
                res = res[0][1]
                res = list(map(lambda x: Click(**x[1]), res))
                return res
        except redis.exceptions.TimeoutError:
            return None

    async def add_new_click(self, click: Click):
        return await self.redis.xadd(self.stream_click_name, click.model_dump(mode="json"))