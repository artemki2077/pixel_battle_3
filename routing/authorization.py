from uuid import uuid4, UUID
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette import status

from depends import sessions_service
from schemas.sessions_data import SessionData
from fastapi.staticfiles import StaticFiles
from services.database_user_service import DataBaseUserService
from services.sessions_service import SessionsService
from depends import get_sessions_service, get_database_user_service
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import datetime as dt

router = APIRouter(prefix="/auth", tags=["authorization"])

templates_login = Jinja2Templates(directory="frontend/login/templates")
router.mount("/auth/static", StaticFiles(directory="frontend/login/static"), name="static_login")


@router.get("/", dependencies=[Depends(sessions_service.cookie)])
async def index_authorization(session_data: SessionData = Depends(sessions_service.verifier)):
    if session_data is None:
        return RedirectResponse("/auth/login", status_code=status.HTTP_302_FOUND)
    return RedirectResponse("/map", status_code=status.HTTP_302_FOUND)


@router.get("/login", dependencies=[Depends(sessions_service.cookie)], response_class=HTMLResponse)
async def get_login_authorization(
    request: Request,
    dataBaseUserService: DataBaseUserService = Depends(get_database_user_service),
    sessionsService: SessionsService = Depends(get_sessions_service),
    session_data: SessionData = Depends(sessions_service.verifier)
):
    if session_data is not None:
        return RedirectResponse("/map", status_code=status.HTTP_302_FOUND)
    return templates_login.TemplateResponse(
        request=request, name="index.html", context={
            "result": ""
        }
    )


@router.post("/login", dependencies=[Depends(sessions_service.cookie)])
async def post_login_authorization(
    request: Request,
    dataBaseUserService: DataBaseUserService = Depends(get_database_user_service),
    sessionsService: SessionsService = Depends(get_sessions_service)
):
    user_data = await request.form()
    # user_data = await request.json()

    if not user_data.get("username") or not user_data.get("password"):
        return templates_login.TemplateResponse(
            request=request, name="index.html", context={
                "result": "в запросе на авторизацию не хватает данных"
            }
        )

    username: str = user_data.get("username")
    password: str = user_data.get("password")

    if username.startswith("@"):
        username = username[1:]
    username = username.lower()

    database_response = await dataBaseUserService.get_user_by_username(username)

    if database_response is None:
        return templates_login.TemplateResponse(
            request=request, name="index.html", context={
                "result": "Данного пользователя не существует"
            }
        )

    user = database_response[0]
    hashed_getter_pass = dataBaseUserService.hash_pass(password, user.password_salt)
    if hashed_getter_pass != user.password_hash:
        return templates_login.TemplateResponse(
            request=request, name="index.html", context={
                "result": "Не правильный пароль или логин"
            }
        )

    session = uuid4()
    data = SessionData(
        username=user.username,
        last_click=user.last_click.isoformat()
    )
    await sessionsService.backend.create(session, data)
    response = RedirectResponse("/map", status_code=status.HTTP_302_FOUND)
    sessionsService.cookie.attach_to_response(response, session)

    return response


@router.get("/logout", dependencies=[Depends(sessions_service.cookie)])
async def post_logout_authorization(
    session_id: UUID = Depends(sessions_service.cookie),
    sessionsService: SessionsService = Depends(get_sessions_service)
):
    await sessionsService.backend.delete(session_id)
    response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    sessionsService.cookie.delete_from_response(response)
    return response