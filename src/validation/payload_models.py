from pydantic import BaseModel

class ClassifyFileRequest(BaseModel):
    filename: str
    customer_id: int

class ClassifyFileResponse(BaseModel):
    message: str
    data: dict