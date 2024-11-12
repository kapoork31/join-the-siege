from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define the base class for all data models
Base = declarative_base()

# Customer table class
# store meta information for a customer
class Customer(Base):
    __tablename__ = 'customers'  # Table name

    # Define the columns for the 'customers' table
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # Relationship between Customer and File
    files = relationship("File", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name})>"

# File table class
# store meta information for a file
class File(Base):
    __tablename__ = 'files'  # The table name in the database

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)  # The name of the file
    s3Path = Column(String, nullable=False)  # The path where the file is stored in S3
    customerId = Column(Integer, ForeignKey('customers.id'))  # Foreign key to link to the Customer table
    fileClassification = Column(String, nullable=True)  # This will store the classification result

    # Relationship to the Customer model
    customer = relationship("Customer", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, filename={self.filename}, s3Path={self.s3Path}, fileClassification={self.fileClassification})>"
