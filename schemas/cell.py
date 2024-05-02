from pydantic_redis.asyncio import Model


class Cell(Model):
    _primary_key_field: str = "cords"
    cords: str  # координаты формата <x y> "костыльнинько, но по другому не придумал"
    color: str
