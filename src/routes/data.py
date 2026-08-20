from fastapi import FastAPI, APIRouter, Depends, UploadFile , status, Request
from fastapi.responses import JSONResponse
import os
from helper.config import get_settings, Settings
from controllers import DataController, ProjectController , ProcessController
from models import ResponseSignal
from models.ProjectModel import ProjectModel
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
async def uploade_data(Request:Request, project_id: str, file: UploadFile,
app_settings : Settings = Depends(get_settings)):

    project_model=ProjectModel(db_client=Request.app.db_client)
    project= await project_model.get_project_or_create_one(
        project_id=project_id
    )
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
         'file_id':file_id,
         "project_id": str(project._id)
     }   
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(project_id: str, ProcessRequest:ProcessRequest):
    file_id =ProcessRequest.file_id
    chunk_size=ProcessRequest.chunk_size
    overlap_size=ProcessRequest.overlap_size

    processcontroller=ProcessController(project_id=project_id)

    file_content=processcontroller.get_file_content(file_id=file_id)

    file_chunks= processcontroller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size= chunk_size,
        overlap_size=overlap_size
    )

    if file_chunks is None or len(file_chunks)==0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                'signal':ResponseSignal.PROCESSING_FAILED
            }
        )

    return file_chunks


    
        

    

