from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from routing.authorization import router as router_authorization
import starlette.status as status
import uvicorn

app = FastAPI(title="pixel battle 3", description="Это третий сезон пиксель батла, всех приветствую, надеюсь будет весело и наберётся много народу))")

app.include_router(router_authorization)


@app.get("/")
async def index():
    return "test"
    # return RedirectResponse("/auth", status_code=status.HTTP_302_FOUND)


if __name__ == '__main__':
    uvicorn.run(app, port=8000)