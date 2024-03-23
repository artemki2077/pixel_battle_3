from fastapi import APIRouter, Depends, Response
from fastapi.responses import RedirectResponse
from depends import sessions_service
from schemas.sessions_data import SessionData

router = APIRouter(prefix="/auth", tags=["authorization"])


@router.get("/", dependencies=[Depends(sessions_service.cookie)])
async def index_authorization(session_data: SessionData = Depends(sessions_service.verifier)):
    if session_data is None:
        return RedirectResponse("/login")
    return "test"


@router.get("login")
def login_authorization(response: Response):
    return