"""
This module manages the connection to the database using SQLAlchemy and variables needed to connect to the DB

- Establishes a connection to the database using the URL stored in environment variables.
- Creates a session factory (`SessionLocal`) to interact with the database.
- Provides a `create_tables` function to create all database tables defined in the models.

The module is responsible for setting up and managing the database as well as connecting to the db
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

from src.data_models.tables import Base

# Load in env vars
load_dotenv()

# get DB URL from env file
DATABASE_URL = os.getenv("DATABASE_URL")

# create connection to the DB.
# For sqlite specifically, this is when the test.db file is created
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# object with which we can access the db
# its used to create db connections by instatiant the object such as db = SessionLocal()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to create tables
def create_tables():
    """
    Creates all tables in the database based on the SQLAlchemy Base metadata class.
    Those are the tables that inherit the SQLAlchemy Base class

    Returns:
        None
    """
    Base.metadata.create_all(bind=engine)