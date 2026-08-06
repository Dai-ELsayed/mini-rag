from fastapi import FastAPI, APIRouter, Depends
import os
from helper.config import get_settings, Settings

base_router=APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)

@base_router.get("/")
async def welcome(app_setting : Settings = Depends(get_settings)): # more efficent
    # app_setting= get_settings()
    ##when use load env
    # app_name=os.getenv("APP_NAME") 
    # app_version=os.getenv("APP_VERSION")
    app_name= app_setting.APP_NAME
    app_version= app_setting.APP_VERSION
    return {
     "app_name":"app_name",
     "app_version":"app_version"
    }