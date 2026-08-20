from pydantic import Field, BaseModel, field_validator
from typing import Optional
from bson.objectid import ObjectId  # from motor

class project(BaseModel):
    id:Optional[ObjectId]
    project_id:str = Field(..., min_length=1)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")

        return value

    class config:
        arbitrary_types_allowed = True