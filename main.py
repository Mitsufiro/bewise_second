import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.staticfiles import StaticFiles
from routers import client,audio

load_dotenv(".env")
app = FastAPI(title="BEWISE Service", version="0.0.1")
app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.include_router(client.ROUTER)
app.include_router(audio.ROUTER)
