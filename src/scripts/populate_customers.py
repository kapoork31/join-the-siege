# crud_operations.py
from sqlalchemy.orm import Session
from src.data_models.tables import Customer

def add_customer(name: str, session: Session) -> Customer:
    """
    Adds a new customer to the database.

    Args:
        name (str): The name of the customer to be added.
        session (Session): The SQLAlchemy session to interact with the database.

    Returns:
        Customer: The newly created customer object with the assigned ID.
    """
    new_customer = Customer(name=name)
    session.add(new_customer)
    session.commit()
    session.refresh(new_customer)  # Refresh to get the newly assigned ID
    return new_customer

def get_customers(session: Session) -> list[Customer]:
    """
    Queries and returns all customers from the database.

    Args:
        session (Session): The SQLAlchemy session to interact with the database.

    Returns:
        list[Customer]: A list of all Customer objects in the database.
    """
    customers = session.query(Customer).all()
    return customers

def populate_customers(session: Session) -> None:
    """
    Populates the database with a sample customer.

    Args:
        session (Session): The SQLAlchemy session to interact with the database.

    Returns:
        None
    """
    # Add a new customer
    new_customer = add_customer("John Doe", session)
