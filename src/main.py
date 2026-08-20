from fastapi import FastAPI
# from dotenv import load_dotenv
# load_dotenv(".env")
from routes import base, data
from motor.motor_asyncio import ASYNCIOMotorClient
from contextlib import asynccontextmanager
from helper.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    #startup
    settings= get_settings()
    app.mongo_conn=ASYNCIOMotorClient(settings.MONGODP_URL)
    app.db_client=app.mongo_conn[settings.MONGODP_DATABASE]

    yield

    # Shutdown
    app.mongo_conn.close()

    
app=FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)

