from fastapi import APIRouter, WebSocket, Depends, Request
from starlette import status
from depends import get_database_map_service
from starlette.responses import RedirectResponse
from config import TIME_WAIT

from schemas.cell import Cell
from schemas.click import Click
import datetime as dt
from services.database_map_service import DataBaseMapService

from depends import sessions_service
from schemas.sessions_data import SessionData

router = APIRouter(prefix="/map", tags=['map'])


@router.get("/", dependencies=[Depends(sessions_service.cookie)])
async def index_map(
    session_data: SessionData = Depends(sessions_service.verifier),
):
    if session_data is None:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    return RedirectResponse("/main", status_code=status.HTTP_302_FOUND)


@router.get("/all_map", dependencies=[Depends(sessions_service.cookie)])
async def get_all_map_api(
    session_data: SessionData = Depends(sessions_service.verifier),
    db_map: DataBaseMapService = Depends(get_database_map_service)
):
    if session_data is None:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    all_map = await db_map.get_all_map()
    if all_map is None:
        return {
            "ok"        : True,
            "result"    : [],
            "last_click": session_data.last_click.isoformat()
        }
    return {
        "ok"        : True,
        "result"    : list(map(lambda x: x.model_dump(mode="json"), all_map)),
        "last_click": session_data.last_click.isoformat()
    }


@router.post("/click", dependencies=[Depends(sessions_service.cookie)])
async def click(
    request: Request,
    session_data: SessionData = Depends(sessions_service.verifier),
    db_map: DataBaseMapService = Depends(get_database_map_service),
):
    if session_data is None:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

    if dt.datetime.now() - session_data.last_click < TIME_WAIT:
        return {
            "ok"            : False,
            "result"        : "wait",
            "last_click"    : session_data.last_click.isoformat(),
            "TIME_WAIT"     : TIME_WAIT,
            "time_left"     : (dt.datetime.now() - session_data.last_click).seconds,
            "time_left_type": "sec"
        }

    data: dict = await request.json()

    if data.get("x") is None or data.get("y") is None or data.get("color") is None:
        return {
            "ok"    : False,
            "result": "not x or not y or not color"
        }

    cell = Cell(
        cords=f"{data.get('x')} {data.get('y')}",
        color=data.get("color")
    )
    click = Click(
        x=data.get('x'),
        y=data.get('y'),
        color=data.get("color"),
        time=dt.datetime.now()
    )

    await db_map.update_cell(cell)
    await db_map.add_new_click(click)
    return {
        "ok"    : True,
        "result": "success"
    }


@router.websocket("/connection")
async def ws_map(
    websocket: WebSocket,
    db_map: DataBaseMapService = Depends(get_database_map_service)
):
    await websocket.accept()
    while True:
        clicks = await db_map.get_new_click()
        if clicks is not None:
            for click in clicks:
                await websocket.send_json(click.model_dump(mode="json"))