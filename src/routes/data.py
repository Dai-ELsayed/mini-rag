from fastapi import FastAPI, APIRouter, Depends, Upload_File
import os
from helper.config import get_settings, Settings

data_router= APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
async def uploade_data(project_id: str, file: Upload_File,
    app_setting : Settings = Depends(get_settings))
