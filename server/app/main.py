from fastapi import FastAPI

from server.app.routes.users import router as users_router

app = FastAPI()

app.include_router(users_router, prefix="/api/users", tags=['users'])