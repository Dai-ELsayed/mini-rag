from fastapi import FastAPI, APIRouter, Depends, UploadFile , status
from fastapi.responses import JSONResponse
import os
from helper.config import get_settings, Settings
from controllers import DataController, ProjectController
from models import ResponseSignal
# from controllers.DataController import DataController
import aiofiles
import logging
from .schema.data import ProcessRequest

logger=logging.getLogger("uvicorn.error")


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
    is_valid, result_signal= data_controller.validate_uploade_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "result_signal":result_signal

            })
    project_path_dir=ProjectController().get_project_path(project_id)
    file_path, file_id= data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:

        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULTE_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"error while uploading file: {e}")
        return JSONResponse(
        status_code= status.HTTP_400_BAD_REQUEST,
        content={
            "result_signal":ResponseSignal.FILE_UPLOAD_FAILED.value
            })
    
    return JSONResponse(
     content={
         "signal":ResponseSignal.FILE_UPLOAD_SUCCESS.value,
         'file_id':file_id
     }   
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, ProcessRequest:ProcessRequest):
    file_id =ProcessRequest.file_id

    return file_id
    
        

    

