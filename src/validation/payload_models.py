from pydantic import BaseModel
from fastapi import Query

class ClassifyFileRequest(BaseModel):
    filename: str
    customer_id: int

class ClassifyFileResponse(BaseModel):
    message: str
    data: dict