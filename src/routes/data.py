from fastapi import FastAPI, APIRouter, Depends, UploadFile
import os
from helper.config import get_settings, Settings
# from controllers import DataController
from controllers.DataController import DataController

data_router= APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
async def uploade_data(project_id: str, file: UploadFile,
app_settings : Settings = Depends(get_settings)):

    #we validate data(the logic) in DataController
    # validate
    data_controller=DataController()
    is_valid= data_controller.validate_uploade_file(file=file)

    return is_valid


