from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional


class ContactBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=15)
    birthday: date
    additional_data: Optional[str] = Field(None, max_length=250)


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    completed: bool


class ContactResponse(ContactBase):
    id: int

    class Config:
        from_attributes = True

