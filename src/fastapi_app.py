from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
import shutil
import boto3
import os
from fastapi.responses import JSONResponse
import logging
from io import BytesIO
from dotenv import load_dotenv

from src.scripts.populate_customers import populate_customers
from src.scripts.populate_files import add_file, populate_files  # Ensure you import add_file
from src.classifier import classify_file_ml
from src.connectors.db_connector import SessionLocal, create_tables
from src.data_models.tables import File as FileModel
from src.utils.utils import logging_decorator, download_file, update_file_classification    
from src.validation.file_type_validation import allowed_file
from src.validation.payload_models import ClassifyFileRequest, ClassifyFileResponse
from src.utils.extract_text import extract_text_from_file
# Load in env vars
load_dotenv()

# get DB URL from env file
BUCKET_NAME = os.getenv("BUCKET_NAME")

app = FastAPI()

# S3 dependency
def get_s3_client():
    return boto3.client('s3')

# fast api dependency to get the database session
# will create a session when the api is hit, and then kill this session when the endpoint returns
# simply put one session for each request and can be reused throughout the request
# only limiting factor is the scale at which requets are created and need to aware of spamming db with reads
# can use a pool here/ limit thread count on the uvicorn workers etc
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# run this code when app is started/ IE when deployed to prepopulate DB/S3 with some data to use
@app.on_event("startup")
def startup():

    # Only remove the existing DB file if it exists
    db_file = 'test.db'
    if os.path.exists(db_file):
        os.remove(db_file)

    create_tables()  # Ensure tables are created at app startup
    
    # populate customers, only customer 1 will eixst
    with SessionLocal() as session:
        populate_customers(session)
    
    # populate files
    with SessionLocal() as session:
        populate_files(session, get_s3_client())


# Define the upload directory
UPLOAD_DIRECTORY = "./uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @app.post("/uploadfile/", status_code=status.HTTP_201_CREATED)
# @logging_decorator
# async def upload_file(customer_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):

#     file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

#     # Save file temporarily
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)


#     #Upload file to S3 and add file record to database
#     try:
#         new_file = add_file(db, customer_id, file.filename, file_path, bucket_name, s3_client)
#     finally:
#         os.remove(file_path)  # Cleanup temporary file after upload

#     return JSONResponse(
#         content={
#             "filename": new_file.filename,
#             "s3_path": new_file.s3Path,
#             "file_id": new_file.id
#         },
#         status_code=200  # Explicitly setting the status code
#     )

@app.post("/classify_file", response_model = ClassifyFileResponse)
@logging_decorator
async def classify_file(
    request: ClassifyFileRequest,
    db: Session = Depends(get_db),
    s3_client = Depends(get_s3_client)
):

    logging.info(f"reading from db  customer {request.customer_id} and file {request.filename}")

    # Check if file extension is allowed
    allowed_file(request.filename)
    
    file_metadata = db.query(FileModel).filter(FileModel.customer_id == request.customer_id, FileModel.filename == request.filename).first()

    # if no file found raise error
    if not file_metadata:
        raise HTTPException(status_code=404, detail= f"File {request.filename} not found for customer {request.customer_id}")

    # Get the s3Path from the metadata
    s3_path = file_metadata.s3Path

    # get file from S3
    # create file bytes object
    # then classify the file using
    # return json response with file_class for given filename and customer_id
    try:
        # Fetch the file from S3 using the s3_path

        file_content = download_file(s3_client, bucket = BUCKET_NAME, s3_path = s3_path)

        # Create a BytesIO object to simulate a file-like object
        file_bytes = BytesIO(file_content)

        try:
            text = extract_text_from_file(file_bytes, request.filename)
        except ValueError as e:
            print(e)


        file_class = classify_file_ml(text)
        
        # Write file classification to db for give  customer and file name
        update_file_classification(db, file_metadata, file_class)

        # Construct the response body
        response_body = {   
                "file_class": file_class,
                "filename": request.filename,
                "customer_id": request.customer_id
        }

        logging.info(f"Classification Response: {response_body}")

        # Return classification result
        return response_body

    except Exception as e:
        logger.error(f"Error processing: {e}")
        raise HTTPException(status_code=500, detail="Error processing")


@app.get("/get_file")
async def get_file_by_filename_and_customer(
    filename: str,  # Query parameter for the filename
    customer_id: int,  # Query parameter for the customer_id
    db: Session = Depends(get_db)  # Dependency for the database session
):
    # Query the File model to get the file metadata
    file_metadata = db.query(FileModel).filter(
        FileModel.filename == filename, FileModel.customer_id == customer_id
    ).first()

    # If file not found, raise 404 error
    if not file_metadata:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found for customer {customer_id}")

    # Return the file metadata as JSON response
    return file_metadata