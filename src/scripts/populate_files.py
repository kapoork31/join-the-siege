import botocore.client
from sqlalchemy.orm import Session
from src.data_models.tables import Customer, File
import os
from botocore.client import BaseClient

def upload_to_s3(file_path: str, bucket_name: str, s3_key: str, s3_client) -> str: 
    """
    Uploads a file to the given S3 bucket.

    Args:
    - file_path (str): file path to upload.
    - bucket_name (str): S3 bucket name.
    - s3_key (str): key/path of the file in s3.

    Returns:
    - str: The S3 path of the uploaded file.
    """
    s3_client.upload_file(file_path, bucket_name, s3_key)
    return f"s3://{bucket_name}/{s3_key}"  # Return the S3 path


def add_file(session: Session, customer_id: int, filename: str, file_path: str, bucket_name: str, s3_client) -> File:
    """
    Adds a new file to the database after uploading it to S3.

    Args:
    - session (Session): The SQLAlchemy session to interact with the DB.
    - customer_id (int): customer ID
    - filename (str): name of file to.
    - file_path (str): local file path
    - bucket_name (str): S3 bucket name.

    Returns:
    - File: The newly created File object.
    """
    # Step 1: Upload the file to S3
    # upload to folder based on customer_id
    s3_key = f"{customer_id}/{filename}"  # You can structure S3 keys as needed
    s3_path = upload_to_s3(file_path, bucket_name, s3_key, s3_client)

    # can assume if a customer Id is being used to upload the equivalent customer will exist in DB
    # if not customer:
    #     raise ValueError(f"Customer with ID {customer_id} not found.")

    # Step 3: Create a new file record in the database
    new_file = File(filename=filename, s3Path=s3_key, customerId=customer_id)

    # Step 4: Add and commit the file record to the database
    session.add(new_file)
    session.commit()
    session.refresh(new_file)

    return new_file


def populate_files(session: Session, s3_client: BaseClient) -> None:
    """
    Function run on start up
    Will take all files from files folder and create items in the FILE table in the db with respective meta information
    This will create a base set of information in the DB to get started with.

    Args:
        session (Session): SQLAlchemy session to interact with the database.
        s3_client (boto3.client): Boto3 S3 client to interact with AWS S3 for file operations.
    
    Returns:
        None
    """
    
    # Local folder files to populate db with
    files_list = os.listdir('files')

    # Default to customer id 1 for initial upload
    customer_id = 1

    # Define parameters
    for f in files_list:
        filename = f
        file_path = "files/" + f
        bucket_name = "heron-data-test-bucket"
        
        # Call the function to add the file
        new_file = add_file(session, customer_id, filename, file_path, bucket_name, s3_client)