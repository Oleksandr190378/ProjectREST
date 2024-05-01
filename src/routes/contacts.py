from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from src import crud, schemas
from src.database.db import get_db
from src.services.auth import auth_service

from src.database.models import User
from fastapi_limiter.depends import RateLimiter


router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.post("/", response_model=schemas.ContactResponse, description='No more than 10 requests per minute',
                         dependencies=[Depends(RateLimiter(times=10, seconds=60))], status_code=status.HTTP_201_CREATED)
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Create a new contact.

    Parameters:
        - contact (schemas.ContactCreate): The contact data to be created.
        - db (Session, optional): The database session. Defaults to the session obtained from the `get_db` dependency.
        - current_user (User, optional): The current authenticated user. Defaults to the user obtained from the `auth_service.get_current_user` dependency.

    Returns:
        - schemas.ContactResponse: The created contact.

    Raises:
        - HTTPException: If the email or phone number is already registered for the current user.

    Description:
        - This endpoint creates a new contact.
        - It checks if the email or phone number is already registered for the current user.
        - If either is already registered, it raises an HTTPException with a status code of 400 and a detail message indicating that the email or phone number is already registered.
        - If both are not already registered, it calls the `crud.create_contact` function to create the contact in the database.
        - The created contact is returned as a `schemas.ContactResponse` object.

    Limitations:
        - This endpoint has a rate limiter that allows no more than 10 requests per minute.
        - It sets the status code of the response to 201 Created.
    """
    db_contact_by_email = await crud.get_contact_by_email(db, email=contact.email, user=current_user)
    db_contact_by_phone = await crud.get_contact_by_phone(db, phone_number=contact.phone_number, user=current_user)
    if db_contact_by_email or db_contact_by_phone:
        raise HTTPException(status_code=400, detail="Email or phone number already registered")
    return await crud.create_contact(db=db, user=current_user, contact=contact)


@router.get("/", response_model=List[schemas.ContactResponse], description='No more than 10 requests per minute',
                         dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):

    contacts = await crud.get_contacts(db, skip=skip, limit=limit, user=current_user)
    return contacts


@router.get("/{contact_id}", response_model=schemas.ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a contact by its ID.

    Parameters:
        contact_id (int): The ID of the contact to retrieve.
        db (Session, optional): The database session. Defaults to the session obtained from the `get_db` dependency.
        user (User, optional): The current authenticated user. Defaults to the user obtained from the `auth_service.get_current_user` dependency.

    Returns:
        ContactResponse: The contact with the specified ID.

    Raises:
        HTTPException: If the contact with the specified ID is not found.
    """
    db_contact = await crud.get_contact(db, contact_id=contact_id, user=user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get("/search/", response_model=List[schemas.ContactResponse])
async def search_contacts(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user)
):
    contacts = await crud.search_contacts(db, first_name=first_name, last_name=last_name, email=email)
    return contacts


@router.get("/birthdays/", response_model=List[schemas.ContactResponse])
async def get_upcoming_birthdays(db: Session = Depends(get_db),
                                 user: User = Depends(auth_service.get_current_user)):
    today = date.today()
    end_date = today + timedelta(days=7)
    contacts = await crud.get_contacts_by_birthday_range(db, start_date=today, end_date=end_date, user=user)
    return contacts


@router.put("/{contact_id}", response_model=schemas.ContactResponse)
async def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    db_contact = await crud.get_contact(db, user=user, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.email and contact.email != db_contact.email:
        db_duplicate_email = await crud.get_contact_by_email(db, email=contact.email, user=user)
        if db_duplicate_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    if contact.phone_number and contact.phone_number != db_contact.phone_number:
        db_duplicate_phone = await crud.get_contact_by_phone(db, phone_number=contact.phone_number, user=user)
        if db_duplicate_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    return await crud.update_contact(db=db, db_contact=db_contact, contact=contact)


@router.delete("/{contact_id}", response_model=schemas.ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    db_contact = await crud.get_contact(db, contact_id=contact_id, user=user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return await crud.delete_contact(db=db, contact_id=contact_id, user=user)

