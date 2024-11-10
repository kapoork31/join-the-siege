import functools
import logging
from typing import Any, Callable
import asyncio
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from botocore.exceptions import ClientError
from sqlalchemy.orm import Session
from botocore.client import BaseClient

from src.errors import FileExtensionNotSupported
from src.data_models.tables import File as FileModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""
    logging function
    wraps all endpoints which allows to have consistent
    logging for all endopints
"""



def logging_decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            # Run the function and get the result (support async and sync functions)
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            return JSONResponse(status_code=200, content={"message": "Success", "data": result})

        except FileExtensionNotSupported as e:
            # Log the error and provide a response with status code and message
            log_detail = {
                "message": e.msg,
                "status_code": e.status_code
            }
            logger.exception(f"File type error: {e.msg}")
            logging.info("File type error detected", extra=log_detail)
            return JSONResponse(status_code=e.status_code, content={"message": e.msg})

        except HTTPException as http_exc:
            # Log HTTPException details and provide a structured response
            logger.exception(
                f"HTTPException raised in {func.__name__}: {http_exc.detail} (status code: {http_exc.status_code})"
            )
            return JSONResponse(status_code=http_exc.status_code, content={"message": http_exc.detail})

        except Exception as e:
            # Log the unexpected error and provide a generic response
            logger.exception(f"Unexpected error in {func.__name__}: {str(e)}")
            return JSONResponse(status_code=500, content={"message": "An internal server error occurred"})

    return wrapper


def download_file(s3_connection: BaseClient, bucket: str, s3_path: str) -> bytes:
    try:
        s3_object = s3_connection.get_object(Bucket=bucket, Key=s3_path)
        return s3_object["Body"].read()
    except s3_connection.s3.exceptions.NoSuchKey:
        raise FileNotFoundError(f"File '{s3_path}' not found in S3")
    except ClientError as e:
        raise Exception(f"Error accessing S3: {e}")

# add the 
def update_file_classification(db: Session, file_metadata: FileModel, file_class: str) -> None:
    try:
        # Update the file classification in the database
        file_metadata.fileClassification = file_class  # Set the classification

        # Commit the changes to the database
        db.commit()
        db.refresh(file_metadata)  # Optionally refresh the instance to get the updated values

        logging.info(f"File classification updated to '{file_class}' for file {file_metadata.filename}")

    except Exception as e:
        logging.error(f"Error updating file classification for {file_metadata.filename}: {str(e)}")
        db.rollback()  # Rollback in case of error
        raise Exception(f"Failed to update file classification for {file_metadata.filename}")
