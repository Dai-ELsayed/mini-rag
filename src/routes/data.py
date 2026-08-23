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
from models.db_schemes import DataChunk
from models.ChunkModel import ChunkModel

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
         "project_id": str(project.id)
     }   
    )

@data_router.post("/process/{project_id}")
async def process_endpoint(Request:Request,project_id: str, ProcessRequest:ProcessRequest):
    file_id =ProcessRequest.file_id
    chunk_size=ProcessRequest.chunk_size
    overlap_size=ProcessRequest.overlap_size
    do_reset= ProcessRequest.do_reset

    project_model=ProjectModel(db_client=Request.app.db_client)
    project= await project_model.get_project_or_create_one(
            project_id=project_id
        )
    

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

    file_chunks_records=[
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,
        )
        for i , chunk in enumerate(file_chunks)
    ]

    chunk_model=ChunkModel(db_client=Request.app.db_client)



    if do_reset == 1:
        deleted_count = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )


    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )



    
        

    

