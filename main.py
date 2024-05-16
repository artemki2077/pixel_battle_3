from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from routing.authorization import router as router_authorization
from routing.map import router as router_map
from fastapi.middleware.cors import CORSMiddleware
import starlette.status as status
import uvicorn

app = FastAPI(title="pixel battle 3", description=
    """
        Это третий сезон пиксель батла, всех приветствую, надеюсь будет весело и наберётся много народу)), 
        после окончание сезона исходники проекта выложу у себя на гите(http://github.com/artemki2077)
    """
)

app.include_router(router_authorization)
app.include_router(router_map)
app.mount("/auth/static", StaticFiles(directory="frontend/login/static"), name="static_login")
app.mount("/map/static", StaticFiles(directory="frontend/map/static"), name="static_map")
# app.mount("/login", StaticFiles(directory="frontend/login/dist", html=True), name="static")
# app.mount("/main", StaticFiles(directory="frontend/map/dist", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)


if __name__ == '__main__':
    uvicorn.run(app, port=8000)