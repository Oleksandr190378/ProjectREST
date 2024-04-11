from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from src import crud, schemas
from src.database.db import get_db
from src.database import models


router = APIRouter()


@router.post("/contacts/", response_model=schemas.ContactResponse)
async def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact_by_email = await crud.get_contact_by_email(db, email=contact.email)
    db_contact_by_phone = await crud.get_contact_by_phone(db, phone_number=contact.phone_number)
    if db_contact_by_email or db_contact_by_phone:
        raise HTTPException(status_code=400, detail="Email or phone number already registered")
    return await crud.create_contact(db=db, contact=contact)


@router.get("/contacts/", response_model=List[schemas.ContactResponse])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await crud.get_contacts(db, skip=skip, limit=limit)
    return contacts


@router.get("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = await crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get("/contacts/search/", response_model=List[schemas.ContactResponse])
async def search_contacts(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    contacts = await crud.search_contacts(db, first_name=first_name, last_name=last_name, email=email)
    return contacts


@router.get("/contacts/birthdays/", response_model=List[schemas.ContactResponse])
async def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    end_date = today + timedelta(days=7)
    contacts = await crud.get_contacts_by_birthday_range(db, start_date=today, end_date=end_date)
    return contacts



@router.put("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def update_contact(contact_id: int, contact: schemas.ContactUpdate, db: Session = Depends(get_db)):
    db_contact = await crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.email and contact.email != db_contact.email:
        db_duplicate_email = await crud.get_contact_by_email(db, email=contact.email)
        if db_duplicate_email:
            raise HTTPException(status_code=400, detail="Email already registered")
    if contact.phone_number and contact.phone_number != db_contact.phone_number:
        db_duplicate_phone = await crud.get_contact_by_phone(db, phone_number=contact.phone_number)
        if db_duplicate_phone:
            raise HTTPException(status_code=400, detail="Phone number already registered")
    return await crud.update_contact(db=db, db_contact=db_contact, contact=contact)



@router.delete("/contacts/{contact_id}", response_model=schemas.ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = await crud.get_contact(db, contact_id=contact_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return await crud.delete_contact(db=db, contact_id=contact_id)
