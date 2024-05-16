from fastapi import APIRouter, WebSocket, Depends, Request
from starlette import status
from depends import get_database_map_service, get_database_user_service
from starlette.responses import RedirectResponse
from config import TIME_WAIT
from schemas.cell import Cell
from schemas.click import Click
import datetime as dt
from services.database_map_service import DataBaseMapService
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from depends import sessions_service
from schemas.sessions_data import SessionData
from services.database_user_service import DataBaseUserService

router = APIRouter(prefix="/map", tags=['map'])

templates_map = Jinja2Templates(directory="frontend/map/templates")


@router.get("/", dependencies=[Depends(sessions_service.cookie)])
async def index_map(
    request: Request,
    session_data: SessionData = Depends(sessions_service.verifier),
):
    if session_data is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)
    return templates_map.TemplateResponse(
        request=request, name="index.html", context={}
    )


@router.get("/all_map", dependencies=[Depends(sessions_service.cookie)])
async def get_all_map_api(
    session_data: SessionData = Depends(sessions_service.verifier),
    db_map: DataBaseMapService = Depends(get_database_map_service),
    db_users: DataBaseUserService = Depends(get_database_user_service)
):
    if session_data is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)

    users = await db_users.get_user_by_username(session_data.username)

    if not users:
        return RedirectResponse("/auth/logout", status_code=status.HTTP_302_FOUND)

    user = users[0]
    all_map = await db_map.get_all_map()
    if all_map is None:
        return {
            "ok"        : True,
            "result"    : [],
            "last_click": user.last_click.isoformat()
        }
    return {
        "ok"        : True,
        "result"    : list(map(lambda x: x.model_dump(mode="json"), all_map)),
        "last_click": user.last_click.isoformat()
    }


@router.post("/click", dependencies=[Depends(sessions_service.cookie)])
async def click(
    request: Request,
    session_data: SessionData = Depends(sessions_service.verifier),
    db_map: DataBaseMapService = Depends(get_database_map_service),
    db_users: DataBaseUserService = Depends(get_database_user_service)
):
    if session_data is None:
        return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)

    users = await db_users.get_user_by_username(session_data.username)
    if not users:
        return RedirectResponse("/auth/logout", status_code=status.HTTP_302_FOUND)

    user = users[0]
    print(dt.datetime.now() - user.last_click)
    if dt.datetime.now() - user.last_click < TIME_WAIT:
        return {
            "ok"            : False,
            "result"        : "wait",
            "last_click"    : user.last_click.isoformat(),
            "TIME_WAIT"     : TIME_WAIT,
            "time_left"     : (TIME_WAIT - (dt.datetime.now() - user.last_click)).seconds,
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
    user.last_click = dt.datetime.now()

    await db_users.add_user(user)
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
            for e_click in clicks:
                await websocket.send_json(e_click.model_dump(mode="json"))