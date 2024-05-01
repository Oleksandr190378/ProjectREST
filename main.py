import re
from typing import Callable
from fastapi import FastAPI, Request, status
from src.routes import contacts
from src.routes import auth, users
import uvicorn
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi.responses import JSONResponse
from src.conf.config import settings
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_agent_ban_list = [r"Googlebot", r"Python-urllib"]


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    response = await call_next(request)
    return response


app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    return {"message": "Contacts Application"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

