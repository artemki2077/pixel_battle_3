from uuid import uuid4, UUID
from fastapi import APIRouter, Depends, Request, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette import status

from depends import sessions_service
from schemas.sessions_data import SessionData
from fastapi.staticfiles import StaticFiles
from services.database_service import DataBaseService
from services.sessions_service import SessionsService
from depends import get_sessions_service, get_database_service
# from depends import sessions_service
import datetime as dt

router = APIRouter(prefix="/auth", tags=["authorization"])


@router.get("/", dependencies=[Depends(sessions_service.cookie)])
async def index_authorization(session_data: SessionData = Depends(sessions_service.verifier)):
    if session_data is None:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    return RedirectResponse("/map", status_code=status.HTTP_302_FOUND)


@router.post("/login", dependencies=[Depends(sessions_service.cookie)])
async def post_login_authorization(
    request: Request,
    response: Response,
    session_data: SessionData = Depends(sessions_service.verifier),
    dataBaseService: DataBaseService = Depends(get_database_service),
    sessionsService: SessionsService = Depends(get_sessions_service)
):
    user_data = await request.json()

    if user_data.get("username") is None or user_data.get("password") is None:
        raise HTTPException(status_code=401, detail="the username or password parameter is missing in the request")

    username = user_data.get("username")
    password = user_data.get("password")
    database_response = await dataBaseService.get_user_by_username(username)

    if database_response is None:
        raise HTTPException(status_code=401, detail="not such username")

    user = database_response[0]
    hashed_getter_pass = dataBaseService.hash_pass(password, user.password_salt)
    if hashed_getter_pass != user.password_hash:
        raise HTTPException(status_code=401, detail="wrong password")

    session = uuid4()
    data = SessionData(
        username=user.username,
        last_click=user.last_click.isoformat()
    )
    await sessionsService.backend.create(session, data)
    sessionsService.cookie.attach_to_response(response, session)

    return RedirectResponse("/map", status_code=status.HTTP_302_FOUND)


@router.get("/logout", dependencies=[Depends(sessions_service.cookie)])
async def post_logout_authorization(
    response: Response,
    session_id: UUID = Depends(sessions_service.cookie),
    sessionsService: SessionsService = Depends(get_sessions_service)
):
    await sessionsService.backend.delete(session_id)
    sessionsService.cookie.delete_from_response(response)
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)